/* The Keeper's Hour: shapes built from BRender model primitives.
 * SPDX-License-Identifier: MIT */
#include <math.h>

#include "kh_shapes.h"

br_material *kh_material(const char *name, int r, int g, int b, int smooth, int two_sided)
{
    br_material *m = BrMaterialAllocate(name);
    m->colour = BR_COLOUR_RGB(r, g, b);
    m->flags = BR_MATF_LIGHT | (smooth ? BR_MATF_SMOOTH : 0) | (two_sided ? BR_MATF_TWO_SIDED : 0);
    m->ka = BR_UFRACTION(0.22);
    m->kd = BR_UFRACTION(0.78);
    m->ks = BR_UFRACTION(0.10);
    m->power = BR_SCALAR(10);
    BrMaterialAdd(m);
    return m;
}

br_material *kh_glow(const char *name, int r, int g, int b)
{
    br_material *m = BrMaterialAllocate(name);
    m->colour = BR_COLOUR_RGB(r, g, b);
    m->flags = BR_MATF_TWO_SIDED;
    BrMaterialAdd(m);
    return m;
}

static void vertex(br_model *m, int i, float x, float y, float z) { BrVector3Set(&m->vertices[i].p, BR_SCALAR(x), BR_SCALAR(y), BR_SCALAR(z)); }
static void uv(br_model *m, int i, float u, float v) { BrVector2Set(&m->vertices[i].map, BR_SCALAR(u), BR_SCALAR(v)); }

static void face(br_model *m, int i, int a, int b, int c, br_uint_16 smoothing)
{
    m->faces[i].vertices[0] = (br_uint_16)a;
    m->faces[i].vertices[1] = (br_uint_16)b;
    m->faces[i].vertices[2] = (br_uint_16)c;
    m->faces[i].smoothing = smoothing;
}

static br_model *prism_build(const char *name, int n, float r0, float r1, float y0, float y1, int caps, int smooth, int inward)
{
    br_model *m = BrModelAllocate(name, 2 * n + 2, 2 * n + (caps ? 2 * n : 0));
    br_uint_16 group = smooth ? 1 : 0;
    int i, f = 0;
    for (i = 0; i < n; i++) {
        float a = 2 * KH_PI * i / n;
        vertex(m, i, r0 * cosf(a), y0, r0 * sinf(a));
        vertex(m, n + i, r1 * cosf(a), y1, r1 * sinf(a));
        /* round the sides: one texture repeat for every two sides, two units high */
        uv(m, i, i * 0.5f, y0 * 0.5f);
        uv(m, n + i, i * 0.5f, y1 * 0.5f);
    }
    vertex(m, 2 * n, 0, y0, 0);
    vertex(m, 2 * n + 1, 0, y1, 0);
    for (i = 0; i < n; i++) {
        int j = (i + 1) % n;
        if (inward) {
            face(m, f++, i, n + j, n + i, group);
            face(m, f++, i, j, n + j, group);
        } else {
            face(m, f++, i, n + i, n + j, group);
            face(m, f++, i, n + j, j, group);
        }
        if (caps) {
            face(m, f++, 2 * n, i, j, 0);
            face(m, f++, 2 * n + 1, n + j, n + i, 0);
        }
    }
    return m;
}

br_model *kh_prism(const char *name, int n, float r0, float r1, float y0, float y1, int caps, int smooth, int inward)
{
    br_model *m = prism_build(name, n, r0, r1, y0, y1, caps, smooth, inward);
    BrModelAdd(m);
    return m;
}

br_model *kh_lens(float radius, float half_height)
{
    const int n = 12;
    br_model *m = BrModelAllocate("lens", n + 2, 2 * n);
    int i, f = 0;
    for (i = 0; i < n; i++)
        vertex(m, i, radius * cosf(2 * KH_PI * i / n), 0, radius * sinf(2 * KH_PI * i / n));
    vertex(m, n, 0, half_height, 0);
    vertex(m, n + 1, 0, -half_height, 0);
    for (i = 0; i < n; i++) {
        face(m, f++, n, (i + 1) % n, i, 0);
        face(m, f++, n + 1, i, (i + 1) % n, 0);
    }
    BrModelAdd(m);
    return m;
}

br_model *kh_panel(float w, float y0, float y1)
{
    br_model *m = BrModelAllocate("panel", 4, 2);
    vertex(m, 0, 0, y0, -w / 2);
    vertex(m, 1, 0, y1, -w / 2);
    vertex(m, 2, 0, y1, w / 2);
    vertex(m, 3, 0, y0, w / 2);
    uv(m, 0, 0.0f, 1.0f);
    uv(m, 1, 0.0f, 0.0f);
    uv(m, 2, 1.0f, 0.0f);
    uv(m, 3, 1.0f, 1.0f);
    face(m, 0, 0, 1, 2, 0);
    face(m, 1, 0, 2, 3, 0);
    BrModelAdd(m);
    return m;
}

br_actor *kh_place(br_actor *parent, br_model *model, br_material *mat, float x, float y, float z, float turn)
{
    br_actor *a = BrActorAdd(parent, BrActorAllocate(BR_ACTOR_MODEL, NULL));
    a->model = model;
    a->material = mat;
    a->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34RotateY(&a->t.t.mat, BR_ANGLE_DEG(turn));
    BrMatrix34PostTranslate(&a->t.t.mat, BR_SCALAR(x), BR_SCALAR(y), BR_SCALAR(z));
    return a;
}

br_model *kh_prism_planar(const char *name, int n, float r0, float r1, float y0, float y1, float scale, float offset)
{
    br_model *m = prism_build(name, n, r0, r1, y0, y1, 1, 0, 0);
    int i;
    /* u, v from x, z, set before BrModelAdd prepares (and may release) the vertices */
    for (i = 0; i < m->nvertices; i++)
        uv(m, i, BrScalarToFloat(m->vertices[i].p.v[0]) * scale + offset, BrScalarToFloat(m->vertices[i].p.v[2]) * scale + offset);
    BrModelAdd(m);
    return m;
}
