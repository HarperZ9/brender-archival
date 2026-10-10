/* The Keeper's Hour: the tower (M1), five rooms and their talkers.
 * Drawn by BRender 1.4 (BlazingRenderer/BRender, MIT) through brdemo and SDL3.
 *
 * KEEPERS_SMOKE=1 runs headless: checks every link in the night script, opens
 * every node once and enters every room, with a frame drawn for each, then
 * quits. The exit code is the number of problems found.
 * SPDX-License-Identifier: MIT */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h> /* the platform entry point: WinMain for a window-only program */
#include <brender.h>
#include "brdemo.h"
#include "kh_boot.h"
#include "kh_save.h"
#include "kh_script.h"
#include "kh_talk.h"
#include "kh_world.h"

static kh_script script;
static kh_talk   talk;
static kh_world  world;
static float     keeper_x = 0.0f, keeper_z = 3.2f, facing = 180.0f, cam_yaw = 0.0f, clock_s;
static int       near_talker = -1, smoke, smoke_node, smoke_room, smoke_ends, problems, ended;
static SDL_Gamepad *pad;

static void go_to_room(const char *id)
{
    int to = kh_room_find(id);
    if (to < 0) { problems++; return; }
    kh_world_enter(&world, to, world.current, &keeper_x, &keeper_z);
    if (!smoke && !ended)
        kh_save_write(kh_save_path(), kh_rooms[to].id, &talk); /* the night is saved at every room */
}

static void new_night(void)
{
    kh_save_forget(kh_save_path());
    kh_talk_init(&talk, &script, 1998u);
    ended = 0;
    kh_world_enter(&world, kh_room_find("lamp"), -1, &keeper_x, &keeper_z);
    kh_talk_open(&talk, "arrive");
}

static void continue_night(void)
{
    char room[64] = "lamp";
    kh_talk saved;
    kh_talk_init(&saved, &script, 1998u);
    if (kh_save_read(kh_save_path(), room, sizeof(room), &saved) != 0 || kh_room_find(room) < 0) {
        new_night();
        return;
    }
    talk = saved;
    kh_world_enter(&world, kh_room_find(room), -1, &keeper_x, &keeper_z);
}

/* A choice led to "@room" or "@@...": walk there, or end, continue or restart the night. */
static void follow(const char *go)
{
    if (strcmp(go, "@end") == 0) {
        ended = 1;
        kh_save_forget(kh_save_path());
    } else if (strcmp(go, "@continue") == 0) {
        continue_night();
    } else if (strcmp(go, "@new") == 0) {
        new_night();
    } else {
        go_to_room(go);
    }
}


static void place_camera(br_demo *demo)
{
    br_actor *cam = demo->camera;
    BrMatrix34Translate(&cam->t.t.mat, 0, 0, BR_SCALAR(10.0f));
    BrMatrix34PostRotateX(&cam->t.t.mat, BR_ANGLE_DEG(-52));
    BrMatrix34PostRotateY(&cam->t.t.mat, BR_ANGLE_DEG(cam_yaw));
    BrMatrix34PostTranslate(&cam->t.t.mat, BR_SCALAR(keeper_x), BR_SCALAR(1.2f), BR_SCALAR(keeper_z));
}

static br_error game_init(br_demo *demo)
{
    br_camera *c;
    SDL_InitSubSystem(SDL_INIT_GAMEPAD);
    smoke = SDL_getenv("KEEPERS_SMOKE") != NULL;
    if (kh_boot_load(&script) != 0)
        return BRE_FAIL;
    kh_talk_init(&talk, &script, 1998u);
    demo->clear_colour = BR_COLOUR_RGBA(6, 7, 12, 255);
    demo->camera = BrActorAdd(demo->world, BrActorAllocate(BR_ACTOR_CAMERA, NULL));
    demo->camera->t.type = BR_TRANSFORM_MATRIX34;
    c = demo->camera->type_data;
    c->type = BR_CAMERA_PERSPECTIVE_FOV;
    c->field_of_view = BR_ANGLE_DEG(55);
    c->hither_z = BR_SCALAR(0.1);
    c->yon_z = BR_SCALAR(60);
    demo->order_table->min_z = c->hither_z;
    demo->order_table->max_z = c->yon_z;
    kh_world_build(&world, demo->world);
    /* KEEPERS_ROOM=<room> starts in that room: for checking a room by eye. */
    kh_world_enter(&world, kh_room_find(SDL_getenv("KEEPERS_ROOM") && kh_room_find(SDL_getenv("KEEPERS_ROOM")) >= 0 ? SDL_getenv("KEEPERS_ROOM") : "lamp"), -1, &keeper_x, &keeper_z);
    /* KEEPERS_OPEN=<node> starts in that conversation: for writers testing a scene. */
    if (SDL_getenv("KEEPERS_OPEN"))
        kh_talk_open(&talk, SDL_getenv("KEEPERS_OPEN"));
    else
        kh_talk_open(&talk, !smoke && kh_save_exists(kh_save_path()) ? "resume" : "arrive");
    place_camera(demo);
    return BRE_OK;
}

