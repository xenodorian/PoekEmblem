#include <mgba/core/core.h>
#include <mgba/gba/core.h>
#include <mgba/core/config.h>
#include <mgba/internal/arm/arm.h>
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char**argv){
  struct mCore* core=mCoreFind(argv[1]); core->init(core); mCoreInitConfig(core,NULL);
  unsigned w,h; core->desiredVideoDimensions(core,&w,&h); color_t* buf=calloc(w*h,4); core->setVideoBuffer(core,buf,w);
  mCoreLoadFile(core,argv[1]); core->reset(core);
  unsigned addr=strtoul(argv[2],0,16); unsigned want=strtoul(argv[3],0,16);
  unsigned prev=core->busRead8(core,addr); long n=0;
  while(n<400000000){ core->step(core); n++; unsigned v=core->busRead8(core,addr);
    if(v!=prev){ struct ARMCore* c=core->cpu; printf("change %02x->%02x after %ld steps pc=%08x lr=%08x r0=%08x\n",prev,v,n,c->gprs[15],c->gprs[14],c->gprs[0]); prev=v; if(--want==0)break; } }
  return 0; }
