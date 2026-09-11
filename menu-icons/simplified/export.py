"""Normalize edited artwork to a limited-palette 32px grid and export 64px items."""
from pathlib import Path
from collections import deque
from PIL import Image,ImageDraw
import shutil
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
NAMES=['hub','disneyland','walt_disney_world','creative']
def normalize(name):
    im=Image.open(HERE/(name+'-generated.png')).convert('RGBA');w,h=im.size
    # Generated checkerboards are opaque: remove only low-chroma regions
    # connected to the exterior, preserving ivory stone and gray gate artwork.
    px=im.load();seen=set();todo=deque([(0,0),(w-1,0),(0,h-1),(w-1,h-1)])
    if name=='hub':todo.append((w//2,int(h*.13)))
    while todo:
        x,y=todo.popleft()
        if (x,y) in seen or not(0<=x<w and 0<=y<h):continue
        seen.add((x,y));r,g,b,a=px[x,y]
        if max(r,g,b)-min(r,g,b)>32 or min(r,g,b)<65:continue
        px[x,y]=(0,0,0,0)
        todo.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
    box=im.getbbox();im=im.crop(box)
    scale=30/max(im.size);size=tuple(round(v*scale) for v in im.size)
    im=im.resize(size,Image.Resampling.NEAREST)
    # Palette reduction without dithering removes remaining smooth shading.
    alpha=im.getchannel('A').point(lambda a:255 if a>=128 else 0)
    sampled=im.copy()
    im=im.convert('RGB').quantize(colors=18,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGBA');im.putalpha(alpha)
    if name=='walt_disney_world':
        for y in range(im.height):
            for x in range(im.width):
                r,g,b,a=sampled.getpixel((x,y))
                if a and r>150 and g>90 and g>b*1.5:
                    im.putpixel((x,y),(255,207,61,255))
    canvas=Image.new('RGBA',(32,32));canvas.alpha_composite(im,((32-im.width)//2,(32-im.height)//2))
    return canvas

def main():
    sheet=Image.new('RGB',(980,650),'#152c49');d=ImageDraw.Draw(sheet)
    d.text((24,18),'SERVER ICONS / ORIGINAL AND SIMPLIFIED',fill='#ffe4a0')
    for i,n in enumerate(NAMES):
        x=24+i*240;d.text((x,52),n.upper().replace('_',' '),fill='#b5edff')
        old=Image.open(ROOT/'Generic RP/assets/magicaldreams/textures/item/menu'/f'{n}.png').convert('RGBA')
        backup=HERE/(n+'-before.png')
        if not backup.exists():old.save(backup)
        old=Image.open(backup).convert('RGBA');new=normalize(n);new.save(HERE/(n+'-grid.png'))
        for row,(label,im) in enumerate([('ORIGINAL',old),('SIMPLIFIED',new)]):
            y=85+row*280;d.text((x,y),label,fill='#b1ccdc')
            for sz,dx in [(16,0),(32,40),(64,100)]:
                small=im.resize((sz,sz),Image.Resampling.NEAREST)
                sheet.paste(small,(x+dx,y+25),small)
            big=im.resize((160,160),Image.Resampling.NEAREST);sheet.paste(big,(x,y+105),big)
        final=new.resize((64,64),Image.Resampling.NEAREST)
        for pack in ['Generic RP','Parks RP']:
            path=ROOT/pack/'assets/magicaldreams/textures/item/menu'/f'{n}.png'
            path.chmod(path.stat().st_mode|0o200);final.save(path)
    sheet.save(HERE/'comparison.png')
if __name__=='__main__':main()
