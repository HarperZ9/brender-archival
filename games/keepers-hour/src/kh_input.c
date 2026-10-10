/* The Keeper's Hour: keyboard, mouse and gamepad, through the remappable keys.
 * SPDX-License-Identifier: MIT */
#include <math.h>

#include "kh_game.h"

static void interact(void)
{
    if (G.ended)
        return;
    if (kh_talk_open_p(&G.talk)) {
        if (G.talk.choosing)
            kh_talk_choose(&G.talk, G.talk.selected);
        else
            kh_talk_advance(&G.talk);
    } else if (G.near_talker >= 0) {
        const kh_talker *t = kh_world_talker(&G.world, G.near_talker);
        if (t->node[0] == '@') kh_game_go(t->node + 1);
        else kh_talk_open(&G.talk, t->node);
    }
}

static void move_selection(int delta)
{
    int count = kh_talk_visible_count(&G.talk);
    if (kh_talk_open_p(&G.talk) && G.talk.choosing && count > 0)
        G.talk.selected = (G.talk.selected + delta + count) % count;
}

static void leave(void)
{
    if (kh_talk_open_p(&G.talk)) {
        kh_talk_close(&G.talk);
    } else {
        SDL_Event q = {.type = SDL_EVENT_QUIT};
        SDL_PushEvent(&q);
    }
}

static void key_down(const SDL_KeyboardEvent *k)
{
    if (G.ended && k->key == SDLK_R) kh_game_new_night();
    else if (kh_options_pressed(&G.opt, KH_ACT_TALK, k->scancode) || k->key == SDLK_SPACE || k->key == SDLK_RETURN) interact();
    else if (kh_options_pressed(&G.opt, KH_ACT_LEAVE, k->scancode)) leave();
    else if (k->key >= SDLK_1 && k->key <= SDLK_6) kh_talk_choose(&G.talk, (int)(k->key - SDLK_1));
    else if (k->key == SDLK_UP) move_selection(-1);
    else if (k->key == SDLK_DOWN) move_selection(1);
}

void kh_input_event(const SDL_Event *e)
{
    if (kh_options_event(&G.opt, e))
        return;
    switch (e->type) {
    case SDL_EVENT_KEY_DOWN: key_down(&e->key); break;
    case SDL_EVENT_MOUSE_BUTTON_DOWN: if (e->button.button == SDL_BUTTON_LEFT) interact(); break;
    case SDL_EVENT_MOUSE_MOTION: if (e->motion.state & SDL_BUTTON_RMASK) G.cam_yaw -= e->motion.xrel * 0.06f * G.opt.look; break;
    case SDL_EVENT_GAMEPAD_ADDED: if (G.pad == NULL) G.pad = SDL_OpenGamepad(e->gdevice.which); break;
    case SDL_EVENT_GAMEPAD_REMOVED: if (G.pad) { SDL_CloseGamepad(G.pad); G.pad = NULL; } break;
    case SDL_EVENT_GAMEPAD_BUTTON_DOWN:
        if (G.ended && e->gbutton.button == SDL_GAMEPAD_BUTTON_START) kh_game_new_night();
        else if (e->gbutton.button == SDL_GAMEPAD_BUTTON_SOUTH) interact();
        else if (e->gbutton.button == SDL_GAMEPAD_BUTTON_EAST) kh_talk_close(&G.talk);
        else if (e->gbutton.button == SDL_GAMEPAD_BUTTON_DPAD_UP) move_selection(-1);
        else if (e->gbutton.button == SDL_GAMEPAD_BUTTON_DPAD_DOWN) move_selection(1);
        break;
    default: break;
    }
}

static float axis(SDL_GamepadAxis a)
{
    float v = G.pad ? SDL_GetGamepadAxis(G.pad, a) / 32767.0f : 0.0f;
    return fabsf(v) < 0.18f ? 0.0f : v;
}

void kh_input_walk(float dt)
{
    const bool *k = SDL_GetKeyboardState(NULL);
    const kh_options *o = &G.opt;
    float fwd = (kh_options_held(o, KH_ACT_FORWARD, k) || k[SDL_SCANCODE_UP]) - (kh_options_held(o, KH_ACT_BACK, k) || k[SDL_SCANCODE_DOWN])
                - axis(SDL_GAMEPAD_AXIS_LEFTY);
    float side = (kh_options_held(o, KH_ACT_RIGHT, k) || k[SDL_SCANCODE_RIGHT]) - (kh_options_held(o, KH_ACT_LEFT, k) || k[SDL_SCANCODE_LEFT])
                 + axis(SDL_GAMEPAD_AXIS_LEFTX);
    float yaw = G.cam_yaw * 3.14159265f / 180.0f, dx, dz;
    G.cam_yaw -= axis(SDL_GAMEPAD_AXIS_RIGHTX) * 24.0f * G.opt.look * dt;
    if (G.ended || G.opt.open || kh_talk_open_p(&G.talk) || (fwd == 0 && side == 0))
        return;
    dx = (side * cosf(yaw) - fwd * sinf(yaw)) * 2.6f * dt;
    dz = (-side * sinf(yaw) - fwd * cosf(yaw)) * 2.6f * dt;
    G.keeper_x += dx;
    G.keeper_z += dz;
    kh_world_clamp(&G.world, &G.keeper_x, &G.keeper_z);
    G.facing = atan2f(dx, dz) * 180.0f / 3.14159265f;
}
