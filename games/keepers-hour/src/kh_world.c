/* The Keeper's Hour: the lamp room, built from BRender primitives.
 * No art files: every shape is made here, so the slice ships with code only.
 * SPDX-License-Identifier: MIT */
#include <math.h>
#include <string.h>

#include "kh_world.h"

#define KH_PI 3.14159265f

static br_material *material(const char *name, int r, int g, int b, br_uint_32 extra)
{
    br_material *m = BrMaterialAllocate(name);
    m->colour = BR_COLOUR_RGB(r, g, b);
    m->flags = BR_MATF_LIGHT | BR_MATF_TWO_SIDED | extra;
    m->ka = BR_UFRACTION(0.22);
    m->kd = BR_UFRACTION(0.78);
    m->ks = BR_UFRACTION(0.10);
    m->power = BR_SCALAR(10);
    BrMaterialAdd(m);
    return m;
}

static void vertex(br_model *m, int i, float x, float y, float z) { BrVector3Set(&m->vertices[i].p, BR_SCALAR(x), BR_SCALAR(y), BR_SCALAR(z)); }

static void face(br_model *m, int i, int a, int b, int c, br_uint_16 smoothing)
{
    m->faces[i].vertices[0] = (br_uint_16)a;
    m->faces[i].vertices[1] = (br_uint_16)b;
    m->faces[i].vertices[2] = (br_uint_16)c;
    m->faces[i].smoothing = smoothing;
}

/* An n-sided prism from y0 to y1, radius r0 at the bottom and r1 at the top.
 * Caps are optional; a cone or a lampshade is a prism with one radius zero. */
static br_model *prism_wound(const char *name, int n, float r0, float r1, float y0, float y1, int caps, br_uint_16 smoothing, int inward);

static br_model *prism(const char *name, int n, float r0, float r1, float y0, float y1, int caps, br_uint_16 smoothing)
{
    return prism_wound(name, n, r0, r1, y0, y1, caps, smoothing, 0);
}

/* inward: side faces point into the prism, so a one-sided wall is seen only
 * from inside the room. That is the cutaway: the camera sits outside and
 * looks in through the near wall, which is not drawn. */
static br_model *prism_wound(const char *name, int n, float r0, float r1, float y0, float y1, int caps, br_uint_16 smoothing, int inward)
{
    br_model *m = BrModelAllocate(name, 2 * n + 2, 2 * n + (caps ? 2 * n : 0));
    int i, f = 0;
    for (i = 0; i < n; i++) {
        float a = 2 * KH_PI * i / n;
        vertex(m, i, r0 * cosf(a), y0, r0 * sinf(a));
        vertex(m, n + i, r1 * cosf(a), y1, r1 * sinf(a));
    }
    vertex(m, 2 * n, 0, y0, 0);
    vertex(m, 2 * n + 1, 0, y1, 0);
    for (i = 0; i < n; i++) {
        int j = (i + 1) % n;
        if (inward) {
            face(m, f++, i, n + j, n + i, smoothing);
            face(m, f++, i, j, n + j, smoothing);
        } else {
            face(m, f++, i, n + i, n + j, smoothing);
            face(m, f++, i, n + j, j, smoothing);
        }
        if (caps) {
            face(m, f++, 2 * n, i, j, 0);
            face(m, f++, 2 * n + 1, n + j, n + i, 0);
        }
    }
    BrModelAdd(m);
    return m;
}

/* A window: one quad facing into the room, so the near ones vanish with the
 * cutaway and the far ones show. */
static br_model *window_quad(void)
{
    br_model *m = BrModelAllocate("window", 4, 2);
    vertex(m, 0, 0, 1.4f, -0.75f);
    vertex(m, 1, 0, 3.2f, -0.75f);
    vertex(m, 2, 0, 3.2f, 0.75f);
    vertex(m, 3, 0, 1.4f, 0.75f);
    face(m, 0, 0, 2, 1, 0);
    face(m, 1, 0, 3, 2, 0);
    BrModelAdd(m);
    return m;
}

