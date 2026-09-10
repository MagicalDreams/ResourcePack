"""Native pixel adaptations for book, game-mode overlay and tiled menu surfaces."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageColor
from draw_ui import P
HERE=Path(__file__).resolve().parent
TEMPLATES=HERE/'templates'
NAMES=['book.png','container/gamemode_switcher.png','sprites/gamemode_switcher/slot.png','sprites/gamemode_switcher/selection.png','menu_background.png','menu_list_background.png','inworld_menu_background.png','inworld_menu_list_background.png','tab_header_background.png','header_separator.png','footer_separator.png','inworld_header_separator.png','inworld_footer_separator.png']
def rgb(name):return ImageColor.getrgb(P.get(name,name))
def draw(source,name):
    out=source.copy();pixels=[]
    for index,(r,g,b,a) in enumerate(source.getdata()):
        x,y=index%source.width,index//source.width
        v=(r+g+b)//3
        if name=='book.png':
            # Light paper keeps the book's black runtime writing legible.
            # Preserve native folds and stitched binding; recolor leather blue.
            if r>180 and g>170 and b>130:
                c='#e0edf2' if v>240 else '#d2e3ec' if v>222 else '#b1ccdc'
            elif 27<=x<=33 and 14<=y<=170 and r>g*1.6 and r>90:c='gold'
            else:c='ink' if v<35 else 'edge' if v<60 else 'blue' if v<100 else 'rim' if v<150 else 'label_edge'
        elif name=='container/gamemode_switcher.png':
            c='ink' if v<10 else 'slot_top' if v<50 else 'rim'
        elif name.endswith('/selection.png'):
            c='ink' if v<20 else 'sky' if v<120 else 'ice'
        elif name.endswith('/slot.png'):
            c='ink' if v<12 else 'slot_top' if v<75 else 'rim'
        elif 'separator' in name:c='rim' if v>128 else 'ink'
        else:c='ink' if 'list' in name or 'tab_header' in name else 'edge'
        pixels.append((*rgb(c),a))
    out.putdata(pixels)
    if name.endswith('/selection.png'):
        d=ImageDraw.Draw(out)
        d.rectangle((0,0,25,25),outline=P['ink'])
        d.rectangle((1,1,24,24),outline=P['sky'])
        d.rectangle((2,2,23,23),outline=P['ice'])
        for x,y in [(2,2),(22,2),(2,22),(22,22)]:d.rectangle((x,y,x+1,y+1),fill=P['gold_light'])
        out.putalpha(source.getchannel('A'))
    return out

def assets():return {name:draw(Image.open(TEMPLATES/name).convert('RGBA'),name) for name in NAMES}

def preview(a):
    sheet=Image.new('RGBA',(1100,790),'#101e31');d=ImageDraw.Draw(sheet)
    d.text((20,16),'BLUE STORYBOOK / BOOK, GAME-MODE SWITCHER AND MENU SURFACES',fill=P['ice'])
    book=a['book.png'].crop((20,0,166,181))
    d.text((20,50),'BOOK — pale pages for dark runtime text',fill=P['label'])
    sheet.alpha_composite(book.resize((438,543),Image.Resampling.NEAREST),(20,74))
    # Preview-only writing is omitted from the runtime texture.
    d.text((86,140),'A new adventure awaits...',fill='#303030')
    d.text((86,168),'Blue covers, gold stitching,',fill='#303030')
    d.text((86,190),'and crisp pixel edges.',fill='#303030')
    d.text((490,50),'F3 + F4 — selected slot stays transparent',fill=P['label'])
    switch=a['container/gamemode_switcher.png'].crop((0,0,125,75))
    for i in range(4):switch.alpha_composite(a['sprites/gamemode_switcher/slot.png'],(7+i*30,31))
    switch.alpha_composite(a['sprites/gamemode_switcher/selection.png'],(37,31))
    sheet.alpha_composite(switch.resize((500,300),Image.Resampling.NEAREST),(490,74))
    d.text((490,402),'MENU TILES — repeated over a sample backdrop',fill=P['label'])
    backdrop=Image.new('RGBA',(560,264),'#527b98')
    for y in range(0,264,16):
        for x in range(0,560,16):backdrop.alpha_composite(a['menu_background.png'],(x,y))
    for y in range(64,224,16):
        for x in range(0,560,16):backdrop.alpha_composite(a['menu_list_background.png'],(x,y))
    for x in range(0,560,32):
        backdrop.alpha_composite(a['header_separator.png'],(x,62))
        backdrop.alpha_composite(a['footer_separator.png'],(x,224))
    sheet.alpha_composite(backdrop,(490,430));d.text((516,454),'Select World',fill='white')
    d.text((516,518),'MagicalDreams',fill='white');d.text((516,544),'Your next story begins here',fill=P['ice'])
    d.text((20,752),'Illustrative texture composites; Minecraft supplies actual text, items and scene backgrounds.',fill=P['label'])
    sheet.convert('RGB').save(HERE/'review-menu-surfaces.png')
if __name__=='__main__':preview(assets())
