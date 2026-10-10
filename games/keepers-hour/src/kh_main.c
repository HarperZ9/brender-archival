/* The Keeper's Hour: the night's main loop.
 * Drawn by BRender 1.4 (BlazingRenderer/BRender, MIT) through brdemo and SDL3.
 *
 * For checking by machine and by eye:
 *   KEEPERS_SMOKE=1   enter every room, open every node, reach every ending,
 *                     round-trip a save; the exit code counts the problems
 *   KEEPERS_SHOT=f    draw one still of the room into f (PPM) and quit
 *   KEEPERS_RECORD=d  write numbered frames at a fixed step (see kh_capture.h)
 *   KEEPERS_ROOM=r    start in room r      KEEPERS_OPEN=n   start in node n
 * SPDX-License-Identifier: MIT */
#include <math.h>
#include <stdio.h>
#include <string.h>

#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h> /* the platform entry point: WinMain for a window-only program */
#include <brender.h>
#include "brdemo.h"
#include "kh_audio.h"
#include "kh_boot.h"
#include "kh_capture.h"
#include "kh_game.h"
#include "kh_save.h"
#include "kh_tex.h"

kh_game G = {.keeper_z = 3.2f, .facing = 180.0f, .near_talker = -1};

static void set_ambience(void)
{
    const char *id = kh_rooms[G.world.current].id;
    kh_audio_ambience(strcmp(id, "lamp") == 0 ? KH_AMB_LAMP : strcmp(id, "radio") == 0 ? KH_AMB_RADIO
                      : strcmp(id, "gallery") == 0 ? KH_AMB_OUTSIDE : KH_AMB_INSIDE);
}

static void enter(int room, int from)
{
    kh_world_enter(&G.world, room, from, &G.keeper_x, &G.keeper_z);
    set_ambience();
}

void kh_game_go(const char *id)
{
    int to = kh_room_find(id);
    if (to < 0) { G.problems++; return; }
    kh_audio_play(KH_SND_DOOR, 0);
    enter(to, G.world.current);
    if (!G.smoke && !G.ended)
        kh_save_write(kh_save_path(), kh_rooms[to].id, &G.talk); /* the night is saved at every room */
}

void kh_game_new_night(void)
{
    kh_save_forget(kh_save_path());
    kh_talk_init(&G.talk, &G.script, 1998u);
    G.ended = 0;
    enter(kh_room_find("lamp"), -1);
    kh_talk_open(&G.talk, "arrive");
}

static void continue_night(void)
{
    char room[64] = "lamp";
    kh_talk saved;
    kh_talk_init(&saved, &G.script, 1998u);
    if (kh_save_read(kh_save_path(), room, sizeof(room), &saved) != 0 || kh_room_find(room) < 0) {
        kh_game_new_night();
        return;
    }
    G.talk = saved;
    enter(kh_room_find(room), -1);
}

void kh_game_follow(const char *go)
{
    if (strcmp(go, "@end") == 0) {
        G.ended = 1;
        kh_audio_play(KH_SND_DAWN, 0);
        kh_save_forget(kh_save_path());
    } else if (strcmp(go, "@continue") == 0) {
        continue_night();
    } else if (strcmp(go, "@new") == 0) {
        kh_game_new_night();
    } else {
        kh_game_go(go);
    }
}

static void place_camera(br_demo *demo)
{
    br_actor *cam = demo->camera;
    BrMatrix34Translate(&cam->t.t.mat, 0, 0, BR_SCALAR(10.0f));
    BrMatrix34PostRotateX(&cam->t.t.mat, BR_ANGLE_DEG(-52));
    BrMatrix34PostRotateY(&cam->t.t.mat, BR_ANGLE_DEG(G.cam_yaw));
    BrMatrix34PostTranslate(&cam->t.t.mat, BR_SCALAR(G.keeper_x), BR_SCALAR(1.2f), BR_SCALAR(G.keeper_z));
}

static br_error game_init(br_demo *demo)
{
    const char *room = SDL_getenv("KEEPERS_ROOM");
    br_camera *c;
    SDL_InitSubSystem(SDL_INIT_GAMEPAD);
    G.smoke = SDL_getenv("KEEPERS_SMOKE") != NULL;
    kh_capture_init();
    if (kh_boot_load(&G.script) != 0)
        return BRE_FAIL;
    kh_options_load(&G.opt, kh_options_path());
    if (!G.smoke && !kh_capture_active() && kh_audio_open() == 0)
        kh_audio_volume(G.opt.volume);
    kh_talk_init(&G.talk, &G.script, 1998u);
    demo->camera = BrActorAdd(demo->world, BrActorAllocate(BR_ACTOR_CAMERA, NULL));
    demo->camera->t.type = BR_TRANSFORM_MATRIX34;
    c = demo->camera->type_data;
    c->type = BR_CAMERA_PERSPECTIVE_FOV;
    c->field_of_view = BR_ANGLE_DEG(55);
    c->hither_z = BR_SCALAR(0.1);
    c->yon_z = BR_SCALAR(60);
    demo->order_table->min_z = c->hither_z;
    demo->order_table->max_z = c->yon_z;
    kh_world_build(&G.world, demo->world);
    enter(kh_room_find(room && kh_room_find(room) >= 0 ? room : "lamp"), -1);
    if (SDL_getenv("KEEPERS_OPEN"))
        kh_talk_open(&G.talk, SDL_getenv("KEEPERS_OPEN"));
    else
        if (!kh_capture_active())
            kh_talk_open(&G.talk, !G.smoke && kh_save_exists(kh_save_path()) ? "resume" : "arrive");
    place_camera(demo);
    return BRE_OK;
}

