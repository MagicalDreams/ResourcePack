#!/usr/bin/env python3
"""Deterministic MagicBand pixel UI. Run from this repository with Python + Pillow.

--output permits staging the pack changes without touching the source pack.
"""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw

ENTRIES = [
    ('parks', 'PARK MENU', 13, 9), ('rides', 'RIDES &\nATTRACTIONS', 12, 12), ('shows', 'SHOWS &\nEVENTS', 11, 15),
    ('food', 'FIND FOOD', 10, 18), ('hotels', 'HOTELS &\nRESORTS', 2, 21), ('shop', 'SHOP', 14, 24),
    ('waits', 'WAIT TIMES', 23, 27), ('counts', 'RIDE COUNTS', 22, 30), ('time', 'PLAYER TIME', 6, 33),
    ('wardrobe', 'WARDROBE', 15, 36), ('backpack', 'BACKPACK', 20, 39), ('locker', 'LOCKER', 24, 42),
    ('profile', 'MY PROFILE', 4, 45), ('customize', 'CUSTOMIZE\nBAND', 19, 48), ('visibility', 'GUEST\nVISIBILITY', 16, 51),
]
# Blue storybook palette from ui-blue/draw_ui.py, with gold navigation accents.
P = dict(ink='#152c49', edge='#244768', blue='#3c6b91', rim='#6c9cb9',
         sky='#67c4ef', ice='#b5edff', gold='#dfb75c', light='#ffe4a0', cream='#fff0c9')
LETTERS = {
 'A':'01110/10001/10001/11111/10001/10001/10001',
 'B':'11110/10001/10001/11110/10001/10001/11110',
 'C':'01111/10000/10000/10000/10000/10000/01111',
 'D':'11110/10001/10001/10001/10001/10001/11110',
 'E':'11111/10000/10000/11110/10000/10000/11111',
 'F':'11111/10000/10000/11110/10000/10000/10000',
 'G':'01111/10000/10000/10111/10001/10001/01111',
 'H':'10001/10001/10001/11111/10001/10001/10001',
 'I':'111/010/010/010/010/010/111',
 'J':'00111/00010/00010/00010/10010/10010/01100',
 'K':'10001/10010/10100/11000/10100/10010/10001',
 'L':'10000/10000/10000/10000/10000/10000/11111',
 'M':'10001/11011/10101/10101/10001/10001/10001',
 'N':'10001/11001/11001/10101/10011/10011/10001',
 'O':'01110/10001/10001/10001/10001/10001/01110',
 'P':'11110/10001/10001/11110/10000/10000/10000',
 'Q':'01110/10001/10001/10001/10101/10010/01101',
 'R':'11110/10001/10001/11110/10100/10010/10001',
 'S':'01111/10000/10000/01110/00001/00001/11110',
 'T':'11111/00100/00100/00100/00100/00100/00100',
 'U':'10001/10001/10001/10001/10001/10001/01110',
 'V':'10001/10001/10001/10001/10001/01010/00100',
 'W':'10001/10001/10001/10101/10101/10101/01010',
 'X':'10001/10001/01010/00100/01010/10001/10001',
 'Y':'10001/10001/01010/00100/00100/00100/00100',
 'Z':'11111/00001/00010/00100/01000/10000/11111',
 '&':'01100/10010/10100/01000/10101/10010/01101',
 ' ':'000/000/000/000/000/000/000',
}

def text(draw, xy, value, color, scale=1):
    x,y = xy
    for char in value:
        rows = LETTERS[char].split('/')
        for dy,row in enumerate(rows):
            for dx,pixel in enumerate(row):
                if pixel == '1': draw.rectangle((x+dx*scale,y+dy*scale,x+(dx+1)*scale-1,y+(dy+1)*scale-1), fill=color)
        x += (len(rows[0])+1)*scale
    return x

class DoubleDraw:
    """Redraw icon geometry at 2x resolution, including finer circular/rounded outlines."""
    def __init__(self, image): self.draw=ImageDraw.Draw(image)
    def __getattr__(self,name):
        def render(xy, *args, **kwargs):
            coords=[tuple(2*v for v in p) for p in xy] if isinstance(xy[0],tuple) else tuple(2*v for v in xy)
            if name=='line': kwargs['width']=2*kwargs.get('width',1)
            if 'radius' in kwargs: kwargs['radius']*=2
            return getattr(self.draw,name)(coords,*args,**kwargs)
        return render

