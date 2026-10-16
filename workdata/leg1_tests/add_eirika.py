import re, shutil, os
from PIL import Image
import numpy as np
SP='/tmp/claude-0/-home-user-PoekEmblem/27b9bd3f-f2d5-5a88-ab9b-85e258b1a44c/scratchpad/playable_allies/Eirika'
os.makedirs('graphics/pokemon/eirika',exist_ok=True)
D='graphics/pokemon/eirika/'
def sub1(path, old, new, count=1):
    s=open(path).read()
    assert old in s, (path, old)
    s=s.replace(old,new,count); open(path,'w').write(s)
# art
back=Image.open(SP+'/back.png'); back.save(D+'back.png'); back.save(D+'front.png')
shutil.copy(SP+'/normal.pal',D+'normal.pal'); shutil.copy(SP+'/shiny.pal',D+'shiny.pal')
shutil.copy('graphics/pokemon/scizor/footprint.png',D+'footprint.png')
shutil.copy(SP+'/normal.pal','graphics/pokemon/icon_palettes/icon_palette_3.pal')
# icon: 32x32 downsample of the portrait, quantized to the portrait palette, two frames (second bobs down 1px)
pal=np.array(back.getpalette()[:48],np.uint8).reshape(16,3).astype(int)
idx=np.array(back); rgb=pal[idx].astype(np.uint8)
mask=(idx!=0)
small=Image.fromarray(rgb).resize((32,32),Image.LANCZOS)
ms=Image.fromarray((mask*255).astype(np.uint8)).resize((32,32),Image.BOX)
a=np.array(small).astype(int); m=np.array(ms)>127
d=((a[:,:,None,:]-pal[None,None,1:,:])**2).sum(-1)
q=d.argmin(-1)+1
q=np.where(m,q,0).astype(np.uint8)
f2=np.zeros_like(q); f2[1:]=q[:-1]
icon=np.vstack([q,f2])
im=Image.fromarray(icon,'P'); im.putpalette(back.getpalette()); im.save(D+'icon.png')
# graphics declarations
sub1('include/graphics.h','extern const u32 gMonFrontPic_Scizor[];','extern const u32 gMonFrontPic_Eirika[];\nextern const u32 gMonPalette_Eirika[];\nextern const u32 gMonBackPic_Eirika[];\nextern const u32 gMonShinyPalette_Eirika[];\nextern const u8 gMonIcon_Eirika[];\nextern const u8 gMonFootprint_Eirika[];\nextern const u32 gMonFrontPic_Scizor[];')
sub1('src/data/graphics/pokemon.h','const u32 gMonFrontPic_Scizor[]','''const u32 gMonFrontPic_Eirika[] = INCBIN_U32("graphics/pokemon/eirika/front.4bpp.lz");
const u32 gMonPalette_Eirika[] = INCBIN_U32("graphics/pokemon/eirika/normal.gbapal.lz");
const u32 gMonBackPic_Eirika[] = INCBIN_U32("graphics/pokemon/eirika/back.4bpp.lz");
const u32 gMonShinyPalette_Eirika[] = INCBIN_U32("graphics/pokemon/eirika/shiny.gbapal.lz");
const u8 gMonIcon_Eirika[] = INCBIN_U8("graphics/pokemon/eirika/icon.4bpp");
const u8 gMonFootprint_Eirika[] = INCBIN_U8("graphics/pokemon/eirika/footprint.1bpp");
const u32 gMonFrontPic_Scizor[]''')
# tables
sub1('src/data/pokemon_graphics/front_pic_table.h','SPECIES_SPRITE(OLD_UNOWN_Z, gMonFrontPic_DoubleQuestionMark)','SPECIES_SPRITE(OLD_UNOWN_Z, gMonFrontPic_Eirika)')
sub1('src/data/pokemon_graphics/back_pic_table.h','SPECIES_SPRITE(OLD_UNOWN_Z, gMonBackPic_DoubleQuestionMark)','SPECIES_SPRITE(OLD_UNOWN_Z, gMonBackPic_Eirika)')
sub1('src/data/pokemon_graphics/palette_table.h','SPECIES_PAL(OLD_UNOWN_Z, gMonPalette_DoubleQuestionMark)','SPECIES_PAL(OLD_UNOWN_Z, gMonPalette_Eirika)')
sub1('src/data/pokemon_graphics/shiny_palette_table.h','SPECIES_SHINY_PAL(OLD_UNOWN_Z, gMonShinyPalette_DoubleQuestionMark)','SPECIES_SHINY_PAL(OLD_UNOWN_Z, gMonShinyPalette_Eirika)')
sub1('src/data/pokemon_graphics/footprint_table.h','[SPECIES_OLD_UNOWN_Z] = gMonFootprint_QuestionMark','[SPECIES_OLD_UNOWN_Z] = gMonFootprint_Eirika')
sub1('src/data/text/species_names.h','[SPECIES_OLD_UNOWN_Z] = _("?")','[SPECIES_OLD_UNOWN_Z] = _("EIRIKA")')
sub1('src/pokemon_icon.c','[SPECIES_OLD_UNOWN_Z] = gMonIcon_QuestionMark','[SPECIES_OLD_UNOWN_Z] = gMonIcon_Eirika')
sub1('src/pokemon_icon.c','[SPECIES_OLD_UNOWN_Z] = 0,','[SPECIES_OLD_UNOWN_Z] = 3,')
sub1('src/pokemon_icon.c','    INCBIN_U16("graphics/pokemon/icon_palettes/icon_palette_2.gbapal")\n','    INCBIN_U16("graphics/pokemon/icon_palettes/icon_palette_2.gbapal"),\n    INCBIN_U16("graphics/pokemon/icon_palettes/icon_palette_3.gbapal")\n')
sub1('include/constants/species.h','#define SPECIES_OLD_UNOWN_Z 276\n','#define SPECIES_OLD_UNOWN_Z 276\n#define SPECIES_EIRIKA SPECIES_OLD_UNOWN_Z\n')
sub1('src/pokemon.c','    if (species <= SPECIES_OLD_UNOWN_Z - 1)\n        return SPECIES_UNOWN - 1;','    if (species == SPECIES_EIRIKA)\n        return SPECIES_SCIZOR - 1; // Eirika uses Scizor\'s cry\n\n    if (species <= SPECIES_OLD_UNOWN_Z - 1)\n        return SPECIES_UNOWN - 1;')
# coordinates (64x64 portrait: use Scizor-like y offsets from the front 0 and back 0)
sub1('src/data/pokemon_graphics/back_pic_coordinates.h','[SPECIES_OLD_UNOWN_Z] =\n    {\n        .size = MON_COORDS_SIZE(64, 64),\n        .y_offset = 1,','[SPECIES_OLD_UNOWN_Z] =\n    {\n        .size = MON_COORDS_SIZE(64, 64),\n        .y_offset = 0,')
sub1('src/data/pokemon_graphics/front_pic_coordinates.h','[SPECIES_OLD_UNOWN_Z] =\n    {\n        .size = MON_COORDS_SIZE(64, 64),\n        .y_offset = 6,','[SPECIES_OLD_UNOWN_Z] =\n    {\n        .size = MON_COORDS_SIZE(64, 64),\n        .y_offset = 0,')
# species info: Scizor's data, female only, own name
s=open('src/data/pokemon/species_info.h').read()
m=re.search(r'    \[SPECIES_SCIZOR\] =\n    \{.*?\n    \},\n',s,re.S); blk=m.group(0)
blk=blk.replace('[SPECIES_SCIZOR]','[SPECIES_EIRIKA]').replace('PERCENT_FEMALE(50)','MON_FEMALE')
s=s.replace('    [SPECIES_OLD_UNOWN_Z] = OLD_UNOWN_SPECIES_INFO,\n',blk)
open('src/data/pokemon/species_info.h','w').write(s)
# tm/hm
s=open('src/data/pokemon/tmhm_learnsets.h').read()
m=re.search(r'    \[SPECIES_SCIZOR\] .*?\),\n',s,re.S); blk=m.group(0)
s=s.replace('    [SPECIES_OLD_UNOWN_Z] = TMHM_LEARNSET(0),\n', blk.replace('[SPECIES_SCIZOR]     ','[SPECIES_EIRIKA]     ',1))
open('src/data/pokemon/tmhm_learnsets.h','w').write(s)
# tutor
s=open('src/data/pokemon/tutor_learnsets.h').read()
m=re.search(r'    \[SPECIES_SCIZOR\] = .*?,\n',s,re.S); blk=m.group(0)
s=s.replace('    [SPECIES_CHIMECHO] =', blk.replace('SCIZOR','EIRIKA')+'\n    [SPECIES_CHIMECHO] =',1)
open('src/data/pokemon/tutor_learnsets.h','w').write(s)
# level up learnset
sub1('src/data/pokemon/level_up_learnset_pointers.h','[SPECIES_OLD_UNOWN_Z] = sSpecies276LevelUpLearnset','[SPECIES_OLD_UNOWN_Z] = sEirikaLevelUpLearnset')
s=open('src/data/pokemon/level_up_learnsets.h').read()
new='''static const u16 sEirikaLevelUpLearnset[] = {
    LEVEL_UP_MOVE( 1, MOVE_QUICK_ATTACK),
    LEVEL_UP_MOVE( 1, MOVE_LEER),
    LEVEL_UP_MOVE( 6, MOVE_FOCUS_ENERGY),
    LEVEL_UP_MOVE( 7, MOVE_SCRATCH),
    LEVEL_UP_MOVE( 9, MOVE_FURY_CUTTER),
    LEVEL_UP_MOVE(11, MOVE_PURSUIT),
    LEVEL_UP_MOVE(12, MOVE_FURY_ATTACK),
    LEVEL_UP_MOVE(14, MOVE_CUT),
    LEVEL_UP_MOVE(16, MOVE_FALSE_SWIPE),
    LEVEL_UP_MOVE(17, MOVE_METAL_CLAW),
    LEVEL_UP_MOVE(19, MOVE_RAZOR_LEAF),
    LEVEL_UP_MOVE(21, MOVE_AGILITY),
    LEVEL_UP_MOVE(22, MOVE_VICE_GRIP),
    LEVEL_UP_MOVE(25, MOVE_SLASH),
    LEVEL_UP_MOVE(28, MOVE_STEEL_WING),
    LEVEL_UP_MOVE(31, MOVE_RAZOR_WIND),
    LEVEL_UP_MOVE(34, MOVE_CROSS_CHOP),
    LEVEL_UP_MOVE(36, MOVE_SWORDS_DANCE),
    LEVEL_UP_MOVE(41, MOVE_IRON_DEFENSE),
    LEVEL_UP_END
};

'''
assert 'static const u16 sScizorLevelUpLearnset[]' in s
s=s.replace('static const u16 sScizorLevelUpLearnset[]',new+'static const u16 sScizorLevelUpLearnset[]',1)
open('src/data/pokemon/level_up_learnsets.h','w').write(s)
print('ok')
