/*
 * brview: a model viewer for BRender, the 1990s Argonaut engine, on a modern PC.
 *
 * Built on BRender 1.4 from BlazingRenderer/BRender (MIT) and its brdemo
 * window layer (SDL3). Opens the period sample models that ship with
 * BRender v1.3.2 (MIT, copyright 1998 Argonaut Software Limited).
 *
 *   brview                 cycle through the bundled period models
 *   brview model.dat       view one model (optionally: texture.pix)
 *   brview --force-software   draw with the software rasteriser instead of OpenGL
 *
 * [ and ] change the pixel size, - and = the field of view, V turns vsync on
 * or off; they are saved in the user's preferences folder. BRVIEW_PIXEL and
 * BRVIEW_FOV set them for one run, and BRVIEW_SHOT=<file.ppm> writes one
 * still of the first model, without spin, and quits.
 *
 * SPDX-License-Identifier: MIT
 */
#include <math.h>
#include <stdio.h>
#include <string.h>

#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h> /* the platform entry point: WinMain for a window-only program */
#include <brender.h>
#include "brdemo.h"
#include "brdisplay.h"
#include "brview_run.h"
#include "brview_scenes.h"

typedef struct viewer {
    br_actor    *model_actor;
    br_actor    *light;
    br_material *material;
    int          scene;
    float        yaw, pitch, distance, pan_x, pan_y;
    float        yaw_rate, pitch_rate, zoom_rate;
    br_boolean   spin, help, textured;
    br_boolean   dragging, panning;
    SDL_Gamepad *pad;
    char         title[128];
    int          pixel, fov, vsync; /* display options, saved */
    int          period;            /* 8: 256 colours through BRender's 8-bit path, saved */
    int          period_shown;      /* the look the material is set up for */
} viewer;

static viewer V;

/* BRVIEW_SMOKE=1: load every scene once, draw one frame of each, then quit.
 * The exit code is the number of scenes that failed to load. */
static int smoke_mode, smoke_failures;

/* BRVIEW_SHOT=<file.ppm>: draw the first model without spin and write one
 * still after the renderer settles. */
static const char *shot_path;
static int shot_frames;
static int shot_scene; /* BRVIEW_SCENE */

/* BRVIEW_PERIOD=1: the period look for this run (stills and checks too). */
static int period_forced;

/* Checks and stills use the defaults, never a player's saved options. */
static void options_load(void)
{
    brview_options o = {1, 50, 1, 0};
    if (!smoke_mode && !shot_path)
        brview_options_load(&o);
    V.pixel = o.pixel; V.fov = o.fov; V.vsync = o.vsync; V.period = o.period;
}

static void options_save(void)
{
    brview_options o = {V.pixel, V.fov, V.vsync, V.period};
    if (!smoke_mode && !shot_path)
        brview_options_save(&o);
}

static void reset_view(void)
{
    V.yaw = 30.0f;
    V.pitch = 20.0f;
    V.distance = 3.0f;
    V.pan_x = V.pan_y = 0.0f;
}

static void place_camera(br_demo *demo)
{
    br_actor *cam = demo->camera;
    cam->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34Translate(&cam->t.t.mat, BR_SCALAR(V.pan_x), BR_SCALAR(V.pan_y), BR_SCALAR(V.distance));
    BrMatrix34PostRotateX(&cam->t.t.mat, BR_ANGLE_DEG(-V.pitch));
    BrMatrix34PostRotateY(&cam->t.t.mat, BR_ANGLE_DEG(V.yaw));
}

static void load_scene(br_demo *demo, int index)
{
    char err[160];
    V.scene = (index + BrViewSceneCount()) % BrViewSceneCount();
    V.period_shown = (V.period || period_forced) && brd_display_period_available(demo);
    BrViewSceneSetSoftware(!demo->hw_accel);
    if (BrViewSceneLoad(V.scene, V.model_actor, V.material, V.textured, V.period_shown, err, sizeof(err)) != BRE_OK) {
        BrLogError("BRVIEW", "%s", err);
        smoke_failures++;
    }
    snprintf(V.title, sizeof(V.title), "%s", BrViewSceneName(V.scene));
    reset_view();
    place_camera(demo);
}

