# Level curve (Leg19)

Chapter level table: `tools/level_curve.py` (`LV`). Regular trainers carry two Pokemon at LV-1 and LV (average LV-0.5). Boss trainers carry three Pokemon at LV, LV+1, LV+2 (average LV+1). Partner allies (Seth, Garcia) carry three Pokemon at LV-2, LV-1, LV.
The party is never raised automatically. Levels come only from battles and items (Rare Candy, vitamins are in the shops).

Wild tables (`tools/leg19_levels.py`): the vanilla FireRed routes were sorted by their weighted average level and staggered over the chapters in order. For each chapter, the nearest unused route within 3.5 levels of the chapter level is copied onto that chapter's map (land, water, rock smash and fishing lists, vanilla encounter rates). Chapters with no route in range get a generated area from the existing species themes, level range LV-2 to LV+2.

The effect depends on the terrain: grass and cave floor give land encounters, water gives surf and fishing encounters. Castle interiors (Renais, Frelia, Fort Rigwald, Jehanna, Grado, Black Temple) and cities with neither grass nor water (Pewter, Lavender, Celadon, Saffron) have no encounter terrain, so they have no table and do not use up a route. Maps with water only (Vermilion, Cerulean, Pallet, Fuchsia, Route 19) get the water and fishing lists only (land lists are dropped).

| Idx | FE8 | Title | Map | Chapter level | Source route | Route avg | Wild table |
|---|---|---|---|---|---|---|---|
| 0 | 0 | The Fall of Renais | STORY_RENAIS_CASTLE | 5 | - | - | none (no grass, cave or water terrain) |
| 1 | 1 | Escape! | ROUTE1 | 6 | vanilla MAP_ROUTE3 | 6.3 | written |
| 2 | 2 | The Protected | STORY_FRELIA_CASTLE | 8 | - | - | none (no grass, cave or water terrain) |
| 3 | 3 | The Bandits of Borgo | ROUTE3 | 10 | vanilla MAP_ROUTE25 | 10.4 | written |
| 4 | 4 | Ancient Horrors | VIRIDIAN_FOREST | 12 | vanilla MAP_ROUTE5 | 13.2 | written |
| 5 | 5x | Unbroken Heart | STORY_RENAIS_CASTLE | 13 | - | - | none (no grass, cave or water terrain) |
| 6 | 5 | The Empire's Reach | PEWTER_CITY | 14 | - | - | none (no grass, cave or water terrain) |
| 7 | 6 | Victims of War | ROUTE2 | 16 | vanilla MAP_ROUTE9 | 14.8 | written |
| 8 | 7 | Waterside Renvall | VERMILION_CITY | 18 | vanilla MAP_ROUTE8 | 17.9 | written |
| 9 | 8 | It's a Trap! | STORY_FORT_RIGWALD | 20 | - | - | none (no grass, cave or water terrain) |
| 10 | 9 | Distant Blade | CERULEAN_CITY | 22 | vanilla MAP_ROUTE21_NORTH | 22.5 | written |
| 11 | 10 | Revolt at Carcino | SAFFRON_CITY | 24 | - | - | none (no grass, cave or water terrain) |
| 12 | 11 | Creeping Darkness | LAVENDER_TOWN | 26 | - | - | none (no grass, cave or water terrain) |
| 13 | 12 | Village of Silence | ROUTE9 | 28 | vanilla MAP_ROUTE13 | 25.0 | written |
| 14 | 13 | Hamill Canyon | ROCK_TUNNEL_1F | 30 | generated | - | written |
| 15 | 14 | Queen of White Dunes | CELADON_CITY | 32 | - | - | none (no grass, cave or water terrain) |
| 16 | 15 | Scorched Sand | STORY_JEHANNA_HALL | 34 | - | - | none (no grass, cave or water terrain) |
| 17 | 16 | Ruled by Madness | FUCHSIA_CITY | 37 | vanilla MAP_ROUTE23 | 35.8 | written |
| 18 | 17 | River of Regrets | PALLET_TOWN | 40 | generated | - | written |
| 19 | 18 | Two Faces of Evil | ROUTE19 | 44 | generated | - | written |
| 20 | 19 | Last Hope | CERULEAN_CAVE_1F | 48 | generated | - | written |
| 21 | 20 | Darkling Woods | VICTORY_ROAD_1F | 52 | generated | - | written |
| 22 | 21 | Sacred Stone | STORY_GRADO_THRONE_ROOM | 56 | - | - | none (no grass, cave or water terrain) |
| 23 | 21x | Sacred Stone (Final) | STORY_BLACK_TEMPLE | 60 | - | - | none (no grass, cave or water terrain) |

Vanilla route averages used (weighted by encounter slot, land or water if no land):

Route1 2.9, Route22 3.3, Route2 3.3, Route3 6.3, Route4 9.4, Route24 9.6, Route25 10.4, Route5 13.2, Route6 13.2, Route11 13.7, Route9 14.8, Route10 14.8, Route8 17.9, Route7 19.0, Route16 19.9, Route21_North 22.5, Route18 23.9, Route17 24.0, Route12 24.4, Route14 24.8, Route13 25.0, Route15 25.0, Route23 35.8.

Routes assigned: Route13, Route21_North, Route23, Route25, Route3, Route5, Route8, Route9.
Routes left unassigned (no free chapter within range): Route1, Route2, Route4, Route6, Route7, Route10, Route11, Route12, Route14, Route15, Route16, Route17, Route18, Route22, Route24.

