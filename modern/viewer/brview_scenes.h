/* brview scenes: the period sample models and how to frame them.
 * SPDX-License-Identifier: MIT */
#ifndef BRVIEW_SCENES_H
#define BRVIEW_SCENES_H

#include <brender.h>

int         BrViewSceneCount(void);
const char *BrViewSceneName(int index);

/* Use a model (and optional texture) from the command line as scene 0. */
void BrViewSceneSetCustom(const char *model_path, const char *texture_path);

/* Replace the children of parent with the scene's models, framed to fit a
 * unit sphere at the origin, all drawn with material. With period, the
 * material is set up for BRender's 8-bit path: a std.pal ramp, or the 8-bit
 * map lit through shade.tab. */
br_error BrViewSceneLoad(int index, br_actor *parent, br_material *material, br_boolean textured, br_boolean period,
                         char *err, size_t err_len);

/* std.pal, the palette the period look is shown through. */
br_pixelmap *BrViewScenePalette(void);

#endif
