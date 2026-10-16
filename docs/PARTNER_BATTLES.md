# In-game partner (double) battles

Ported from pokeemerald's tag battle. Used from FE8 Chapter 3 onward, when the player first has more than 6 deployment slots. Seth is the AI partner for the Chapter 3 and 4 double battles, Garcia (the Blaine slot) takes the partner slot from Chapter 5.

## How a battle works

- Two opposing trainers (`BATTLE_TYPE_TWO_OPPONENTS`), the player plus an AI partner (`BATTLE_TYPE_INGAME_PARTNER`), `BATTLE_TYPE_DOUBLE` and `BATTLE_TYPE_MULTI` are set together.
- The player fights with party slots 0 to 2. The partner's party is created into slots 3 to 5 when the battle starts. The opposing parties are slots 0 to 2 (first trainer) and 3 to 5 (second trainer) of the enemy party.
- The player's slots 3 to 5 are saved before the battle and restored afterward, win or lose. A loss goes to the normal whiteout after the party is restored.
- The partner chooses moves with the trainer AI, switches to its next living Pokemon when one faints, never uses items, and does not gain experience. Its Pokemon always obey.
- Battle intro text, send-out text, the party menu (the partner's Pokemon show as locked) and the defeat text all have two-trainer versions.

## Script use

```
setvar VAR_0x8004, TRAINER_<first opponent>
setvar VAR_0x8005, TRAINER_<second opponent>
setvar VAR_0x8006, TRAINER_<partner>      @ any trainer slot; its party is the partner's party
special StartPartnerBattle
waitstate
```

Seth is the `TRAINER_LEADER_BROCK` slot and Garcia is the `TRAINER_LEADER_BLAINE` slot in the cast list. Edit their parties in `src/data/trainers.h` to set what the partner brings.

## Source map

| Area | File |
| --- | --- |
| Special, party save and restore, end-of-battle callback | `src/battle_setup.c` (`StartPartnerBattle`) |
| Partner controller (AI move choice, switch choice, front-pic trainer art) | `src/battle_controller_player_partner.c` |
| Controller setup, party indexes | `src/battle_controllers.c` |
| Start-up state machine, second opponent party creation | `src/battle_main.c` |
| Opponent right-side trainer art, shiny and healthbox intro flow | `src/battle_controller_opponent.c` |
| Text and new placeholders `B_TRAINER2_*`, `B_PARTNER_*` | `src/battle_message.c`, `charmap.txt`, `include/battle_message.h` |
| Two-trainer win script | `data/battle_scripts_1.s` (`BattleScript_LocalTwoTrainersDefeated`) |
| Party order after switches | `src/party_menu.c` (`SwitchPartyOrderInGameMulti`) |
| Switch rules, party halves, no partner exp | `src/battle_script_commands.c`, `src/battle_util.c`, `src/battle_ai_switch_items.c`, `src/battle_ai_script_commands.c` |

## Tested (mGBA, headless)

A test map script (not committed) starts `StartPartnerBattle` from the player's room with TRAINER_YOUNGSTER_BEN and TRAINER_LASS_JANICE against TRAINER_LEADER_BROCK, with six player Pokemon.

- Intro text and art for both trainers, both opposing send-outs, both player-side send-outs.
- Partner picks moves and acts every turn, switches to its next Pokemon when one faints (Geodude to Onix).
- Opponent switches to the next of its own trainer's Pokemon (Rattata to Ekans).
- Player's lead faints: party menu opens with the partner's Pokemon locked, choosing the next Pokemon sends it out.
- Win: experience goes to the player's Pokemon only, then the party is back to the original six in the original order.
- Loss: party restored, whiteout script runs.

## Not done

- Opposing trainers have no separate withdraw text for the right-hand trainer.
- Money reward uses the first trainer only (doubled for a double battle).
- The partner is shown with its front picture, flipped, like Emerald's Battle Frontier partners. The player keeps the Eirika back picture.
- The ally attack animation hooks assume the player is battler 0; they run for Eirika in doubles but have not been checked for the other eight allies.
