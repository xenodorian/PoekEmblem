import numpy as np
from PIL import Image
S='harness/seq/'
LX,LY=48,48
REL=32
seq=[(1,20),(2,6),(3,6),(4,24),(0,1)]
lf=[Image.open(f'banim/leaf_frame{i}.png').convert('RGBA') for i in range(5)]
def leaf_at(t):
    if t<0: return lf[0]
    for k,d in seq:
        if t<d: return lf[k]
        t-=d
    return lf[0]
ex=np.zeros((160,240),bool); ex[112:]=True
for x0,y0,x1,y1 in [(10,14,112,48),(134,72,230,112)]: ex[y0:y1,x0:x1]=True
# name, outfile, effect start (projectile created), end (impact + tail)
for nm,out,start,end in [('slap','leaf_slap',175,236)]:
    def rec(n): return Image.open(f'{S}{nm}_{n:03d}.png').convert('RGB')
    base=np.array(rec(140)).astype(int)
    frames=[]
    for n in range(start-REL-2,end,2):
        fr=np.array(rec(n)).astype(int)
        m=(abs(fr-base).sum(-1)>24)&~ex
        bg=rec(140).convert('RGBA'); bg.alpha_composite(leaf_at(n-(start-REL)),(LX,LY))
        a=np.array(bg); a[m,:3]=fr[m]; a[112:,:,:3]=fr[112:]
        frames.append(Image.fromarray(a).convert('RGB').resize((960,640),Image.NEAREST))
    frames[0].save(f'banim/{out}.gif',save_all=True,append_images=frames[1:],duration=[30,30,40]*(len(frames)//3+1),loop=0)
    k=len(frames)
    sh=Image.new('RGB',(960,640))
    for i,j in enumerate([0,k//5,2*k//5,3*k//5,4*k//5,k-1]) if False else []: pass
    sel=[frames[j].resize((480,320)) for j in (0,k//4,k//2,k-1)]
    for i,f in enumerate(sel): sh.paste(f,((i%2)*480,(i//2)*320))
    sh.save(f'banim/{out}_sheet.png'); print(out,k)
