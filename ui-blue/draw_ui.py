"""Blue storybook UI, drawn at Minecraft's native GUI pixel resolution."""
from pathlib import Path
import json
import shutil
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'ui-blue'
PACKS = ('Generic RP', 'Parks RP')
P = {
 'ink':'#152c49', 'edge':'#244768', 'blue':'#3c6b91',
 'rim':'#6c9cb9', 'panel':'#527b98', 'label':'#b1ccdc',
 'label_edge':'#8cadc4', 'slot':'#384d61', 'slot_top':'#263b50',
 'slot_light':'#7895aa', 'sky':'#67c4ef', 'ice':'#b5edff',
 'gold':'#dfb75c', 'gold_light':'#ffe4a0', 'cream':'#fff0c9',
}

def blank(w,h): return Image.new('RGBA',(w,h))

def panel(im, box, fill, edge=None, rim=None):
    x0,y0,x1,y1=box
    d=ImageDraw.Draw(im)
    # One-pixel cut corners, then a crisp inner bevel.
    d.polygon([(x0+1,y0),(x1-1,y0),(x1,y0+1),(x1,y1-1),
               (x1-1,y1),(x0+1,y1),(x0,y1-1),(x0,y0+1)],fill=edge or P['ink'])
    d.rectangle((x0+1,y0+1,x1-1,y1-1),fill=fill)
    d.line((x0+2,y0+1,x1-2,y0+1),fill=rim or P['rim'])
    d.line((x0+1,y0+2,x0+1,y1-2),fill=rim or P['rim'])
    d.line((x0+2,y1-1,x1-1,y1-1),fill=P['edge'])
    d.line((x1-1,y0+2,x1-1,y1-1),fill=P['edge'])

def slot(im,x,y):
    d=ImageDraw.Draw(im)
    d.rectangle((x,y,x+17,y+17),fill=P['slot_top'])
    # The full 16x16 item region is flat and unobstructed.
    d.rectangle((x+1,y+1,x+16,y+16),fill=P['slot'])
    d.line((x,y+17,x+17,y+17),fill=P['slot_light'])
    d.line((x+17,y,x+17,y+17),fill=P['slot_light'])

def chest():
    im=blank(256,256)
    panel(im,(0,0,175,221),P['panel'])
    d=ImageDraw.Draw(im)
    # Continuous vertical borders permit Minecraft's 1-6-row crop/reassembly.
    d.rectangle((3,3,172,16),fill=P['label'])
    d.line((4,3,171,3),fill='#d0e3ed')
    d.line((3,16,172,16),fill=P['label_edge'])
    d.rectangle((3,126,172,138),fill=P['label'])
    d.line((3,126,172,126),fill=P['label_edge'])
    d.line((3,138,172,138),fill=P['label_edge'])
    for row in range(6):
        for col in range(9): slot(im,7+18*col,17+18*row)
    for row in range(3):
        for col in range(9): slot(im,7+18*col,139+18*row)
    for col in range(9): slot(im,7+18*col,197)
    # Tiny book-cover corners: gold remains outside text and item regions.
    for x,sign in [(2,1),(173,-1)]:
        d.line((x,2,x+sign*4,2),fill=P['gold_light'])
        d.line((x,2,x,6),fill=P['gold'])
        d.line((x,219,x+sign*4,219),fill=P['gold'])
        d.line((x,215,x,219),fill=P['gold'])
    d.line((8,195,167,195),fill=P['edge'])
    return im

def hotbar():
    im=blank(182,22)
    panel(im,(0,0,181,21),P['edge'],rim=P['rim'])
    d=ImageDraw.Draw(im)
    for i in range(9):
        x=3+20*i
        d.rectangle((x,3,x+15,18),fill=(29,48,68,210))
        d.line((x-1,2,x+16,2),fill=P['ink'])
        d.line((x-1,2,x-1,19),fill=P['ink'])
        d.line((x,19,x+16,19),fill=P['blue'])
    return im

