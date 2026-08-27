from __future__ import annotations

from engine_revival.brender_json_receipt import json_receipt_helpers_source


def asset_audit_source() -> str:
    """C source for the BRender portable-core asset-audit rung.

    First rung of the R4 asset pipeline: load arbitrary .dat model assets with
    BRender's own BrModelLoad and walk their geometry without rendering,
    validating the invariants the remaster lane depends on and emitting one
    machine-readable JSON summary per model. Assets are audited in place; the
    archive still vendors no game assets.
    """
    return r"""/*
 * BRender v1.3.2 portable-core asset-audit rung.
 *
 * R4 seam of the remaster lane: instead of rendering, this rung loads real
 * .dat models with BrModelLoad and validates the structural invariants that
 * downstream asset-pipeline work depends on:
 *
 *   - vertex coordinates finite
 *   - every face's three vertex indices inside [0, nvertices)
 *   - degenerate faces (repeated vertex indices) counted
 *   - counts and identifier reported for the archive record
 *
 * One JSON object per model on stdout; exit 0 only if every model passes.
 * Assets are read in place from wherever the operator points it.
 *
 * Usage: brender_core_asset_audit <model.dat> [more.dat ...]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#if defined(_DEBUG)
#include <crtdbg.h>
#endif
#include <string.h>
""" + json_receipt_helpers_source() + r"""

static int audit_model(const char *path, int *all_valid)
{
    br_model *model;
    int nv, nf, i;
    long nonfinite_vertices = 0;
    long out_of_range_faces = 0;
    long degenerate_faces = 0;
    long faces_with_material = 0;
    int valid;

    model = BrModelLoad((char *)path);
    if (model == NULL) {
        fprintf(stderr, "asset-audit: BrModelLoad failed: %s\n", path);
        fputs("{\"model\":", stdout);
        json_write_string(stdout, path);
        fputs(",\"loaded\":false,\"valid\":false}\n", stdout);
        *all_valid = 0;
        return 0;
    }

    nv = (int)model->nvertices;
    nf = (int)model->nfaces;

    for (i = 0; i < nv; i++) {
        float x = BrScalarToFloat(model->vertices[i].p.v[0]);
        float y = BrScalarToFloat(model->vertices[i].p.v[1]);
        float z = BrScalarToFloat(model->vertices[i].p.v[2]);
        if (!(x == x) || !(y == y) || !(z == z)) {
            nonfinite_vertices++;
            continue;
        }
        if (!((x - x) == 0.0f) || !((y - y) == 0.0f) || !((z - z) == 0.0f)) {
            nonfinite_vertices++;
        }
    }

    for (i = 0; i < nf; i++) {
        int a = model->faces[i].vertices[0];
        int b = model->faces[i].vertices[1];
        int c = model->faces[i].vertices[2];
        if (a < 0 || a >= nv || b < 0 || b >= nv || c < 0 || c >= nv) {
            out_of_range_faces++;
            continue;
        }
        if (a == b || b == c || a == c) {
            degenerate_faces++;
            continue;
        }
        if (model->faces[i].material != NULL) {
            faces_with_material++;
        }
    }

    valid = (nv > 0) && (nf > 0) && (model->vertices != NULL)
        && (model->faces != NULL) && (nonfinite_vertices == 0)
        && (out_of_range_faces == 0);
    if (!valid) *all_valid = 0;

    fputs("{\"model\":", stdout);
    json_write_string(stdout, path);
    fputs(",\"loaded\":true,\"id\":", stdout);
    json_write_string(stdout, model->identifier ? model->identifier : "?");
    printf(",\"nvertices\":%d,\"nfaces\":%d,"
        "\"nonfinite_vertices\":%ld,\"out_of_range_faces\":%ld,"
        "\"degenerate_faces\":%ld,\"faces_with_material\":%ld,\"valid\":%s}\n",
        nv, nf, nonfinite_vertices, out_of_range_faces, degenerate_faces,
        faces_with_material, valid ? "true" : "false");

    BrModelFree(model);
    return 1;
}

int main(int argc, char **argv)
{
    int i, all_valid = 1, audited = 0;

    if (argc < 2) {
        fprintf(stderr, "usage: %s <model.dat> [more.dat ...]\n", argv[0]);
        return 2;
    }

    if (BrBegin() != BRE_OK) return 3;
#if defined(_DEBUG)
    _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_DEBUG);
#endif

    for (i = 1; i < argc; i++) {
        if (!audit_model(argv[i], &all_valid)) continue;
        audited++;
    }

    if (BrEnd() != BRE_OK) return 4;
    if (audited < 1) return 5;
    return all_valid ? 0 : 6;
}
"""


