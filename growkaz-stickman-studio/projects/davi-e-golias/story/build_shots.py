# build_shots.py — writes story/shots.json from the draft (timing) + this shot plan.
# Each entry: original id -> list of parts. A part = (first word of the part or None, plan dict).
# plan: k (shot kind) + params, scene (description), in, bars, sfx, amb.
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, '..')
draft = json.load(open(os.path.join(P, 'story', 'shots.draft.json'), encoding='utf-8'))
words = json.load(open(os.path.join(P, 'timeline', 'words.json'), encoding='utf-8'))
words = words.get('words', words) if isinstance(words, dict) else words
norm = lambda s: re.sub(r"[^\wà-ú]", '', s.lower())

def X(k, scene, **kw):
    d = {'k': k, 'scene': scene}; d.update(kw); return d

AMB_FIELD = {'name': 'wind', 'gain': -26}
AMB_ARMY = {'name': 'murmur', 'gain': -28}
AMB_ROOM = {'name': 'roomtone', 'gain': -28}
AMB_CITY = {'name': 'city', 'gain': -28}
POP = lambda at=0.3, g=-14: {'at': at, 'name': 'pop', 'gain': g}
WH = lambda at=0.0, g=-10: {'at': at, 'name': 'whoosh', 'gain': g}

PLAN = {
 's001': [(None, X('valley', 'Empty Valley of Elah at dusk, fog over the brook, slow push in', mode='empty', z=[1.0, 1.12], **{'in': {'type': 'fade', 'dur': 0.8}}, bars='scope', amb=AMB_FIELD))],
 's002': [(None, X('valley', "Wide 2D: Israel's army on the left hill, banners, camera drifts left", pan=[-260, -420], z=[1.05, 1.1], focus='israel', amb=AMB_ARMY))],
 's003': [(None, X('valley', 'Whip to the Philistine hill (right), plumed soldiers with spears; on "no meio" the empty middle', pan=[380, 0], z=[1.1, 1.0], focus='phil', **{'in': {'type': 'whip', 'dur': 0.3, 'dir': 1}}, sfx=[WH()]))],
 's004': [(None, X('goliath', 'Low-angle reveal of Goliath rising into frame, dimension line "≈ 2,9 m"', mode='reveal', bars='scope', sfx=[{'at': 0.0, 'name': 'riser', 'gain': -10}, {'at': 1.2, 'name': 'impact', 'gain': -6}]))],
 's005': [(None, X('camp', 'Israelite soldiers huddled behind rocks, scared, day counter ticks 1→40', soldiers='scared', counter=[1, 40], amb=AMB_ARMY, sfx=[{'at': 0.4, 'name': 'counter', 'gain': -14}]))],
 's006': [(None, X('pasture', 'Silhouette of a teenager walking along a ridge against the sunset', mode='ridgeWalk', amb=AMB_FIELD)),
          ('com', X('insert', 'Insert: a hand holding a sling, five smooth stones counted 1..5', obj='slingStones', sfx=[POP(0.6), POP(0.9), POP(1.2), POP(1.5), POP(1.8)]))],
 's007': [(None, X('title', 'Title card DAVI E GOLIAS over the valley at dusk', **{'in': {'type': 'fade', 'dur': 0.5}}, bars='scope', sfx=[{'at': 0.1, 'name': 'stinger', 'gain': -6}]))],
 's008': [(None, X('insert', "Insert: a children's storybook with a stick-figure drawing, pages turning", obj='book', sfx=[{'at': 0.5, 'name': 'swish', 'gain': -14}]))],
 's009': [(None, X('modern', 'Modern street at night: YOU standing before a giant shadow on a wall', mode='shadow', **{'in': {'type': 'whip', 'dur': 0.3}}, amb=AMB_CITY, sfx=[WH(), {'at': 0.8, 'name': 'stinger', 'gain': -10}]))],
 's010': [(None, X('bp', 'Blueprint timeline sliding to "≈ 1000 a.C."', mode='year', **{'in': {'type': 'dip', 'dur': 0.5}}, sfx=[{'at': 0.6, 'name': 'counter', 'gain': -14}])),
          ('israel', X('tent', 'King Saul standing tall in his royal tent, crown glowing, lamp light', mode='saulKing', amb=AMB_ROOM))],
 's011': [(None, X('camp', 'Saul in front of his soldiers, pointing to the battle; soldiers raise spears', mode='saulLead', soldiers='cheer', amb=AMB_ARMY))],
 's012': [(None, X('face', 'Close-up: Saul worried, the warm light fades to cold', who='saul', expr='worried', bg='tent', fade=True))],
 's013': [(None, X('house', 'Night: the prophet Samuel secretly pours oil from a horn over a kneeling youth', mode='secret', **{'in': {'type': 'dip', 'dur': 0.4}}, sfx=[{'at': 1.2, 'name': 'shimmer', 'gain': -12}]))],
 's014': [(None, X('pasture', 'Golden hills of Bethlehem: young shepherd David with staff among sheep', mode='shepherd', amb=AMB_FIELD))],
 's015': [(None, X('face', 'Close-up: David smiling, label DAVI', who='david', expr='smile', bg='pasture', label='DAVI', sfx=[POP(0.4)]))],
 's016': [(None, X('house', "Jesse's house at dusk: Samuel arrives at the lit doorway", mode='arrive', amb=AMB_FIELD)),
          ('olhou', X('house', 'Samuel looks up at the tall eldest son Eliabe', mode='eldest'))],
 's017': [(None, X('face', 'Close-up: Samuel pleased, then light from above (god rays) interrupts', who='samuel', expr='smile', bg='house', rays=1.6, sfx=[{'at': 1.6, 'name': 'shimmer', 'gain': -10}]))],
 's018': [(None, X('bp', 'Blueprint: tall figure with a height dimension, then crossed out', mode='appearance'))],
 's019': [(None, X('bp', 'Blueprint: an eye sees the outline; then a heart glows inside the figure', mode='eyeHeart', sfx=[{'at': 2.2, 'name': 'heartbeat', 'gain': -10}]))],
 's020': [(None, X('house', 'Sons pass one by one in front of Samuel', mode='lineup'))],
 's021': [(None, X('face', 'Close-up: Samuel confused, shaking his head', who='samuel', expr='confused', bg='house', shake=True))],
 's022': [(None, X('pasture', 'Far wide: tiny David alone among the sheep in the field', mode='far', amb=AMB_FIELD))],
 's023': [(None, X('pasture', 'David sitting alone on a rock at dusk, sheep grazing', mode='alone'))],
 's024': [(None, X('house', 'Samuel anoints David; god rays and sparkles', mode='anoint', **{'in': {'type': 'flash', 'dur': 0.3}}, sfx=[{'at': 0.2, 'name': 'shimmer', 'gain': -8}]))],
 's025': [(None, X('line', 'Glowing key icon + GUARDE ESTA FRASE', str='GUARDE ESTA FRASE', icon='key', sfx=[{'at': 0.3, 'name': 'ding', 'gain': -12}]))],
 's026': [(None, X('line', 'O HOMEM VÊ A APARÊNCIA with an eye icon', str='O HOMEM VÊ A APARÊNCIA', icon='eye'))],
 's027': [(None, X('line', 'DEUS VÊ O CORAÇÃO with a glowing heart', str='DEUS VÊ O CORAÇÃO', icon='heart', **{'in': {'type': 'flash', 'dur': 0.25}}, sfx=[{'at': 0.1, 'name': 'heartbeat', 'gain': -8}]))],
 's028': [(None, X('valley', 'Philistine column marching, plumed helmets and spears, storm sky', mode='march', focus='phil', mood='storm', pan=[0, 120], z=[1.25, 1.3], **{'in': {'type': 'dip', 'dur': 0.4}}, amb={'name': 'wind', 'gain': -24}, sfx=[{'at': 0.2, 'name': 'footstep', 'gain': -10}]))],
 's029': [(None, X('bp', 'Blueprint map: coastline, five fortified cities and an iron sword icon', mode='map', sfx=[POP(0.8), POP(1.6)]))],
 's030': [(None, X('bp', 'Map: arrow from the coast into the Valley of Elah', mode='march'))],
 's031': [(None, X('valley', 'Wide: two armies on opposite hills, the valley and brook between, slow pull out', mode='two', z=[1.12, 1.0], amb=AMB_ARMY))],
 's032': [(None, X('valley', 'Tense medium: both front lines, empty ground between, slight roll', focus='mid', z=[1.35, 1.45], roll=True))],
 's033': [(None, X('bp', 'Top-down diagram: the valley, a dotted path down, red zone EXPOSTO', mode='exposed', sfx=[{'at': 1.2, 'name': 'buzz', 'gain': -14}]))],
 's034': [(None, X('goliath', 'Goliath emerges from the Philistine tents and walks forward, ground shakes', mode='emerge', sfx=[{'at': 0.6, 'name': 'footstep', 'gain': -6}, {'at': 1.7, 'name': 'footstep', 'gain': -6}, {'at': 2.8, 'name': 'footstep', 'gain': -6}]))],
 's035': [(None, X('face', 'Close-up: Goliath in his bronze helmet, smirk; label GOLIAS · GATE', who='goliath', expr='smirk', bg='valley', label='GOLIAS · GATE', bars='scope', sfx=[POP(0.5)]))],
 's036': [(None, X('bp', 'Blueprint height chart: soldier vs Goliath, label 6 CÔVADOS + 1 PALMO', mode='height1', sfx=[POP(1.0)]))],
 's037': [(None, X('bp', 'Same chart: big dimension ≈ 2,9 m', mode='height2', sfx=[{'at': 0.2, 'name': 'impact', 'gain': -10}]))],
 's038': [(None, X('insert', 'Insert: bronze helmet and scale armour glinting', obj='armor', sfx=[{'at': 0.5, 'name': 'shimmer', 'gain': -14}])),
          ('que', X('bp', 'Readout: scale weighing the armour, counter to ≈ 57 kg', mode='kg57', sfx=[{'at': 0.3, 'name': 'counter', 'gain': -14}]))],
 's039': [(None, X('insert', 'Insert: the iron spearhead, readout ≈ 7 kg', obj='spear', sfx=[{'at': 1.6, 'name': 'blip', 'gain': -12}]))],
 's040': [(None, X('goliath', 'Shield-bearer walks ahead with the big shield; Goliath behind raises his spear', mode='bearer', sfx=[{'at': 2.4, 'name': 'stinger', 'gain': -10}]))],
 's041': [(None, X('face', 'Close-up: Goliath shouting the challenge', who='goliath', expr='angry', bg='valley', talk=True, bars='scope'))],
 's042': [(None, X('goliath', 'Goliath points at himself, talking', mode='talkSelf', talk=True))],
 's043': [(None, X('goliath', 'Low angle: Goliath points at Israel, talking', mode='talkPoint', talk=True))],
 's044': [(None, X('face', 'Giant close-up: Goliath roaring, shake + rings', who='goliath', expr='shocked', bg='valley', talk=True, roar=True, bars='scope', sfx=[{'at': 0.2, 'name': 'impact', 'gain': -8}]))],
 's045': [(None, X('camp', 'Saul among his soldiers, all turned toward the valley, listening', mode='saulListen', soldiers='idle', amb=AMB_ARMY))],
 's046': [(None, X('camp', 'Soldiers terrified: hands on heads, stepping back', soldiers='scared', z=[1.15, 1.25]))],
 's047': [(None, X('goliath', 'Time-lapse: Goliath silhouette shouting as the sun crosses from morning to evening', mode='timelapse', sfx=[{'at': 0.2, 'name': 'clock', 'gain': -16}]))],
 's048': [(None, X('bp', 'Day counter racing to 40 with sun/moon cycling', mode='days', sfx=[{'at': 0.1, 'name': 'counter', 'gain': -12}]))],
 's049': [(None, X('pasture', 'Bethlehem fields, golden: David with his staff watches the sheep', mode='shepherd', **{'in': {'type': 'dip', 'dur': 0.5}}, amb=AMB_FIELD))],
 's050': [(None, X('camp', "David's three older brothers in the army line, Eliabe in blue, labels", mode='brothers', soldiers='idle'))],
 's051': [(None, X('house', 'Jesse at the door talking to David', mode='jesse', talk=True))],
 's052': [(None, X('insert', 'Insert: a sack of roasted grain and ten loaves counted', obj='bread', sfx=[{'at': 1.2, 'name': 'counter', 'gain': -16}]))],
 's053': [(None, X('insert', 'Insert: ten cheeses, then David takes the bundle', obj='cheese', sfx=[POP(0.6)]))],
 's054': [(None, X('camp', 'David arrives at the Israelite camp with a sack on his shoulder', mode='arrive', **{'in': {'type': 'whip', 'dur': 0.3}}, sfx=[WH()], amb=AMB_ARMY)),
          ('bem', X('valley', 'The army rushes out shouting toward the battle line', mode='rush', focus='israel', pan=[-200, -60], z=[1.2, 1.25], sfx=[{'at': 0.2, 'name': 'cheer', 'gain': -12}]))],
 's055': [(None, X('camp', 'David runs between the tents to his brothers', mode='run', sfx=[{'at': 0.1, 'name': 'footstep', 'gain': -12}]))],
 's056': [(None, X('goliath', 'Goliath climbs onto a rock in the valley and shouts again', mode='rock', talk=True))],
 's057': [(None, X('camp', 'Soldiers flee past David, who stands still', mode='flee', soldiers='flee', sfx=[WH(0.3, -12)]))],
 's058': [(None, X('camp', 'Two soldiers whisper, David listens', mode='whisper'))],
 's059': [(None, X('insert', 'Insert: a pile of glowing treasure: coins and jewels', obj='coins', sfx=[{'at': 0.4, 'name': 'shimmer', 'gain': -12}]))],
 's060': [(None, X('bp', "Icon: crown + ring — the king's daughter in marriage", mode='iconRing', sfx=[POP(0.4)])),
          ('e', X('bp', 'Icon: tax scroll stamped ISENTO', mode='iconTax', sfx=[{'at': 0.9, 'name': 'hit', 'gain': -12}])),
          ('davi', X('face', 'Close-up: David determined', who='david', expr='determined', bg='camp'))],
 's061': [(None, X('camp', 'David talks to the soldiers, pointing toward the valley', mode='davidAsks', talk=True))],
 's062': [(None, X('face', 'Close-up: Eliabe furious', who='eliabe', expr='angry', bg='camp')),
          ('por', X('camp', 'Two-shot: Eliabe points at David, talking', mode='eliabe', talk=True))],
 's063': [(None, X('pasture', 'Cutaway: a few lonely sheep in the desert', mode='few', amb=AMB_FIELD))],
 's064': [(None, X('camp', 'Over-the-shoulder: Eliabe big blurred foreground, David sharp', mode='ots', talk=True))],
 's065': [(None, X('camp', 'Eliabe arms crossed, still talking', mode='eliabeCross', talk=True)),
          ('davi', X('camp', 'David shrugs and answers', mode='davidShrug', talk=True))],
 's066': [(None, X('face', 'Close-up: David, calm, talking', who='david', expr='neutral', bg='camp', talk=True))],
 's067': [(None, X('modern', 'Modern home doorway: YOU with a backpack, a family silhouette arms crossed in the door', mode='home', amb=AMB_ROOM))],
 's068': [(None, X('tent', "Outside the king's tent: a soldier hurries in", mode='messenger', amb=AMB_ARMY))],
 's069': [(None, X('tent', 'Inside: David is brought before seated Saul', mode='enter', amb=AMB_ROOM))],
 's070': [(None, X('tent', 'David talks to Saul with open hands', mode='davidTalk', talk=True))],
 's071': [(None, X('face', 'Close-up: David determined, talking', who='david', expr='determined', bg='tent', talk=True))],
 's072': [(None, X('tent', 'Saul shakes his head and talks', mode='saulNo', talk=True))],
 's073': [(None, X('bp', 'Blueprint compare: RAPAZ vs GUERREIRO experience bars', mode='compare', sfx=[POP(0.6), POP(1.2)]))],
 's074': [(None, X('pasture', 'Flashback at night: a lion grabs a lamb from the flock', mode='lion', **{'in': {'type': 'dip', 'dur': 0.4}}, sfx=[{'at': 1.2, 'name': 'stinger', 'gain': -10}]))],
 's075': [(None, X('pasture', 'Flashback: David runs at the lion with his staff and rescues the lamb', mode='rescue', sfx=[{'at': 1.6, 'name': 'hit', 'gain': -8}]))],
 's076': [(None, X('pasture', 'Flashback: a bear rears up; David stands his ground', mode='bear', sfx=[{'at': 0.8, 'name': 'impact', 'gain': -10}]))],
 's077': [(None, X('tent', 'David points out toward the valley; Saul listens', mode='davidPoint', talk=True))],
 's078': [(None, X('tent', 'David points up; rays of light through the tent opening', mode='pointUp', talk=True, sfx=[{'at': 2.5, 'name': 'shimmer', 'gain': -12}]))],
 's079': [(None, X('bp', 'Blueprint: strength meter stays low', mode='strength'))],
 's080': [(None, X('face', 'Close-up: David eyes closed, memories (lion, bear) float around', who='david', expr='sleepy', bg='tent', memories=True))],
 's081': [(None, X('tent', "Saul dresses David in the king's armour", mode='armor'))],
 's082': [(None, X('insert', 'Insert: helmet, breastplate and sword pop in with labels', obj='armorPieces', sfx=[POP(0.2), POP(0.9), POP(1.6)])),
          ('davi', X('tent', 'David wobbles in the oversized armour and stops', mode='wobble', sfx=[{'at': 0.8, 'name': 'hit', 'gain': -14}]))],
 's083': [(None, X('face', 'Close-up: David, helmet slipping over his eyes, talking', who='david', expr='worried', bg='tent', talk=True, helmet=True)),
          ('e', X('tent', 'The armour pieces drop to the floor', mode='drop', sfx=[{'at': 0.3, 'name': 'hit', 'gain': -8}]))],
 's084': [(None, X('bp', 'Blueprint: copy of Saul’s outline crossed out', mode='copy'))],
 's085': [(None, X('pasture', 'David slings at a target in the field, the stone hits', mode='practice', sfx=[{'at': 1.2, 'name': 'swish', 'gain': -10}]))],
 's086': [(None, X('brook', 'David crouches at the brook choosing five smooth stones', amb={'name': 'rain', 'gain': -32}))],
 's087': [(None, X('insert', 'Insert: stones dropping into the leather shepherd’s bag', obj='pouch', sfx=[{'at': 0.5, 'name': 'tick', 'gain': -12}, {'at': 1.0, 'name': 'tick', 'gain': -12}]))],
 's088': [(None, X('insert', 'Insert: the sling hanging from his hand, swaying', obj='sling'))],
 's089': [(None, X('valley', 'Wide: tiny David walks down toward huge Goliath', mode='approach', focus='mid', bars='scope', amb=AMB_ARMY))],
 's090': [(None, X('bp', 'Blueprint: the sling drawn as a weapon, label ARMA', mode='slingWeapon'))],
 's091': [(None, X('bp', 'Blueprint: a row of ancient slingers', mode='slingers'))],
 's092': [(None, X('bp', 'Blueprint: dotted trajectory hits a single hair; label JUÍZES 20:16', mode='hair', sfx=[{'at': 3.6, 'name': 'ding', 'gain': -12}]))],
 's093': [(None, X('bp', 'Blueprint: whirling sling, speed counter to 100+ km/h', mode='speed', sfx=[{'at': 0.3, 'name': 'riser', 'gain': -14}, {'at': 2.8, 'name': 'whoosh', 'gain': -8}]))],
 's094': [(None, X('pasture', 'Night field under stars: David alone with the sheep', mode='night', amb=AMB_FIELD))],
 's095': [(None, X('pasture', 'Montage: David slinging day after day, sun cycling, day counter', mode='montage'))],
 's096': [(None, X('pasture', 'Wide: light from the sky falls on David practising alone', mode='seen', sfx=[{'at': 1.4, 'name': 'shimmer', 'gain': -12}]))],
 's097': [(None, X('valley', 'Face-off: Goliath looks down at small David', mode='faceoff', focus='mid', bars='scope'))],
 's098': [(None, X('goliath', 'Over Goliath’s shoulder: small David sharp, label RUIVO', mode='otsDavid', sfx=[POP(0.6)]))],
 's099': [(None, X('face', 'Close-up: Goliath sneering, talking', who='goliath', expr='angry', bg='valley', talk=True))],
 's100': [(None, X('goliath', 'Goliath raises a fist to the dark sky, lightning far away', mode='curse', sfx=[{'at': 1.0, 'name': 'thunder', 'gain': -10}]))],
 's101': [(None, X('goliath', 'Goliath points at David; vultures circle overhead', mode='vultures', talk=True, sfx=[{'at': 0.5, 'name': 'wind', 'gain': -20, 'dur': 4}]))],
 's102': [(None, X('face', 'Close-up: David determined, slow push, wind', who='david', expr='determined', bg='valley', bars='scope', sfx=[{'at': 1.5, 'name': 'riser', 'gain': -12}]))],
 's103': [(None, X('valley', 'David talks; sword, spear and shield icons pop over Goliath', mode='weapons', focus='mid', talk=True, sfx=[POP(0.6), POP(1.5), POP(2.4)]))],
 's104': [(None, X('valley', 'David points up; god rays break through the clouds', mode='davidUp', focus='mid', talk=True, sfx=[{'at': 0.8, 'name': 'shimmer', 'gain': -10}]))],
 's105': [(None, X('valley', 'Israel’s army watching from the hill', mode='watchIsr', focus='israel'))],
 's106': [(None, X('valley', 'Wide: both armies watching; David small in the middle facing Goliath', mode='watch', focus='mid', talk=True, z=[1.0, 1.06]))],
 's107': [(None, X('line', 'A BATALHA É DO SENHOR over David backlit by the sun', str='A BATALHA É DO SENHOR', icon='david', bars='scope', sfx=[{'at': 0.2, 'name': 'stinger', 'gain': -6}]))],
 's108': [(None, X('goliath', 'Goliath starts walking forward, heavy steps, shake', mode='advance', sfx=[{'at': 0.3, 'name': 'footstep', 'gain': -6}, {'at': 1.1, 'name': 'footstep', 'gain': -6}])),
          ('e', X('valley', 'David breaks into a run, speed lines', mode='davidRun', focus='mid', sfx=[{'at': 0.6, 'name': 'whoosh', 'gain': -8}])),
          ('não', X('valley', 'Side wide: David running TOWARD Goliath, the gap closing', mode='closing', focus='mid', sfx=[{'at': 0.2, 'name': 'footstep', 'gain': -10}]))],
 's109': [(None, X('insert', 'Insert: hand pulls one stone from the bag', obj='handStone', sfx=[{'at': 0.6, 'name': 'tick', 'gain': -10}])),
          ('girou', X('insert', 'Insert: the sling whirling, motion rings', obj='whirl', sfx=[{'at': 0.0, 'name': 'swish', 'gain': -8}, {'at': 0.5, 'name': 'swish', 'gain': -8}, {'at': 1.0, 'name': 'swish', 'gain': -8}])),
          ('e', X('freeze', 'FREEZE: the stone hangs in mid-air between David and Goliath', **{'in': {'type': 'flash', 'dur': 0.3}}, bars='scope', sfx=[{'at': 0.0, 'name': 'freeze', 'gain': -6}, {'at': 0.1, 'name': 'slowmo', 'gain': -10}]))],
 's110': [(None, X('face', 'Close-up: Goliath shocked as the stone strikes his forehead, flash + shake', who='goliath', expr='shocked', bg='valley', hit=True, sfx=[{'at': 0.15, 'name': 'impact', 'gain': -3}]))],
 's111': [(None, X('goliath', 'The giant falls face down, dust cloud', mode='fall', sfx=[{'at': 1.7, 'name': 'impact', 'gain': -4}]))],
 's112': [(None, X('valley', 'Backlit silhouette: David lifts the giant’s sword against the sunset (no gore)', mode='sword', focus='mid', bars='scope', sfx=[{'at': 1.5, 'name': 'stinger', 'gain': -8}]))],
 's113': [(None, X('valley', 'The Philistines flee to the right', mode='philFlee', focus='phil', pan=[200, 420], sfx=[{'at': 0.3, 'name': 'murmur', 'gain': -14, 'dur': 3}]))],
 's114': [(None, X('valley', 'Israel’s army rises and charges, cheering', mode='charge', focus='israel', pan=[-300, 100], sfx=[{'at': 0.3, 'name': 'cheer', 'gain': -8}]))],
 's115': [(None, X('line', 'Question on a calm sky: O QUE ESSA HISTÓRIA ENSINA?', str='O QUE ESSA HISTÓRIA ENSINA?', icon='none', **{'in': {'type': 'dip', 'dur': 0.6}}))],
 's116': [(None, X('lesson', 'Lesson 1: Goliath silhouette, unchanged', n=1, mode='giant', sfx=[POP(0.2)]))],
 's117': [(None, X('face', 'Close-up: David looking up', who='david', expr='awe', bg='valley', look=[0.3, -0.9]))],
 's118': [(None, X('bp', 'Blueprint: soldiers’ eyes fixed on the giant (arrows)', mode='look1'))],
 's119': [(None, X('bp', 'Blueprint: David looks up to an immense light; the giant is tiny', mode='look2'))],
 's120': [(None, X('lesson', 'Lesson 2: hidden place — night field', n=2, mode='hidden', sfx=[POP(0.2)]))],
 's121': [(None, X('pasture', 'Empty field: lion and bear shadows, no audience', mode='noAudience')),
          ('foram', X('bp', 'Diagram: arrow from FIELD to VALLEY', mode='fieldToValley'))],
 's122': [(None, X('lesson', 'Lesson 3: the king’s armour lying on the floor', n=3, mode='armor', sfx=[POP(0.2)]))],
 's123': [(None, X('insert', 'Insert: hand with sling and stone, glowing', obj='handGlow'))],
 's124': [(None, X('lesson', 'Lesson 4: one victory lifts a whole people', n=4, mode='people', sfx=[POP(0.2), {'at': 1.0, 'name': 'cheer', 'gain': -16}]))],
 's125': [(None, X('modern', 'YOU walk forward; people behind stand up one by one', mode='others', amb=AMB_CITY))],
 's126': [(None, X('modern', 'YOU facing a towering shadow giant', mode='giant')),
          ('medo', X('modern', 'Words appear on the giant: MEDO, DOENÇA, DÍVIDA, ANSIEDADE, VÍCIO', mode='words', sfx=[{'at': 0.1, 'name': 'hit', 'gain': -12}]))],
 's127': [(None, X('modern', 'The shadow giant roars at YOU, badge 40 DIAS', mode='shout', sfx=[{'at': 0.3, 'name': 'impact', 'gain': -12}]))],
 's128': [(None, X('face', 'Close-up: YOU looking up, hope', who='you', expr='awe', bg='modern', look=[0.2, -0.8]))],
 's129': [(None, X('line', 'A BATALHA É DO SENHOR (callback)', str='A BATALHA É DO SENHOR', icon='david', bars='scope', sfx=[{'at': 0.1, 'name': 'shimmer', 'gain': -10}]))],
 's130': [(None, X('modern', 'YOU small in front of the giant, but smiling', mode='small'))],
 's131': [(None, X('lesson', 'The heavy armour on the floor (callback)', n=0, mode='armor'))],
 's132': [(None, X('valley', 'Golden Valley of Elah, the young shepherd standing alone by the brook', mode='golden', mood='golden', z=[1.3, 1.4]))],
 's133': [(None, X('bp', 'Glowing heart inside a figure (callback)', mode='heart', sfx=[{'at': 0.2, 'name': 'heartbeat', 'gain': -10}]))],
 's134': [(None, X('pasture', 'Night field, stars: David alone with his sheep (callback)', mode='night'))],
 's135': [(None, X('insert', 'Insert: a modern hand picks up smooth stones', obj='modernStones', sfx=[{'at': 0.8, 'name': 'tick', 'gain': -12}]))],
 's136': [(None, X('insert', 'Insert: hand with the glowing sling', obj='handGlow', sfx=[{'at': 0.3, 'name': 'shimmer', 'gain': -12}]))],
 's137': [(None, X('modern', 'YOU walk toward the shadow giant', mode='approach')),
          ('não', X('modern', 'YOU keep walking; dawn light rises and the shadow shrinks', mode='dawn', sfx=[{'at': 0.5, 'name': 'riser', 'gain': -12}]))],
 's138': [(None, X('line', 'Final: A BATALHA É DO SENHOR at sunrise', str='A BATALHA É DO SENHOR', icon='sunrise', bars='scope', sfx=[{'at': 0.1, 'name': 'stinger', 'gain': -6}]))],
 's139': [(None, X('end', 'End screen: question, subscribe and the cast', **{'in': {'type': 'fade', 'dur': 0.5}}))],
 's140': [(None, X('end', 'End screen continues', cont=True))],
}