static void interact(void)
{
    if (ended)
        return;
    if (kh_talk_open_p(&talk)) {
        if (talk.choosing)
            kh_talk_choose(&talk, talk.selected);
        else
            kh_talk_advance(&talk);
    } else if (near_talker >= 0) {
        const kh_talker *t = kh_world_talker(&world, near_talker);
        if (t->node[0] == '@') go_to_room(t->node + 1);
        else kh_talk_open(&talk, t->node);
    }
}

static void move_selection(int delta)
{
    int count = kh_talk_visible_count(&talk);
    if (kh_talk_open_p(&talk) && talk.choosing && count > 0)
        talk.selected = (talk.selected + delta + count) % count;
}

static void game_event(br_demo *demo, const SDL_Event *e)
{
    (void)demo;
    switch (e->type) {
    case SDL_EVENT_KEY_DOWN:
        if (ended && e->key.key == SDLK_R) { new_night(); break; }
        if (e->key.key == SDLK_E || e->key.key == SDLK_SPACE || e->key.key == SDLK_RETURN) interact();
        else if (e->key.key >= SDLK_1 && e->key.key <= SDLK_6) kh_talk_choose(&talk, (int)(e->key.key - SDLK_1));
        else if (e->key.key == SDLK_UP) move_selection(-1);
        else if (e->key.key == SDLK_DOWN) move_selection(1);
        else if (e->key.key == SDLK_ESCAPE) {
            if (kh_talk_open_p(&talk)) kh_talk_close(&talk);
            else { SDL_Event q = {.type = SDL_EVENT_QUIT}; SDL_PushEvent(&q); }
        }
        break;
    case SDL_EVENT_MOUSE_BUTTON_DOWN: if (e->button.button == SDL_BUTTON_LEFT) interact(); break;
    case SDL_EVENT_MOUSE_MOTION: if (e->motion.state & SDL_BUTTON_RMASK) cam_yaw -= e->motion.xrel * 0.3f; break;
    case SDL_EVENT_GAMEPAD_ADDED: if (pad == NULL) pad = SDL_OpenGamepad(e->gdevice.which); break;
    case SDL_EVENT_GAMEPAD_REMOVED: if (pad) { SDL_CloseGamepad(pad); pad = NULL; } break;
    case SDL_EVENT_GAMEPAD_BUTTON_DOWN:
        if (ended && e->gbutton.button == SDL_GAMEPAD_BUTTON_START) new_night();
        else if (e->gbutton.button == SDL_GAMEPAD_BUTTON_SOUTH) interact();
        else if (e->gbutton.button == SDL_GAMEPAD_BUTTON_EAST) kh_talk_close(&talk);
        else if (e->gbutton.button == SDL_GAMEPAD_BUTTON_DPAD_UP) move_selection(-1);
        else if (e->gbutton.button == SDL_GAMEPAD_BUTTON_DPAD_DOWN) move_selection(1);
        break;
    default: break;
    }
}

static float axis(SDL_GamepadAxis a)
{
    float v = pad ? SDL_GetGamepadAxis(pad, a) / 32767.0f : 0.0f;
    return fabsf(v) < 0.18f ? 0.0f : v;
}

static void walk(float dt)
{
    const bool *k = SDL_GetKeyboardState(NULL);
    float fwd = (k[SDL_SCANCODE_W] || k[SDL_SCANCODE_UP]) - (k[SDL_SCANCODE_S] || k[SDL_SCANCODE_DOWN]) - axis(SDL_GAMEPAD_AXIS_LEFTY);
    float side = (k[SDL_SCANCODE_D] || k[SDL_SCANCODE_RIGHT]) - (k[SDL_SCANCODE_A] || k[SDL_SCANCODE_LEFT]) + axis(SDL_GAMEPAD_AXIS_LEFTX);
    float yaw = cam_yaw * 3.14159265f / 180.0f, dx, dz;
    cam_yaw -= axis(SDL_GAMEPAD_AXIS_RIGHTX) * 120.0f * dt;
    if (ended || kh_talk_open_p(&talk) || (fwd == 0 && side == 0))
        return;
    dx = (side * cosf(yaw) - fwd * sinf(yaw)) * 2.6f * dt;
    dz = (-side * sinf(yaw) - fwd * cosf(yaw)) * 2.6f * dt;
    keeper_x += dx;
    keeper_z += dz;
    kh_world_clamp(&world, &keeper_x, &keeper_z);
    facing = atan2f(dx, dz) * 180.0f / 3.14159265f;
}