def material_audit_source() -> str:
    """C source for the BRender portable-core material/pixelmap audit rung.

    Second R4 rung: probe period pixelmap assets (.pix) through BrPixelmapLoad
    and report decode results honestly instead of claiming fidelity. Known
    issues recorded up front: indexed variants carry no embedded palette and
    need an external .pal, and 15-bit variants currently decode only partially
    through this harness's BrPixelmapLoad path. The audit surfaces what loaded,
    its geometry, and whether pixels decoded at all; .mat and .pal loaders are
    verified against the pinned checkout before they get a rung of their own.
    """
    return r"""/*
 * BRender v1.3.2 portable-core material/pixelmap audit rung.
 *
 * Loads period pixelmap assets with BrPixelmapLoad and emits one JSON object
 * per file describing what actually decoded: dimensions, BRender pixel type,
 * row bytes, and whether pixels are present. This rung does NOT render and
 * does not claim full decode fidelity; the texture smoke documents that
 * indexed .pix need an external .pal and 15-bit variants partially decode.
 *
 * Usage: brender_core_material_audit <texture.pix> [more ...]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <stdio.h>
#include <stdlib.h>
#if defined(_DEBUG)
#include <crtdbg.h>
#endif
""" + json_receipt_helpers_source() + r"""

static int audit_pixelmap(const char *path, int *all_valid)
{
    br_pixelmap *pm;
    int valid;

    pm = BrPixelmapLoad((char *)path);
    if (pm == NULL) {
        fprintf(stderr, "material-audit: BrPixelmapLoad failed: %s\n", path);
        fputs("{\"file\":", stdout);
        json_write_string(stdout, path);
        fputs(",\"loaded\":false,\"valid\":false}\n", stdout);
        *all_valid = 0;
        return 0;
    }

    valid = (pm->pixels != NULL) && (pm->width > 0) && (pm->height > 0)
        && (pm->row_bytes > 0);
    if (!valid) *all_valid = 0;

    fputs("{\"file\":", stdout);
    json_write_string(stdout, path);
    printf(",\"loaded\":true,\"type\":%d,"
        "\"width\":%d,\"height\":%d,\"row_bytes\":%d,"
        "\"pixels_decoded\":%s,\"valid\":%s}\n",
        (int)pm->type, (int)pm->width, (int)pm->height,
        (int)pm->row_bytes, (pm->pixels != NULL) ? "true" : "false",
        valid ? "true" : "false");

    BrPixelmapFree(pm);
    return 1;
}

int main(int argc, char **argv)
{
    int i, all_valid = 1, audited = 0;

    if (argc < 2) {
        fprintf(stderr, "usage: %s <texture.pix> [more ...]\n", argv[0]);
        return 2;
    }

    if (BrBegin() != BRE_OK) return 3;
#if defined(_DEBUG)
    _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_DEBUG);
#endif

    for (i = 1; i < argc; i++) {
        if (!audit_pixelmap(argv[i], &all_valid)) continue;
        audited++;
    }

    if (BrEnd() != BRE_OK) return 4;
    if (audited < 1) return 5;
    return all_valid ? 0 : 6;
}
"""


