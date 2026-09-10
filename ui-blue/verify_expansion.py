"""Validate expanded GUI geometry, scaling metadata, pack parity and HUD exclusion."""
import json
import subprocess
from pathlib import Path
from PIL import Image
from draw_all_ui import ROOT,TEMPLATES,expanded_assets,metadata
from draw_ui import PACKS,P

output=expanded_assets();sidecars=metadata();slot_count=0
for name,expected in output.items():
    source=Image.open(TEMPLATES/name).convert('RGBA')
    assert expected.size==source.size,name
    assert expected.getchannel('A').tobytes()==source.getchannel('A').tobytes(),name
    pair=[]
    for pack in PACKS:
        path=ROOT/pack/'assets/minecraft/textures/gui'/name
        actual=Image.open(path).convert('RGBA')
        assert actual.size==expected.size and actual.tobytes()==expected.tobytes(),str(path)
        pair.append(path.read_bytes())
        if name in sidecars:
            assert json.loads(Path(str(path)+'.mcmeta').read_text())==sidecars[name],name
    assert pair[0]==pair[1],name
    assert not name.startswith('sprites/hud/'),name
    # Find native flat 16px item wells by their corner and original gray fill.
    # Every detected item window must remain flat and fully opaque at the same UV.
    if name.startswith('container/'):
        s=source.load();gray=(139,139,139,255)
        for y in range(1,source.height-15):
            for x in range(1,source.width-15):
                if s[x,y]!=gray or s[x-1,y]==gray or s[x,y-1]==gray:continue
                if set(source.crop((x,y,x+16,y+16)).getdata())!={gray}:continue
                well=expected.crop((x,y,x+16,y+16))
                expected_fill=tuple(bytes.fromhex(P['slot'][1:]))+(255,)
                assert set(well.getdata())=={expected_fill},(name,x,y)
                slot_count+=1

for name,m in sidecars.items():
    scaling=m.get('gui',{}).get('scaling',{})
    if scaling.get('type')!='nine_slice':continue
    w,h=scaling['width'],scaling['height'];b=scaling['border']
    left=right=top=bottom=b if isinstance(b,int) else 0
    if isinstance(b,dict):left,right,top,bottom=[b[k] for k in ('left','right','top','bottom')]
    assert left+right<w and top+bottom<h,(name,'invalid nine-slice center')
    assert min(left,right,top,bottom)>=0,name

# Every paired interactive state must actually differ, not just have another name.
state_pairs=0
for name,im in output.items():
    if not name.endswith('_highlighted.png'):continue
    normal=name.replace('_highlighted.png','.png')
    if normal in output:
        assert im.tobytes()!=output[normal].tobytes(),name
        state_pairs+=1
assert output['sprites/recipe_book/slot_craftable.png'].tobytes()!=output['sprites/recipe_book/slot_uncraftable.png'].tobytes()
assert output['sprites/recipe_book/filter_enabled.png'].tobytes()!=output['sprites/recipe_book/filter_disabled.png'].tobytes()
assert not output['sprites/tooltip/frame.png'].getchannel('A').crop((10,10,90,90)).getbbox()

# Verify the pre-existing hotbar set is byte-identical to the committed first pass.
for pack in PACKS:
    for path in (ROOT/pack/'assets/minecraft/textures/gui/sprites/hud').glob('*'):
        rel=path.relative_to(ROOT).as_posix()
        previous=subprocess.run(['git','show',f'HEAD:{rel}'],cwd=ROOT,capture_output=True,check=True).stdout
        assert previous==path.read_bytes(),f'Unexpected HUD change: {rel}'

assert output['sprites/toast/system.png'].size==(160,32)
assert sidecars['sprites/toast/system.png']['gui']['scaling']['height']==32
print(f'PASS: {len(output)} PNGs, {len(sidecars)} sidecars match both packs.')
print(f'PASS: exact source dimensions/alpha, {slot_count} item windows, {state_pairs} hover pairs.')
print('PASS: tooltip center, recipe states, nine-slice borders, legacy system-toast size, unchanged HUD.')
