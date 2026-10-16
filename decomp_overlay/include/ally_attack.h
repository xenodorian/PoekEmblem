#ifndef GUARD_ALLY_ATTACK_H
#define GUARD_ALLY_ATTACK_H

// Plays a recruited character's own FE8 attack animation in battle, in place of their portrait battle sprite.
bool8 ShouldPlayAllyAttack(u8 battler);
void StartAllyAttack(u8 battler);
bool8 HasAllyAttackReachedHit(void);
bool8 IsAllyAttackDone(void);
void EndAllyAttack(void);
void HideAllyPortraitSprites(void);
bool8 IsAllyAttackHidingBattler(u8 battler);

#endif // GUARD_ALLY_ATTACK_H
