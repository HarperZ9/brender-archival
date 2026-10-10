/* The Keeper's Hour: options (volume, look speed) and key remapping, saved
 * to the player's preferences folder.
 * SPDX-License-Identifier: MIT */
#ifndef KH_OPTIONS_H
#define KH_OPTIONS_H

#include <SDL3/SDL.h>
#include <brender.h>

typedef enum kh_action { KH_ACT_FORWARD, KH_ACT_BACK, KH_ACT_LEFT, KH_ACT_RIGHT, KH_ACT_TALK, KH_ACT_LEAVE, KH_ACT_COUNT } kh_action;

typedef struct kh_options {
    int          volume;               /* 0 to 10 */
    int          look;                 /* 1 to 10: how fast the view turns */
    SDL_Scancode keys[KH_ACT_COUNT];
    int          open;                 /* the options screen is showing */
    int          row;                  /* highlighted row */
    int          capturing;            /* waiting for a key for this row's action */
} kh_options;

void kh_options_defaults(kh_options *o);
int  kh_options_load(kh_options *o, const char *path); /* 0 if read; defaults otherwise */
int  kh_options_save(const kh_options *o, const char *path);
const char *kh_options_path(void);

/* F2 or the gamepad's Back button opens and closes the screen. Returns 1 when
 * the event was used by the options screen and the game should ignore it. */
int  kh_options_event(kh_options *o, const SDL_Event *e);
int  kh_options_pressed(const kh_options *o, kh_action a, SDL_Scancode sc);
int  kh_options_held(const kh_options *o, kh_action a, const bool *keys);

/* Rebind a key and change the volume by simulated key presses, save to a
 * scratch file and read it back. For the smoke run; returns the problems. */
int kh_options_check(void);

void kh_options_draw(const kh_options *o, br_pixelmap *pm, br_colour ink, br_colour accent, br_colour panel);

#endif
