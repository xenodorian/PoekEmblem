#include "global.h"
#include "gflib.h"
#include "event_data.h"
#include "pokedex.h"
#include "region_map.h"
#include "save_menu_util.h"
#include "constants/maps.h"

// Leg20: story rooms borrow donor map sections (SILPH CO. and so on); show their FE8 names instead
static const u8 sStoryName_Renais[] = _("RENAIS CASTLE");
static const u8 sStoryName_Frelia[] = _("FRELIA CASTLE");
static const u8 sStoryName_Jehanna[] = _("JEHANNA HALL");
static const u8 sStoryName_Rigwald[] = _("FORT RIGWALD");
static const u8 sStoryName_Grado[] = _("GRADO KEEP");
static const u8 sStoryName_Temple[] = _("BLACK TEMPLE");
static const u8 sStoryName_CampCenter[] = _("CAMP CENTER");
static const u8 sStoryName_CampMart[] = _("CAMP MART");

static const struct { u16 map; const u8 *name; } sStoryMapNames[] = {
    { MAP_STORY_RENAIS_CASTLE, sStoryName_Renais },
    { MAP_STORY_FRELIA_CASTLE, sStoryName_Frelia },
    { MAP_STORY_JEHANNA_HALL, sStoryName_Jehanna },
    { MAP_STORY_FORT_RIGWALD, sStoryName_Rigwald },
    { MAP_STORY_GRADO_THRONE_ROOM, sStoryName_Grado },
    { MAP_STORY_BLACK_TEMPLE, sStoryName_Temple },
    { MAP_STORY_CAMP_CENTER, sStoryName_CampCenter },
    { MAP_STORY_CAMP_MART, sStoryName_CampMart },
};

u8 *GetCurrentLocationName(u8 *dest)
{
    u32 i;
    for (i = 0; i < NELEMS(sStoryMapNames); i++)
    {
        if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(sStoryMapNames[i].map)
         && gSaveBlock1Ptr->location.mapNum == MAP_NUM(sStoryMapNames[i].map))
            return StringCopy(dest, sStoryMapNames[i].name);
    }
    return GetMapNameGeneric(dest, gMapHeader.regionMapSectionId);
}

void SaveStatToString(u8 gameStatId, u8 *dest0, u8 color)
{
    int nBadges;
    int flagId;

    u8 *dest = dest0;
    *dest++ = EXT_CTRL_CODE_BEGIN;
    *dest++ = EXT_CTRL_CODE_COLOR;
    *dest++ = color;
    *dest++ = EXT_CTRL_CODE_BEGIN;
    *dest++ = EXT_CTRL_CODE_SHADOW;
    *dest++ = color + 1;
    switch (gameStatId)
    {
    case SAVE_STAT_NAME:
        dest = StringCopy(dest, gSaveBlock2Ptr->playerName);
        break;
    case SAVE_STAT_POKEDEX:
        if (IsNationalPokedexEnabled())
            dest = ConvertIntToDecimalStringN(dest, GetNationalPokedexCount(1), STR_CONV_MODE_LEFT_ALIGN, 3);
        else
            dest = ConvertIntToDecimalStringN(dest, GetKantoPokedexCount(1), STR_CONV_MODE_LEFT_ALIGN, 3);
        break;
    case SAVE_STAT_TIME:
        dest = ConvertIntToDecimalStringN(dest, gSaveBlock2Ptr->playTimeHours, STR_CONV_MODE_LEFT_ALIGN, 3);
        *dest++ = CHAR_COLON;
        dest = ConvertIntToDecimalStringN(dest, gSaveBlock2Ptr->playTimeMinutes, STR_CONV_MODE_LEADING_ZEROS, 2);
        break;
    case SAVE_STAT_TIME_HR_RT_ALIGN:
        dest = ConvertIntToDecimalStringN(dest, gSaveBlock2Ptr->playTimeHours, STR_CONV_MODE_RIGHT_ALIGN, 3);
        *dest++ = CHAR_COLON;
        dest = ConvertIntToDecimalStringN(dest, gSaveBlock2Ptr->playTimeMinutes, STR_CONV_MODE_LEADING_ZEROS, 2);
        break;
    case SAVE_STAT_LOCATION:
        GetCurrentLocationName(dest);
        break;
    case SAVE_STAT_BADGES:
        for (flagId = FLAG_BADGE01_GET, nBadges = 0; flagId < FLAG_BADGE01_GET + 8; flagId++)
        {
            if (FlagGet(flagId))
                nBadges++;
        }
        *dest++ = nBadges + CHAR_0;
        *dest++ = 10; // 'こ'
        *dest++ = EOS;
        break;
    }
}

