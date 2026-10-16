@ Recruitment scripts for the friendly characters. Call one of these from a story event.
EventScript_RecruitAlly::
	special RecruitAlly
	copyvar VAR_0x8005, VAR_RESULT
	playfanfare MUS_LEVEL_UP
	waitfanfare
	goto_if_eq VAR_0x8005, 0, EventScript_AllyJoinedParty
	goto_if_eq VAR_0x8005, 1, EventScript_AllySentToPC
	goto EventScript_AllyNoRoom

EventScript_AllyJoinedParty::
	msgbox Text_AllyJoinedParty
	return

EventScript_AllySentToPC::
	msgbox Text_AllySentToPC
	return

EventScript_AllyNoRoom::
	msgbox Text_AllyNoRoom
	return

EventScript_RecruitInnes::
	setvar VAR_0x8004, SPECIES_INNES
	goto EventScript_RecruitAlly

EventScript_RecruitTana::
	setvar VAR_0x8004, SPECIES_TANA
	goto EventScript_RecruitAlly

EventScript_RecruitLArachel::
	setvar VAR_0x8004, SPECIES_LARACHEL
	goto EventScript_RecruitAlly

EventScript_RecruitDozla::
	setvar VAR_0x8004, SPECIES_DOZLA
	goto EventScript_RecruitAlly

EventScript_RecruitJoshua::
	setvar VAR_0x8004, SPECIES_JOSHUA
	goto EventScript_RecruitAlly

EventScript_RecruitDuessel::
	setvar VAR_0x8004, SPECIES_DUESSEL
	goto EventScript_RecruitAlly

EventScript_RecruitCormag::
	setvar VAR_0x8004, SPECIES_CORMAG
	goto EventScript_RecruitAlly

EventScript_RecruitMyrrh::
	setvar VAR_0x8004, SPECIES_MYRRH
	goto EventScript_RecruitAlly

Text_AllyJoinedParty::
	.string "{STR_VAR_1} joined {PLAYER}'s party!$"

Text_AllySentToPC::
	.string "{STR_VAR_1} joined {PLAYER}'s party!\n"
	.string "The party is full, so {STR_VAR_1} was\l"
	.string "sent to a BOX in the PC.$"

Text_AllyNoRoom::
	.string "There is no room for {STR_VAR_1}.$"