static br_error viewer_init(br_demo *demo)
{
    br_camera *camera_data;

    SDL_InitSubSystem(SDL_INIT_GAMEPAD);
    demo->clear_colour = BR_COLOUR_RGBA(18, 16, 13, 255);

    demo->camera = BrActorAdd(demo->world, BrActorAllocate(BR_ACTOR_CAMERA, NULL));
    camera_data = demo->camera->type_data;
    camera_data->type = BR_CAMERA_PERSPECTIVE_FOV;
    camera_data->field_of_view = BR_ANGLE_DEG(50); /* then the saved option, below */
    camera_data->hither_z = BR_SCALAR(0.05);
    camera_data->yon_z = BR_SCALAR(100);
    demo->order_table->min_z = camera_data->hither_z;
    demo->order_table->max_z = camera_data->yon_z;

    V.light = BrActorAdd(demo->world, BrActorAllocate(BR_ACTOR_LIGHT, NULL));
    V.light->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34RotateX(&V.light->t.t.mat, BR_ANGLE_DEG(-35));
    BrMatrix34PostRotateY(&V.light->t.t.mat, BR_ANGLE_DEG(40));
    BrLightEnable(V.light);

    V.model_actor = BrActorAdd(demo->world, BrActorAllocate(BR_ACTOR_NONE, NULL));
    V.material = BrMaterialAllocate("brview");
    V.textured = BR_TRUE;
    if (shot_path) { /* a still of one scene, as the environment sets it */
        brview_still still = brview_still_from_env();
        V.textured = still.textured ? BR_TRUE : BR_FALSE;
        BrViewSceneSetUnlit(still.unlit);
        shot_scene = still.scene;
    }
    V.help = BR_TRUE;
    V.spin = shot_path == NULL;
    brd_display_init("BRVIEW");
    options_load();
    brd_display_apply(demo, V.fov, V.vsync);

    if (demo->args->pos_argc > 0)
        BrViewSceneSetCustom(demo->args->pos_argv[0], demo->args->pos_argc > 1 ? demo->args->pos_argv[1] : NULL);
    load_scene(demo, shot_scene);
    return BRE_OK;
}

static void on_key(br_demo *demo, SDL_Keycode key)
{
    switch (key) {
    case SDLK_TAB: case SDLK_N: load_scene(demo, V.scene + 1); break;
    case SDLK_P: load_scene(demo, V.scene - 1); break;
    case SDLK_R: reset_view(); break;
    case SDLK_SPACE: V.spin = !V.spin; break;
    case SDLK_H: case SDLK_F1: V.help = !V.help; break;
    case SDLK_T: V.textured = !V.textured; load_scene(demo, V.scene); break;
    case SDLK_LEFTBRACKET: V.pixel = SDL_clamp(V.pixel - 1, BRD_PIXEL_MIN, BRD_PIXEL_MAX); options_save(); break;
    case SDLK_RIGHTBRACKET: V.pixel = SDL_clamp(V.pixel + 1, BRD_PIXEL_MIN, BRD_PIXEL_MAX); options_save(); break;
    case SDLK_MINUS: V.fov = SDL_clamp(V.fov - BRD_FOV_STEP, BRD_FOV_MIN, BRD_FOV_MAX); options_save(); break;
    case SDLK_EQUALS: V.fov = SDL_clamp(V.fov + BRD_FOV_STEP, BRD_FOV_MIN, BRD_FOV_MAX); options_save(); break;
    case SDLK_V: V.vsync = !V.vsync; options_save(); break;
    case SDLK_8: V.period = !V.period; options_save(); load_scene(demo, V.scene); break;
    case SDLK_ESCAPE: { SDL_Event quit = {.type = SDL_EVENT_QUIT}; SDL_PushEvent(&quit); } break;
    default: break;
    }
}

static void on_button(br_demo *demo, Uint8 button)
{
    switch (button) {
    case SDL_GAMEPAD_BUTTON_SOUTH: load_scene(demo, V.scene + 1); break;
    case SDL_GAMEPAD_BUTTON_WEST: load_scene(demo, V.scene - 1); break;
    case SDL_GAMEPAD_BUTTON_EAST: V.spin = !V.spin; break;
    case SDL_GAMEPAD_BUTTON_NORTH: V.textured = !V.textured; load_scene(demo, V.scene); break;
    case SDL_GAMEPAD_BUTTON_BACK: V.help = !V.help; break;
    case SDL_GAMEPAD_BUTTON_START: reset_view(); break;
    default: break;
    }
}

