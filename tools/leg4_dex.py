import re
D='src/data/pokemon/'
allies=[ # sp name, dexconst, cat, h(dm), w(hg), text
 ('INNES','OLD_UNOWN_B','ARCHER',18,660,"Crown prince of Frelia and a sniper\nwith no equal. He is calm and proud,\nand he guards his sister Tana."),
 ('TANA','OLD_UNOWN_C','PEGASUS',16,480,"A pegasus knight of Frelia and\nInnes's younger sister. She is\nbright and quick, and loves to fly."),
 ('LARACHEL','OLD_UNOWN_D','TROUBADOUR',15,450,"A Rausten princess who wields a\nstaff and a loud voice. She thinks\nshe is a hero and acts like one."),
 ('DOZLA','OLD_UNOWN_E','BERSERKER',22,1100,"A strong axe fighter of Jehanna.\nHe looks fierce but is kind, and\nhe never leaves a friend behind."),
 ('JOSHUA','OLD_UNOWN_F','MYRMIDON',17,580,"A swordsman from Jehanna. He lives\nby the dice and wins more than\nhe loses, with a blade or a bet."),
 ('DUESSEL','OLD_UNOWN_G','GREAT KNIGHT',19,1200,"Once the Silver Axe of Grado. A\nloyal and serious knight who left\nthe empire to keep his honor."),
 ('CORMAG','OLD_UNOWN_H','WYVERN',18,700,"A wyvern rider of Grado who chose\nto leave the empire. He is quiet,\nsteady and loyal to his friends."),
 ('MYRRH','OLD_UNOWN_I','MANAKETE',12,300,"A young manakete who can turn into\na dragon. She is shy and gentle,\nand she is always hungry."),
 ('EIRIKA','OLD_UNOWN_Z','PRINCESS',16,520,"Princess of Renais and twin sister\nof Ephraim. She wields a rapier and\nleads the march to save the land."),
]
# enum reorder
p='include/constants/pokedex.h'; t=open(p).read()
import string
unk=[f"    NATIONAL_DEX_OLD_UNOWN_{c},\n" for c in "JKLMNOPQRSTUVWXY"]
for u in unk: assert u in t; t=t.replace(u,'',1)
t=t.replace("    NATIONAL_DEX_OLD_UNOWN_Z,\n","    NATIONAL_DEX_OLD_UNOWN_Z,\n"+''.join(unk),1)
# Z already moved? place Z right after I
t=t.replace("    NATIONAL_DEX_OLD_UNOWN_Z,\n"+''.join(unk),"@@")
t=t.replace("    NATIONAL_DEX_OLD_UNOWN_I,\n","    NATIONAL_DEX_OLD_UNOWN_I,\n    NATIONAL_DEX_OLD_UNOWN_Z,\n"+''.join(unk),1)
t=t.replace("@@","")
t=t.replace("#define NATIONAL_DEX_COUNT  NATIONAL_DEX_DEOXYS","#define NATIONAL_DEX_COUNT  NATIONAL_DEX_OLD_UNOWN_Z")
open(p,'w').write(t)
# texts
tx="// Pokedex text for Eirika and the 8 allies (original wording)\n"
for n,d,c,h,w,s in allies:
    nm=n.capitalize() if n!='LARACHEL' else 'LArachel'
    tx+=f'const u8 g{nm}PokedexText[] = _(\n'+'\n'.join('    "'+l+('\\n' if i<2 else '')+'"' for i,l in enumerate(s.split('\n')))+');\n\nconst u8 g%sPokedexTextUnused[] = _("");\n\n'%nm
open(D+'pokedex_text_allies.h','w').write(tx)
open(D+'pokedex_text.h','a').write('#include "pokedex_text_allies.h"\n')
# entries
e=open(D+'pokedex_entries.h').read()
add=''
for n,d,c,h,w,s in allies:
    nm=n.capitalize() if n!='LARACHEL' else 'LArachel'
    add+=f"""    [NATIONAL_DEX_{d}] =
    {{
        .categoryName = _("{c}"),
        .height = {h},
        .weight = {w},
        .description = g{nm}PokedexText,
        .unusedDescription = g{nm}PokedexTextUnused,
        .pokemonScale = 256,
        .pokemonOffset = 0,
        .trainerScale = 256,
        .trainerOffset = 0,
    }},

"""
i=e.rstrip().rfind('};')
e=e[:i].rstrip('\n')+"\n\n"+add.rstrip('\n')+"\n};\n"
open(D+'pokedex_entries.h','w').write(e)
# parse heights/weights
ent={}
for m in re.finditer(r'\[NATIONAL_DEX_(\w+)\] =\s*\{.*?\.height = (\d+),\s*\.weight = (\d+)',e,re.S):
    ent[m.group(1)]=(int(m.group(2)),int(m.group(3)))
o=open(D+'pokedex_orders.h').read()
def tbl(name):
    m=re.search(r'(const u16 %s\[\] =\s*\{)(.*?)(\};)'%name,o,re.S); return m
new=[a[1] for a in allies]
for name,idx in (('gPokedexOrder_Weight',1),('gPokedexOrder_Height',0)):
    m=tbl(name); items=[x.strip() for x in m.group(2).split(',') if x.strip()]
    for d in new:
        key=ent[d][idx]; pos=len(items)
        for k,it in enumerate(items):
            if ent[it.replace('NATIONAL_DEX_','')][idx]>key: pos=k;break
        items.insert(pos,'NATIONAL_DEX_'+d)
    o=o.replace(m.group(0),m.group(1)+'\n    '+',\n    '.join(items)+'\n'+m.group(3))
# alphabetical
names={'OLD_UNOWN_B':'INNES','OLD_UNOWN_C':'TANA','OLD_UNOWN_D':"L'ARACHEL",'OLD_UNOWN_E':'DOZLA','OLD_UNOWN_F':'JOSHUA','OLD_UNOWN_G':'DUESSEL','OLD_UNOWN_H':'CORMAG','OLD_UNOWN_I':'MYRRH','OLD_UNOWN_Z':'EIRIKA'}
sn=open('src/data/text/species_names.h').read()
def nm(it):
    c=it.replace('NATIONAL_DEX_','')
    if c in names: return names[c]
    m=re.search(r'\[SPECIES_%s\] = _\("([^"]*)"\)'%c,sn)
    return m.group(1) if m else c.replace('_',' ')
m=tbl('gPokedexOrder_Alphabetical'); items=[x.strip() for x in m.group(2).split(',') if x.strip()]
un=[i for i in items if 'OLD_UNOWN' in i and i.replace('NATIONAL_DEX_OLD_UNOWN_','') not in 'BCDEFGHIZ']
rest=[i for i in items if i not in un and 'OLD_UNOWN' not in i]
for d in new:
    key=names[d]; pos=len(rest)
    for k,it in enumerate(rest):
        if nm(it)>key: pos=k;break
    rest.insert(pos,'NATIONAL_DEX_'+d)
items=rest+un; assert len(items)==411,len(items)
o=o.replace(m.group(0),m.group(1)+'\n    '+',\n    '.join(items)+'\n'+m.group(3))
open(D+'pokedex_orders.h','w').write(o)
