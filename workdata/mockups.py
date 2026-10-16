from PIL import Image, ImageDraw, ImageFont, ImageOps
import os, sys
G = '/home/user/pret/pokefirered/graphics/'
SP = sys.argv[1]
F = lambda s, b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), s)

def load(path, frame=0, size=None, scale=1, flip=False):
    im = Image.open(path).convert('RGBA')
    if im.height > im.width:  # sprite sheet of square frames
        im = im.crop((0, frame * im.width, im.width, (frame + 1) * im.width))
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    if flip:
        im = ImageOps.mirror(im)
    return im

def chibi(scale=3, flip=False):
    im = Image.open(os.path.join(SP, 'innes_chibi.png')).convert('RGBA')
    key = im.getpixel((0, 0))
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][:3] == key[:3]:
                px[x, y] = (0, 0, 0, 0)
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    return ImageOps.mirror(im) if flip else im

def canvas(title, sub):
    W, H = 960, 600
    bg = Image.new('RGBA', (W, H), (236, 244, 230, 255))
    d = ImageDraw.Draw(bg)
    d.rectangle([0, 0, W, 62], fill=(40, 52, 70, 255))
    d.text((24, 12), title, font=F(26, True), fill=(255, 255, 255, 255))
    d.text((24, 40), sub, font=F(14), fill=(200, 210, 225, 255))
    d.ellipse([560, 250, 940, 340], fill=(190, 214, 176, 255))   # enemy ground
    d.ellipse([40, 380, 420, 480], fill=(190, 214, 176, 255))    # player ground
    d.text((24, H - 36), 'MOCKUP for comparison. Sprites are scaled. Not rendered from the ROM.', font=F(13), fill=(60, 60, 60, 255))
    return bg, d

def box(d, xy, name, lvl):
    x, y = xy
    d.rounded_rectangle([x, y, x + 300, y + 62], radius=8, fill=(255, 255, 255, 255), outline=(40, 52, 70, 255), width=2)
    d.text((x + 14, y + 10), name, font=F(18, True), fill=(30, 30, 30, 255))
    sub = 'Trainer' if lvl is None else 'Lv %d   HP ██████████' % lvl
    d.text((x + 14, y + 36), sub, font=F(14), fill=(30, 30, 30, 255))

def paste(bg, im, xy):
    bg.alpha_composite(im, dest=xy)

def enemy_rattata(bg):
    paste(bg, load(G + 'pokemon/rattata/front.png', scale=3), (640, 130))

def idea1():
    bg, d = canvas('Idea 1: FE8 art as Pokemon sprite', 'Innes is a party Pokemon; battle art is FE8 art')
    enemy_rattata(bg)
    paste(bg, chibi(scale=4, flip=True), (150, 230))
    box(d, (40, 90), 'Rattata', 12)
    box(d, (600, 400), 'INNES', 10)
    d.text((24, 510), 'Player-side view = mirrored FE8 chibi art (placeholder for the back sprite)', font=F(13), fill=(60, 60, 60, 255))
    return bg

def idea2():
    bg, d = canvas('Idea 2: trainer portraits as battle sprites', 'Innes is a party Pokemon; battle art is her trainer portrait')
    enemy_rattata(bg)
    paste(bg, chibi(scale=4), (150, 230))
    box(d, (40, 90), 'Rattata', 12)
    box(d, (600, 400), 'INNES', 10)
    d.text((24, 510), 'Portrait (FE8 chibi) used for front and back. Back view is a placeholder.', font=F(13), fill=(60, 60, 60, 255))
    return bg

def idea3():
    bg, d = canvas('Idea 3: standard Pokemon art', 'Innes is a Fearow; battle art is Fearow front/back')
    enemy_rattata(bg)
    paste(bg, load(G + 'pokemon/fearow/back.png', scale=3), (150, 230))
    box(d, (40, 90), 'Rattata', 12)
    box(d, (600, 400), 'INNES', 10)
    d.text((24, 510), 'Fearow back sprite (species-based art, not FE8 art)', font=F(13), fill=(60, 60, 60, 255))
    return bg

def idea4():
    bg, d = canvas('Idea 4: allied trainers in doubles', '2 allies vs 2 enemies. Trainers send out their own Pokemon.')
    paste(bg, load(G + 'trainers/front_pics/lass_front_pic.png', scale=3), (700, 90))
    paste(bg, load(G + 'trainers/front_pics/youngster_front_pic.png', scale=3), (560, 230))
    paste(bg, load(G + 'trainers/back_pics/leaf_back_pic.png', frame=0, scale=3), (110, 210))
    paste(bg, chibi(scale=3), (300, 290))
    box(d, (40, 90), 'EIRIKA', None)
    box(d, (600, 70), 'Lass', None)
    box(d, (600, 380), 'Youngster', None)
    d.text((24, 510), 'Doubles: Eirika (Leaf back pic) and Innes (chibi placeholder) vs two trainers', font=F(13), fill=(60, 60, 60, 255))
    return bg

for n, fn in [('idea1', idea1), ('idea2', idea2), ('idea3', idea3), ('idea4', idea4)]:
    im = fn().convert('RGB')
    im.save(os.path.join(SP, n + '.png'))
    print(os.path.join(SP, n + '.png'), im.size)
