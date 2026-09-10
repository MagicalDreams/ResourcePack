"""Offline layout checks for the shared blue UI. Run after draw_ui.py."""
from pathlib import Path
from PIL import Image
import json
from draw_ui import ROOT, PACKS, assets, assembled_chest, nine_slice, P

expected=assets()
for rel,source in expected.items():
    copies=[]
    for pack in PACKS:
        p=ROOT/pack/'assets/minecraft/textures/gui'/rel
        im=Image.open(p)
        assert im.mode=='RGBA' and im.size==source.size,rel
        assert im.tobytes()==source.tobytes(),rel
        copies.append(p.read_bytes())
    assert copies[0]==copies[1],rel

# Every 16px item window must remain flat, opaque and at vanilla coordinates,
# even after the two atlas regions are stitched for each chest height.
slot_color=tuple(bytes.fromhex(P['slot'][1:]))+(255,)
for rows in range(1,7):
    im=assembled_chest(expected['container/generic_54.png'],rows)
    origins=[(8+18*c,18+18*r) for r in range(rows) for c in range(9)]
    inventory_y=rows*18+31
    origins += [(8+18*c,inventory_y+18*r) for r in range(3) for c in range(9)]
    origins += [(8+18*c,inventory_y+58) for c in range(9)]
    for x,y in origins:
        assert set(im.crop((x,y,x+16,y+16)).getdata())=={slot_color},(rows,x,y)
    # The two source strips join without an alpha seam at either side.
    seam=rows*18+17
    assert all(im.getpixel((x,seam))[3]==255 for x in range(176))

selection=expected['sprites/hud/hotbar_selection.png']
assert not selection.getchannel('A').crop((4,4,20,20)).getbbox()
assert expected['sprites/hud/hotbar_offhand_left.png'].getchannel('A').crop((22,0,29,24)).getbbox() is None
assert expected['sprites/hud/hotbar_offhand_right.png'].getchannel('A').crop((0,0,7,24)).getbbox() is None

for suffix in ('','_highlighted','_disabled'):
    rel=f'sprites/widget/button{suffix}.png'
    for pack in PACKS:
        m=json.loads((ROOT/pack/'assets/minecraft/textures/gui'/(rel+'.mcmeta')).read_text())
        assert m['gui']['scaling']=={'type':'nine_slice','width':200,'height':20,'border':3}
    for width,height in [(20,20),(66,20),(150,20),(200,20),(220,20),(100,32)]:
        im=nine_slice(expected[rel],width,height)
        assert im.size==(width,height)
        assert im.crop((0,0,3,3)).tobytes()==expected[rel].crop((0,0,3,3)).tobytes()
        assert im.crop((width-3,height-3,width,height)).tobytes()==expected[rel].crop((197,17,200,20)).tobytes()

print('PASS: 8 PNGs match in both packs; 6 chest heights preserve all item windows;')
print('selection stays clear; offhand padding matches vanilla; 3 button states scale correctly.')
