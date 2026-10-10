/* The Keeper's Hour: options (volume, look speed) and key remapping.
 *
 * Rows: Volume, Look speed, one row per action, Reset, Close. Up and Down move,
 * Left and Right change a value, Enter on an action waits for the next key and
 * binds it. Every change is saved at once.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>

#include "kh_tex.h"
#include "kh_audio.h"
#include "kh_options.h"

static const char *action_names[KH_ACT_COUNT] = {"Walk forward", "Walk back", "Step left", "Step right", "Talk, continue, choose", "Leave a conversation"};
static const char *action_ids[KH_ACT_COUNT] = {"forward", "back", "left", "right", "talk", "leave"};
#define ROW_VOLUME 0
#define ROW_LOOK   1
#define ROW_KEYS   2
#define ROW_RESET  (ROW_KEYS + KH_ACT_COUNT)
#define ROW_CLOSE  (ROW_RESET + 1)
#define ROWS       (ROW_CLOSE + 1)

void kh_options_defaults(kh_options *o)
{
    static const SDL_Scancode keys[KH_ACT_COUNT] = {SDL_SCANCODE_W, SDL_SCANCODE_S, SDL_SCANCODE_A, SDL_SCANCODE_D, SDL_SCANCODE_E, SDL_SCANCODE_ESCAPE};
    int open = o->open, row = o->row;
    memset(o, 0, sizeof(*o));
    o->volume = 6;
    o->look = 5;
    memcpy(o->keys, keys, sizeof(keys));
    o->open = open;
    o->row = row;
}

static const char *path_override; /* the self-check saves somewhere else */

const char *kh_options_path(void)
{
    static char path[1024];
    char *dir;
    if (path_override)
        return path_override;
    if (path[0] == '\0' && (dir = SDL_GetPrefPath("HarperZ9", "The Keeper's Hour")) != NULL) {
        snprintf(path, sizeof(path), "%soptions.cfg", dir);
        SDL_free(dir);
    }
    return path[0] ? path : NULL;
}

int kh_options_load(kh_options *o, const char *path)
{
    char word[32];
    int a, v;
    FILE *f;
    kh_options_defaults(o);
    if (path == NULL || (f = fopen(path, "r")) == NULL)
        return -1;
    while (fscanf(f, "%31s %d", word, &v) == 2) {
        if (strcmp(word, "volume") == 0 && v >= 0 && v <= 10) o->volume = v;
        else if (strcmp(word, "look") == 0 && v >= 1 && v <= 10) o->look = v;
        for (a = 0; a < KH_ACT_COUNT; a++)
            if (strcmp(word, action_ids[a]) == 0 && v > 0 && v < SDL_SCANCODE_COUNT) o->keys[a] = (SDL_Scancode)v;
    }
    fclose(f);
    return 0;
}

int kh_options_save(const kh_options *o, const char *path)
{
    FILE *f;
    int a;
    if (path == NULL || (f = fopen(path, "w")) == NULL)
        return -1;
    fprintf(f, "volume %d\nlook %d\n", o->volume, o->look);
    for (a = 0; a < KH_ACT_COUNT; a++)
        fprintf(f, "%s %d\n", action_ids[a], (int)o->keys[a]);
    return fclose(f) == 0 ? 0 : -1;
}

int kh_options_pressed(const kh_options *o, kh_action a, SDL_Scancode sc) { return o->keys[a] == sc; }
int kh_options_held(const kh_options *o, kh_action a, const bool *keys) { return keys[o->keys[a]]; }

static void change(kh_options *o, int delta)
{
    if (o->row == ROW_VOLUME) {
        o->volume = SDL_clamp(o->volume + delta, 0, 10);
        kh_audio_volume(o->volume);
    } else if (o->row == ROW_LOOK) {
        o->look = SDL_clamp(o->look + delta, 1, 10);
    }
}

static void activate(kh_options *o)
{
    if (o->row >= ROW_KEYS && o->row < ROW_RESET) o->capturing = 1;
    else if (o->row == ROW_RESET) { kh_options_defaults(o); kh_audio_volume(o->volume); }
    else if (o->row == ROW_CLOSE) o->open = 0;
}