static void viewer_event(br_demo *demo, const SDL_Event *evt)
{
    switch (evt->type) {
    case SDL_EVENT_KEY_DOWN: on_key(demo, evt->key.key); break;
    case SDL_EVENT_MOUSE_BUTTON_DOWN:
    case SDL_EVENT_MOUSE_BUTTON_UP: {
        br_boolean down = evt->type == SDL_EVENT_MOUSE_BUTTON_DOWN;
        if (evt->button.button == SDL_BUTTON_LEFT) V.dragging = down;
        if (evt->button.button == SDL_BUTTON_RIGHT || evt->button.button == SDL_BUTTON_MIDDLE) V.panning = down;
        if (down) V.spin = BR_FALSE;
    } break;
    case SDL_EVENT_MOUSE_MOTION:
        if (V.dragging) { V.yaw -= evt->motion.xrel * 0.4f; V.pitch += evt->motion.yrel * 0.4f; }
        if (V.panning) { V.pan_x -= evt->motion.xrel * 0.004f * V.distance; V.pan_y += evt->motion.yrel * 0.004f * V.distance; }
        break;
    case SDL_EVENT_MOUSE_WHEEL: V.distance *= evt->wheel.y > 0 ? 0.9f : 1.1f; break;
    case SDL_EVENT_GAMEPAD_ADDED: if (V.pad == NULL) V.pad = SDL_OpenGamepad(evt->gdevice.which); break;
    case SDL_EVENT_GAMEPAD_REMOVED: if (V.pad != NULL) { SDL_CloseGamepad(V.pad); V.pad = NULL; } break;
    case SDL_EVENT_GAMEPAD_BUTTON_DOWN: on_button(demo, evt->gbutton.button); break;
    default: break;
    }
    brd_display_apply(demo, V.fov, V.vsync); /* a changed option takes effect at once */
}

static float stick(SDL_GamepadAxis axis)
{
    float v = V.pad ? SDL_GetGamepadAxis(V.pad, axis) / 32767.0f : 0.0f;
    return fabsf(v) < 0.15f ? 0.0f : v;
}

static void smoke_step(br_demo *demo)
{
    static int frames;
    if (++frames >= BrViewSceneCount()) {
        SDL_Event quit = {.type = SDL_EVENT_QUIT};
        SDL_PushEvent(&quit);
        return;
    }
    load_scene(demo, V.scene + 1);
}

static void viewer_update(br_demo *demo, br_scalar dt)
{
    if (smoke_mode) {
        smoke_step(demo);
        return;
    }
    if (shot_path) {
        place_camera(demo);
        return;
    }
    {
    const bool *keys = SDL_GetKeyboardState(NULL);
    float s = BrScalarToFloat(dt);
    float yaw_in = (keys[SDL_SCANCODE_A] || keys[SDL_SCANCODE_LEFT]) - (keys[SDL_SCANCODE_D] || keys[SDL_SCANCODE_RIGHT]) - stick(SDL_GAMEPAD_AXIS_LEFTX);
    float pitch_in = (keys[SDL_SCANCODE_W] || keys[SDL_SCANCODE_UP]) - (keys[SDL_SCANCODE_S] || keys[SDL_SCANCODE_DOWN]) - stick(SDL_GAMEPAD_AXIS_LEFTY);
    float zoom_in = keys[SDL_SCANCODE_E] - keys[SDL_SCANCODE_Q] + stick(SDL_GAMEPAD_AXIS_RIGHT_TRIGGER) - stick(SDL_GAMEPAD_AXIS_LEFT_TRIGGER);

    if (yaw_in != 0 || pitch_in != 0) V.spin = BR_FALSE;
    V.yaw += (yaw_in * 90.0f + (V.spin ? 20.0f : 0.0f)) * s;
    V.pitch += pitch_in * 90.0f * s;
    V.pitch = V.pitch > 89.0f ? 89.0f : (V.pitch < -89.0f ? -89.0f : V.pitch);
    V.distance *= 1.0f - zoom_in * 1.5f * s;
    V.distance = V.distance < 0.4f ? 0.4f : (V.distance > 40.0f ? 40.0f : V.distance);
    place_camera(demo);
    }
}