/* The lens: two faceted cones base to base, an eye seen edge-on. */
static br_model *lens(void)
{
    const int n = 12;
    br_model *m = BrModelAllocate("lens", n + 2, 2 * n);
    int i, f = 0;
    for (i = 0; i < n; i++)
        vertex(m, i, 0.55f * cosf(2 * KH_PI * i / n), 0, 0.55f * sinf(2 * KH_PI * i / n));
    vertex(m, n, 0, 0.75f, 0);
    vertex(m, n + 1, 0, -0.75f, 0);
    for (i = 0; i < n; i++) {
        face(m, f++, n, (i + 1) % n, i, 0);
        face(m, f++, n + 1, i, (i + 1) % n, 0);
    }
    BrModelAdd(m);
    return m;
}

static br_actor *place(br_actor *root, br_model *model, br_material *mat, float x, float y, float z, float turn)
{
    br_actor *a = BrActorAdd(root, BrActorAllocate(BR_ACTOR_MODEL, NULL));
    a->model = model;
    a->material = mat;
    a->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34RotateY(&a->t.t.mat, BR_ANGLE_DEG(turn));
    BrMatrix34PostTranslate(&a->t.t.mat, BR_SCALAR(x), BR_SCALAR(y), BR_SCALAR(z));
    return a;
}

static void build_room(kh_world *w, br_actor *root)
{
    br_material *stone = material("stone", 112, 104, 92, BR_MATF_SMOOTH);
    stone->flags &= ~BR_MATF_TWO_SIDED; /* one-sided: the cutaway */
    BrMaterialUpdate(stone, BR_MATU_ALL);
    br_material *floor = material("boards", 82, 60, 42, 0);
    br_material *iron = material("iron", 58, 62, 68, BR_MATF_SMOOTH);
    br_material *glass = material("window", 22, 30, 52, 0);
    br_model *pane = window_quad();
    int i;

    w->room_radius = 5.2f;
    place(root, prism("floor", 8, 6.0f, 6.0f, -0.1f, 0.0f, 1, 0), floor, 0, 0, 0, 22.5f);
    place(root, prism_wound("wall", 8, 6.0f, 5.6f, 0.0f, 4.2f, 0, 0, 1), stone, 0, 0, 0, 22.5f);
    (void)iron; /* no roof: the room is seen from above */
    glass->flags &= ~BR_MATF_TWO_SIDED;
    BrMaterialUpdate(glass, BR_MATU_ALL);
    for (i = 0; i < 8; i += 2) /* four dark windows onto a sea that is not there */
        place(root, pane, glass, 5.5f * cosf(KH_PI * i / 4), 0, 5.5f * sinf(KH_PI * i / 4), -45.0f * i);
}

static void add_talker(kh_world *w, const char *name, const char *node, float x, float z)
{
    kh_talker *t = &w->talkers[w->ntalkers++];
    t->name = name;
    t->node = node;
    t->x = x;
    t->z = z;
}

