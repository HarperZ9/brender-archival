/* The Keeper's Hour: the state of one night, shared by the main loop and input.
 * SPDX-License-Identifier: MIT */
#ifndef KH_GAME_H
#define KH_GAME_H

#include <SDL3/SDL.h>
#include "kh_options.h"
#include "kh_script.h"
#include "kh_talk.h"
#include "kh_world.h"

typedef struct kh_game {
    kh_script    script;
    kh_talk      talk;
    kh_world     world;
    kh_options   opt;
    float        keeper_x, keeper_z, facing, cam_yaw, clock_s;
    int          near_talker, ended, problems;
    int          smoke, smoke_node, smoke_room, smoke_ends;
    SDL_Gamepad *pad;
    const char  *shot_path;  /* KEEPERS_SHOT=<file.ppm>: draw one still of the room, save it, quit */
    int          shot_frames;
} kh_game;

extern kh_game G;

void kh_game_go(const char *room_id);  /* walk to a room: door sound, ambience, save */
void kh_game_new_night(void);
void kh_game_follow(const char *go);    /* "@room", "@end", "@continue", "@new" */

void kh_input_event(const SDL_Event *e);
void kh_input_walk(float dt);

#endif
