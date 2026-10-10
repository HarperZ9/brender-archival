/* The Keeper's Hour: shapes built from BRender model primitives.
 * No art files: every shape is made in code.
 * SPDX-License-Identifier: MIT */
#ifndef KH_SHAPES_H
#define KH_SHAPES_H

#include <brender.h>

#define KH_PI 3.14159265f

/* A lit material. two_sided 0 makes a one-sided surface (the cutaway walls). */
br_material *kh_material(const char *name, int r, int g, int b, int smooth, int two_sided);
/* An unlit material: the thing is its own light (the lens, the town lights). */
br_material *kh_glow(const char *name, int r, int g, int b);

/* An n-sided prism from y0 to y1, radius r0 at the bottom and r1 at the top.
 * inward: side faces point into the prism, so a one-sided wall shows only
 * from inside. A cone is a prism with one radius zero. */
br_model *kh_prism(const char *name, int n, float r0, float r1, float y0, float y1, int caps, int smooth, int inward);
/* Two faceted cones base to base: the lens, an eye seen edge-on. */
br_model *kh_lens(float radius, float half_height);
/* An upright quad of width w from y0 to y1 facing -x: a window or a picture. */
br_model *kh_panel(float w, float y0, float y1);

br_actor *kh_place(br_actor *parent, br_model *model, br_material *mat, float x, float y, float z, float turn);

#endif
