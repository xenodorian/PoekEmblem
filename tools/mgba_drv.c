// Headless mGBA driver (reads commands from file or "-" for stdin; adds r16p/w16p pointer deref, echo, quit). Commands (one per line) are read from a script file:
//   run N            run N frames
//   keys HEX N       hold key mask HEX for N frames (A=1 B=2 SELECT=4 START=8 RIGHT=10 LEFT=20 UP=40 DOWN=80 R=100 L=200)
//   shot FILE        save the 240x160 screen as PNG
//   r32 ADDR | r16 ADDR | r8 ADDR    print memory
//   w32 ADDR VAL | w16 ADDR VAL | w8 ADDR VAL    write memory
//   rununtil16 ADDR VAL MAXFRAMES     run until the u16 at ADDR equals VAL
#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/gba/core.h>
#include <mgba-util/vfs.h>
#include <mgba/core/config.h>
#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: shot rom script\n"); return 2; }
    struct mCore* core = mCoreFind(argv[1]);
    if (!core) { fprintf(stderr, "no core\n"); return 1; }
    core->init(core);
    mCoreInitConfig(core, NULL);
    unsigned w, h; core->desiredVideoDimensions(core, &w, &h);
    color_t* buf = calloc(w * h, sizeof(color_t));
    core->setVideoBuffer(core, buf, w);
    if (!mCoreLoadFile(core, argv[1])) { fprintf(stderr, "load fail\n"); return 1; }
    core->setAudioBufferSize(core, 1024);
    core->reset(core);
    FILE* f = strcmp(argv[2],"-")?fopen(argv[2], "r"):stdin;
    char line[512];
    while (fgets(line, sizeof line, f)) {
        char cmd[32], a[256]; unsigned long x = 0, y = 0, z = 0;
        if (sscanf(line, "%31s", cmd) != 1) continue;
        if (!strcmp(cmd, "run")) { sscanf(line, "%*s %lu", &x); for (unsigned long i = 0; i < x; i++) core->runFrame(core); }
        else if (!strcmp(cmd, "keys")) { sscanf(line, "%*s %lx %lu", &x, &y); core->setKeys(core, x); for (unsigned long i = 0; i < y; i++) core->runFrame(core); core->setKeys(core, 0); }
        else if (!strcmp(cmd, "shot")) { sscanf(line, "%*s %255s", a); struct VFile* vf = VFileOpen(a, O_CREAT | O_WRONLY | O_TRUNC); if (!vf || !mCoreTakeScreenshotVF(core, vf)) fprintf(stderr, "shot failed %s\n", a); if (vf) vf->close(vf); }
        else if (!strcmp(cmd, "shotseq")) { sscanf(line, "%*s %255s %lu", a, &x); for (unsigned long i = 0; i < x; i++) { core->runFrame(core); char fn[300]; snprintf(fn, sizeof fn, "%s_%03lu.png", a, i); struct VFile* vf = VFileOpen(fn, O_CREAT | O_WRONLY | O_TRUNC); if (vf) { mCoreTakeScreenshotVF(core, vf); vf->close(vf); } } }
        else if (!strcmp(cmd, "r16p")) { sscanf(line, "%*s %lx %lx", &x, &y); unsigned p = core->busRead32(core, x); printf("r16p %04x\n", core->busRead16(core, p + y)); }
        else if (!strcmp(cmd, "w16p")) { sscanf(line, "%*s %lx %lx %lx", &x, &y, &z); unsigned p = core->busRead32(core, x); core->busWrite16(core, p + y, z); }
        else if (!strcmp(cmd, "echo")) { printf("echo\n"); }
        else if (!strcmp(cmd, "quit")) break;
        else if (!strcmp(cmd, "r32")) { sscanf(line, "%*s %lx", &x); printf("r32 %08lx = %08x\n", x, core->busRead32(core, x)); }
        else if (!strcmp(cmd, "r16")) { sscanf(line, "%*s %lx", &x); printf("r16 %08lx = %04x\n", x, core->busRead16(core, x)); }
        else if (!strcmp(cmd, "r8"))  { sscanf(line, "%*s %lx", &x); printf("r8 %08lx = %02x\n", x, core->busRead8(core, x)); }
        else if (!strcmp(cmd, "w32")) { sscanf(line, "%*s %lx %lx", &x, &y); core->busWrite32(core, x, y); }
        else if (!strcmp(cmd, "w16")) { sscanf(line, "%*s %lx %lx", &x, &y); core->busWrite16(core, x, y); }
        else if (!strcmp(cmd, "w8"))  { sscanf(line, "%*s %lx %lx", &x, &y); core->busWrite8(core, x, y); }
        else if (!strcmp(cmd, "rununtil16")) { sscanf(line, "%*s %lx %lx %lu", &x, &y, &z); unsigned long i; for (i = 0; i < z && core->busRead16(core, x) != y; i++) core->runFrame(core); printf("rununtil16 done after %lu frames\n", i); }
        fflush(stdout);
    }
    core->deinit(core);
    return 0;
}
