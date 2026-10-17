/* The Keeper's Hour: the title screen. The lamp room turns slowly behind the
 * name of the game, and a short menu starts the night: Begin the night,
 * Carry on (when a night is saved), Options and Quit.
 * SPDX-License-Identifier: MIT */
#ifndef KH_TITLE_H
#define KH_TITLE_H

#include <SDL3/SDL.h>
#include <brender.h>

void kh_title_open(int can_continue);
int  kh_title_active(void);

/* Up and Down (or the D-pad) move, Enter, Space, E or A choose, Esc quits.
 * Returns 1 when the title used the event. */
int  kh_title_event(const SDL_Event *e);

void kh_title_draw(br_pixelmap *pm, br_colour ink, br_colour accent, br_colour panel);

/* While walking: the room name at the top, and at the bottom what the talk
 * key would do here, or the controls. */
void kh_hud_draw(br_pixelmap *pm, br_colour ink, br_colour accent);

#endif
