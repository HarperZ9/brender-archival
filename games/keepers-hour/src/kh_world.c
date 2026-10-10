/* The Keeper's Hour: the tower, built from the room table, one room on stage at a time.
 * Walls are one-sided and face inward: the camera looks in through the near
 * wall, which is not drawn (the cutaway).
 * SPDX-License-Identifier: MIT */
#include <math.h>
#include <string.h>

#include "kh_shapes.h"
#include "kh_tex.h"
#include "kh_world.h"

static br_actor *add_light(kh_room_stage *s, br_actor *parent, br_uint_8 type, int r, int g, int b)
{
    br_actor *a = BrActorAdd(parent, BrActorAllocate(BR_ACTOR_LIGHT, NULL));
    br_light *l = a->type_data;
    l->type = type;
    l->colour = BR_COLOUR_RGB(r, g, b);
    a->t.type = BR_TRANSFORM_MATRIX34;
    s->lights[s->nlights++] = a;
    return a;
}

static void build_shell(kh_room_stage *s, const kh_room *room)
{
    /* boards indoors, stone flags outside on the gallery; stone walls */
    br_material *floor = kh_tex_material(room->walled ? "boards" : "stone", 1);
    br_model *floor_model = kh_prism_planar("floor", 8, 6.0f, 6.0f, -0.1f, 0.0f, 0.4f, 0.0f);
    br_actor *fill;
    kh_place(s->root, floor_model, floor, 0, 0, 0, 22.5f);
    if (room->walled)
        kh_place(s->root, kh_prism("wall", 8, 6.0f, 5.6f, 0.0f, 4.2f, 0, 0, 1), kh_tex_material("stone", 0), 0, 0, 0, 22.5f);
    fill = add_light(s, s->root, BR_LIGHT_DIRECT, room->walled ? 120 : 70, room->walled ? 116 : 80, room->walled ? 130 : 130);
    BrMatrix34RotateX(&fill->t.t.mat, BR_ANGLE_DEG(-65));
    BrMatrix34PostRotateY(&fill->t.t.mat, BR_ANGLE_DEG(30));
}

static void build_prop(kh_room_stage *s, const kh_prop *p, int index)
{
    char name[16];
    br_material *mat;
    br_model *model;
    name[0] = (char)('a' + index % 26);
    name[1] = '\0';
    switch (p->kind) {
    case KH_GLOW:
        mat = kh_glow(name, p->r, p->g, p->b);
        model = kh_prism(name, p->sides, p->r0, p->r1, p->y0, p->y1, 1, 0, 0);
        break;
    case KH_PANEL:
        mat = p->tex ? kh_tex_material(p->tex, 0) : kh_material(name, p->r, p->g, p->b, 0, 0);
        model = kh_panel(p->r0, p->y0, p->y1);
        break;
    default:
        mat = p->tex ? kh_tex_material(p->tex, 1) : kh_material(name, p->r, p->g, p->b, p->sides > 6, 1);
        if (p->tex && p->y1 - p->y0 < p->r0) /* a flat textured box (the letter) shows its picture once on top */
            model = kh_prism_planar(name, p->sides, p->r0, p->r1, p->y0, p->y1, 0.5f / p->r0, 0.5f);
        else
            model = kh_prism(name, p->sides, p->r0, p->r1, p->y0, p->y1, 1, p->sides > 6, 0);
        break;
    }
    /* a panel shows its face to the room centre; the near ones vanish with the cutaway */
    {
        /* the wall leans in (apothem 5.5 at the floor, 5.2 at the top): a panel
         * hangs at 4.95 from the centre so the whole of it is in front of the wall */
        float x = p->x, z = p->z, d = sqrtf(x * x + z * z);
        if (p->kind == KH_PANEL && d > 4.95f) { x *= 4.95f / d; z *= 4.95f / d; }
        kh_place(s->root, model, mat, x, 0, z, p->kind == KH_PANEL ? p->turn + 180.0f : p->turn);
    }
    if (p->talker && s->ntalkers < KH_MAX_TALKERS) {
        kh_talker *t = &s->talkers[s->ntalkers++];
        t->name = p->talker;
        t->node = p->node;
        t->x = p->x;
        t->z = p->z;
    }
}

static void build_lamp(kh_world *w, kh_room_stage *s)
{
    br_actor *beam;
    br_light *spot;
    w->lens = kh_place(s->root, kh_lens(0.55f, 0.75f), kh_glow("lens", 255, 246, 214), 0, 2.2f, 0, 0);
    beam = add_light(s, w->lens, BR_LIGHT_SPOT, 255, 236, 190);
    spot = beam->type_data;
    spot->cone_outer = BR_ANGLE_DEG(32);
    spot->cone_inner = BR_ANGLE_DEG(12);
    BrMatrix34RotateY(&beam->t.t.mat, BR_ANGLE_DEG(90));
}

