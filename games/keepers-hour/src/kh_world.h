/* The Keeper's Hour: the lamp room, built from BRender primitives.
 * SPDX-License-Identifier: MIT */
#ifndef KH_WORLD_H
#define KH_WORLD_H

#include <brender.h>

#define KH_MAX_TALKERS 4

typedef struct kh_talker {
    const char *name;   /* shown when you are close enough to talk */
    const char *node;   /* the script node the conversation starts at */
    float       x, z;   /* where it stands on the floor */
} kh_talker;

typedef struct kh_world {
    br_actor  *keeper;      /* the player figure */
    br_actor  *lens;        /* the turning lamp */
    br_actor  *beam;        /* the spot light that sweeps the room */
    kh_talker  talkers[KH_MAX_TALKERS];
    int        ntalkers;
    float      room_radius;
} kh_world;

br_error kh_world_build(kh_world *w, br_actor *root);
void     kh_world_turn_lamp(kh_world *w, float seconds);

/* Keep a point inside the room and out of the furniture. */
void kh_world_clamp(const kh_world *w, float *x, float *z);

/* The talker within reach of (x, z) facing (dx, dz), or -1. */
int kh_world_talker_near(const kh_world *w, float x, float z, float dx, float dz);

#endif
