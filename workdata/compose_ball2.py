import sys, glob, struct, importlib.util, numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-user-PoekEmblem/27b9bd3f-f2d5-5a88-ab9b-85e258b1a44c/scratchpad'; G='/home/user/pret/pokefirered/graphics/'; seq=SP+'/harness/seq'
spec=importlib.util.spec_from_file_location('br',SP+'/banim_render.py'); br=importlib.util.module_from_spec(spec); spec.loader.exec_module(br)
oam,script=br.load('/home/user/fireemblemuniverse/fireemblem8u','lorf_sw1')
# Eirika's hit moment: sum of frame durations before banim_code_hit_normal in her attack_close script
t=0; hit=None
for e in script['attack_close']:
    if e[0]=='event':
        if e[1]=='hit_normal': hit=t; break
    else: t+=e[0]
print('Eirika hit command at t =',hit,'units')
HUD=[(10,14,112,48),(134,72,230,112)]
ex=np.zeros((160,240),bool); ex[112:,:]=True
for x0,y0,x1,y1 in HUD: ex[y0:y1,x0:x1]=True
def recorder(prefix,n):
    return lambda i: Image.open(f'{seq}/{prefix}_{min(n-1,max(0,i)):03d}.png').convert('RGB')
def sprite(path):
    im=Image.open(path); idx=np.array(im); pal=np.array(im.getpalette()[:48],np.uint8).reshape(16,3)
    return Image.fromarray(np.dstack([pal[idx],np.where(idx==0,0,255).astype(np.uint8)]),'RGBA')
# Leaf pieces
leaf=[Image.open(f'{SP}/banim/leaf_frame{k}.png').convert('RGBA') for k in range(5)]
leaf_seq=[(1,20),(2,6),(3,6),(4,24),(0,1)]; LX,LY=48,48
def leaf_at(t):
    c=0
    for fr,d in leaf_seq:
        c+=d
        if t<c: return leaf[fr]
    return leaf[0]
dd=open(G+'interface/ball/poke.gbapal','rb').read()
bpal=np.array([(((v:=struct.unpack_from('<H',dd,i)[0])&31)*8,((v>>5)&31)*8,((v>>10)&31)*8) for i in range(0,32,2)],np.uint8)
bi=np.array(Image.open(G+'interface/ball/poke.png').convert('P'))[0:16]
ball=Image.fromarray(np.dstack([bpal[bi],np.where(bi==0,0,255).astype(np.uint8)]),'RGBA')
REL=26; FLIGHT=18; P0=(LX+54,LY+26); P1=(170,50)
def ball_at(t):
    if t<REL or t>=REL+FLIGHT: return None
    u=(t-REL)/FLIGHT; return int(P0[0]+(P1[0]-P0[0])*u-8), int(P0[1]+(P1[1]-P0[1])*u-34*4*u*(1-u)-8)
# Eirika pieces
meta=open(f'{SP}/banim/eirika_l/_meta.txt').read().split('\n')
EW,EH,eox,eoy=map(int,meta[0].split()); edur=[int(l.split()[1]) for l in meta[1:]]
efr=[Image.open(f).convert('RGBA') for f in sorted(glob.glob(f'{SP}/banim/eirika_l/f*.png'))]
eground=int(np.where(np.array(efr[0])[...,3].any(1))[0].max()); ex_left=66-eox; ex_top=109-eground
def eirika_at(t):
    c=0
    for i,d in enumerate(edur):
        c+=d
        if t<c: return efr[i]
    return None
stand=sprite(f'{SP}/playable_allies/Eirika/back.png'); SX,SY=40,55
def build(kind,name,prefix,n,eff_start,align_t,peek_t):
    rec=recorder(prefix,n); base=np.array(rec(140)).astype(int); outs=[]
    for t in range(0,96,2):
        f=rec(eff_start-align_t+t); fa=np.array(f).astype(int); out=f.convert('RGBA')
        if kind=='leaf': out.alpha_composite(leaf_at(t),(LX,LY))
        else:
            fr=eirika_at(t)
            if fr is not None: out.alpha_composite(fr,(ex_left,ex_top))
            else: out.alpha_composite(stand,(SX,SY))
        m=(np.abs(fa-base).sum(-1)>24)&~ex
        out.alpha_composite(Image.fromarray(np.dstack([fa.astype(np.uint8),(m*255).astype(np.uint8)]),'RGBA'))
        if kind=='leaf':
            b=ball_at(t)
            if b: out.alpha_composite(ball,b)
        elif eirika_at(t) is None: out.paste(f.crop((0,112,240,160)),(0,112))
        if kind=='leaf': out.paste(rec(230).crop((0,112,240,160)),(0,112))
        outs.append(out.convert('RGB').resize((960,640),Image.NEAREST))
        if t==peek_t: outs[-1].save(f'{SP}/banim/{name}_peek.png')
    ms=([30,30,40]*(len(outs)//3+1))[:len(outs)]
    outs[0].save(f'{SP}/banim/{name}.gif',save_all=True,append_images=outs[1:],duration=ms,loop=0,disposal=1,optimize=False); print(name,len(outs),'frames')
build('leaf','leaf_ball_throw_v2','ballthrow',330,213,REL+FLIGHT,46)
