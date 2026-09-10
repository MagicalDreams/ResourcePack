"""Creative inventory and recipe book: native UVs with blue storybook surfaces.

The official templates are geometry masks, not resized artwork. Color regions
are translated deliberately so tab seams, slot bevels and semantic pictograms
remain exact. Run this file to regenerate the review; assets() is side-effect free.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageColor
from draw_ui import P

BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / 'templates'

def rgba(value):
    return ImageColor.getrgb(P.get(value, value)) + (255,)

def recolor(src, mapping):
    result=src.copy()
    lut={k if isinstance(k,tuple) else (k,k,k):rgba(v) for k,v in mapping.items()}
    result.putdata([lut.get(p[:3],p) if p[3] else p for p in src.getdata()])
    return result

BASE_MAP={0:'ink',55:'slot_top',85:'edge',139:'slot',198:'panel',204:'rim',255:'slot_light'}

def creative_background(src, name):
    im=recolor(src,BASE_MAP)
    d=ImageDraw.Draw(im)
    # Original slot locations are preserved, including equipment and delete slots.
    # A player silhouette needs its original darker well to keep skins legible.
    if name=='tab_inventory':
        for y in range(src.height):
            for x in range(src.width):
                if 72<=x<=104 and 4<=y<=48 and src.getpixel((x,y))==(0,0,0,255):
                    im.putpixel((x,y),rgba('#1d3044'))
    else:
        # Runtime Minecraft text is dark; it requires a light title band.
        right=77 if name=='tab_item_search' else 190
        d.rectangle((5,4,right,14),fill=P['label'])
        d.line((5,14,right,14),fill=P['label_edge'])
    if name=='tab_item_search':
        # Text box occupies the existing source rectangle; light text is runtime.
        d.rectangle((81,5,168,13),fill=P['ink'])
    # Bright outer top bevel, deliberately no new edge at selected tab seams.
    for y in range(3):
        for x in range(195):
            if src.getpixel((x,y))==(255,255,255,255): im.putpixel((x,y),rgba('rim'))
    im.putalpha(src.getchannel('A'))
    return im

def creative_sprite(src,name):
    mapping=BASE_MAP.copy()
    mapping[139]='blue'
    mapping[255]='rim'
    if name=='scroller':
        mapping.update({198:'rim',139:'blue',255:'ice'})
    elif name=='scroller_disabled':
        mapping.update({198:'#62788b',139:'#394e60',255:'#78909f'})
    # Selected fill matches the background precisely; unselected fill is darker.
    return recolor(src,mapping)

def recipe_background(src):
    im=recolor(src,{**BASE_MAP,55:'panel',255:'rim'})
    d=ImageDraw.Draw(im)
    # Vanilla gives the book one continuous interior; isolate its search field
    # without crossing the filter button at x110 or the first recipe row at y31.
    d.rectangle((9,12,105,27),fill=P['ink'])
    d.line((10,27,104,27),fill=P['rim'])
    # Retain the complete magnifying-glass pictogram and its native position.
    im.paste(src.crop((11,13,24,27)),(11,13))
    # Replace only the original background surrounding the glass.
    for y in range(13,27):
        for x in range(11,24):
            if src.getpixel((x,y))==(55,55,55,255):im.putpixel((x,y),rgba('ink'))
    im.putalpha(src.getchannel('A'))
    return im

def recipe_sprite(src,name):
    mapping={**BASE_MAP,139:'blue',255:'rim'}
    # Vanilla purple hover chrome is replaced with the existing button hover blue.
    mapping.update({(136,146,201):'#3f83b0',(0,7,62):'ink',
                    (52,62,117):'#24597f',(0,3,30):'ink',
                    (68,73,100):'#24597f',(95,100,127):'edge',
                    (175,182,218):'ice'})
    if 'highlighted' in name: mapping[255]='ice'
    if name.startswith('slot_'):
        mapping[139]='slot'
        mapping[204]='sky'
        # Red is functional: unavailable recipes remain clearly distinguishable.
        mapping.update({106:'#3c4659',(138,34,34):'#965d68',
                        (80,27,27):'#553b50',(194,79,79):'#d8959b'})
    if name.startswith('page_'):
        mapping.update({139:'gold',(136,146,201):'gold_light',255:'cream'})
    if 'overlay' in name and 'disabled' in name:
        mapping.update({(147,107,107):'#785c72',(141,126,153):'#987a94'})
    if 'filter_enabled' in name:
        # Enabled filter has teal face plus the original green check pictogram.
        mapping.update({(33,135,86):'#286e7e',(174,197,122):'sky',
                        (14,39,37):'ink'})
    im=recolor(src,mapping)
    if 'filter_' in name:
        # Preserve furnace/crafting-table pictogram, including its gray pixels.
        chrome={(139,139,139),(198,198,198),(136,146,201),
                (175,182,218),(33,135,86),(174,197,122),(14,39,37),
                (68,73,100),(255,255,255)}
        for y in range(2,15):
            for x in range(13,25):
                pixel=src.getpixel((x,y))
                if pixel[:3] not in chrome:im.putpixel((x,y),pixel)
    return im

def assets():
    output={}
    for p in sorted((TEMPLATES/'container/creative_inventory').glob('*.png')):
        output[p.relative_to(TEMPLATES).as_posix()]=creative_background(Image.open(p).convert('RGBA'),p.stem)
    for p in sorted((TEMPLATES/'sprites/container/creative_inventory').glob('*.png')):
        output[p.relative_to(TEMPLATES).as_posix()]=creative_sprite(Image.open(p).convert('RGBA'),p.stem)
    output['recipe_book.png']=recipe_background(Image.open(TEMPLATES/'recipe_book.png').convert('RGBA'))
    for p in sorted((TEMPLATES/'sprites/recipe_book').glob('*.png')):
        output[p.relative_to(TEMPLATES).as_posix()]=recipe_sprite(Image.open(p).convert('RGBA'),p.stem)
    return output

def review(a):
    """Before/after native composites and every sprite state at integer scale."""
    w=1060
    states=[k for k in a if k.startswith('sprites/')]
    sheet=Image.new('RGBA',(w,720+((len(states)+7)//8)*112),'#12243a')
    d=ImageDraw.Draw(sheet)
    d.text((12,8),'CREATIVE INVENTORY / RECIPE BOOK — NATIVE PIXEL REVIEW',fill=P['ice'])
    # Native composites: unselected tabs first, background, then selected tab.
    for row,source in enumerate([False,True]):
        y=48+row*310
        d.text((12,y-20),'BLUE STORYBOOK' if source else 'VANILLA GEOMETRY REFERENCE',fill=P['cream'])
        def get(key):return a[key] if source else Image.open(TEMPLATES/key).convert('RGBA')
        for col,stem in enumerate(['tab_items','tab_item_search','tab_inventory']):
            canvas=Image.new('RGBA',(204,196))
            for j in range(7):
                state='selected' if j==col else 'unselected'
                # Vanilla creative tabs use 26px width and 2px gaps.
                for edge,ty in [('top',0),('bottom',160)]:
                    tab=get(f'sprites/container/creative_inventory/tab_{edge}_{state}_{j+1}.png')
                    if state=='unselected':canvas.alpha_composite(tab,(j*28,ty))
            canvas.alpha_composite(get(f'container/creative_inventory/{stem}.png').crop((0,0,195,136)),(0,28))
            for edge,ty in [('top',0),('bottom',160)]:
                tab=get(f'sprites/container/creative_inventory/tab_{edge}_selected_{col+1}.png')
                canvas.alpha_composite(tab,(col*28,ty))
            cd=ImageDraw.Draw(canvas)
            if stem!='tab_inventory':cd.text((8,33),'Search' if stem=='tab_item_search' else 'Building Blocks',fill='#404040',font_size=8)
            if stem=='tab_item_search':cd.text((83,33),'stone',fill='#ffffff',font_size=8)
            if stem!='tab_inventory':canvas.alpha_composite(get('sprites/container/creative_inventory/scroller.png'),(175,46))
            sheet.alpha_composite(canvas,(12+col*228,y))
        book=get('recipe_book.png').crop((0,0,148,167))
        for r in range(5):
            for c in range(5):
                key='slot_uncraftable' if c==4 else 'slot_craftable'
                book.alpha_composite(get(f'sprites/recipe_book/{key}.png'),(11+c*25,31+r*25))
        book.alpha_composite(get('sprites/recipe_book/filter_enabled.png'),(110,12))
        sheet.alpha_composite(book,(736,y+28))
    d.text((12,680),'ALL RUNTIME SPRITES / 2X NEAREST — HOVER, ENABLED, DISABLED, SELECTED, MULTIPLE RECIPES',fill=P['ice'])
    for i,key in enumerate(states):
        x=12+(i%8)*130;y=716+(i//8)*112
        label=Path(key).stem
        words=label.split('_'); lines=[];line=''
        for word in words:
            if len(line)+len(word)>20:lines.append(line);line=word
            else:line+=(' ' if line else '')+word
        lines.append(line)
        d.text((x,y),'\n'.join(lines),fill=P['label'],font_size=9)
        im=a[key];sheet.alpha_composite(im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST),(x,y+44))
    sheet.convert('RGB').save(BASE/'review-creative-recipes.png')

if __name__=='__main__':
    result=assets()
    for key,im in result.items():
        ref=Image.open(TEMPLATES/key).convert('RGBA')
        assert im.size==ref.size,key
        assert im.getchannel('A').tobytes()==ref.getchannel('A').tobytes(),key
    review(result)
    print(f'{len(result)} creative/recipe assets; dimensions and alpha masks verified')