def pixelmap_roundtrip_source() -> str:
    """C source for the BRender portable-core pixelmap round-trip rung.

    Closes a recorded readiness blocker: the archive previously wrote only raw
    PPM dumps. BrPixelmapSave is verified public API in the pinned tree
    (core/pixelmap/pmfile.c), so this rung exercises the native datafile write
    path end to end: load a period .pix asset, save it as a BRender datafile,
    reload it, and compare type and geometry. The temporary file is removed on
    every exit path; the archive commits no generated assets.
    """
    return r"""/*
 * BRender v1.3.2 portable-core pixelmap round-trip rung.
 *
 * Native datafile write-path proof:
 *
 *   BrBegin
 *     -> src = BrPixelmapLoad("<...>/dat/<asset>.pix")
 *     -> BrPixelmapSave("brender-roundtrip-check.pix", src)
 *     -> back = BrPixelmapLoad("brender-roundtrip-check.pix")
 *     -> compare type, width, height, row_bytes
 *   BrEnd (temp file removed on every exit path)
 *
 * One JSON object on stdout; exit 0 only when the round trip preserves type
 * and geometry.
 *
 * Usage: brender_core_pixelmap_roundtrip <asset.pix> [workfile]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <stdio.h>
#include <stdlib.h>
#if defined(_DEBUG)
#include <crtdbg.h>
#endif
#include <string.h>
""" + json_receipt_helpers_source() + r"""

static void emit(const char *asset, const char *result, int ok)
{
    fputs("{\"asset\":", stdout);
    json_write_string(stdout, asset);
    fputs(",\"roundtrip\":", stdout);
    json_write_string(stdout, result);
    printf(",\"valid\":%s}\n", ok ? "true" : "false");
}

static int path_exists(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (f == NULL) return 0;
    fclose(f);
    return 1;
}

int main(int argc, char **argv)
{
    const char *asset_path = (argc > 1) ? argv[1] : NULL;
    const char *work_path = (argc > 2) ? argv[2] : "brender-roundtrip-check.pix";
    br_pixelmap *src = NULL, *back = NULL;
    int ok = 0;
    int created_workfile = 0;

    if (asset_path == NULL) {
        fprintf(stderr, "usage: %s <asset.pix> [workfile]\n", argv[0]);
        return 2;
    }

    if (BrBegin() != BRE_OK) return 3;
#if defined(_DEBUG)
    _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_DEBUG);
#endif

    src = BrPixelmapLoad((char *)asset_path);
    if (src == NULL || src->pixels == NULL) {
        fprintf(stderr, "pixelmap-roundtrip: source load failed: %s\n", asset_path);
        emit(asset_path, "source-load-failed", 0);
        goto out;
    }

    if (path_exists(work_path)) {
        fprintf(stderr, "pixelmap-roundtrip: workfile already exists: %s\n", work_path);
        emit(asset_path, "workfile-exists", 0);
        goto out;
    }

    /* BrPixelmapSave returns the count saved (1), not a br_error. */
    if (BrPixelmapSave((char *)work_path, src) != 1) {
        if (path_exists(work_path)) created_workfile = 1;
        fprintf(stderr, "pixelmap-roundtrip: BrPixelmapSave failed: %s\n", work_path);
        emit(asset_path, "save-failed", 0);
        goto out;
    }
    created_workfile = 1;

    back = BrPixelmapLoad((char *)work_path);
    if (back == NULL || back->pixels == NULL) {
        fprintf(stderr, "pixelmap-roundtrip: reload failed: %s\n", work_path);
        emit(asset_path, "reload-failed", 0);
        goto out;
    }

    ok = (back->type == src->type)
        && (back->width == src->width)
        && (back->height == src->height)
        && (back->row_bytes == src->row_bytes);

    fputs("{\"asset\":", stdout);
    json_write_string(stdout, asset_path);
    printf(",\"type\":%d,\"width\":%d,\"height\":%d,"
        "\"row_bytes\":%d,\"match\":%s,\"valid\":%s}\n",
        (int)src->type, (int)src->width, (int)src->height,
        (int)src->row_bytes, ok ? "true" : "false", ok ? "true" : "false");
out:
    if (created_workfile) remove(work_path);
    if (back != NULL) BrPixelmapFree(back);
    if (src != NULL) BrPixelmapFree(src);
    if (BrEnd() != BRE_OK) return 4;
    return ok ? 0 : 5;
}
"""