static void smoke_step(void)
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

static void game_update(br_demo *demo, br_scalar dt_s)
{
    float dt = BrScalarToFloat(dt_s), fx, fz;
    if (kh_capture_active()) { /* game time comes from the frame number, not the wall clock */
        G.clock_s = kh_capture_clock();
        G.cam_yaw = kh_capture_yaw();
    } else {
        G.clock_s += dt;
    }
    if (G.smoke) smoke_step();
    else if (!kh_capture_active()) kh_input_walk(dt);
    if (G.talk.go[0]) {
        char go[KH_ID_LEN];
        snprintf(go, sizeof(go), "%s", G.talk.go);
        G.talk.go[0] = '\0';
        kh_game_follow(go);
    }
    demo->clear_colour = kh_world_sky(&G.world, demo->colour_buffer);
    kh_world_turn_lamp(&G.world, G.clock_s);
    G.world.keeper->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34RotateY(&G.world.keeper->t.t.mat, BR_ANGLE_DEG(G.facing));
    BrMatrix34PostTranslate(&G.world.keeper->t.t.mat, BR_SCALAR(G.keeper_x), 0, BR_SCALAR(G.keeper_z));
    fx = sinf(G.facing * 3.14159265f / 180.0f);
    fz = cosf(G.facing * 3.14159265f / 180.0f);
    G.near_talker = kh_world_talker_near(&G.world, G.keeper_x, G.keeper_z, fx, fz);
    place_camera(demo);
}

static void hud(br_pixelmap *pm, br_colour ink, br_colour accent)
{
    char text[128];
    snprintf(text, sizeof(text), "The Keeper's Hour   %s", kh_rooms[G.world.current].title);
    kh_text(pm, -pm->origin_x + 12, -pm->origin_y + 20, accent, text);
    if (G.ended || kh_talk_open_p(&G.talk))
        return;
    if (G.near_talker >= 0) {
        const kh_talker *t = kh_world_talker(&G.world, G.near_talker);
        snprintf(text, sizeof(text), "%s, click or A: %s %s", SDL_GetScancodeName(G.opt.keys[KH_ACT_TALK]),
                 t->node[0] == '@' ? "go through" : "talk to", t->name);
        kh_text(pm, -BrPixelmapTextWidth(pm, BrFontProp7x9, text) / 2, pm->height - pm->origin_y - 40, ink, text);
    } else {
        kh_text(pm, -pm->origin_x + 12, pm->height - pm->origin_y - 24, ink,
                       "Walk: WASD or left stick   Look: right drag or right stick   Options: F2   Quit: Esc");
    }
}

static void game_render(br_demo *demo)
{
    br_pixelmap *pm = demo->colour_buffer;
    br_colour ink = kh_px(pm, 236, 230, 216), accent = kh_px(pm, 232, 180, 92), panel = kh_px(pm, 14, 13, 18);
    kh_text_via_memory(!demo->hw_accel);
    BrDemoDefaultRender(demo);
    if (kh_capture_active()) {
        if (kh_capture_ui()) {
            hud(pm, ink, accent);
            kh_talk_draw(&G.talk, pm, ink, accent, panel);
        }
        if (kh_capture_frame(pm, demo->hw_accel, &G.problems)) {
            SDL_Event q = {.type = SDL_EVENT_QUIT};
            SDL_PushEvent(&q);
        }
        return;
    }
    hud(pm, ink, accent);
    if (G.ended)
        kh_end_card(pm, &G.talk, ink, accent, panel);
    else
        kh_talk_draw(&G.talk, pm, ink, accent, panel);
    kh_options_draw(&G.opt, pm, ink, accent, panel);
}

static void game_event(br_demo *demo, const SDL_Event *e) { (void)demo; kh_input_event(e); }
static void game_destroy(br_demo *demo) { (void)demo; kh_audio_close(); }

static const br_demo_dispatch dispatch = {
    .init = game_init, .process_event = game_event, .update = game_update,
    .render = game_render, .on_resize = BrDemoDefaultOnResize, .destroy = game_destroy,
};

int main(int argc, char **argv)
{
    br_demo_run_args args;
    char **used;
    int ret, n;
    BrDemoDefaultArgs(&args);
    args.title = "The Keeper's Hour";
    used = kh_boot_argv(argc, argv, &n);
    if (BrDemoParseArgs(&args, n, used) != 0)
        return 1;
    args.no_stats = 1;
    BrLogSetLevel(args.verbose);
    ret = BrDemoRunArg(&dispatch, &args);
    if (G.smoke)
        printf("keepers smoke: %d rooms entered, %d nodes opened, %d problems, run %s\n", G.smoke_room, G.smoke_node, G.problems,
               ret == 0 ? "ok" : "failed");
    return ret != 0 ? ret : G.problems;
}