int kh_options_event(kh_options *o, const SDL_Event *e)
{
    int was_open = o->open;
    if (e->type == SDL_EVENT_KEY_DOWN && o->capturing) {
        if (e->key.scancode != SDL_SCANCODE_F2)
            o->keys[o->row - ROW_KEYS] = e->key.scancode;
        o->capturing = 0;
        kh_options_save(o, kh_options_path());
        return 1;
    }
    if ((e->type == SDL_EVENT_KEY_DOWN && e->key.scancode == SDL_SCANCODE_F2)
        || (e->type == SDL_EVENT_GAMEPAD_BUTTON_DOWN && e->gbutton.button == SDL_GAMEPAD_BUTTON_BACK)) {
        o->open = !o->open;
        o->capturing = 0;
        return 1;
    }
    if (!o->open)
        return 0;
    if (e->type == SDL_EVENT_KEY_DOWN) {
        switch (e->key.scancode) {
        case SDL_SCANCODE_UP: o->row = (o->row + ROWS - 1) % ROWS; break;
        case SDL_SCANCODE_DOWN: o->row = (o->row + 1) % ROWS; break;
        case SDL_SCANCODE_LEFT: change(o, -1); break;
        case SDL_SCANCODE_RIGHT: change(o, 1); break;
        case SDL_SCANCODE_RETURN: case SDL_SCANCODE_SPACE: activate(o); break;
        case SDL_SCANCODE_ESCAPE: o->open = 0; break;
        default: break;
        }
    } else if (e->type == SDL_EVENT_GAMEPAD_BUTTON_DOWN) {
        switch (e->gbutton.button) {
        case SDL_GAMEPAD_BUTTON_DPAD_UP: o->row = (o->row + ROWS - 1) % ROWS; break;
        case SDL_GAMEPAD_BUTTON_DPAD_DOWN: o->row = (o->row + 1) % ROWS; break;
        case SDL_GAMEPAD_BUTTON_DPAD_LEFT: change(o, -1); break;
        case SDL_GAMEPAD_BUTTON_DPAD_RIGHT: change(o, 1); break;
        case SDL_GAMEPAD_BUTTON_SOUTH: activate(o); break;
        case SDL_GAMEPAD_BUTTON_EAST: o->open = 0; break;
        default: break;
        }
    }
    if (was_open) kh_options_save(o, kh_options_path());
    return 1;
}

void kh_options_draw(const kh_options *o, br_pixelmap *pm, br_colour ink, br_colour accent, br_colour panel)
{
    br_int_32 x = -210, y = -150, step = BrPixelmapTextHeight(pm, BrFontProp7x9) + 9;
    char row[128];
    int r;
    if (!o->open)
        return;
    BrPixelmapRectangleFill(pm, x - 24, y - 24, 468, step * (ROWS + 4) + 24, panel);
    kh_text(pm, x, y, accent, "Options   (F2 or Back to close)");
    y += step * 2;
    for (r = 0; r < ROWS; r++, y += step) {
        if (r == ROW_VOLUME) snprintf(row, sizeof(row), "Volume              < %d >", o->volume);
        else if (r == ROW_LOOK) snprintf(row, sizeof(row), "Look speed          < %d >", o->look);
        else if (r < ROW_RESET)
            snprintf(row, sizeof(row), "%-24s %s", action_names[r - ROW_KEYS],
                     o->capturing && o->row == r ? "press a key..." : SDL_GetScancodeName(o->keys[r - ROW_KEYS]));
        else snprintf(row, sizeof(row), "%s", r == ROW_RESET ? "Reset to defaults" : "Close");
        kh_text(pm, x, y, r == o->row ? accent : ink, row);
    }
    kh_text(pm, x, y + step, ink, "Up, Down: choose   Left, Right: change   Enter: set a key");
}

static void send_key(kh_options *o, SDL_Scancode sc)
{
    SDL_Event e;
    SDL_zero(e);
    e.type = SDL_EVENT_KEY_DOWN;
    e.key.scancode = sc;
    kh_options_event(o, &e);
}

int kh_options_check(void)
{
    char path[1100];
    kh_options o, back;
    int ok;
    const char *real = kh_options_path();
    snprintf(path, sizeof(path), "%s.check", real ? real : "options.cfg");
    path_override = path;
    SDL_zero(o);
    kh_options_defaults(&o);
    /* the way a player rebinds: F2, down twice to "Walk forward", Enter, then the new key */
    send_key(&o, SDL_SCANCODE_F2);
    send_key(&o, SDL_SCANCODE_DOWN);
    send_key(&o, SDL_SCANCODE_DOWN);
    send_key(&o, SDL_SCANCODE_RETURN);
    send_key(&o, SDL_SCANCODE_Q);
    send_key(&o, SDL_SCANCODE_UP);
    send_key(&o, SDL_SCANCODE_UP);
    send_key(&o, SDL_SCANCODE_RIGHT); /* volume up one */
    send_key(&o, SDL_SCANCODE_F2);
    ok = o.keys[KH_ACT_FORWARD] == SDL_SCANCODE_Q && o.volume == 7 && !o.open
         && kh_options_load(&back, path) == 0 && back.keys[KH_ACT_FORWARD] == SDL_SCANCODE_Q && back.volume == 7;
    remove(path);
    path_override = NULL;
    printf("keepers options: rebind and save %s\n", ok ? "ok" : "failed");
    return ok ? 0 : 1;
}
