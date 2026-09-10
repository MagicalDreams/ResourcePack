"""Geometry-preserving blue storybook container artwork at native pixel resolution.

Official template silhouettes, semantic indicators and item windows are retained.
No runtime labels are baked into these textures. assets() has no export side effects.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageColor
from draw_ui import P

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / 'templates'

def rgb(hex_color):
    return ImageColor.getrgb(hex_color)

NEUTRAL = {
    0: P['ink'], 33: '#1c334b', 55: P['slot_top'],
    56: '#253a50', 68: '#304c68', 85: P['edge'],
    115: '#355c7a', 139: P['slot'], 140: P['slot'],
    173: '#7193aa', 198: P['panel'], 255: P['slot_light'],
}
# The brown/pink recipe button materials are UI surfaces, not item illustrations.
SURFACES = {
    (160,145,114): P['label'], (81,73,58): P['edge'],
    (84,76,59): P['edge'], (107,97,76): P['blue'],
    (33,29,23): P['ink'],
}

def remap(source, surfaces=False):
    im=source.copy()
    pixels=[]
    for r,g,b,a in source.getdata():
        c=(r,g,b)
        if a and r==g==b and r in NEUTRAL:
            c=rgb(NEUTRAL[r])
        elif a and surfaces and c in SURFACES:
            c=rgb(SURFACES[c])
        pixels.append((*c,a))
    im.putdata(pixels)
    return im

# Vanilla dark labels: (left, top, right, bottom), with no extra painted text.
# Masked to the original flat panel so decorations, slots and UVs remain intact.
LABEL_BANDS = {
    'inventory': [(95,3,172,15)],
    'smithing': [(44,15,172,29),(3,71,172,81)],
    'anvil': [(58,3,172,15),(3,71,172,81)],
    'hopper': [(3,3,172,16),(3,38,172,48)],
    'beacon': [],
    'villager': [(3,3,272,15),(103,71,272,81)],
}

def background(source, name):
    im=remap(source,surfaces=True)
    sp=source.load(); ip=im.load()
    if name=='anvil':
        # The official atlas has a red debug placeholder under the dynamic name
        # field. Replace it too so no red can flash behind that overlay.
        for y in range(source.height):
            for x in range(source.width):
                if sp[x,y]==(255,0,0,255): ip[x,y]=(*rgb(P['label']),255)
    bands=LABEL_BANDS.get(name,[(3,3,172,15),(3,71,172,81)])
    for x0,y0,x1,y1 in bands:
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                if sp[x,y] == (198,198,198,255):
                    color=P['label_edge'] if y==y1 else '#d0e3ed' if y==y0 else P['label']
                    ip[x,y]=(*rgb(color),255)
    # Restrict border work to its existing 4px perimeter. Exact alpha is unchanged.
    _,_,w,h=source.getbbox()
    d=ImageDraw.Draw(im)
    d.line((3,1,w-4,1), fill=P['rim'])
    d.line((1,3,1,h-4), fill=P['rim'])
    d.line((3,h-2,w-4,h-2), fill=P['edge'])
    d.line((w-2,3,w-2,h-4), fill=P['edge'])
    for x,s in [(2,1),(w-3,-1)]:
        d.line((x,2,x+s*3,2),fill=P['gold_light'])
        d.line((x,2,x,5),fill=P['gold'])
        d.line((x,h-3,x+s*3,h-3),fill=P['gold'])
    im.putalpha(source.getchannel('A'))
    return im

def surface_button(source,name):
    # Preserve bevel geometry/alpha, assign ranked surface colors to the UI state.
    if 'disabled' in name:
        ramp=['#20364b','#2d4051','#394e60','#62788b']
    elif 'highlighted' in name:
        ramp=[P['ink'],'#24597f','#3f83b0',P['ice']]
    elif 'selected' in name:
        ramp=[P['ink'],P['edge'],P['blue'],P['gold']]
    elif 'enchantment_slot' in name or 'text_field' in name:
        # Dark rune/name text must retain contrast.
        ramp=[P['ink'],P['label_edge'],P['label'],'#d0e3ed']
    else:
        ramp=[P['ink'],P['edge'],'#305c83','#719db9']
    colors=sorted({p[:3] for p in source.getdata() if p[3]},key=lambda c:sum(c))
    mapping={c:rgb(ramp[round(i*3/max(1,len(colors)-1))]) for i,c in enumerate(colors)}
    im=source.copy(); im.putdata([(*mapping[p[:3]],p[3]) if p[3] else p for p in source.getdata()])
    return im

def sprite(source,relative):
    name=relative.stem
    parent=relative.parent.name
    if parent=='slot':
        # Empty slot glyphs need to remain distinguishable from their slate fill.
        im=source.copy();im.putdata([(*rgb(P['slot_light']),p[3]) if p[3] else p for p in source.getdata()]);return im
    surface_names={'button','button_highlighted','button_selected','button_disabled',
        'pattern','pattern_highlighted','pattern_selected','recipe','recipe_highlighted','recipe_selected',
        'enchantment_slot','enchantment_slot_highlighted','enchantment_slot_disabled',
        'text_field','text_field_disabled','scroller','scroller_disabled'}
    if name in surface_names:
        return surface_button(source,name)
    if 'slot_highlight' in name:
        im=source.copy();im.putdata([(*rgb(P['sky']),p[3]) if p[3] else p for p in source.getdata()]);return im
    # Progress colors, red errors, green confirmations, map parchment, enchantment
    # numerals and redstone are semantic; retain their colored pixels verbatim.
    im=remap(source)
    if name in {'burn_progress','brew_progress','bubbles','trade_arrow'}:
        im.putdata([(*rgb(P['panel'] if p[0]==198 else P['ice'] if p[0]==255 else P['sky']),p[3])
                    if p[3] and p[0]==p[1]==p[2] else p for p in source.getdata()])
    if parent=='bundle' and name=='slot_background':
        im.putdata([(*rgb(P['ink']),p[3]) if p[3] else p for p in source.getdata()])
    if parent=='loom' and name in {'banner_slot','dye_slot','pattern_slot'}:
        im.putdata([(*rgb(P['slot_light']),p[3]) if p[:3]==(55,55,55) else q for p,q in zip(source.getdata(),im.getdata())])
    if name=='effect_background_ambient':
        im.putdata([(*rgb(P['sky']),p[3]) if p[3] and p[1]>p[0]+40 else p for p in im.getdata()])
    # Legacy grey slot outlines get blue-gray hints for sufficient contrast.
    if parent in {'horse','loom'} and name.endswith('_slot'):
        src=list(source.getdata());dst=list(im.getdata())
        for i,p in enumerate(src):
            if p[3] and p[0]==p[1]==p[2] and p[0] not in NEUTRAL:
                dst[i]=(*rgb(P['slot_light']),p[3])
        im.putdata(dst)
    return im

def assets():
    result={}
    for path in sorted((TEMPLATES/'container').glob('*.png')):
        if path.stem in {'generic_54','gamemode_switcher'}:continue
        result[path.relative_to(TEMPLATES).as_posix()]=background(Image.open(path).convert('RGBA'),path.stem)
    for path in sorted((TEMPLATES/'sprites/container').rglob('*.png')):
        if 'creative_inventory' in path.parts:continue
        rel=path.relative_to(TEMPLATES)
        result[rel.as_posix()]=sprite(Image.open(path).convert('RGBA'),rel)
    return result

def preview(a):
    backgrounds=[(k,v) for k,v in a.items() if k.startswith('container/')]
    sprites=[(k,v) for k,v in a.items() if k.startswith('sprites/')]
    # 2x backgrounds and 3x sprite art: no filtering or smoothed shapes.
    cols=4; cw=560; rh=490
    bg_height=((len(backgrounds)+cols-1)//cols)*rh
    spr_h=130; spr_cols=6; spr_w=370
    sheet=Image.new('RGB',(cols*cw,bg_height+((len(sprites)+spr_cols-1)//spr_cols)*spr_h),'#12243a')
    d=ImageDraw.Draw(sheet)
    for i,(name,im) in enumerate(backgrounds):
        x=i%cols*cw;y=i//cols*rh
        d.text((x+12,y+8),name,fill=P['ice'],font_size=18)
        crop=im.crop(im.getbbox()).resize((im.getbbox()[2]*2,im.getbbox()[3]*2),Image.Resampling.NEAREST)
        sheet.paste(crop,(x+6,y+38),crop)
    for i,(name,im) in enumerate(sprites):
        x=i%spr_cols*spr_w;y=bg_height+i//spr_cols*spr_h
        label=name.removeprefix('sprites/container/')
        d.text((x+8,y+5),label,fill=P['ice'],font_size=12)
        scale=min(3, max(1,350//im.width),max(1,90//im.height))
        art=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
        sheet.paste(art,(x+8,y+28),art)
    sheet.save(HERE/'review-containers.png')

if __name__=='__main__':
    a=assets()
    for name,im in a.items():
        original=Image.open(TEMPLATES/name).convert('RGBA')
        assert im.size==original.size, name
        assert im.getchannel('A').tobytes()==original.getchannel('A').tobytes(),name
    preview(a)
    print(f'Reviewed dimensions and exact alpha for {len(a)} textures; preview written.')
