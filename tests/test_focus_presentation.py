"""Presentation contracts for compact trees and unchanged focus descriptions.

Coordinates are checked for usable bounds, collisions and graph direction. The
description fixture was captured before the 16 October presentation revision;
it deliberately hashes the literal localization values, including punctuation
and escapes, rather than descriptions imported from a generator after editing.
"""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import unittest

from script_runtime import ROOT, Block, parse


FOCUS_FILES = (
    "TFR_EST_opening.txt", "TFR_EST_ratas.txt", "TFR_EST_kallas.txt",
    "TFR_EST_normal.txt", "TFR_EST_occupation.txt",
)


def focus_catalog(filename):
    path = ROOT / "common/national_focus" / filename
    tree = parse(path.read_text(encoding="utf-8-sig"), str(path))
    return {
        entry.value.get("id"): entry.value
        for _, entry in tree.walk()
        if entry.key in ("focus", "shared_focus")
        and isinstance(entry.value, Block) and entry.value.get("id")
    }


def localization_values():
    values = {}
    for path in (ROOT / "localisation/english").glob("TFR_EST*.yml"):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = re.match(r"^\s*(\S+):\d+\s+(.+)$", line)
            if match:
                if match[1] in values:
                    raise AssertionError(f"Duplicate localization: {match[1]}")
                values[match[1]] = match[2]
    return values


class FocusPresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogs = {name: focus_catalog(name) for name in FOCUS_FILES}
        cls.focuses = {key: value for catalog in cls.catalogs.values()
                       for key, value in catalog.items()}
        fixture = ROOT / "tests/fixtures/focus_description_hashes.json"
        cls.description_hashes = json.loads(fixture.read_text(encoding="utf-8"))["descriptions"]
        cls.localization = localization_values()

    def test_description_snapshot_covers_every_existing_focus(self):
        self.assertEqual(len(self.focuses), 235)
        self.assertEqual({name + "_desc" for name in self.focuses},
                         set(self.description_hashes))

    def test_all_235_focus_description_values_are_byte_for_byte_unchanged(self):
        for key, expected in self.description_hashes.items():
            with self.subTest(key=key):
                self.assertIn(key, self.localization)
                actual = hashlib.sha256(self.localization[key].encode("utf-8")).hexdigest()
                self.assertEqual(actual, expected,
                                 "Focus descriptions must stay unchanged during this revision")

    def test_compact_widths_and_heights(self):
        # One coordinate is one engine focus-grid unit. These bounds preserve
        # label spacing while substantially reducing the old 15/16/39/36 spans.
        limits = {
            "TFR_EST_opening.txt": (10, 3),
            "TFR_EST_ratas.txt": (8, 7),
            "TFR_EST_kallas.txt": (8, 6),
            "TFR_EST_normal.txt": (26, None),
            "TFR_EST_occupation.txt": (12, 11),
        }
        for name, (max_width, max_height) in limits.items():
            positions = [(int(f.get("x")), int(f.get("y")))
                         for f in self.catalogs[name].values()]
            with self.subTest(tree=name):
                self.assertLessEqual(max(x for x, _ in positions) - min(x for x, _ in positions),
                                     max_width)
                if max_height is not None:
                    self.assertLessEqual(max(y for _, y in positions) - min(y for _, y in positions),
                                         max_height)

    def test_opening_uses_four_compact_branches_and_one_final_row(self):
        expected = {
            "pension_reform": (0, 0), "pension_increase": (0, 1),
            "teacher_pay": (2, 0), "research_budget": (2, 1),
            "kose_voobu": (5, 0), "eastern_border": (4, 1),
            "three_seas": (6, 1), "covid_emergency": (9, 0),
            "wage_compensation": (8, 1), "excise_relief": (10, 1),
            "marriage_referendum": (5, 3),
        }
        actual = {
            key.removeprefix("TFR_EST_opening_"): (int(value.get("x")), int(value.get("y")))
            for key, value in self.catalogs["TFR_EST_opening.txt"].items()
        }
        self.assertEqual(actual, expected)

    def test_retained_ratas_and_kallas_share_compact_five_branch_columns(self):
        for filename, prefix, root, conclusion, root_y, end_y in (
            ("TFR_EST_ratas.txt", "TFR_EST_ratas_", "renew_agreement", "account_to_voters", 4, 11),
            ("TFR_EST_kallas.txt", "TFR_EST_kallas_", "govern_together", "account_to_voters", 0, 6),
        ):
            catalog = self.catalogs[filename]
            root_id = prefix + root
            with self.subTest(tree=filename):
                self.assertEqual((int(catalog[root_id].get("x")), int(catalog[root_id].get("y"))),
                                 (4, root_y))
                self.assertEqual((int(catalog[prefix + conclusion].get("x")),
                                  int(catalog[prefix + conclusion].get("y"))), (4, end_y))
                children = [focus for focus in catalog.values()
                            if any(root_id in block.all("focus")
                                   for block in focus.all("prerequisite"))]
                self.assertEqual(sorted(int(focus.get("x")) for focus in children),
                                 [0, 2, 4, 6, 8])
                self.assertEqual({int(focus.get("y")) for focus in children}, {root_y + 1})

    def test_no_focus_icon_collisions_within_a_programme(self):
        # Different mandates share a tree but are mutually hidden. Check each
        # actual programme separately, including all seven occupation variants.
        for name, catalog in self.catalogs.items():
            positions = defaultdict(list)
            for focus_id, focus in catalog.items():
                positions[(focus.get("x"), focus.get("y"))].append(focus_id)
            with self.subTest(tree=name):
                self.assertFalse({position: ids for position, ids in positions.items()
                                  if len(ids) > 1})

    def test_prerequisite_connections_always_point_down_the_tree(self):
        for focus_id, focus in self.focuses.items():
            for block in focus.all("prerequisite"):
                for parent_id in block.all("focus"):
                    if parent_id in self.focuses:
                        with self.subTest(child=focus_id, parent=parent_id):
                            self.assertGreater(int(focus.get("y")),
                                               int(self.focuses[parent_id].get("y")))

    def test_parallel_nodes_keep_two_grid_units_for_their_labels(self):
        for name, catalog in self.catalogs.items():
            rows = defaultdict(list)
            for focus in catalog.values():
                rows[int(focus.get("y"))].append(int(focus.get("x")))
            for y, values in rows.items():
                ordered = sorted(values)
                for left, right in zip(ordered, ordered[1:]):
                    with self.subTest(tree=name, row=y, left=left, right=right):
                        self.assertGreaterEqual(right - left, 2)


if __name__ == "__main__":
    unittest.main()
