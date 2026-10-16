import numpy as np
from PIL import Image
S='harness/seq/'
LX,LY=48,48
seq=[(1,20),(2,6),(3,6),(4,24),(0,1)]
lf=[Image.open(f'banim/leaf_frame{i}.png').convert('RGBA') for i in range(5)]
def leaf_at(t):
    for k,d in seq:
        if t<d: return lf[k]
        t-=d
    return lf[0]
def rec(n,name): return Image.open(f'{S}{name}_{n:03d}.png').convert('RGB')
ex=np.zeros((160,240),bool); ex[112:]=True
for x0,y0,x1,y1 in [(10,14,112,48),(134,72,230,112)]: ex[y0:y1,x0:x1]=True
REL=26
for name,out,start in [('barrage','leaf_throw_barrage',192),('eggbomb','leaf_throw_egg_bomb',194),('shadowball','leaf_throw_shadow_ball',218)]:
    base=np.array(rec(140,name)).astype(int)
    frames=[]
    for t in range(0,96,2):
        n=min(max(start-REL+t,0),359)
        fr=np.array(rec(n,name)).astype(int)
        m=(abs(fr-base).sum(-1)>24)&~ex
        bg=rec(140,name).convert('RGBA')
        bg.alpha_composite(leaf_at(t),(LX,LY))
        a=np.array(bg)
        a[m,:3]=fr[m]; a[112:,:,:3]=fr[112:]
        if name=='shadowball':
            a=np.array(rec(n,name).convert('RGBA')); b=Image.fromarray(a); b.alpha_composite(leaf_at(t),(LX,LY)); a=np.array(b)
        frames.append(Image.fromarray(a).convert('RGB').resize((960,640),Image.NEAREST))
    frames[0].save(f'banim/{out}.gif',save_all=True,append_images=frames[1:],duration=[30,30,40]*(len(frames)//3+1),loop=0)
    frames[28].save(f'banim/{out}_peek.png')
