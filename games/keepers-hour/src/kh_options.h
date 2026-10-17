/* The Keeper's Hour: options (volume, look speed, pixel size, field of view,
 * vsync, period look) and key remapping, saved
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
    int          pixel;                /* 1 to 6: screen pixels per scene pixel (brdisplay.h) */
    int          fov;                  /* 40 to 90 degrees, vertical, in steps of 5 */
    int          vsync;                /* 0 or 1: wait for the display (OpenGL only) */
    int          period;               /* 0 or 1: 256 colours through BRender's 8-bit path */
    int          text;                 /* KH_TEXT_AUTO (0) or 1 to 3: text size (kh_text.h) */
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

/* 0 when a change to the period look waits for the next start (OpenGL). */
extern int kh_options_period_now;

void kh_options_draw(const kh_options *o, br_pixelmap *pm, br_colour ink, br_colour accent, br_colour panel);

#endif
