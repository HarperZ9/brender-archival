/* brview: the command line it runs with, and the settings of a still frame.
 * SPDX-License-Identifier: MIT */
#ifndef BRVIEW_RUN_H
#define BRVIEW_RUN_H

/* argv with "--software-bpp 24" added unless a depth was given, and
 * "--force-software" when `software` is set (the period look needs it). Both
 * go straight after the program name, so they parse as options. */
char **brview_argv(int argc, char **argv, int software, int *out_argc);

/* A still (BRVIEW_SHOT) of one scene, set from the environment:
 *   BRVIEW_SCENE=n    the scene, counted from 0 (default 0)
 *   BRVIEW_TEXTURE=0  draw it untextured
 *   BRVIEW_UNLIT=1    draw it without lighting, in its flat material colour
 * Renderer comparisons use these (modern/parity/gl_vs_software.py). */
typedef struct brview_still {
    int scene, textured, unlit;
} brview_still;

brview_still brview_still_from_env(void);

/* The saved display options, in the preferences folder (options.cfg). Load
 * keeps the given values for anything missing or out of range. */
typedef struct brview_options {
    int pixel, fov, vsync, period;
} brview_options;

void brview_options_load(brview_options *o);
void brview_options_save(const brview_options *o);

#endif
