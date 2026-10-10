/* The Keeper's Hour: reading the night script and checking it against the rooms.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>

#include <SDL3/SDL.h>
#include <brender.h>
#include "kh_boot.h"
#include "kh_rooms.h"

/* Every "@room" in the script and in the room table must name a room. */
static int check_rooms(const kh_script *s)
{
    int i, j, r, bad = 0;
    for (i = 0; i < s->nnodes; i++)
        for (j = 0; j < s->nodes[i].nchoices; j++) {
            const char *to = s->nodes[i].choices[j].pass;
            if (to[0] == '@' && to[1] != '@' && kh_room_find(to + 1) < 0) { BrLogError("KEEPER", "node %s: no room %s", s->nodes[i].id, to); bad++; }
        }
    for (r = 0; r < kh_room_count; r++)
        for (j = 0; j < kh_rooms[r].nprops; j++) {
            const kh_prop *p = &kh_rooms[r].props[j];
            if (p->node == NULL) continue;
            if (p->node[0] == '@' ? kh_room_find(p->node + 1) < 0 : kh_script_find(s, p->node) == NULL) {
                BrLogError("KEEPER", "room %s: %s leads to missing %s", kh_rooms[r].id, p->talker, p->node);
                bad++;
            }
        }
    return bad ? -1 : 0;
}

int kh_boot_load(kh_script *s)
{
    char path[1024], err[200];
    size_t size = 0;
    char *text;
    snprintf(path, sizeof(path), "%sdata/night.txt", SDL_GetBasePath());
    if ((text = SDL_LoadFile(path, &size)) == NULL) {
        BrLogError("KEEPER", "cannot read %s", path);
        return -1;
    }
    if (kh_script_parse(s, text, err, sizeof(err)) != 0 || kh_script_check_links(s, err, sizeof(err)) != 0) {
        BrLogError("KEEPER", "%s", err);
        SDL_free(text);
        return -1;
    }
    SDL_free(text);
    return check_rooms(s);
}