static void build_furniture(kh_world *w, br_actor *root)
{
    br_material *brass = material("brass", 196, 152, 64, BR_MATF_SMOOTH);
    br_material *wood = material("table", 104, 72, 46, 0);
    br_material *paper = material("logbook", 120, 36, 30, 0);
    br_material *tin = material("kettle", 150, 156, 160, BR_MATF_SMOOTH);
    br_material *glow = material("lens", 255, 246, 214, 0);
    br_material *coat = material("keeper", 40, 58, 92, BR_MATF_SMOOTH);

    glow->flags = BR_MATF_TWO_SIDED; /* unlit: the lens is the light */
    BrMaterialUpdate(glow, BR_MATU_ALL);

    place(root, prism("pedestal", 8, 0.9f, 0.6f, 0.0f, 1.4f, 1, 1), brass, 0, 0, 0, 0);
    w->lens = place(root, lens(), glow, 0, 2.2f, 0, 0);
    place(root, prism("table", 4, 0.9f, 0.9f, 0.0f, 0.9f, 1, 0), wood, 3.2f, 0, -2.0f, 45);
    place(root, prism("book", 4, 0.32f, 0.32f, 0.9f, 1.0f, 1, 0), paper, 3.2f, 0, -2.0f, 20);
    place(root, prism("stove", 6, 0.45f, 0.45f, 0.0f, 0.8f, 1, 0), wood, -3.0f, 0, 2.6f, 0);
    place(root, prism("kettle", 10, 0.32f, 0.18f, 0.8f, 1.25f, 1, 1), tin, -3.0f, 0, 2.6f, 0);

    w->keeper = place(root, prism("keeper", 8, 0.32f, 0.22f, 0.0f, 1.55f, 1, 1), coat, 0, 0, 3.2f, 0);
    place(w->keeper, prism("head", 8, 0.17f, 0.0f, 1.55f, 1.95f, 1, 1), brass, 0, 0, 0, 0);

    add_talker(w, "the lamp", "lamp", 0.0f, 0.0f);
    add_talker(w, "the logbook", "logbook", 3.2f, -2.0f);
    add_talker(w, "the kettle", "kettle", -3.0f, 2.6f);
}

br_error kh_world_build(kh_world *w, br_actor *root)
{
    br_light *spot;
    br_actor *ambient;
    memset(w, 0, sizeof(*w));
    build_room(w, root);
    build_furniture(w, root);

    w->beam = BrActorAdd(w->lens, BrActorAllocate(BR_ACTOR_LIGHT, NULL));
    spot = w->beam->type_data;
    spot->type = BR_LIGHT_SPOT;
    spot->cone_outer = BR_ANGLE_DEG(32);
    spot->cone_inner = BR_ANGLE_DEG(12);
    spot->colour = BR_COLOUR_RGB(255, 236, 190);
    w->beam->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34RotateY(&w->beam->t.t.mat, BR_ANGLE_DEG(90));
    BrLightEnable(w->beam);

    ambient = BrActorAdd(root, BrActorAllocate(BR_ACTOR_LIGHT, NULL));
    ((br_light *)ambient->type_data)->type = BR_LIGHT_DIRECT;
    ((br_light *)ambient->type_data)->colour = BR_COLOUR_RGB(70, 76, 110);
    ambient->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34RotateX(&ambient->t.t.mat, BR_ANGLE_DEG(-70));
    BrLightEnable(ambient);
    return BRE_OK;
}

void kh_world_turn_lamp(kh_world *w, float seconds)
{
    /* four seconds a sweep */
    float degrees = fmodf(seconds * 90.0f, 360.0f);
    BrMatrix34RotateY(&w->lens->t.t.mat, BR_ANGLE_DEG(degrees));
    BrMatrix34PostTranslate(&w->lens->t.t.mat, 0, BR_SCALAR(2.2f), 0);
}

void kh_world_clamp(const kh_world *w, float *x, float *z)
{
    float d = sqrtf(*x * *x + *z * *z);
    int i;
    if (d > w->room_radius) {
        *x *= w->room_radius / d;
        *z *= w->room_radius / d;
    }
    for (i = 0; i < w->ntalkers; i++) { /* furniture is solid: keep 1.1 units away */
        float dx = *x - w->talkers[i].x, dz = *z - w->talkers[i].z, r = sqrtf(dx * dx + dz * dz);
        if (r < 1.1f && r > 1e-4f) {
            *x = w->talkers[i].x + dx * 1.1f / r;
            *z = w->talkers[i].z + dz * 1.1f / r;
        }
    }
}

int kh_world_talker_near(const kh_world *w, float x, float z, float dx, float dz)
{
    int i, best = -1;
    float best_d = 2.0f;
    for (i = 0; i < w->ntalkers; i++) {
        float tx = w->talkers[i].x - x, tz = w->talkers[i].z - z, d = sqrtf(tx * tx + tz * tz);
        if (d < best_d && (d < 1e-4f || (tx * dx + tz * dz) / d > 0.3f)) {
            best = i;
            best_d = d;
        }
    }
    return best;
}
