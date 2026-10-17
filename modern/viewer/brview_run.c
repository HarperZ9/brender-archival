/* brview: the command line it runs with, and the settings of a still frame.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>

#include <SDL3/SDL.h>
#include "brdisplay.h"
#include "brview_run.h"

char **brview_argv(int argc, char **argv, int software, int *out_argc)
{
    static char *used[64];
    int i, n = 0, given = 0, forced = 0;
    for (i = 0; i < argc && i < 58; i++) {
        given |= strcmp(argv[i], "--software-bpp") == 0;
        forced |= strcmp(argv[i], "--force-software") == 0;
    }
    for (i = 0; i < argc && i < 58; i++) {
        used[n++] = argv[i];
        if (i == 0 && !given) {
            used[n++] = "--software-bpp";
            used[n++] = "24";
        }
        if (i == 0 && !forced && software)
            used[n++] = "--force-software";
    }
    *out_argc = n;
    return used;
}

static int env_int(const char *name, int fallback)
{
    const char *v = SDL_getenv(name);
    return v != NULL && *v != '\0' ? SDL_atoi(v) : fallback;
}

brview_still brview_still_from_env(void)
{
    brview_still s;
    s.scene = env_int("BRVIEW_SCENE", 0);
    s.textured = env_int("BRVIEW_TEXTURE", 1) != 0;
    s.unlit = env_int("BRVIEW_UNLIT", 0) != 0;
    return s;
}

static const char *options_path(void)
{
    static char path[1024];
    char *dir;
    if (path[0] == '\0' && (dir = SDL_GetPrefPath("HarperZ9", "brview")) != NULL) {
        SDL_snprintf(path, sizeof(path), "%soptions.cfg", dir);
        SDL_free(dir);
    }
    return path[0] ? path : NULL;
}

void brview_options_load(brview_options *o)
{
    char word[32];
    int v;
    FILE *f;
    if (options_path() == NULL || (f = fopen(options_path(), "r")) == NULL)
        return;
    while (fscanf(f, "%31s %d", word, &v) == 2) {
        if (strcmp(word, "pixel") == 0 && v >= BRD_PIXEL_MIN && v <= BRD_PIXEL_MAX) o->pixel = v;
        else if (strcmp(word, "fov") == 0 && v >= BRD_FOV_MIN && v <= BRD_FOV_MAX) o->fov = v;
        else if (strcmp(word, "vsync") == 0 && (v == 0 || v == 1)) o->vsync = v;
        else if (strcmp(word, "period") == 0 && (v == 0 || v == 1)) o->period = v;
    }
    fclose(f);
}

void brview_options_save(const brview_options *o)
{
    FILE *f;
    if (options_path() == NULL || (f = fopen(options_path(), "w")) == NULL)
        return;
    fprintf(f, "pixel %d\nfov %d\nvsync %d\nperiod %d\n", o->pixel, o->fov, o->vsync, o->period);
    fclose(f);
}
