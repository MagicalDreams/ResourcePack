"""Blue storybook controls, preserving official sprite geometry and alpha masks.

All pixel art is deterministic; no smoothing or generated raster artwork.
The original masks and glyphs keep checkbox, lock, and tutorial meanings intact.
"""
from pathlib import Path
from PIL import Image, ImageColor, ImageDraw
from draw_ui import P, button, nine_slice

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / 'templates'

def rgb(c):
    return ImageColor.getrgb(P.get(c,c))

def recolor(source, fn):
    result = source.copy()
    result.putdata([(*fn(r,g,b),a) if a else (0,0,0,0) for r,g,b,a in source.getdata()])
    return result

def tone(r,g,b):
    v=(r+g+b)//3
    return rgb('ink' if v<24 else 'slot_top' if v<65 else 'edge' if v<100 else 'blue' if v<145 else 'rim' if v<190 else 'ice')

def flat_control(source,name):
    """Keep exact native alpha, while eliminating the vanilla noise texture."""
    w,h=source.size
    hi='highlighted' in name
    disabled='disabled' in name
    state='disabled' if disabled else 'highlighted' if hi else 'normal'
    if name.startswith(('locked_button','unlocked_button','cross_button')):
        out=button(state,w,h)
        # Copy only the interior glyph: original background is the 108–113 band.
        for y in range(2,h-2):
            for x in range(2,w-2):
                r,g,b,a=source.getpixel((x,y));v=(r+g+b)//3
                if name.startswith('cross'):
                    glyph=v>175 or v<50
                else:
                    glyph=4<=x<=15 and 3<=y<=16 and (v>125 or v<65)
                if glyph:
                    color='rim' if disabled and v>125 else 'cream' if v>=170 else 'rim' if v>=125 else 'ink'
                    out.putpixel((x,y),(*rgb(color),a))
    elif name.startswith('checkbox'):
        out=Image.new('RGBA',source.size,P['slot_top'])
        d=ImageDraw.Draw(out)
        d.rectangle((0,0,w-1,h-1),outline=P['ice'] if hi else P['ink'])
        d.rectangle((1,1,w-2,h-2),outline=P['sky'] if hi else P['edge'])
        if 'selected' in name:
            for y in range(2,h-2):
                for x in range(2,w-2):
                    v=source.getpixel((x,y))[0]
                    if v>=120:out.putpixel((x,y),(*rgb('cream' if v>=200 else 'rim'),255))
    elif name.startswith('text_field'):
        out=Image.new('RGBA',source.size,P['ink']);d=ImageDraw.Draw(out)
        d.rectangle((0,0,w-1,h-1),outline=P['ice'] if hi else P['rim'])
    elif name=='preedit':
        # IME composition text is rendered dark on the native white field.
        out=Image.new('RGBA',source.size,P['label']);d=ImageDraw.Draw(out)
        d.rectangle((0,0,w-1,h-1),outline=P['sky'])
    elif name.startswith('slider_handle'):
        out=button(state,w,h)
    elif name.startswith('slider'):
        out=Image.new('RGBA',source.size,P['slot_top']);d=ImageDraw.Draw(out)
        d.rectangle((0,0,w-1,h-1),outline=P['ice'] if hi else P['ink'])
    elif name=='scroller':
        out=Image.new('RGBA',source.size,P['blue']);d=ImageDraw.Draw(out)
        d.line((0,0,w-1,0),fill=P['rim']);d.line((0,0,0,h-1),fill=P['rim'])
        d.line((w-1,1,w-1,h-1),fill=P['edge']);d.line((1,h-1,w-1,h-1),fill=P['edge'])
    elif name=='scroller_background':
        out=Image.new('RGBA',source.size,P['ink'])
    elif name.startswith('page_'):
        # Preserve vanilla's page-turn arrow silhouette and readable tip.
        out=recolor(source,lambda r,g,b: rgb('ice' if hi and max(r,g,b)>200 else 'sky' if hi else 'cream' if min(r,g,b)>180 else 'gold' if max(r,g,b)>160 else 'edge'))
    elif name.startswith('tab'):
        # Selected tab centers must stay clear so the underlying screen shows.
        out=recolor(source,lambda r,g,b: rgb(('ice' if hi else 'rim') if r>127 else 'blue' if 'selected' in name else 'ink'))
    else:
        out=recolor(source,tone)
    # panel() cuts its corners; native opaque masks need ink under those pixels.
    under=Image.new('RGBA',out.size,P['ink'])
    under.alpha_composite(out)
    out=under
    out.putalpha(source.getchannel('A'))
    return out

