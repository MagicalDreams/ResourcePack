"""Regression checks for shared-model preservation during asset regeneration."""
import json
import tempfile
import unittest
from pathlib import Path

from draw_magicband import export, paper_definitions

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
