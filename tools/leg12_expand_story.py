#!/usr/bin/env python3
"""Leg12: expand story/chapters.json (one time, guarded by the 'v12' key).
Adds per chapter: display label, a skirmish battle (fresh trainers, theme picked here), extra scene lines
before/after (scene_before, scene_after as [speaker species or null, text]), Ephraim appearances and the
missing chapter 5x. Usage: leg12_expand_story.py story/chapters.json"""
import json, sys
p = sys.argv[1]; d = json.load(open(p))
if d.get('v12'): raise SystemExit('already expanded')
E_ = 'SPECIES_EIRIKA'
def S(sp, t): return [sp, t]
N = None
# old id -> (skirmish theme(s), scene_before, scene_after)
X = {
0: ('brute', [S(N,"Seth: Princess Eirika, the king has fallen. Grado is inside the walls."), S(E_,"Eirika: Father... Then we fight our way out.")],
             [S(N,"Seth: Frelia will shelter us. Ephraim is the one hope Renais has left."), S(E_,"Eirika: I will not let Renais fall for nothing.")]),
1: ('knight', [S(N,"Seth: Grado soldiers hold the road. Stay behind me, Princess."), S(E_,"Eirika: Frelia is just beyond the border. Keep moving.")],
             [S(N,"Seth: The Mulan border is behind us. Lyon is with Grado, Princess."), S(E_,"Eirika: Lyon... I cannot believe he would let this happen.")]),
2: ('brute', [S(N,"Ross: Eirika! Garcia and I will cover the pass."), S(N,"Garcia: Hah! A few bandits. Leave them to me.")],
             [S(N,"Ross: Ow. Did we win? Dad would be proud."), S(N,"Ephraim: Eirika! I came as fast as I could. Are you hurt?")]),
3: ('brute', [S(N,"Seth: Borgo Ridge ahead. Bandits, and worse, I fear."), S(E_,"Eirika: Stay close, Seth. We cannot be delayed.")],
             [S(N,"Colm: Easy, Princess. I only steal from people who deserve it."), S(E_,"Eirika: Then you may travel with us, Colm. Please behave.")]),
4: ('dark', [S(N,"Seth: The dead walk here. I have never seen the like."), S(E_,"Eirika: Something is calling them. Hold steady.")],
             [S(N,"Seth: The graveyard is quiet again. Whatever stirred them is gone."), S(E_,"Eirika: Magvel is not what it was. We should hurry.")]),
5: ('brute', [S(N,"Seth: Grado holds the city. Be ready for anything."), S(E_,"Eirika: Joshua. We meet again at last.")],
             [S(N,"Joshua: Tch. Grado pays badly. You pay better, Princess."), S(E_,"Eirika: Then ride with us, Joshua. We are going to Renvall.")]),
6: ('dark', [S(N,"Novala: Burn the villages. Leave nothing for Renais."), S(E_,"Eirika: Whole villages stand empty. Who does this?")],
             [S(N,"Seth: The last of Novala's mages have fled. The survivors are safe."), S(E_,"Eirika: I will remember every name on this road.")]),
7: ('water', [S(N,"Murray: Renvall is ours. Take the docks and leave nothing."), S(E_,"Eirika: The harbor is the key to the coast. Take it back.")],
             [S(N,"Seth: The docks are clear. A ship can take us to Frelia."), S(E_,"Eirika: Then we sail. Ephraim must be told of this.")]),
8: ('archer', [S(N,"Tirado: A trap, Princess. The road ends here."), S(E_,"Eirika: Seth, they knew we would come. Hold the line.")],
             [S(N,"Ephraim: Eirika, we must split here. I will march on Grado itself."), S(E_,"Eirika: Then I will go to Frelia and find Prince Innes. Be careful, brother.")]),
9: ('brute', [S(N,"Tana: Princess Eirika! Frelia's walls are in sight."), S(N,"Amelia: Um, hello! I am only a recruit, but I will help!")],
             [S(N,"Tana: Prince Innes holds Port Kiris against the revolt."), S(E_,"Eirika: Then we go to him. Thank you, Tana.")]),
10: ('water', [S(N,"Gerik: Mercenaries for hire. Pay well and we cover your flank."), S(N,"Tethys: Hmm, a princess. How exciting.")],
             [S(N,"Innes: Eirika, the revolt is quelled. Your timing was good."), S(N,"Ephraim (letter): Grado's border forts have fallen to me. I march on the capital.")]),
11: ('dark', [S(N,"L'Arachel: Fear not, for I, L'Arachel, have come!"), S(N,"Dozla: Dozla follows. Princess L'Arachel talks too much.")],
             [S(N,"L'Arachel: The dead will not rise again while I have my staff!"), S(E_,"Eirika: We should find out what is waking them.")]),
12: ('dark', [S(N,"Maelduin: Quiet, quiet. The village sleeps. Do not wake it."), S(E_,"Eirika: Something is wrong here. Stay together.")],
             [S(N,"Fado: ...Peace, at last."), S(E_,"Eirika: Poor man. The village can rest now.")]),
13: ('wyvern', [S(N,"Aias: Hamill Canyon is Grado's. Turn back."), S(E_,"Eirika: We cannot. The only road to Jehanna runs through it.")],
             [S(N,"Amelia: I am a real knight now, Princess! Well, nearly."), S(N,"Ephraim (letter): Grado's General Duessel was not at the front. Be watchful.")]),
14: ('knight', [S(N,"Caellach: Jehanna's queen has sold the desert to Grado."), S(E_,"Eirika: Then we take it back, for her people.")],
             [S(N,"Rennac: Hmm. A scavenger, perhaps. Fine, I will fight for coin."), S(E_,"Eirika: Welcome, Rennac. The desert is open.")]),
15: ('wyvern', [S(N,"Valter: Heh heh. A lost princess in my desert."), S(E_,"Eirika: Valter. You will answer for Renais.")],
             [S(N,"Valter: Curse you... Grado will..."), S(N,"Ephraim (letter): The Sacred Stone is in the Black Temple, Eirika. We must reach it first.")]),
16: ('rider', [S(N,"Orson: Frelia, Renais... all will burn. Ha ha ha!"), S(E_,"Eirika: This is not the Orson I knew.")],
             [S(N,"Orson: ...What have I done?"), S(E_,"Eirika: It was not you. Rest now.")]),
17: ('dark', [S(N,"Syrene: Princess Eirika. Renais has suffered enough."), S(E_,"Eirika: Lyon! Why have you done this?")],
             [S(N,"Syrene: Lyon is possessed by the Demon King. Please, save him."), S(E_,"Eirika: Then we go to the temple and end this.")]),
18: ('water', [S(N,"Innes: This river is cursed. Tana, scout ahead."), S(E_,"Eirika: Two faces of evil. Stand together.")],
             [S(N,"Ephraim: Eirika! You made it. I am glad to see you safe."), S(E_,"Eirika: And you, brother. Together we finish this war.")]),
19: ('wyvern', [S(N,"Ephraim: The summit is ahead. Riev's priests guard it."), S(E_,"Eirika: Neleras is the way to the Sacred Stone. We climb.")],
             [S(N,"Ephraim: The path to the temple is open. Stay together."), S(E_,"Eirika: Whatever waits inside, we face it together.")]),
20: ('dark', [S(N,"Riev: The Sacred Stone belongs to Grado. You are too late."), S(E_,"Eirika: Lyon is not himself. He is being used.")],
             [S(N,"Ephraim: Riev and Morva fall. The way is open."), S(E_,"Eirika: Then let us save Lyon before it is too late.")]),
21: ('knight', [S(N,"Lyon: Eirika... Run. Please, run."), S(E_,"Eirika: Lyon! Fight it. I am here.")],
             [S(N,"Lyon: Thank you, Eirika. ...I am sorry for everything."), S(N,"Ephraim: The Demon King wakes. Eirika, he is here!")]),
22: ('dark', [S(N,"Fomortiis: Foolish children. I am the Demon King."), S(E_,"Eirika: Ephraim, we finish this together.")],
             [S(N,"Ephraim: It is done. The Sacred Stone is sealed."), S(E_,"Eirika: Magvel is at peace. Renais will rise again.")]),
}
LABEL = {i: str(i) for i in range(23)}; LABEL[22] = '21x'
new = []
for c in d['chapters']:
    i = c['id']; th, sb, sa = X[i]
    c['label'] = LABEL[i]
    c['skirmish_theme'] = th
    c['scene_before'] = sb; c['scene_after'] = sa
    new.append(c)
    if i == 4:
        new.append({'id': 99, 'label': '5x', 'title': 'Unbroken Heart', 'map': 'MAP_STORY_RENAIS_CASTLE',
          'before': ["Eirika dreams of Renais. A shadow of the siege plays out once more."],
          'battles': [{'a': 'TRAINER_COOLTRAINER_GEORGE', 'boss': True}],
          'skirmish_theme': 'knight',
          'scene_before': [S(N,"Zonta: Renais will fall again, Princess. Again and again."), S(E_,"Eirika: No. This time I stand and fight.")],
          'mid': {'speaker': E_, 'text': "I will not run from my own home again."},
          'after': ["Zonta fades. The dream releases Eirika."],
          'scene_after': [S(N,"Seth: Princess? You were speaking in your sleep."), S(E_,"Eirika: Only a memory, Seth. I am ready now.")]})
for k, c in enumerate(new): c['id'] = k
d['chapters'] = new; d['v12'] = True
json.dump(d, open(p, 'w'), indent=1)
print('chapters', len(new))
