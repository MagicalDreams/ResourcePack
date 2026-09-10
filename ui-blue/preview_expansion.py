"""Compact native-pixel overview; captions are outside runtime artwork."""
from pathlib import Path
from PIL import Image, ImageDraw
HERE=Path(__file__).resolve().parent
GUI=HERE.parent/'Generic RP/assets/minecraft/textures/gui'
PANELS=[
 ('PLAYER INVENTORY','container/inventory.png',(0,0,176,166)),
 ('CREATIVE INVENTORY','container/creative_inventory/tab_items.png',(0,0,195,136)),
 ('CRAFTING','container/crafting_table.png',(0,0,176,166)),
 ('FURNACE','container/furnace.png',(0,0,176,166)),
 ('ANVIL','container/anvil.png',(0,0,176,166)),
 ('SMITHING','container/smithing.png',(0,0,176,166)),
 ('BREWING','container/brewing_stand.png',(0,0,176,166)),
 ('ENCHANTING','container/enchanting_table.png',(0,0,176,166)),
 ('LOOM','container/loom.png',(0,0,176,166)),
 ('STONECUTTER','container/stonecutter.png',(0,0,176,166)),
 ('SHULKER BOX','container/shulker_box.png',(0,0,176,166)),
 ('RECIPE BOOK','recipe_book.png',(0,0,147,166)),
]
def main():
    canvas=Image.new('RGB',(1648,1220),'#101e31');d=ImageDraw.Draw(canvas)
    d.text((24,18),'MAGICALDREAMS  /  BLUE STORYBOOK UI',fill='#ffe4a0')
    d.text((24,38),'Shared artwork for both packs. Texture previews; Minecraft supplies text, items and dynamic controls.',fill='#b1ccdc')
    for i,(label,name,box) in enumerate(PANELS):
        x=24+(i%4)*408;y=80+(i//4)*380
        d.text((x,y),label,fill='#b5edff')
        im=Image.open(GUI/name).convert('RGBA').crop(box)
        canvas.paste(im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST),(x,y+24),im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST))
    canvas.save(HERE/'expansion-preview.png')
if __name__=='__main__':main()
