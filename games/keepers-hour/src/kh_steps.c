/* The Keeper's Hour: steps of the night that are not drawing or input: the
 * smoke route, the dawn, and opening nodes for stills.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>

#include "kh_audio.h"
#include "kh_capture.h"
#include "kh_game.h"
#include "kh_save.h"

/* KEEPERS_OPEN: one node, or several separated by commas, opened in turn
 * (for stills: what was seen tonight decides some lines and the dawn card). */
void kh_game_open_list(const char *list)
{
    char id[KH_ID_LEN];
    while (*list) {
        size_t n = strcspn(list, ",");
        snprintf(id, sizeof(id), "%.*s", (int)(n < sizeof(id) - 1 ? n : sizeof(id) - 1), list);
        G.problems += kh_talk_open(&G.talk, id) != 0;
        list += n + (list[n] == ',');
    }
}

/* Once the keeper has decided, the sky greys at the edges; at an ending it
 * turns to dawn. Stills and recordings take the sky as it will be. */
void kh_game_dawn_step(float dt)
{
    const char *last = G.talk.last;
    float target = G.ended || (kh_talk_open_p(&G.talk) && strncmp(last, "ending_", 7) == 0) ? 1.0f
                 : kh_talk_visited(&G.talk, "decide") ? 0.35f : 0.0f;
    if (kh_capture_active() || G.world.dawn > target + 0.5f) G.world.dawn = target; /* a new night starts dark */
    else if (G.world.dawn < target) G.world.dawn = SDL_min(target, G.world.dawn + 0.12f * dt);
}

void kh_game_smoke_step(void)
{
    SDL_Event q = {.type = SDL_EVENT_QUIT};
    if (G.smoke_room < kh_room_count) {
        kh_game_go(kh_rooms[G.smoke_room++].id);
    } else if (G.smoke_node < G.script.nnodes) {
        G.problems += kh_talk_open(&G.talk, G.script.nodes[G.smoke_node++].id) != 0;
    } else if (!G.smoke_ends) {
        G.smoke_ends = 1;
        G.problems += kh_end_check(&G.script);
        G.problems += kh_audio_check();
        G.problems += kh_options_check();
    } else {
        SDL_PushEvent(&q);
    }
}
