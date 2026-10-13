"""Preserve TFR's shared executive display while adding party-led Estonia.

These structural checks exercise the reproducible localisation adapter. Native
GUI rendering and presidential/cabinet lifecycle checks are separate tests.
"""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from patch_tfr_compatibility import (DEFAULT_PARENT, ESTONIA_PARTIES,
                                     HOG_LOCALISATION_PATH, parent_patch, parse)
from clausewitz import Block, parse as clausewitz_parse


def shape(entry):
    return entry.key, entry.value, tuple(shape(child) for child in entry.children)


def child(entry, key):
    return next((item for item in entry.children if item.key == key), None)


def scalar(entry, key):
    item = child(entry, key)
    return item.value if item else None


def shared_definition(entries):
    return next(item for item in entries if item.key == "defined_text" and
                scalar(item, "name") == "head_of_gov_dynamic_loc")


class ExecutiveDisplayAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upstream_bytes = (DEFAULT_PARENT / HOG_LOCALISATION_PATH).read_bytes()
        cls.upstream_text = cls.upstream_bytes.decode("utf-8-sig")
        cls.patched_text, cls.audit = parent_patch(cls.upstream_text, HOG_LOCALISATION_PATH)
        cls.upstream = parse(cls.upstream_text)
        cls.patched = parse(cls.patched_text)

    def test_every_upstream_defined_text_entry_is_unchanged(self):
        original = shared_definition(self.upstream)
        patched = shared_definition(self.patched)
        additions = [entry for entry in patched.children if entry.key == "text" and
                     (scalar(entry, "localization_key") or "").startswith("TFR_EST_hog_")]
        retained = [entry for entry in patched.children if entry not in additions]
        self.assertEqual([shape(entry) for entry in original.children],
                         [shape(entry) for entry in retained])
        self.assertEqual([shape(entry) for entry in self.upstream if entry is not original],
                         [shape(entry) for entry in self.patched if entry is not patched])
        self.assertEqual(len(additions), 7)
        # The implementation only inserts content: all original selector text,
        # including portraits, date tests and other countries, survives exactly.
        for entry in original.children:
            self.assertIn(self.upstream_text[entry.start:entry.end], self.patched_text)

    def test_independent_parser_confirms_outer_insertion_with_compact_punctuation(self):
        # The upstream file contains NOT ={. An independent parser prevents a
        # shared tokenizer mistake from silently putting selectors inside that
        # country's text entry instead of at the outer defined_text level.
        upstream = clausewitz_parse(self.upstream_text)
        patched = clausewitz_parse(self.patched_text)
        self.assertEqual(len(upstream.entries), 1)
        self.assertEqual(len(patched.entries), 1)
        original = upstream.get("defined_text")
        current = patched.get("defined_text")
        extras = [entry for entry in current.entries if entry.key == "text" and
                  str(entry.value.get("localization_key", "")).startswith("TFR_EST_hog_")]
        self.assertEqual(len(extras), 7)

        def independent_shape(entry):
            value = (tuple(independent_shape(item) for item in entry.value.entries)
                     if isinstance(entry.value, Block) else entry.value)
            return entry.key, entry.op, value

        self.assertEqual([independent_shape(entry) for entry in original.entries],
                         [independent_shape(entry) for entry in current.entries if entry not in extras])

    def test_seven_selectors_follow_party_ledger_even_for_shared_ideologies(self):
        definition = shared_definition(self.patched)
        selectors = [entry for entry in definition.children if entry.key == "text" and
                     (scalar(entry, "localization_key") or "").startswith("TFR_EST_hog_")]
        self.assertEqual([scalar(entry, "localization_key") for entry in selectors],
                         [f"TFR_EST_hog_{party}" for party in ESTONIA_PARTIES])
        for party_id, entry in enumerate(selectors, 1):
            trigger = child(entry, "trigger")
            self.assertEqual([item.key for item in trigger.children],
                             ["TFR_EST_constitutional_executive", "check_variable"])
            self.assertEqual(scalar(trigger, "TFR_EST_constitutional_executive"), "yes")
            check = child(trigger, "check_variable")
            self.assertEqual(scalar(check, "var"), "TFR_EST_pm_party")
            self.assertEqual(scalar(check, "value"), str(party_id))
            self.assertEqual(scalar(check, "compare"), "equals")
        # Reform/Parempoolsed and Centre/Eesti 200 must select different records,
        # even though each pair projects into the same generic TFR ideology.
        self.assertNotEqual(scalar(child(child(selectors[0], "trigger"), "check_variable"), "value"),
                            scalar(child(child(selectors[6], "trigger"), "check_variable"), "value"))
        self.assertNotEqual(scalar(child(child(selectors[1], "trigger"), "check_variable"), "value"),
                            scalar(child(child(selectors[5], "trigger"), "check_variable"), "value"))

    def test_adapter_is_reproducible_and_baseline_hash_is_recorded(self):
        generated = self.patched_text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
        if self.upstream_bytes.startswith(b"\xef\xbb\xbf"):
            generated = b"\xef\xbb\xbf" + generated
        self.assertEqual((ROOT / HOG_LOCALISATION_PATH).read_bytes(), generated)
        manifest = json.loads((ROOT / "docs/compatibility.json").read_text(encoding="utf-8"))
        adapter = next(item for item in manifest["overrides"] if item["path"] == HOG_LOCALISATION_PATH)
        self.assertEqual(adapter["upstream_sha256"], hashlib.sha256(self.upstream_bytes).hexdigest())
        self.assertEqual(adapter["generated_sha256"], hashlib.sha256(generated).hexdigest())
        self.assertEqual(len(adapter["changes"]), 7)
        self.assertEqual(adapter["changes"], self.audit)

    def test_shared_gui_and_diplomacy_interface_are_inherited(self):
        self.assertFalse((ROOT / "common/scripted_guis/TFR_hog_gui.txt").exists())
        self.assertFalse((ROOT / "interface/countrydiplomacyview.gui").exists())
        self.assertFalse((ROOT / "localisation/english/TFR_hog_l_english.yml").exists())


if __name__ == "__main__":
    unittest.main()
