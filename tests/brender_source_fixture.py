"""A minimal fake BRender checkout, enough for the materializer to run in tests."""
from engine_revival.brender_harness import CORE_FLOAT_DIRS as CORE_DIRS


def _write_source_fixture(root):
    (root / "inc").mkdir(parents=True)
    (root / "inc" / "brender.h").write_text("/* public header fixture */\n", encoding="utf-8")
    (root / "core" / "inc").mkdir(parents=True)
    softrend_dir = root / "drivers" / "softrend"
    softrend_dir.mkdir(parents=True)
    (softrend_dir / "alpha.c").write_text("void sr_alpha(void) {}\n", encoding="utf-8")
    (softrend_dir / "clip.c").write_text("void sr_clip(void) {}\n", encoding="utf-8")
    (softrend_dir / "makefile").write_text(
        "\n".join([
            "OBJS_C=\\",
            "    $(BLD_DIR)/alpha$(OBJ_EXT)\\",
            "    $(BLD_DIR)/clip$(OBJ_EXT)\\",
            "",
            "OBJS_ASM=\\",
            "    $(BLD_DIR)/cull$(OBJ_EXT)\\",
            ""],
        ),
        encoding="utf-8",
    )

    pentprim_dir = root / "drivers" / "pentprim"
    pentprim_dir.mkdir(parents=True)
    (pentprim_dir / "driver.c").write_text("void pp_driver(void) {}\n", encoding="utf-8")
    (pentprim_dir / "l_pi.c").write_text("void pp_lpi(void) {}\n", encoding="utf-8")

    (pentprim_dir / "awtmz.c").write_text("void pp_awtmz(void) {}\n", encoding="utf-8")
    (pentprim_dir / "makefile").write_text(
        "\n".join([
            "OBJS_C=\\",
            "    $(BLD_DIR)/driver$(OBJ_EXT)\\",
            "",
            "XOBJS_C=\\",
            "    $(BLD_DIR)/l_pi$(OBJ_EXT)\\",
            "",
            "XOBJS_ASM=\\",
            "    $(BLD_DIR)/zb8$(OBJ_EXT)\\",
            ""],
        ),
        encoding="utf-8",
    )
    for name in CORE_DIRS:
        directory = root / "core" / name
        directory.mkdir(parents=True)
        (directory / f"{name}_listed.c").write_text("void fixture(void) {}\n", encoding="utf-8")
        (directory / f"{name}_unlisted.c").write_text("void skip_me(void) {}\n", encoding="utf-8")
        (directory / f"{name}_commented.c").write_text("void skip_comment(void) {}\n", encoding="utf-8")
        (directory / "makefile").write_text(
            "\n".join([
                "OBJS_C=\\",
                f"    $(BLD_DIR)/{name}_listed$(OBJ_EXT)\\",
                f"#   $(BLD_DIR)/{name}_commented$(OBJ_EXT)\\",
                "",
                "OBJS_ASM=\\",
                "",
            ]),
        encoding="utf-8",
    )
