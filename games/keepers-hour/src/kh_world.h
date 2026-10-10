/* The Keeper's Hour: the tower, built from the room table, one room on stage at a time.
 * SPDX-License-Identifier: MIT */
#ifndef KH_WORLD_H
#define KH_WORLD_H

#include <brender.h>
#include "kh_rooms.h"

#define KH_MAX_ROOMS   8
#define KH_MAX_TALKERS 12
#define KH_MAX_LIGHTS  2

typedef struct kh_talker {
    const char *name;   /* shown when you are close enough to talk */
    const char *node;   /* the script node, or "@room" for a way through */
    float       x, z;
} kh_talker;

typedef struct kh_room_stage {
    br_actor  *root;                   /* detached unless this room is on stage */
    br_actor  *lights[KH_MAX_LIGHTS];
    int        nlights;
    kh_talker  talkers[KH_MAX_TALKERS];
    int        ntalkers;
} kh_room_stage;

typedef struct kh_world {
    br_actor      *stage;               /* the demo world: the current room hangs here */
    br_actor      *keeper;              /* moves with the player between rooms */
    br_actor      *lens;                /* the turning lamp (lamp room) */
    kh_room_stage  rooms[KH_MAX_ROOMS];
    int            current;
} kh_world;

br_error kh_world_build(kh_world *w, br_actor *stage);

/* Put room `index` on stage. The keeper appears beside the way back to
 * `from` (a room index), or at the room's start when from is -1. */
void kh_world_enter(kh_world *w, int index, int from, float *x, float *z);

void kh_world_turn_lamp(kh_world *w, float seconds);
void kh_world_clamp(const kh_world *w, float *x, float *z);
int  kh_world_talker_near(const kh_world *w, float x, float z, float dx, float dz);
const kh_talker *kh_world_talker(const kh_world *w, int i);
br_colour kh_world_sky(const kh_world *w);

#endif
