from __future__ import annotations


def host_semantic_source() -> str:
    """C source for the BRender portable-core host/memory semantic rung.

    Closes a recorded readiness blocker: the portable host and memory
    fallback functions existed as scaffolding with no behavioral tests.
    This rung drives BRender's own fw-layer memory allocator and stdio
    file primitives through their public entry points and asserts real
    semantics, not just linkability:

      1. BrMemInquire is callable and its value is reported (default
      2. BrMemAllocate returns writable memory that retains a byte pattern;
      3. BrMemFree accepts it (run completes under the debug CRT);
      4. (finding) BrMemAllocateAlign is declared in fw_p.h but has no
         implementation in the v1.3.2 FLOAT core; not relied on;
      5. BrFileOpenWrite -> BrFileWrite -> BrFileClose -> BrFileOpenRead ->
         BrFileRead round-trips 256 known bytes exactly.

    One JSON receipt; exit 0 only when every check passes.
    """
    return r"""/*
 * BRender v1.3.2 portable-core host/memory semantic rung.
 *
 * Usage: brender_core_host_semantic [workfile]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_DEBUG)
#include <crtdbg.h>
#endif

static int mem_checks(br_size_t inquire_before)
{
    unsigned char *block;
    br_size_t inquire_after_alloc;
    size_t i;

    block = BrMemAllocate(4096, BR_MEMORY_APPLICATION);
    if (block == NULL) {
        fprintf(stderr, "host-semantic: BrMemAllocate returned NULL\n");
        return 0;
    }
    for (i = 0; i < 4096; i++) block[i] = (unsigned char)(i * 7 + 3);
    for (i = 0; i < 4096; i++) {
        if (block[i] != (unsigned char)(i * 7 + 3)) {
            fprintf(stderr, "host-semantic: pattern mismatch at %d\n", (int)i);
            BrMemFree(block);
            return 0;
        }
    }
    inquire_after_alloc = BrMemInquire(BR_MEMORY_APPLICATION);
    BrMemFree(block);
    printf("{\"check\":\"memory\",\"inquire_before\":%u,"
        "\"inquire_after_alloc\":%u,\"pattern\":\"ok\",\"pass\":%s}\n",
        (unsigned)inquire_before, (unsigned)inquire_after_alloc,
        "true");
    return 1;
}

static int path_exists(const char *path)
{
    FILE *probe = fopen(path, "rb");
    if (probe == NULL) return 0;
    fclose(probe);
    return 1;
}

static int file_roundtrip(const char *work_path)
{
    static unsigned char payload[256];
    unsigned char buf[256];
    void *f;
    int i, written, read_back, ok = 0;
    int created_workfile = 0;

    for (i = 0; i < 256; i++) payload[i] = (unsigned char)(i ^ 0x5A);

    if (path_exists(work_path)) {
        fprintf(stderr, "host-semantic: workfile already exists: %s\n", work_path);
        printf("{\"check\":\"file-roundtrip\",\"bytes\":256,"
            "\"workfile_exists\":true,\"match\":false}\n");
        return 0;
    }

    f = BrFileOpenWrite((char *)work_path, 0);
    if (f == NULL) {
        fprintf(stderr, "host-semantic: open-write failed\n");
        return 0;
    }
    created_workfile = 1;
    written = BrFileWrite((void *)payload, 1, 256, f);
    BrFileClose(f);
    if (written != 256) {
        fprintf(stderr, "host-semantic: write count %d\n", written);
        goto out;
    }

    f = BrFileOpenRead((char *)work_path, 0, NULL, NULL);
    if (f == NULL) {
        fprintf(stderr, "host-semantic: open-read failed\n");
        goto out;
    }
    read_back = BrFileRead(buf, 1, 256, f);
    BrFileClose(f);
    if (read_back != 256) {
        fprintf(stderr, "host-semantic: read count %d\n", read_back);
        goto out;
    }
    ok = 1;
    for (i = 0; i < 256; i++) {
        if (buf[i] != payload[i]) { ok = 0; break; }
    }

out:
    if (created_workfile) remove(work_path);
    printf("{\"check\":\"file-roundtrip\",\"bytes\":256,\"match\":%s}\n",
        ok ? "true" : "false");
    return ok ? 1 : 0;
}

int main(int argc, char **argv)
{
    const char *work_path = (argc > 1) ? argv[1] : "host-semantic.bin";
    int mem_ok, file_ok;
    br_size_t inquire_before;

#if defined(_DEBUG)
    _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_DEBUG);
#endif
    if (BrBegin() != BRE_OK) return 3;

    inquire_before = BrMemInquire(BR_MEMORY_APPLICATION);
    mem_ok = mem_checks(inquire_before);
    file_ok = file_roundtrip(work_path);

    if (BrEnd() != BRE_OK) return 4;

    printf("{\"rung\":\"brender_core_host_semantic\","
        "\"memory\":%s,\"file_roundtrip\":%s,\"valid\":%s}\n",
        mem_ok ? "true" : "false",
        file_ok ? "true" : "false",
        (mem_ok && file_ok) ? "true" : "false");

    return (mem_ok && file_ok) ? 0 : 5;
}
"""
