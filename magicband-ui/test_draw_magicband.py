"""Regression checks for glyph rendering and shared-model preservation."""
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops
from draw_magicband import export, paper_definitions, panel
from validate_magicband import validate_panel

class PanelGlyphTest(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]
        self.image=panel()
        self.font=json.loads((root/'Parks RP/assets/magicaldreams/font/magicband.json').read_text())['providers']

    def test_source_cells_fit_and_reconstruct_the_original_artwork(self):
        placements=validate_panel(self.image,self.font)
        assembled=Image.new('RGBA',self.image.size)
        for column,(_,x,_) in enumerate(placements):
            cell=self.image.crop((column*176,0,(column+1)*176,252))
            assembled.paste(cell,(int(x*2),0))
        self.assertIsNone(ImageChops.difference(self.image,assembled).convert('RGB').getbbox())

    def test_previous_single_glyph_is_rejected_even_at_half_display_size(self):
        self.font[1]['chars']=['\ue7a1']
        with self.assertRaisesRegex(AssertionError,'256x256 font atlas'):
            validate_panel(self.image,self.font)

    def test_tall_source_cells_are_also_rejected(self):
        with self.assertRaisesRegex(AssertionError,'256x256 font atlas'):
            validate_panel(Image.new('RGBA',(352,258)),self.font)

    def test_missing_negative_space_is_rejected(self):
        self.font[0]['advances']['\ue7a4']=0
        with self.assertRaisesRegex(AssertionError,'gap or overlap'):
            validate_panel(self.image,self.font)

    def test_shifted_player_title_is_rejected(self):
        self.font[0]['advances']['\ue7a2']=-168
        with self.assertRaisesRegex(AssertionError,'title must retain'):
            validate_panel(self.image,self.font)

class PaperModelPreservationTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.legacy=self.root/'Parks RP/assets/minecraft/models/item/paper.json'
        self.legacy.parent.mkdir(parents=True)
        self.legacy.write_text(json.dumps({'parent':'item/generated','textures':{'layer0':'item/paper'}}))
        self.modern=self.root/'Parks RP/assets/minecraft/items/paper.json'
        self.modern.parent.mkdir(parents=True)

    def test_original_and_previously_generated_models_are_accepted(self):
        legacy,modern=paper_definitions(self.root)
        self.legacy.write_text(json.dumps(legacy))
        self.modern.write_text(json.dumps(modern))
        self.assertEqual((legacy,modern),paper_definitions(self.root))

    def test_other_legacy_overrides_are_rejected_before_any_output(self):
        legacy,_=paper_definitions(self.root)
        legacy['overrides'].append({'predicate':{'custom_model_data':800000},'model':'other:ticket'})
        self.legacy.write_text(json.dumps(legacy))
        output=self.root/'output'
        with self.assertRaisesRegex(ValueError,'legacy paper'):
            export(self.root,output)
        self.assertFalse(output.exists())
        self.assertEqual(legacy,json.loads(self.legacy.read_text()))

    def test_other_modern_entries_are_rejected_even_when_our_reservation_exists(self):
        _,modern=paper_definitions(self.root)
        modern['model']['entries'].append({'threshold':800000,'model':{'type':'minecraft:empty'}})
        self.modern.write_text(json.dumps(modern))
        output=self.root/'output'
        with self.assertRaisesRegex(ValueError,'modern paper'):
            export(self.root,output)
        self.assertFalse(output.exists())
        self.assertEqual(modern,json.loads(self.modern.read_text()))

if __name__=='__main__':
    unittest.main()
