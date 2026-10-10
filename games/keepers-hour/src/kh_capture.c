/* The Keeper's Hour: capturing frames for films and checks, with no wall clock.
 * See kh_capture.h for the settings.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <stdlib.h>

#include <SDL3/SDL.h>
#include "kh_capture.h"
#include "kh_tex.h"

#define WARMUP 20 /* frames drawn before the first one is kept: the renderer settles */

static struct {
    const char *shot, *dir;
    float       clock0, fps, yaw0, yaw_speed;
    int         total, drawn, written, ui;
} C;

static float env_float(const char *name, float fallback)
{
    const char *v = SDL_getenv(name);
    return v ? (float)atof(v) : fallback;
}

int kh_capture_init(void)
{
    C.shot = SDL_getenv("KEEPERS_SHOT");
    C.dir = C.shot ? NULL : SDL_getenv("KEEPERS_RECORD");
    C.clock0 = env_float("KEEPERS_CLOCK", C.shot ? 1.0f : 0.0f);
    C.fps = env_float("KEEPERS_FPS", 30.0f);
    if (C.fps <= 0.0f) C.fps = 30.0f;
    C.total = C.dir ? (int)(env_float("KEEPERS_SECONDS", 4.0f) * C.fps + 0.5f) : 1;
    if (C.total < 1) C.total = 1;
    C.yaw0 = env_float("KEEPERS_YAW", 0.0f);
    C.yaw_speed = env_float("KEEPERS_YAW_SPEED", 0.0f);
    C.ui = SDL_getenv("KEEPERS_CAPTURE_UI") != NULL;
    if (C.dir) SDL_CreateDirectory(C.dir);
    return kh_capture_active();
}

int kh_capture_active(void) { return C.shot != NULL || C.dir != NULL; }
int kh_capture_ui(void) { return C.ui; }

static float game_time(void) { return C.drawn < WARMUP ? 0.0f : (float)(C.drawn - WARMUP) / C.fps; }

float kh_capture_clock(void) { return C.clock0 + game_time(); }
float kh_capture_yaw(void) { return C.yaw0 + C.yaw_speed * game_time(); }

int kh_capture_frame(br_pixelmap *pm, int hw_accel, int *problems)
{
    char path[1100];
    if (!kh_capture_active())
        return 0;
    if (C.drawn++ < WARMUP)
        return 0;
    if (C.shot)
        snprintf(path, sizeof(path), "%s", C.shot);
    else
        snprintf(path, sizeof(path), "%s/frame-%05d.ppm", C.dir, C.written);
    *problems += kh_frame_write(pm, path, hw_accel) != 0;
    return ++C.written >= C.total;
}
