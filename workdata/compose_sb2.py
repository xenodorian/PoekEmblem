import numpy as np
from PIL import Image
S='harness/seq/'
LX,LY=48,48
seq=[(1,20),(2,6),(3,6),(4,24),(0,1)]
lf=[Image.open(f'banim/leaf_frame{i}.png').convert('RGBA') for i in range(5)]
def leaf_at(t):
    if t<0: return lf[0]
    for k,d in seq:
        if t<d: return lf[k]
        t-=d
    return lf[0]
frames=[]
for n in range(218,316,2):
    a=Image.open(f'{S}shadowball_{n:03d}.png').convert('RGBA')
    a.alpha_composite(leaf_at(n-272),(LX,LY))
    frames.append(a.convert('RGB').resize((960,640),Image.NEAREST))
frames[0].save('banim/leaf_throw_shadow_ball_v2.gif',save_all=True,append_images=frames[1:],duration=[30,30,40]*(len(frames)//3+1),loop=0)
for i in (0,14,27,len(frames)-1): frames[i].save(f'banim/sb2_{i}.png')
