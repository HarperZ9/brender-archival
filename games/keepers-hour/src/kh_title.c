/* The Keeper's Hour: the title screen and the walking HUD. See kh_title.h.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>

#include "kh_audio.h"
#include "kh_game.h"
#include "kh_tex.h"
#include "kh_title.h"

enum { ITEM_BEGIN, ITEM_CONTINUE, ITEM_OPTIONS, ITEM_QUIT, ITEM_COUNT };

static const char *item_names[ITEM_COUNT] = {"Begin the night", "Carry on from where you were", "Options", "Quit"};

static struct {
    int active, can_continue, selected;
    br_int_32 item_y[ITEM_COUNT], item_h, origin_y; /* where the items were drawn, for the mouse */
} T;

static int shown(int item) { return item != ITEM_CONTINUE || T.can_continue; }

void kh_title_open(int can_continue)
{
    T.active = 1;
    T.can_continue = can_continue;
    T.selected = can_continue ? ITEM_CONTINUE : ITEM_BEGIN;
}

int kh_title_active(void) { return T.active; }

static void move(int delta)
{
    do T.selected = (T.selected + delta + ITEM_COUNT) % ITEM_COUNT;
    while (!shown(T.selected));
}

static void choose(void)
{
    SDL_Event quit = {.type = SDL_EVENT_QUIT};
    switch (T.selected) {
    case ITEM_BEGIN: T.active = 0; kh_game_new_night(); break;
    case ITEM_CONTINUE: T.active = 0; kh_game_follow("@continue"); break;
    case ITEM_OPTIONS: G.opt.open = 1; break;
    default: SDL_PushEvent(&quit); break;
    }
    kh_audio_play(KH_SND_LINE, 2);
}

int kh_title_event(const SDL_Event *e)
{
    if (!T.active)
        return 0;
    if (e->type == SDL_EVENT_KEY_DOWN) {
        SDL_Keycode k = e->key.key;
        if (k == SDLK_UP || k == SDLK_W) move(-1);
        else if (k == SDLK_DOWN || k == SDLK_S) move(1);
        else if (k == SDLK_RETURN || k == SDLK_SPACE || k == SDLK_E) choose();
        else if (k == SDLK_ESCAPE) { T.selected = ITEM_QUIT; choose(); }
        return 1;
    }
    if (e->type == SDL_EVENT_GAMEPAD_BUTTON_DOWN) {
        if (e->gbutton.button == SDL_GAMEPAD_BUTTON_DPAD_UP) move(-1);
        else if (e->gbutton.button == SDL_GAMEPAD_BUTTON_DPAD_DOWN) move(1);
        else if (e->gbutton.button == SDL_GAMEPAD_BUTTON_SOUTH || e->gbutton.button == SDL_GAMEPAD_BUTTON_START) choose();
        return 1;
    }
    if (e->type == SDL_EVENT_MOUSE_MOTION) { /* the item under the pointer */
        br_int_32 y = (br_int_32)e->motion.y - T.origin_y;
        int i;
        for (i = 0; i < ITEM_COUNT; i++)
            if (shown(i) && y >= T.item_y[i] - T.item_h / 4 && y < T.item_y[i] + T.item_h)
                T.selected = i;
        return 1;
    }
    if (e->type == SDL_EVENT_MOUSE_BUTTON_DOWN && e->button.button == SDL_BUTTON_LEFT) {
        choose();
        return 1;
    }
    return 0;
}

/* Centred text, at k times the current text size. */
static void centred(br_pixelmap *pm, br_int_32 y, br_colour colour, const char *s, int k)
{
    br_int_32 w = BrPixelmapTextWidth(pm, BrFontProp7x9, s) * kh_text_scale() * k;
    kh_text_at(pm, -w / 2, y, colour, s, kh_text_scale() * k);
}

void kh_title_draw(br_pixelmap *pm, br_colour ink, br_colour accent, br_colour panel)
{
    br_int_32 top = -pm->origin_y, h = kh_text_h(pm), y;
    char row[96];
    int i;
    if (!T.active)
        return;
    T.item_h = h + kh_ui(10);
    T.origin_y = pm->origin_y;
    y = top + pm->height / 6;
    { /* a band behind the name, so the room does not show through the letters */
        br_int_32 w = BrPixelmapTextWidth(pm, BrFontProp7x9, "The Keeper's Hour") * kh_text_scale() * 3 + kh_ui(80);
        BrPixelmapRectangleFill(pm, -w / 2, y - kh_ui(18), w, h * 4 + kh_ui(44), panel);
    }
    centred(pm, y, accent, "The Keeper's Hour", 3);
    centred(pm, y += h * 3 + kh_ui(10), ink, "The last night of the light at Relay Nine.", 1);
    y = top + pm->height * 3 / 5;
    BrPixelmapRectangleFill(pm, kh_ui(-170), y - kh_ui(14), kh_ui(340), (h + kh_ui(10)) * (ITEM_COUNT - !T.can_continue) + kh_ui(20), panel);
    for (i = 0; i < ITEM_COUNT; i++) {
        if (!shown(i))
            continue;
        snprintf(row, sizeof(row), "%s %s %s", i == T.selected ? ">" : " ", item_names[i], i == T.selected ? "<" : " ");
        centred(pm, y, i == T.selected ? accent : ink, row, 1);
        T.item_y[i] = y;
        y += h + kh_ui(10);
    }
    centred(pm, pm->height - pm->origin_y - kh_ui(28), ink,
            "Up, Down and Enter, or the gamepad   F2: options   Drawn by BRender, Argonaut 1998", 1);
}

/* The room name, and what the E key would do here. */
void kh_hud_draw(br_pixelmap *pm, br_colour ink, br_colour accent)
{
    char text[128];
    snprintf(text, sizeof(text), "The Keeper's Hour   %s", kh_rooms[G.world.current].title);
    kh_text(pm, -pm->origin_x + kh_ui(12), -pm->origin_y + kh_ui(20), accent, text);
    if (G.ended || kh_talk_open_p(&G.talk))
        return;
    if (G.near_talker >= 0) {
        const kh_talker *t = kh_world_talker(&G.world, G.near_talker);
        snprintf(text, sizeof(text), "%s, click or A: %s %s", SDL_GetScancodeName(G.opt.keys[KH_ACT_TALK]),
                 t->node[0] == '@' ? "go through" : "talk to", t->name);
        kh_text(pm, -kh_text_w(pm, text) / 2, pm->height - pm->origin_y - kh_ui(40), ink, text);
    } else {
        kh_text(pm, -pm->origin_x + kh_ui(12), pm->height - pm->origin_y - kh_ui(24), ink,
                       "Walk: WASD or left stick   Look: right drag or right stick   Options: F2   Quit: Esc");
    }
}