def toast(source,name):
    w,h=source.size
    if name in {'advancement','now_playing','recipe','system','tutorial'}:
        # Advancement, music and system use light text; recipe/tutorial dark text.
        light=name in {'recipe','tutorial'}
        face='label' if light else 'ink'
        out=Image.new('RGBA',source.size,P[face]);d=ImageDraw.Draw(out)
        d.rectangle((0,0,w-1,h-1),outline=P['ink'])
        d.rectangle((1,1,w-2,h-2),outline=P['rim'] if light else P['blue'])
        d.line((3,2,w-4,2),fill=P['ice'] if light else P['rim'])
        d.line((2,3,2,h-4),fill=P['rim'])
        d.line((3,h-3,w-3,h-3),fill=P['label_edge'] if light else P['edge'])
        if name=='system':
            # Compact marker stays within the fixed top16/left17 corner.
            # Minecraft clamps each border to half the destination dimension;
            # the original y8..24 marker crosses that clamp in a 32px toast.
            d.rectangle((8,5,10,11),fill=P['gold'])
            d.line((8,5,8,10),fill=P['cream'])
            d.rectangle((8,13,10,14),fill=P['gold'])
            d.point((8,13),fill=P['cream'])
        out.putalpha(source.getchannel('A'))
        return out
    # Keep botanical/material and green recipe-book semantics; retint neutral UI art.
    return recolor(source,lambda r,g,b: tone(r,g,b) if max(r,g,b)-min(r,g,b)<14 else (r,g,b))

def assets():
    result={}
    for category in ('widget','tooltip','toast'):
        for path in sorted((TEMPLATES/'sprites'/category).glob('*.png')):
            if path.stem in {'button','button_highlighted','button_disabled'}:continue
            source=Image.open(path).convert('RGBA')
            if category=='widget':im=flat_control(source,path.stem)
            elif category=='toast':im=toast(source,path.stem)
            else:
                im=recolor(source,lambda r,g,b:rgb('ink' if path.stem=='background' else 'sky' if b>=190 else 'rim'))
            result[path.relative_to(TEMPLATES).as_posix()]=im
    return result

def metadata_overrides():
    """One system toast works at both legacy32px and modern64px heights."""
    return {'sprites/toast/system.png': {'gui': {'scaling': {
        'type':'nine_slice','width':160,'height':32,
        'border':{'left':17,'top':16,'right':4,'bottom':4}
    }}}}


def preview(a):
    # Each row shows a native sprite and a nearest-neighbor enlarged copy.
    pairs=list(a.items());cols=3;cw=360;rh=125
    rows=(len(pairs)+cols-1)//cols
    sheet=Image.new('RGBA',(cw*cols,rows*rh+210),'#17263b');d=ImageDraw.Draw(sheet)
    for i,(name,im) in enumerate(pairs):
        x=i%cols*cw+10;y=i//cols*rh+8
        d.text((x,y),name.removeprefix('sprites/'),fill=P['ice'])
        d.text((x,y+13),f'{im.width} x {im.height} / native + enlarged',fill=P['rim'])
        sheet.alpha_composite(im,(x,y+30))
        scale=min(3,150//im.width,80//im.height)
        if scale>=1:sheet.alpha_composite(im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST),(x+205,y+30))
    y=rows*rh+10
    d.text((10,y),'TOOLTIP COMPOSITE / native + nine-slice resized',fill=P['ice'])
    for x,w,h in [(10,100,100),(150,270,80)]:
        bg=nine_slice(a['sprites/tooltip/background.png'],w,h,9)
        fr=nine_slice(a['sprites/tooltip/frame.png'],w,h,10)
        bg.alpha_composite(fr)
        ImageDraw.Draw(bg).text((14,14),'Diamond Sword',fill='#ffffff')
        sheet.alpha_composite(bg,(x,y+22))
    d.text((470,y),'TOAST READABILITY / runtime text colors',fill=P['ice'])
    for i,(name,fill,label) in enumerate([('recipe','#500050','New Recipes Unlocked!'),('tutorial','#000000','Move with WASD'),('advancement','#ffff00','Advancement Made!')]):
        im=a[f'sprites/toast/{name}.png'].copy();ImageDraw.Draw(im).text((30,10),label,fill=fill)
        sheet.alpha_composite(im,(470+i*190,y+28))
    # Legacy and modern system heights, exercising the asymmetric metadata.
    for x,w,h in [(470,160,32),(650,200,64),(870,200,80)]:
        source=a['sprites/toast/system.png']
        target=Image.new('RGBA',(w,h))
        xs=[0,17,156,160];ys=[0,16,28,32]
        xd=[0,17,w-4,w];yd=[0,16,h-4,h]
        for row in range(3):
            for col in range(3):
                tile=source.crop((xs[col],ys[row],xs[col+1],ys[row+1]))
                dw,dh=xd[col+1]-xd[col],yd[row+1]-yd[row]
                for ty in range(0,dh,tile.height):
                    for tx in range(0,dw,tile.width):
                        part=tile.crop((0,0,min(tile.width,dw-tx),min(tile.height,dh-ty)))
                        target.alpha_composite(part,(xd[col]+tx,yd[row]+ty))
        ImageDraw.Draw(target).text((18,7),'System notification',fill='#ffff00')
        sheet.alpha_composite(target,(x,y+95))
    sheet.convert('RGB').save(HERE/'review-controls.png')

if __name__=='__main__':
    a=assets();preview(a)
    for name,im in a.items():
        source=Image.open(TEMPLATES/name).convert('RGBA')
        assert source.size==im.size
        assert source.getchannel('A').tobytes()==im.getchannel('A').tobytes(),name
    print(f'Reviewed {len(a)} controls: native dimensions and alpha masks preserved.')
