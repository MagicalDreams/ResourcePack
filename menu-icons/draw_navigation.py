"""Author navigation icons at 32px; export exact 2x textures and review sheet."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SIZE = 32
COLORS = {'outline': '#071b43', 'gold': '#ffcc16', 'light': '#ffe35b',
          'highlight': '#fff2aa', 'amber': '#eaa012', 'shadow': '#bd740a'}

def mask_for(name):
    mask = Image.new('L', (SIZE, SIZE))
    draw = ImageDraw.Draw(mask)
    if name == 'back':
        draw.polygon([(4,15),(15,4),(15,11),(27,11),(27,20),(15,20),(15,27),(4,16)], fill=255)
    elif name == 'close':
        for y in range(6,26):
            for x in range(6,26):
                if abs(x-y)<=3 or abs(x+y-31)<=3:
                    mask.putpixel((x,y),255)
    elif name == 'refresh':
        # Compact versions of the navigation arrow: right above, left below.
        # Rotate the geometry exactly so both arrows have equal visual weight.
        upper = [(26,9),(21,4),(21,7),(5,7),(5,11),(21,11),(21,14)]
        draw.polygon(upper, fill=255)
        draw.polygon([(31-x,31-y) for x,y in upper], fill=255)
    return mask

def shade(mask):
    image=Image.new('RGBA',(SIZE,SIZE))
    image.paste(COLORS['outline'], (0,0), mask.filter(ImageFilter.MaxFilter(3)))
    def has(x,y):
        return 0<=x<SIZE and 0<=y<SIZE and mask.getpixel((x,y))>0
    for y in range(SIZE):
        for x in range(SIZE):
            if not has(x,y): continue
            # Broad face, one-pixel bevel, shared lighting across the family.
            c='gold'
            if not has(x,y+1): c='shadow'
            elif not has(x+1,y): c='amber'
            elif not has(x,y-1): c='highlight'
            elif not has(x-1,y): c='light'
            image.putpixel((x,y), tuple(bytes.fromhex(COLORS[c][1:]))+(255,))
    return image

def sprites():
    icons={n:shade(mask_for(n)) for n in ['back','close','refresh']}
    icons['next']=ImageOps.mirror(icons['back'])
    return {n:icons[n] for n in ['back','next','close','refresh']}

def preview(icons):
    sheet=Image.new('RGB',(960,460),'#192330')
    d=ImageDraw.Draw(sheet)
    d.text((24,18),'NAVIGATION / exact pixel grid / 6x preview',fill='#ffffff')
    for i,(name,im) in enumerate(icons.items()):
        x=24+i*234
        d.text((x,48),name.upper(),fill='#ffffff')
        # Both dark and Minecraft-like neutral backgrounds reveal outline/alpha issues.
        tile=Image.new('RGBA',(208,208),'#c6c6c6')
        large=im.resize((192,192),Image.Resampling.NEAREST)
        tile.alpha_composite(large,(8,8))
        sheet.paste(tile.convert('RGB'),(x,72))
        d.text((x,305),'32px          64px',fill='#aebbc9')
        sheet.paste(im,(x,334),im)
        rt=im.resize((64,64),Image.Resampling.NEAREST)
        sheet.paste(rt,(x+86,326),rt)
        d.text((x,411),'16px slot',fill='#aebbc9')
        small=im.resize((16,16),Image.Resampling.NEAREST)
        sheet.paste(small,(x+86,409),small)
    sheet.save(ROOT/'menu-icons/navigation-preview.png')

def export(icons):
    for name,im in icons.items():
        im.save(ROOT/f'menu-icons/source/{name}-grid.png')
        for pack in ['Generic RP','Parks RP']:
            root=ROOT/pack/'assets/magicaldreams'
            im.resize((64,64),Image.Resampling.NEAREST).save(root/f'textures/item/menu/{name}.png')
            definitions={f'items/menu/{name}.json':{'model':{'type':'minecraft:model','model':f'magicaldreams:item/menu/{name}'}},f'models/item/menu/{name}.json':{'parent':'minecraft:item/generated','textures':{'layer0':f'magicaldreams:item/menu/{name}'},'gui_light':'front'}}
            for rel,data in definitions.items(): (root/rel).write_text(json.dumps(data,indent=2)+'\n')
    icons['refresh'].resize((512,512),Image.Resampling.NEAREST).save(ROOT/'menu-icons/refresh-preview.png')

if __name__=='__main__':
    icons=sprites()
    preview(icons)
    export(icons)