def selection():
    im=blank(24,23);d=ImageDraw.Draw(im)
    d.rectangle((0,0,23,22),outline=P['ink'])
    d.rectangle((1,1,22,21),outline=P['sky'])
    d.rectangle((2,2,21,20),outline=P['ice'])
    # Match vanilla's 16x16 unobstructed item window at (4,4).
    d.line((3,3,20,3),fill=P['sky'])
    d.line((3,3,3,19),fill=P['sky'])
    for x,y,sx,sy in [(1,1,1,1),(22,1,-1,1),(1,21,1,-1),(22,21,-1,-1)]:
        d.line((x,y,x+sx*2,y),fill=P['gold_light'])
        d.line((x,y,x,y+sy*2),fill=P['gold'])
    return im

def offhand(right=False):
    im=blank(29,24)
    panel(im,(0,1,21,22),P['edge'])
    ImageDraw.Draw(im).rectangle((3,4,18,19),fill=(29,48,68,210))
    return ImageOps.mirror(im) if right else im

def button(state,w=200,h=20):
    im=blank(w,h)
    colors={
        'normal':('#305c83','#719db9','#183c60'),
        'highlighted':('#3f83b0','#b5edff','#24597f'),
        'disabled':('#394e60','#62788b','#2d4051'),
    }
    face,light,dark=colors[state]
    panel(im,(0,0,w-1,h-1),face,rim=light)
    d=ImageDraw.Draw(im)
    d.line((2,h-3,w-3,h-3),fill=dark)
    if state=='highlighted':
        # Decorative pixels are contained in the 3px nine-slice corners.
        for x in [1,w-2]:
            d.point((x,1),fill=P['gold_light'])
            d.point((x,h-2),fill=P['gold'])
    return im

def assets():
    a={'container/generic_54.png':chest(),
       'sprites/hud/hotbar.png':hotbar(),
       'sprites/hud/hotbar_selection.png':selection(),
       'sprites/hud/hotbar_offhand_left.png':offhand(),
       'sprites/hud/hotbar_offhand_right.png':offhand(True)}
    for state,suffix in [('normal',''),('highlighted','_highlighted'),('disabled','_disabled')]:
        a[f'sprites/widget/button{suffix}.png']=button(state)
    return a

