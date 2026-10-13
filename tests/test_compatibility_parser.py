"""Independent parsing regressions for generated parent compatibility patches."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from clausewitz import Block, atom, parse as independent_parse
from patch_tfr_compatibility import DEFAULT_PARENT, parse, walk


def patch_shape(entry):
    value = atom(entry.value) if isinstance(entry.value, str) else entry.value
    return entry.key, value, tuple(patch_shape(child) for child in entry.children)


def independent_shape(entry):
    if entry.op is None:
        return entry.key, None, ()
    if isinstance(entry.value, Block):
        return entry.key, None, tuple(independent_shape(child) for child in entry.value.entries)
    return entry.key, entry.value, ()


def matching(tree, key):
    return [entry for _, entry in tree.walk() if entry.key == key]


class CompatibilityParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / "docs/compatibility.json").read_text(encoding="utf-8"))
        cls.pairs = {}
        for override in manifest["overrides"]:
            path = override["path"]
            cls.pairs[path] = (
                independent_parse((DEFAULT_PARENT / path).read_text(encoding="utf-8-sig"), path),
                independent_parse((ROOT / path).read_text(encoding="utf-8-sig"), path),
            )

    def test_compact_operators_and_adjacent_braces_do_not_truncate_blocks(self):
        sources = (
            "outer={first = 1 NOT ={tag = MON} last = 2} after = 3",
            "outer={NOT ={OR={a=yes b=no}} end=4} after=5",
            "outer={check={value>=2 value!=3 value<=4}} tail={marker=yes}",
        )
        for source in sources:
            with self.subTest(source=source):
                self.assertEqual([patch_shape(entry) for entry in parse(source)],
                                 [independent_shape(entry) for entry in independent_parse(source).entries])

    def test_entire_installed_upstream_inventory_matches_independent_parser(self):
        for path, (upstream, _) in self.pairs.items():
            text = (DEFAULT_PARENT / path).read_text(encoding="utf-8-sig")
            self.assertEqual([patch_shape(entry) for entry in parse(text)],
                             [independent_shape(entry) for entry in upstream.entries], path)

    def test_independent_parser_retains_every_original_annex_action(self):
        for path, (upstream, patched) in self.pairs.items():
            self.assertEqual([independent_shape(entry) for entry in matching(upstream, "annex_country")],
                             [independent_shape(entry) for entry in matching(patched, "annex_country")], path)

    def test_independent_parser_retains_parent_war_and_story_dispatches(self):
        # Country/news event definitions enclose the actual changed settlements;
        # compare dispatch blocks rather than comparing that entire definition.
        def dispatches(tree, key):
            return [independent_shape(entry) for entry in matching(tree, key)
                    if not isinstance(entry.value, Block) or entry.value.get("option") is None]

        for path, (upstream, patched) in self.pairs.items():
            for key in ("declare_war_on", "white_peace", "country_event", "news_event",
                        "complete_national_focus", "load_oob", "set_global_flag", "clr_global_flag"):
                self.assertEqual(dispatches(upstream, key), dispatches(patched, key), f"{path}: {key}")

    def test_late_file_estonia_paths_are_protected_after_compact_parent_source(self):
        # The prior tokenizer ended before these real later-file campaign hooks.
        decisions = parse((ROOT / "common/decisions/TFR_decisions_SOV.txt").read_text(encoding="utf-8-sig"))
        restore = next(entry for entry, _ in walk(decisions) if entry.key == "SOV_restore_order_estonia")
        keys = [entry.key for entry, _ in walk(restore.children)]
        self.assertIn("TFR_EST_russian_occupation_or_absent", keys)
        self.assertIn("any_owned_state", keys)
        self.assertIn("is_owned_by", keys)
        events = parse((ROOT / "events/TFR_events_SOV.txt").read_text(encoding="utf-8-sig"))
        event = next(entry for entry in events if entry.key == "country_event" and
                     any(item.key == "id" and item.value == "russia.589" for item in entry.children))
        self.assertIn("TFR_EST_preserve_annexation", [entry.key for entry, _ in walk(event.children)])


if __name__ == "__main__":
    unittest.main()