def material_file_audit_source() -> str:
    """C source for the BRender portable-core material-file audit rung.

    Ground truth from the pinned tree and local build: BrMaterialLoad/
    BrMaterialSave live in core/v1db/v1dbfile.c and read/write BINARY chunk
    datafiles only; the period .mat files shipped in dat/ (std.mat,
    winstd.mat) are TEXT material scripts the binary loader legitimately
    rejects. This rung therefore does two things honestly:

      1. probes each argv path and reports whether it is a text script
         (leading '##') or an unreadable/unrecognized file;
      2. proves the binary material datafile path end to end: allocate,
         save, reload, compare identifier, free, remove the temp file.

    Exit 0 iff the binary round trip holds; argv probe results are recorded
    in the receipt without failing the rung.
    """
    return r"""/*
 * BRender v1.3.2 portable-core material-file audit rung.
 *
 * Usage: brender_core_material_file_audit [paths-to-probe ...]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
""" + json_receipt_helpers_source() + r"""

#if defined(_DEBUG)
#include <crtdbg.h>
#endif

static void probe_path(const char *path)
{
    br_material *mat;
    FILE *f;
    char magic[2] = {0, 0};

    f = fopen(path, "rb");
    if (f != NULL) {
        if (fread(magic, 1, 2, f) != 2) { magic[0] = 0; }
        fclose(f);
    }
    if (magic[0] == '#' && magic[1] == '#') {
        fputs("{\"file\":", stdout);
        json_write_string(stdout, path);
        fputs(",\"kind\":\"text-material-script\","
            "\"binary_loadable\":false}\n", stdout);
        return;
    }
    mat = BrMaterialLoad((char *)path);
    if (mat == NULL) {
        fputs("{\"file\":", stdout);
        json_write_string(stdout, path);
        fputs(",\"kind\":\"unrecognized\","
            "\"binary_loadable\":false}\n", stdout);
        return;
    }
    fputs("{\"file\":", stdout);
    json_write_string(stdout, path);
    fputs(",\"kind\":\"binary-datafile\",\"loaded\":true,\"id\":", stdout);
    json_write_string(stdout, mat->identifier ? mat->identifier : "?");
    printf(",\"flags\":%lu,\"index_base\":%d,"
        "\"has_colour_map\":%s}\n",
        (unsigned long)mat->flags, (int)mat->index_base,
        (mat->colour_map != NULL) ? "true" : "false");
    BrMaterialFree(mat);
}

static int path_exists(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (f == NULL) return 0;
    fclose(f);
    return 1;
}

int main(int argc, char **argv)
{
    const char *work_path = "material-audit-roundtrip.mat";
    br_material *mat = NULL, *back = NULL;
    int i, ok = 0;
    int created_workfile = 0;

#if defined(_DEBUG)
    _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_DEBUG);
#endif
    if (BrBegin() != BRE_OK) return 3;

    if (path_exists(work_path)) {
        fputs("{\"roundtrip\":", stdout);
        json_write_string(stdout, work_path);
        fputs(",\"workfile_exists\":true,\"valid\":false}\n", stdout);
        goto out;
    }

    /* Binary material datafile round trip: the positive control. */
    mat = BrMaterialAllocate("audit-default");
    if (mat == NULL) { BrEnd(); return 4; }
    if (BrMaterialSave((char *)work_path, mat) != 1) {
        if (path_exists(work_path)) created_workfile = 1;
        fprintf(stderr, "material-file-audit: BrMaterialSave failed\n");
        goto out;
    }
    created_workfile = 1;
    back = BrMaterialLoad((char *)work_path);
    if (back == NULL) {
        fprintf(stderr, "material-file-audit: reload failed\n");
        goto out;
    }
    ok = (back->identifier != NULL
        && strcmp(back->identifier, "audit-default") == 0);
    fputs("{\"roundtrip\":", stdout);
    json_write_string(stdout, work_path);
    printf(",\"id_match\":%s,\"valid\":%s}\n",
        ok ? "true" : "false", ok ? "true" : "false");

out:
    if (created_workfile) remove(work_path);
    if (back != NULL) BrMaterialFree(back);
    if (mat != NULL) BrMaterialFree(mat);

    /* Informational probes of operator-supplied paths. */
    for (i = 1; i < argc; i++) {
        probe_path(argv[i]);
    }

    if (BrEnd() != BRE_OK) return 6;
    return ok ? 0 : 5;
}
"""