# Preview-only 5x7 bitmap lettering. No labels are baked into runtime textures.
FONT={
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['111','010','010','010','010','010','111'],
'J':['00111','00010','00010','00010','10010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
' ':['000']*7,'/':['00001','00010','00100','01000','10000','00000','00000'],
}

def text_width(text):return sum(len(FONT[c][0])+1 for c in text.upper())-1

def text(im,xy,label,color=P['cream'],shadow=False):
    if shadow:text(im,(xy[0]+1,xy[1]+1),label,'#14283d')
    x,y=xy;d=ImageDraw.Draw(im)
    for c in label.upper():
        rows=FONT[c]
        for j,row in enumerate(rows):
            for i,bit in enumerate(row):
                if bit=='1':d.point((x+i,y+j),fill=color)
        x+=len(rows[0])+1

def assembled_chest(atlas,rows):
    height=rows*18+114
    im=blank(176,height)
    top=rows*18+17
    im.alpha_composite(atlas.crop((0,0,176,top)),(0,0))
    im.alpha_composite(atlas.crop((0,126,176,222)),(0,top))
    return im

def item(name):
    return Image.open(ROOT/f'Generic RP/assets/magicaldreams/textures/item/menu/{name}.png').convert('RGBA').resize((16,16),Image.Resampling.NEAREST)

def nine_slice(source,width,height,border=3):
    dest=blank(width,height);sw,sh=source.size
    xs=[0,border,sw-border,sw];ys=[0,border,sh-border,sh]
    xd=[0,border,width-border,width];yd=[0,border,height-border,height]
    for r in range(3):
        for c in range(3):
            tile=source.crop((xs[c],ys[r],xs[c+1],ys[r+1]))
            w,h=xd[c+1]-xd[c],yd[r+1]-yd[r]
            # Vanilla tiles the center and the edges; corners remain fixed.
            for y in range(0,h,tile.height):
                for x in range(0,w,tile.width):
                    piece=tile.crop((0,0,min(tile.width,w-x),min(tile.height,h-y)))
                    dest.alpha_composite(piece,(xd[c]+x,yd[r]+y))
    return dest

def preview(a):
    sheet=Image.new('RGBA',(450,330),'#12243a')
    text(sheet,(14,13),'MAGICALDREAMS / BLUE STORYBOOK',P['ice'])
    text(sheet,(14,29),'CHEST MENU',P['rim'])
    chest_im=assembled_chest(a['container/generic_54.png'],6)
    text(chest_im,(8,6),'MAGICALDREAMS','#404040')
    text(chest_im,(8,128),'INVENTORY','#404040')
    for col,name in zip([1,3,5,7],['hub','disneyland','walt_disney_world','creative']):
        chest_im.alpha_composite(item(name),(8+col*18,18+18))
    for col,name in [(0,'back'),(3,'refresh'),(5,'close'),(8,'next')]:
        chest_im.alpha_composite(item(name),(8+col*18,18+5*18))
    sheet.alpha_composite(chest_im,(14,43))
    text(sheet,(212,29),'BUTTON STATES',P['rim'])
    for y,state,suffix,label in [(47,'normal','','NORMAL'),(81,'highlighted','_highlighted','HIGHLIGHTED'),(115,'disabled','_disabled','DISABLED')]:
        b=nine_slice(a[f'sprites/widget/button{suffix}.png'],220,20)
        text(b,((220-text_width(label))//2,6),label,'#a0a0a0' if state=='disabled' else P['cream'],True)
        sheet.alpha_composite(b,(212,y))
    text(sheet,(212,153),'COMPACT BUTTONS',P['rim'])
    for x,state,suffix,label in [(212,'normal','','BACK'),(284,'normal','','NEXT'),(356,'highlighted','_highlighted','PLAY')]:
        b=nine_slice(a[f'sprites/widget/button{suffix}.png'],66,20)
        text(b,((66-text_width(label))//2,6),label,P['cream'],True)
        sheet.alpha_composite(b,(x,168))
    text(sheet,(212,211),'NAVIGATION',P['rim'])
    for x,name in zip([218,269,320,371],['back','next','close','refresh']):
        sprite=Image.open(ROOT/f'menu-icons/source/{name}-grid.png').convert('RGBA')
        sheet.alpha_composite(sprite,(x,228))
    text(sheet,(14,281),'HOTBAR / SELECTED SLOT',P['rim'])
    bar=a['sprites/hud/hotbar.png'].copy()
    for i,n in enumerate(['hub','disneyland','walt_disney_world','creative','back','next','refresh','close']):
        bar.alpha_composite(item(n),(3+i*20,3))
    sheet.alpha_composite(bar,(28,298))
    sheet.alpha_composite(a['sprites/hud/hotbar_selection.png'],(27+2*20,297))
    sheet.alpha_composite(a['sprites/hud/hotbar_offhand_left.png'],(0,297))
    sheet.alpha_composite(a['sprites/hud/hotbar_offhand_right.png'],(219,297))
    text(sheet,(264,302),'PIXEL ART / FIRST PASS',P['rim'])
    sheet.convert('RGB').resize((1350,990),Image.Resampling.NEAREST).save(OUT/'preview.png')
    # Review all six chest heights with actual vanilla UV stitching.
    heights=Image.new('RGBA',(560,460),'#12243a')
    for r in range(1,7):
        c=assembled_chest(a['container/generic_54.png'],r)
        text(c,(8,6),'CHEST','#404040')
        text(c,(8,c.height-94),'INVENTORY','#404040')
        x=8+((r-1)%3)*184;y=8+((r-1)//3)*226
        heights.alpha_composite(c,(x,y))
    heights.convert('RGB').resize((1120,920),Image.Resampling.NEAREST).save(OUT/'chest-heights.png')

def export(a):
    for pack in PACKS:
        root=ROOT/pack/'assets/minecraft/textures/gui'
        for name,im in a.items():
            p=root/name
            if p.exists():
                backup=OUT/'original'/pack/name
                if not backup.exists():
                    backup.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(p,backup)
            p.parent.mkdir(parents=True,exist_ok=True)
            im.save(p)
            if name.startswith('sprites/widget/'):
                metadata={'gui':{'scaling':{'type':'nine_slice','width':200,'height':20,'border':3}}}
                Path(str(p)+'.mcmeta').write_text(json.dumps(metadata,indent=2)+'\n')
    (OUT/'palette.json').write_text(json.dumps(P,indent=2)+'\n')

if __name__=='__main__':
    a=assets()
    preview(a)
    export(a)