MUSIC = [
 (0, 19.87, 'mystery', 0.35), (19.87, 28.55, 'epic', 0.5), (28.55, 51.81, 'mystery', 0.3), (51.81, 87.17, 'wonder', 0.4),
 (87.17, 130.17, 'tension', 0.55), (130.17, 154.83, 'dark', 0.65), (154.83, 170.89, 'hopeful', 0.3), (170.89, 200.73, 'tension', 0.5),
 (200.73, 239.91, 'tension', 0.35), (239.91, 264.59, 'action', 0.45), (264.59, 285.01, 'playful', 0.3), (285.01, 323.15, 'wonder', 0.4),
 (323.15, 361.63, 'epic', 0.6), (361.63, 378.37, 'action', 0.9), (378.37, 392.31, 'triumph', 0.85), (392.31, 431.89, 'hopeful', 0.35),
 (431.89, 443.93, 'dark', 0.35), (443.93, 472.49, 'triumph', 0.55), (472.49, 482.7, 'calm', 0.3),
]

def split_time(a, b, first):
    f = norm(first)
    for w in words:
        if a + 0.2 < w['start'] < b - 0.2 and norm(w['word']).startswith(f):
            return round(max(a + 0.4, w['start'] - 0.15), 2)
    raise SystemExit(f'split word {first!r} not found in {a}-{b}')

