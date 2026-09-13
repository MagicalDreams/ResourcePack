#!/usr/bin/env python3
"""Validate the MagicBand asset/slot contract; optionally compare ParkManager Java."""
import argparse
import json
import re
from pathlib import Path
from PIL import Image

def validate(root, java=None):
    metadata=json.loads((root/'Parks RP/pack.mcmeta').read_text())
    assert 'magicaldreams:magicband_menu_v1' in metadata.get('mdcore',{}).get('capabilities',[]), 'Missing MDCore skin capability'
    assets=root/'Parks RP/assets'
    layout=json.loads((root/'magicband-ui/layout.json').read_text())
    entries=layout['entries']
    assert layout['size']==54 and layout['custom_model_data']==730001
    slots=[s for e in entries for s in e['slots']]
    assert slots==list(range(9,54)), 'Each button third must have one unique slot, with a decorative first row'
    assert len({e['original_slot'] for e in entries})==15
    image=Image.open(assets/'magicaldreams/textures/gui/magicband/home.png').convert('RGBA')
    assert image.size==(352,252)
    assert image.getchannel('A').getextrema()==(255,255), 'Panel must cover the vanilla slot background'
    font=json.loads((assets/'magicaldreams/font/magicband.json').read_text())['providers']
    spaces=font[0]['advances'];bitmap=font[1]
    assert bitmap['height']==126 and bitmap['ascent']==13 and bitmap['chars']==['\ue7a1']
    assert 6+7-bitmap['ascent']==0, 'Panel must align with chest top'
    assert spaces['\ue7a0']+image.width*bitmap['height']/image.height+1+spaces['\ue7a2']==0, 'Player title must retain its original position'
    default=json.loads((assets/'minecraft/font/default.json').read_text())['providers']
    assert default.count({'type':'reference','id':'magicaldreams:magicband'})==1
    for provider in default:
        characters=''.join(provider.get('chars',[]))+''.join(provider.get('advances',{}))
        assert not set('\ue7a0\ue7a1\ue7a2').intersection(characters), 'Font codepoint collision'
    modern=json.loads((assets/'minecraft/items/paper.json').read_text())['model']
    legacy=json.loads((assets/'minecraft/models/item/paper.json').read_text())['overrides']
    for value in (0,730000,730001,730002,999999):
        choices=[e for e in modern['entries'] if e['threshold']<=value]
        selected=max(choices,key=lambda e:e['threshold'])['model'] if choices else modern['fallback']
        assert (selected['type']=='minecraft:empty')==(value==730001), 'Ordinary paper must remain visible'
        choices=[e for e in legacy if e['predicate']['custom_model_data']<=value]
        selected=choices[-1]['model'] if choices else 'minecraft:item/paper'
        assert selected.endswith('/hit_area')==(value==730001)
    assert json.loads((assets/'magicaldreams/models/item/magicband/hit_area.json').read_text())=={'elements':[]}
    if java:
        source=(java/'src/main/java/us/magicaldreams/parkmanager/magicband/bandGuis/MagicBandMenuLayout.java').read_text()
        actual=[(a,int(b),int(c)) for a,b,c in re.findall(r'new Entry\("([a-z]+)", (\d+), (\d+)\)',source)]
        assert actual==[(e['id'],e['original_slot'],e['slots'][0]) for e in entries], 'Java slots and artwork disagree'
    print('PASS: 15 buttons / 45 hit areas, title alignment, glyph reservation, legacy + modern paper fallback' + (' and Java layout' if java else ''))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--java',type=Path)
    args=parser.parse_args();validate(args.root,args.java)