def icon(name):
    im=Image.new('RGBA',(22,22)); d=DoubleDraw(im)
    c=P['light']; a=P['sky']
    if name=='parks':
        d.rectangle((1,4,9,9),fill=c); d.rectangle((4,1,6,9),fill=c)
        for x in (1,4,7): d.polygon([(x,4),(x+1,1),(x+2,4)],fill=a)
        d.rectangle((4,6,6,9),fill=P['ink'])
    elif name=='rides':
        d.line([(0,7),(2,7),(4,2),(6,2),(8,7),(10,7)],fill=a,width=1)
        d.rectangle((2,5,8,7),fill=c)
        for x in (3,7): d.rectangle((x,8,x+1,9),fill=c)
    elif name=='shows':
        for xy in [(5,0,5,3),(5,7,5,10),(0,5,3,5),(7,5,10,5),(1,1,3,3),(7,7,9,9),(7,3,9,1),(1,9,3,7)]: d.line(xy,fill=c)
        d.point((5,5),fill=a)
    elif name=='food':
        d.line((2,0,2,10),fill=c); d.line((0,0,0,3,4,3,4,0),fill=c)
        d.rectangle((7,0,9,4),fill=a);d.line((8,4,8,10),fill=c)
    elif name=='hotels':
        d.rectangle((0,5,10,8),fill=a);d.rectangle((1,3,3,5),fill=c)
        d.line((0,2,0,10),fill=c);d.line((10,5,10,10),fill=c)
    elif name=='shop':
        d.rectangle((1,4,9,10),outline=c);d.arc((3,0,7,7),180,360,fill=a)
        d.line((3,3,3,5),fill=a);d.line((7,3,7,5),fill=a)
    elif name in ('waits','time'):
        d.ellipse((0,0,10,10),outline=c);d.line((5,2,5,5,8,5),fill=a)
        if name=='waits': d.rectangle((7,7,10,10),fill=P['ink']); d.line((7,8,10,8),fill=c); d.line((7,10,10,10),fill=c)
    elif name=='counts':
        for x,h in [(1,3),(4,6),(7,9)]:d.rectangle((x,10-h,x+1,9),fill=c if x==7 else a)
    elif name=='wardrobe':
        d.polygon([(3,1),(0,3),(1,5),(3,4),(3,10),(7,10),(7,4),(9,5),(10,3),(7,1),(6,3),(4,3)],fill=a)
        d.line((3,9,7,9),fill=c)
    elif name=='backpack':
        d.arc((3,0,7,5),180,360,fill=c);d.rounded_rectangle((1,2,9,10),radius=2,outline=c)
        d.rectangle((3,6,7,9),outline=a)
    elif name=='locker':
        d.rectangle((2,4,8,10),fill=c);d.arc((3,0,7,7),180,360,fill=a)
        d.line((3,3,3,5),fill=a);d.line((7,3,7,5),fill=a);d.line((5,6,5,8),fill=P['ink'])
    elif name=='profile':
        d.ellipse((3,0,7,4),fill=c);d.rounded_rectangle((1,6,9,10),radius=2,fill=a)
    elif name=='customize':
        d.rectangle((3,0,7,10),fill=a);d.rounded_rectangle((1,2,9,8),radius=2,fill=c)
        d.rectangle((4,4,6,6),fill=P['ink'])
    elif name=='visibility':
        d.ellipse((0,2,10,8),outline=c);d.ellipse((4,3,6,7),fill=a)
    return im

def panel():
    im=Image.new('RGBA',(352,252),P['ink']);d=ImageDraw.Draw(im)
    d.rectangle((2,2,349,251),outline=P['rim'],width=2)
    d.rectangle((6,6,345,31),fill=P['edge']) # Runtime player name and chosen title color.
    for x in (4,338):d.line((x,4,x+8,4),fill=P['light'],width=2)
    im.alpha_composite(icon('customize'),(20,42))
    text(d,(56,45),'MAGICALDREAMS',P['light'],2)
    for name,label,old,first in ENTRIES:
        x,y=16+36*(first%9),36+36*(first//9)
        d.rounded_rectangle((x,y,x+103,y+31),radius=10,fill=P['rim'])
        d.rounded_rectangle((x+1,y+1,x+102,y+30),radius=9,fill=P['edge'])
        d.line((x+10,y+1,x+93,y+1),fill=P['sky'] if first<18 else P['blue'])
        im.alpha_composite(icon(name),(x+5,y+5))
        lines=label.split('\n')
        for i,line in enumerate(lines):
            end=text(d,(x+32,y+(7 if len(lines)>1 else 12)+i*11),line,P['cream'])
            assert end <= x+101, (label,end-x)
    return im

def write_json(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=True)+'\n')