static void viewer_render(br_demo *demo)
{
    static const char *help[] = {
        "Drag: orbit   Right drag: pan   Wheel or Q/E: zoom   WASD/arrows: orbit",
        "Tab/N, P: next, previous model   T: texture on/off   Space: spin   R: reset",
        "Gamepad: left stick orbit, triggers zoom, A/X next/previous, B spin, Y texture",
        "[ ]: pixel size   - =: field of view   V: vsync   8: period look (256 colours)   H or F1: hide this help",
        "Alt+Enter: fullscreen   Esc: quit",
    };
    br_int_32 x = -demo->colour_buffer->origin_x + 8;
    br_int_32 y = demo->colour_buffer->height - demo->colour_buffer->origin_y - 8;
    int i, line = BrPixelmapTextHeight(demo->colour_buffer, BrFontProp7x9) + 3;

    if (!V.period_shown || brd_display_render_period(demo, V.pixel, BrViewScenePalette(), 0) != 0)
        brd_display_render(demo, V.pixel);
    if (shot_path) {
        if (++shot_frames == 20) { /* the renderer settles first */
            SDL_Event quit = {.type = SDL_EVENT_QUIT};
            if (brd_frame_write_ppm(demo->colour_buffer, demo->palette, shot_path, demo->hw_accel) != 0) smoke_failures++;
            SDL_PushEvent(&quit);
        }
        return;
    }
    BrPixelmapTextF(demo->colour_buffer, x, -demo->colour_buffer->origin_y + 20, demo->text_colour, BrFontProp7x9,
                    "%s  (%d of %d)   pixel %d  fov %d  vsync %s%s", V.title, V.scene + 1, BrViewSceneCount(),
                    brd_display_pixel(V.pixel), brd_display_fov(V.fov), V.vsync ? "on" : "off",
                    V.period_shown ? "   period: 256 colours, BRender's 8-bit path"
                    : V.period ? "   period: needs the software renderer (restart, or --force-software)" : "");
    if (!V.help)
        return;
    for (i = 0; i < (int)BR_ASIZE(help); i++)
        BrPixelmapText(demo->colour_buffer, x, y - (int)(BR_ASIZE(help) - i) * line, demo->text_colour, BrFontProp7x9, help[i]);
}

static void viewer_resize(br_demo *demo, br_uint_16 width, br_uint_16 height)
{
    BrDemoDefaultOnResize(demo, width, height);
    brd_display_release(); /* remade for the new size on the next frame */
}

static void viewer_destroy(br_demo *demo)
{
    brd_display_release();
    BrDemoDefaultDestroy(demo);
}

static const br_demo_dispatch dispatch = {
    .init = viewer_init,
    .process_event = viewer_event,
    .update = viewer_update,
    .render = viewer_render,
    .on_resize = viewer_resize,
    .destroy = viewer_destroy,
};

int main(int argc, char **argv)
{
    int ret;
    smoke_mode = SDL_getenv("BRVIEW_SMOKE") != NULL;
    shot_path = SDL_getenv("BRVIEW_SHOT");
    period_forced = SDL_getenv("BRVIEW_PERIOD") != NULL && SDL_atoi(SDL_getenv("BRVIEW_PERIOD")) != 0;
    options_load(); /* to know before the window opens whether the period look wants the software renderer */
    {
        br_demo_run_args args;
        BrDemoDefaultArgs(&args);
        args.title = "brview: BRender on a modern PC";
        /* The software rasteriser draws in 24-bit colour unless --software-bpp
         * is given, as in the game: brdemo's 8-bit default has no palette for
         * stills, and the scenes are true-colour. The period look draws on the
         * software renderer. */
        int n;
        char **used = brview_argv(argc, argv, period_forced || V.period, &n);
        if (BrDemoParseArgs(&args, n, used) != 0)
            return 1;
        args.no_stats = 1;
        BrLogSetLevel(args.verbose);
        ret = BrDemoRunArg(&dispatch, &args);
    }
    if (smoke_mode)
        printf("brview smoke: %d scenes, %d failed to load, run %s\n", BrViewSceneCount(), smoke_failures, ret == 0 ? "ok" : "failed");
    return ret != 0 ? ret : smoke_failures;
}