out = []
for s in draft['shots']:
    parts = PLAN[s['id']]
    times = [s['start']] + [split_time(s['start'], s['end'], fw) for fw, _ in parts[1:]] + [s['end']]
    for i, (fw, pl) in enumerate(parts):
        pl = dict(pl); sid = s['id'] + ('abcdef'[i] if len(parts) > 1 else '')
        a, b = times[i], times[i + 1]
        wl = [w['word'] for w in words if a - 0.05 <= w['start'] < b - 0.05]
        sh = {'id': sid, 'start': a, 'end': b, 'line': ' '.join(wl) or s['line'], 'scene': pl.pop('scene'), 'set': pl.get('k'),
              'bars': pl.pop('bars', None), 'in': pl.pop('in', {'type': 'cut'}), 'sfx': pl.pop('sfx', []), 'notes': ''}
        if 'amb' in pl: sh['amb'] = pl.pop('amb')
        sh['params'] = pl
        out.append(sh)
for i in range(1, len(out)): assert abs(out[i]['start'] - out[i - 1]['end']) < 1e-6, out[i]['id']
story = {'title': draft['title'], 'duration': draft['duration'], 'shots': out,
         'music': [{'start': a, 'end': b, 'mood': m, 'intensity': k} for a, b, m, k in MUSIC]}
json.dump(story, open(os.path.join(P, 'story', 'shots.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
d = [s['end'] - s['start'] for s in out]; d.sort()
print(len(out), 'shots; median', round(d[len(d) // 2], 2), 'min', round(d[0], 2), 'max', round(d[-1], 2))
from collections import Counter; print(Counter(s['params']['k'] for s in out))
