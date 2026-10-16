#include "global.h"
#include "gflib.h"
#include "battle.h"
#include "battle_anim.h"
#include "constants/species.h"
#include "ally_attack.h"

#define ALLY_ATTACK_HOLD     8        // frames the last pose is held after the swing
#define ALLY_ATTACK_PAL_TAG  0xEA01
#define ALLY_ATTACK_MAX_PARTS 8

#define tTimer   data[0]
#define tBattler data[1]

struct AllyAttackPart
{
    const struct SpriteTemplate *template;
    s16 x, y;   // center of the part on screen
};

struct AllyAttackAnim
{
    u16 species;
    const struct AllyAttackPart *parts;
    u8 numParts;
    u8 hit;             // frames from the start until the hit lands (the move effect starts here)
    const u16 *pal;
};

static void SpriteCB_AllyAttack(struct Sprite *sprite);

#define OAM_DATA(w, h) \
static const struct OamData sOamData_##w##x##h = \
{ \
    .affineMode = ST_OAM_AFFINE_OFF, \
    .objMode = ST_OAM_OBJ_NORMAL, \
    .shape = SPRITE_SHAPE(w##x##h), \
    .size = SPRITE_SIZE(w##x##h), \
    .priority = 1, \
}

OAM_DATA(64, 64);
OAM_DATA(32, 64);
OAM_DATA(64, 32);
OAM_DATA(32, 32);

#include "data/ally_attack/Eirika.h"
#include "data/ally_attack/Innes.h"
#include "data/ally_attack/Tana.h"
#include "data/ally_attack/Larachel.h"
#include "data/ally_attack/Dozla.h"
#include "data/ally_attack/Joshua.h"
#include "data/ally_attack/Duessel.h"
#include "data/ally_attack/Cormag.h"
#include "data/ally_attack/Myrrh.h"

#define ANIM_ENTRY(species, name, key) { species, s##name##Parts, ARRAY_COUNT(s##name##Parts), key##_ATTACK_HIT, s##name##Pal }

static const struct AllyAttackAnim sAllyAttackAnims[] =
{
    ANIM_ENTRY(SPECIES_EIRIKA,   Eirika,   EIRIKA),
    ANIM_ENTRY(SPECIES_INNES,    Innes,    INNES),
    ANIM_ENTRY(SPECIES_TANA,     Tana,     TANA),
    ANIM_ENTRY(SPECIES_LARACHEL, Larachel, LARACHEL),
    ANIM_ENTRY(SPECIES_DOZLA,    Dozla,    DOZLA),
    ANIM_ENTRY(SPECIES_JOSHUA,   Joshua,   JOSHUA),
    ANIM_ENTRY(SPECIES_DUESSEL,  Duessel,  DUESSEL),
    ANIM_ENTRY(SPECIES_CORMAG,   Cormag,   CORMAG),
    ANIM_ENTRY(SPECIES_MYRRH,    Myrrh,    MYRRH),
};

static u8 sSpriteIds[ALLY_ATTACK_MAX_PARTS];
static u8 sBattler;
static bool8 sActive;
static const struct AllyAttackAnim *sAnim;
static struct SpritePalette sPalette;

static void SpriteCB_AllyAttack(struct Sprite *sprite)
{
    sprite->tTimer++;
}

static const struct AllyAttackAnim *FindAnim(u16 species)
{
    u32 i;
    for (i = 0; i < ARRAY_COUNT(sAllyAttackAnims); i++)
        if (sAllyAttackAnims[i].species == species)
            return &sAllyAttackAnims[i];
    return NULL;
}

bool8 ShouldPlayAllyAttack(u8 battler)
{
    return GetBattlerSide(battler) == B_SIDE_PLAYER && FindAnim(gBattleMons[battler].species) != NULL;
}

void StartAllyAttack(u8 battler)
{
    u32 i;

    sAnim = FindAnim(gBattleMons[battler].species);
    sPalette.data = sAnim->pal;
    sPalette.tag = ALLY_ATTACK_PAL_TAG;
    LoadSpritePalette(&sPalette);
    sBattler = battler;
    for (i = 0; i < sAnim->numParts; i++)
    {
        const struct AllyAttackPart *part = &sAnim->parts[i];
        sSpriteIds[i] = CreateSprite(part->template, part->x, part->y, 0);
        gSprites[sSpriteIds[i]].tBattler = battler;
    }
    gSprites[gBattlerSpriteIds[battler]].invisible = TRUE;
    sActive = TRUE;
}

// Called every frame before the OAM is built: the portrait, and any copies of it that move animations
// make (after-images and the like), are never drawn while the attack animation is on screen
void HideAllyPortraitSprites(void)
{
    u32 i;
    struct Sprite *portrait;

    if (!sActive)
        return;
    portrait = &gSprites[gBattlerSpriteIds[sBattler]];
    portrait->invisible = TRUE;
    for (i = 0; i < MAX_SPRITES; i++)
    {
        if (gSprites[i].inUse && &gSprites[i] != portrait
         && gSprites[i].template == portrait->template && gSprites[i].oam.tileNum == portrait->oam.tileNum)
            gSprites[i].invisible = TRUE;
    }
}

bool8 IsAllyAttackHidingBattler(u8 battler)
{
    return sActive && sBattler == battler;
}

bool8 HasAllyAttackReachedHit(void)
{
    return gSprites[sSpriteIds[0]].tTimer >= sAnim->hit;
}

bool8 IsAllyAttackDone(void)
{
    u32 i;
    for (i = 0; i < sAnim->numParts; i++)
        if (!gSprites[sSpriteIds[i]].animEnded)
            return FALSE;
    return TRUE;
}

void EndAllyAttack(void)
{
    u32 i;
    for (i = 0; i < sAnim->numParts; i++)
        DestroySprite(&gSprites[sSpriteIds[i]]);
    FreeSpritePaletteByTag(ALLY_ATTACK_PAL_TAG);
    sActive = FALSE;
    gSprites[gBattlerSpriteIds[sBattler]].invisible = FALSE;
}