br_error kh_world_build(kh_world *w, br_actor *stage)
{
    int r, i;
    memset(w, 0, sizeof(*w));
    w->stage = stage;
    w->current = -1;
    for (r = 0; r < kh_room_count && r < KH_MAX_ROOMS; r++) {
        kh_room_stage *s = &w->rooms[r];
        s->root = BrActorAllocate(BR_ACTOR_NONE, NULL);
        build_shell(s, &kh_rooms[r]);
        for (i = 0; i < kh_rooms[r].nprops; i++)
            build_prop(s, &kh_rooms[r].props[i], i);
        if (kh_rooms[r].lamp)
            build_lamp(w, s);
    }
    w->keeper = BrActorAllocate(BR_ACTOR_MODEL, NULL);
    w->keeper->model = kh_prism("keeper", 8, 0.32f, 0.22f, 0.0f, 1.55f, 1, 1, 0);
    w->keeper->material = kh_material("keeper", 40, 58, 92, 1, 1);
    w->keeper->t.type = BR_TRANSFORM_MATRIX34;
    kh_place(w->keeper, kh_prism("head", 8, 0.17f, 0.0f, 1.55f, 1.95f, 1, 1, 0), kh_material("head", 196, 152, 64, 1, 1), 0, 0, 0, 0);
    return BRE_OK;
}

void kh_world_enter(kh_world *w, int index, int from, float *x, float *z)
{
    kh_room_stage *s;
    int i;
    if (w->current >= 0) {
        kh_room_stage *old = &w->rooms[w->current];
        for (i = 0; i < old->nlights; i++)
            BrLightDisable(old->lights[i]);
        BrActorRemove(old->root);
        BrActorRemove(w->keeper);
    }
    w->current = index;
    s = &w->rooms[index];
    BrActorAdd(w->stage, s->root);
    BrActorAdd(s->root, w->keeper);
    for (i = 0; i < s->nlights; i++)
        BrLightEnable(s->lights[i]);
    *x = 0.0f;
    *z = kh_rooms[index].inner > 0 ? kh_rooms[index].inner + 0.6f : 3.2f;
    for (i = 0; from >= 0 && i < s->ntalkers; i++) {
        const kh_talker *t = &s->talkers[i];
        if (t->node[0] == '@' && kh_room_find(t->node + 1) == from) {
            float d = sqrtf(t->x * t->x + t->z * t->z), toward = d > 1e-3f ? 1.4f / d : 0.0f;
            *x = t->x - t->x * toward;
            *z = t->z - t->z * toward;
        }
    }
    kh_world_clamp(w, x, z);
}

void kh_world_turn_lamp(kh_world *w, float seconds)
{
    float degrees = fmodf(seconds * 90.0f, 360.0f); /* four seconds a sweep */
    BrMatrix34RotateY(&w->lens->t.t.mat, BR_ANGLE_DEG(degrees));
    BrMatrix34PostTranslate(&w->lens->t.t.mat, 0, BR_SCALAR(2.2f), 0);
}

void kh_world_clamp(const kh_world *w, float *x, float *z)
{
    const kh_room *room = &kh_rooms[w->current];
    const kh_room_stage *s = &w->rooms[w->current];
    float d = sqrtf(*x * *x + *z * *z);
    int i;
    if (d > room->radius) { *x *= room->radius / d; *z *= room->radius / d; }
    if (room->inner > 0 && d < room->inner && d > 1e-4f) { *x *= room->inner / d; *z *= room->inner / d; }
    for (i = 0; i < s->ntalkers; i++) { /* furniture is solid: keep 1.0 units away */
        float dx = *x - s->talkers[i].x, dz = *z - s->talkers[i].z, r = sqrtf(dx * dx + dz * dz);
        if (r < 1.0f && r > 1e-4f) { *x = s->talkers[i].x + dx / r; *z = s->talkers[i].z + dz / r; }
    }
}

int kh_world_talker_near(const kh_world *w, float x, float z, float dx, float dz)
{
    const kh_room_stage *s = &w->rooms[w->current];
    int i, best = -1;
    float best_d = 2.0f;
    for (i = 0; i < s->ntalkers; i++) {
        float tx = s->talkers[i].x - x, tz = s->talkers[i].z - z, d = sqrtf(tx * tx + tz * tz);
        if (d < best_d && (d < 1e-4f || (tx * dx + tz * dz) / d > 0.3f)) { best = i; best_d = d; }
    }
    return best;
}

const kh_talker *kh_world_talker(const kh_world *w, int i) { return &w->rooms[w->current].talkers[i]; }

br_colour kh_world_sky(const kh_world *w, const br_pixelmap *target)
{
    const kh_room *room = &kh_rooms[w->current];
    return kh_px(target, room->sky[0], room->sky[1], room->sky[2]);
}
