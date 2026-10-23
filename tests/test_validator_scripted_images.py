"""Validate real defined_text image references against effective mod catalogs."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import validate_mod


class ScriptedImageValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.game, self.parent, self.mod = (base / name for name in ("game", "parent", "mod"))
        for root in (self.game, self.parent, self.mod):
            (root / "interface").mkdir(parents=True)
        (self.mod / "common/scripted_localisation").mkdir(parents=True)
        (self.mod / "localisation/english").mkdir(parents=True)
        self.source = self.mod / "common/scripted_localisation/TFR_EST_images.txt"
        self.write_sprite(self.game / "interface/base.gfx", "GFX_game_image")
        self.write_sprite(self.game / "interface/shared.gfx", "GFX_shadowed_image")
        self.write_sprite(self.parent / "interface/shared.gfx", "GFX_parent_image")
        self.write_sprite(self.mod / "interface/TFR_EST_icons.gfx", "GFX_TFR_EST_image")
        (self.mod / "localisation/english/TFR_EST_images_l_english.yml").write_text(
            'l_english:\n TFR_EST_known_text:0 "Known text"\n'
            ' GFX_missing_image:0 "A localisation entry cannot supply a sprite"\n',
            encoding="utf-8-sig")

    def write_sprite(self, path, name):
        path.write_text('spriteTypes = { spriteType = { name = "' + name +
                        '" texturefile = "gfx/example.png" } }\n', encoding="utf-8")

    def validate_references(self, *references):
        selectors = ['text = { trigger = { always = yes } localization_key = "' + ref + '" }'
                     for ref in references]
        self.source.write_text('defined_text = { name = TFR_EST_test_image\n' +
                               '\n'.join(selectors) + '\n}\n', encoding="utf-8")
        with patch.object(validate_mod, "ROOT", self.mod):
            return validate_mod.validate(self.parent, self.game)["errors"]

    def test_existing_game_parent_and_submod_sprites_and_normal_text_are_valid(self):
        self.assertEqual(self.validate_references("GFX_game_image", "GFX_parent_image",
                                                 "GFX_TFR_EST_image", "TFR_EST_known_text"), [])

    def test_missing_sprite_is_rejected_even_when_a_localisation_entry_exists(self):
        errors = self.validate_references("GFX_missing_image")
        self.assertEqual(len(errors), 1)
        self.assertIn("missing scripted image sprite GFX_missing_image", errors[0])

    def test_sprite_from_a_shadowed_vanilla_file_is_not_accepted(self):
        errors = self.validate_references("GFX_shadowed_image")
        self.assertEqual(len(errors), 1)
        self.assertIn("missing scripted image sprite GFX_shadowed_image", errors[0])

    def test_missing_normal_localisation_remains_an_error(self):
        errors = self.validate_references("TFR_EST_missing_text")
        self.assertEqual(len(errors), 1)
        self.assertIn("missing scripted localization TFR_EST_missing_text", errors[0])


if __name__ == "__main__":
    unittest.main()