static void smoke_step(void)
{
    if (smoke_room < kh_room_count) {
        go_to_room(kh_rooms[smoke_room++].id);
        return;
    }
    if (smoke_node < script.nnodes) {
        if (kh_talk_open(&talk, script.nodes[smoke_node].id) != 0)
            problems++;
        smoke_node++;
        return;
    }
    if (!smoke_ends) {
        smoke_ends = 1;
        problems += kh_end_check(&script);
    }
    {
        SDL_Event q = {.type = SDL_EVENT_QUIT};
        SDL_PushEvent(&q);
    }
}

static void game_update(br_demo *demo, br_scalar dt_s)
{
    float dt = BrScalarToFloat(dt_s), fx, fz;
    clock_s += dt;
    if (smoke) smoke_step();
    else walk(dt);
    if (talk.go[0]) {
        char go[KH_ID_LEN];
        snprintf(go, sizeof(go), "%s", talk.go);
        talk.go[0] = '\0';
        follow(go);
    }
    demo->clear_colour = kh_world_sky(&world);
    kh_world_turn_lamp(&world, clock_s);
    world.keeper->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34RotateY(&world.keeper->t.t.mat, BR_ANGLE_DEG(facing));
    BrMatrix34PostTranslate(&world.keeper->t.t.mat, BR_SCALAR(keeper_x), 0, BR_SCALAR(keeper_z));
    fx = sinf(facing * 3.14159265f / 180.0f);
    fz = cosf(facing * 3.14159265f / 180.0f);
    near_talker = kh_world_talker_near(&world, keeper_x, keeper_z, fx, fz);
    place_camera(demo);
}

static void game_render(br_demo *demo)
{
    br_pixelmap *pm = demo->colour_buffer;
    br_colour ink = BR_COLOUR_RGBA(236, 230, 216, 255), accent = BR_COLOUR_RGBA(232, 180, 92, 255);
    BrDemoDefaultRender(demo);
    {
        char title[96];
        snprintf(title, sizeof(title), "The Keeper's Hour   %s", kh_rooms[world.current].title);
        BrPixelmapText(pm, -pm->origin_x + 12, -pm->origin_y + 20, accent, BrFontProp7x9, title);
    }
    if (!ended && !kh_talk_open_p(&talk) && near_talker >= 0) {
        char prompt[96];
        const kh_talker *t = kh_world_talker(&world, near_talker);
        snprintf(prompt, sizeof(prompt), "E, click or A: %s %s", t->node[0] == '@' ? "go through" : "talk to", t->name);
        BrPixelmapText(pm, -BrPixelmapTextWidth(pm, BrFontProp7x9, prompt) / 2, pm->height - pm->origin_y - 40, ink, BrFontProp7x9, prompt);
    } else if (!ended && !kh_talk_open_p(&talk)) {
        BrPixelmapText(pm, -pm->origin_x + 12, pm->height - pm->origin_y - 24, ink, BrFontProp7x9,
                       "WASD or left stick: walk   right drag or right stick: look   Esc: quit");
    }
    if (ended)
        kh_end_card(pm, &talk, ink, accent, BR_COLOUR_RGBA(14, 13, 18, 255));
    else
        kh_talk_draw(&talk, pm, ink, accent, BR_COLOUR_RGBA(14, 13, 18, 255));
}

static const br_demo_dispatch dispatch = {
    .init = game_init, .process_event = game_event, .update = game_update,
    .render = game_render, .on_resize = BrDemoDefaultOnResize, .destroy = BrDemoDefaultDestroy,
};

int main(int argc, char **argv)
{
    br_demo_run_args args;
    int ret;
    BrDemoDefaultArgs(&args);
    args.title = "The Keeper's Hour";
    if (BrDemoParseArgs(&args, argc, argv) != 0)
        return 1;
    args.no_stats = 1;
    BrLogSetLevel(args.verbose);
    ret = BrDemoRunArg(&dispatch, &args);
    if (SDL_getenv("KEEPERS_SMOKE") != NULL)
        printf("keepers smoke: %d rooms entered, %d nodes opened, %d problems, run %s\n", smoke_room, smoke_node, problems, ret == 0 ? "ok" : "failed");
    return ret != 0 ? ret : problems;
}
