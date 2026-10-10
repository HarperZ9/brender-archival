/* The Keeper's Hour: saving the night at each room, and the end of the night.
 *
 * The save is plain text: the room, the dice state, the voices' tallies and
 * the ids of every node already visited.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>

#include <SDL3/SDL.h>
#include "kh_save.h"

const char *kh_save_path(void)
{
    static char path[1024];
    char *dir;
    if (path[0])
        return path;
    if ((dir = SDL_GetPrefPath("HarperZ9", "The Keeper's Hour")) == NULL)
        return NULL;
    snprintf(path, sizeof(path), "%snight.sav", dir);
    SDL_free(dir);
    return path;
}

int kh_save_write(const char *path, const char *room, const kh_talk *t)
{
    FILE *f;
    int i;
    if (path == NULL || (f = fopen(path, "w")) == NULL)
        return -1;
    fprintf(f, "keepers-hour-save 1\nroom %s\nrng %u\nheard", room, t->rng);
    for (i = 0; i < KH_VOICE_COUNT; i++) fprintf(f, " %d", t->heard[i]);
    fprintf(f, "\nasked");
    for (i = 0; i < KH_VOICE_COUNT; i++) fprintf(f, " %d", t->asked[i]);
    fprintf(f, "\nvisited");
    for (i = 0; i < t->script->nnodes; i++)
        if (t->visited[i]) fprintf(f, " %s", t->script->nodes[i].id);
    fprintf(f, "\n");
    return fclose(f) == 0 ? 0 : -1;
}

int kh_save_read(const char *path, char *room, size_t room_len, kh_talk *t)
{
    char line[8192], word[64];
    FILE *f;
    int version = 0, i;
    if (path == NULL || (f = fopen(path, "r")) == NULL)
        return -1;
    while (fgets(line, sizeof(line), f) != NULL) {
        if (sscanf(line, "keepers-hour-save %d", &version) == 1) continue;
        if (sscanf(line, "room %63s", word) == 1) snprintf(room, room_len, "%s", word);
        else if (sscanf(line, "rng %u", &t->rng) == 1) continue;
        else if (strncmp(line, "heard", 5) == 0) sscanf(line + 5, "%d %d %d %d", &t->heard[0], &t->heard[1], &t->heard[2], &t->heard[3]);
        else if (strncmp(line, "asked", 5) == 0) sscanf(line + 5, "%d %d %d %d", &t->asked[0], &t->asked[1], &t->asked[2], &t->asked[3]);
        else if (strncmp(line, "visited", 7) == 0) {
            char *p = line + 7;
            int used = 0;
            while (sscanf(p, "%63s%n", word, &used) == 1) {
                const kh_node *n = kh_script_find(t->script, word);
                if (n != NULL) t->visited[n - t->script->nodes] = 1;
                p += used;
            }
        }
    }
    fclose(f);
    for (i = 0; i < KH_VOICE_COUNT; i++)
        if (t->heard[i] < 0 || t->asked[i] < t->heard[i]) return -1;
    return version == 1 ? 0 : -1;
}

int  kh_save_exists(const char *path) { FILE *f = path ? fopen(path, "r") : NULL; if (f) fclose(f); return f != NULL; }
void kh_save_forget(const char *path) { if (path) remove(path); }

static const char *endings[][2] = {
    {"ending_keep", "The light kept"},
    {"ending_ceremony", "The light let go"},
    {"ending_town", "The light given away"},
};

const char *kh_ending_title(const char *node_id)
{
    size_t i;
    for (i = 0; i < sizeof(endings) / sizeof(endings[0]); i++)
        if (strcmp(node_id, endings[i][0]) == 0) return endings[i][1];
    return NULL;
}

void kh_end_card(br_pixelmap *pm, const kh_talk *t, br_colour ink, br_colour accent, br_colour panel)
{
    const char *title = kh_ending_title(t->last);
    br_int_32 x = -180, y = -110, step = BrPixelmapTextHeight(pm, BrFontProp7x9) + 8;
    char row[128];
    int v;
    BrPixelmapRectangleFill(pm, x - 24, y - 24, 408, 260, panel);
    BrPixelmapText(pm, x, y, accent, BrFontProp7x9, "Dawn. 06:12.");
    BrPixelmapText(pm, x, y += step * 2, ink, BrFontProp7x9, title ? title : "The night ends");
    BrPixelmapText(pm, x, y += step * 2, accent, BrFontProp7x9, "The voices you listened to tonight:");
    for (v = 0; v < KH_VOICE_COUNT; v++) {
        snprintf(row, sizeof(row), "%-7s heard %d of %d times", kh_voice_name((kh_voice)v), t->heard[v], t->asked[v]);
        BrPixelmapText(pm, x + 12, y += step, ink, BrFontProp7x9, row);
    }
    BrPixelmapText(pm, x, y += step * 2, accent, BrFontProp7x9, "R or Start: begin the night again   Esc: leave");
}

typedef struct route { const char *needs[2]; const char *choice; const char *ending; } route;

static int run_route(const kh_script *s, const route *r)
{
    kh_talk t;
    int i, k;
    kh_talk_init(&t, s, 1998u);
    for (i = 0; i < 2 && r->needs[i]; i++)
        if (kh_talk_open(&t, r->needs[i]) != 0) return 1;
    if (kh_talk_open(&t, "decide") != 0) return 1;
    while (!t.choosing) kh_talk_advance(&t);
    for (k = 0; k < kh_talk_visible_count(&t); k++)
        if (strncmp(t.node->choices[kh_talk_visible(&t, k)].text, r->choice, strlen(r->choice)) == 0) break;
    kh_talk_choose(&t, k);
    if (strcmp(t.last, r->ending) != 0 || t.node == NULL) return 1;
    while (!t.choosing) kh_talk_advance(&t);
    kh_talk_choose(&t, 0);
    return strcmp(t.go, "@end") == 0 ? 0 : 1;
}

int kh_end_check(const kh_script *s)
{
    static const route routes[] = {
        {{"letter", NULL}, "Keep it burning", "ending_keep"},
        {{"letter", "painting_two_ledger"}, "Do what Agnes did", "ending_ceremony"},
        {{"letter", "town_window"}, "Turn the lens by hand", "ending_town"},
    };
    char path[1200], room[64] = "";
    kh_talk a, b;
    int i, reached = 0, save_ok;
    for (i = 0; i < 3; i++) reached += run_route(s, &routes[i]) == 0;
    kh_talk_init(&a, s, 7u);
    kh_talk_open(&a, "radio_tune");
    a.heard[KH_LEDGER] = 2; a.asked[KH_LEDGER] = 3;
    snprintf(path, sizeof(path), "%s.check", kh_save_path() ? kh_save_path() : "night.sav");
    kh_talk_init(&b, s, 1u);
    save_ok = kh_save_write(path, "radio", &a) == 0 && kh_save_read(path, room, sizeof(room), &b) == 0 && strcmp(room, "radio") == 0
              && b.rng == a.rng && b.heard[KH_LEDGER] == 2 && memcmp(a.visited, b.visited, sizeof(a.visited)) == 0;
    kh_save_forget(path);
    printf("keepers endings: %d of 3 reached, save %s\n", reached, save_ok ? "ok" : "failed");
    return (3 - reached) + !save_ok;
}