def paper_definitions(root):
    """Only replace the original paper models or this generator's exact previous output."""
    assets=root/'Parks RP/assets/minecraft'
    original={'parent':'item/generated','textures':{'layer0':'item/paper'}}
    legacy={**original,'overrides':[
        {'predicate':{'custom_model_data':730001},'model':'magicaldreams:item/magicband/hit_area'},
        {'predicate':{'custom_model_data':730002},'model':'magicaldreams:item/magicband/paper'},
    ]}
    vanilla={'type':'minecraft:model','model':'minecraft:item/paper'}
    modern={'model':{
        'type':'minecraft:range_dispatch','property':'minecraft:custom_model_data','index':0,
        'fallback':vanilla,'entries':[
            {'threshold':730001,'model':{'type':'minecraft:empty'}},
            {'threshold':730002,'model':vanilla},
        ]}}
    if json.loads((assets/'models/item/paper.json').read_text()) not in (original,legacy):
        raise ValueError('Existing legacy paper definition requires a manual merge; no files written')
    path=assets/'items/paper.json'
    if path.exists() and json.loads(path.read_text()) != modern:
        raise ValueError('Existing modern paper definition requires a manual merge; no files written')
    return legacy,modern

def export(root, output):
    # Check conflicts before writing artwork or any shared font/model file.
    paper,modern=paper_definitions(root)
    pack=Path('Parks RP'); dest=output/pack; assets=dest/'assets'
    metadata=json.loads((root/pack/'pack.mcmeta').read_text())
    caps=metadata.setdefault('mdcore',{}).setdefault('capabilities',[])
    if 'magicaldreams:magicband_menu_v1' not in caps: caps.append('magicaldreams:magicband_menu_v1')
    write_json(dest/'pack.mcmeta',metadata)
    image=panel()
    target=assets/'magicaldreams/textures/gui/magicband/home.png'
    target.parent.mkdir(parents=True,exist_ok=True);image.save(target)
    font={'providers':[
        {'type':'space','advances':{'\ue7a0':-8,'\ue7a2':-169}},
        {'type':'bitmap','file':'magicaldreams:gui/magicband/home.png','ascent':13,'height':126,'chars':['\ue7a1']},
    ]}
    write_json(assets/'magicaldreams/font/magicband.json',font)
    default=root/pack/'assets/minecraft/font/default.json'
    raw=default.read_text(); data=json.loads(raw)
    reference={'type':'reference','id':'magicaldreams:magicband'}
    if reference not in data['providers']:
        # Preserve the large, existing spacing font byte-for-byte except for the new provider.
        pos=raw.index('[',raw.index('"providers"'))+1
        raw=raw[:pos]+json.dumps(reference,separators=(',',':'))+','+raw[pos:]
    path=assets/'minecraft/font/default.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(raw)
    write_json(assets/'magicaldreams/models/item/magicband/hit_area.json',{'elements':[]})
    normal={'parent':'minecraft:item/generated','textures':{'layer0':'minecraft:item/paper'}}
    write_json(assets/'magicaldreams/models/item/magicband/paper.json',normal)
    write_json(assets/'minecraft/models/item/paper.json',paper)
    write_json(assets/'minecraft/items/paper.json',modern)
    review=output/'magicband-ui';review.mkdir(parents=True,exist_ok=True)
    write_json(review/'layout.json',{'size':54,'custom_model_data':730001,'entries':[
        {'id':name,'label':label,'original_slot':old,'slots':[first,first+1,first+2]}
        for name,label,old,first in ENTRIES]})
    # Illustrative preview: source panel + the existing park chest's player inventory section.
    chest=Image.open(root/pack/'assets/minecraft/textures/gui/container/generic_54.png').convert('RGBA')
    preview=Image.new('RGBA',(352,444));preview.alpha_composite(image)
    preview.alpha_composite(chest.crop((0,126,176,222)).resize((352,192),Image.Resampling.NEAREST),(0,252))
    d=ImageDraw.Draw(preview);text(d,(16,14),'YOUR MAGICBAND',P['light'],2)
    text(d,(16,258),'INVENTORY',P['ink'],2)
    preview.resize((704,888),Image.Resampling.NEAREST).save(review/'preview.png')
    guide=preview.copy();g=ImageDraw.Draw(guide)
    for _,_,_,first in ENTRIES:
        for slot in range(first,first+3):
            x,y=16+36*(slot%9),36+36*(slot//9)
            g.rectangle((x,y,x+31,y+31),outline='#ff7799')
    guide.resize((704,888),Image.Resampling.NEAREST).save(review/'hit-areas.png')
    print('Exported 15 buttons, 45 hit areas, font panel and legacy/modern paper mappings to',output)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();export(args.root,args.output or args.root)
