from __future__ import annotations


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
#include <string.h>

static int audit_model(const char *path, int *all_valid)
{
    br_model *model;
    int nv, nf, i;
    long nonfinite_vertices = 0;
    long out_of_range_faces = 0;
    long degenerate_faces = 0;
    int valid;

    model = BrModelLoad((char *)path);
    if (model == NULL) {
        fprintf(stderr, "asset-audit: BrModelLoad failed: %s\n", path);
        printf("{\"model\":\"%s\",\"loaded\":false,\"valid\":false}\n", path);
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
        }
    }

    valid = (nv > 0) && (nf > 0) && (model->vertices != NULL)
        && (model->faces != NULL) && (nonfinite_vertices == 0)
        && (out_of_range_faces == 0);
    if (!valid) *all_valid = 0;

    printf("{\"model\":\"%s\",\"loaded\":true,\"id\":\"%s\","
        "\"nvertices\":%d,\"nfaces\":%d,"
        "\"nonfinite_vertices\":%ld,\"out_of_range_faces\":%ld,"
        "\"degenerate_faces\":%ld,\"valid\":%s}\n",
        path, model->identifier ? model->identifier : "?",
        nv, nf, nonfinite_vertices, out_of_range_faces, degenerate_faces,
        valid ? "true" : "false");

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

    for (i = 1; i < argc; i++) {
        if (!audit_model(argv[i], &all_valid)) continue;
        audited++;
    }

    if (BrEnd() != BRE_OK) return 4;
    if (audited < 1) return 5;
    return all_valid ? 0 : 6;
}
"""
