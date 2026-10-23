"""Exercise party artwork selection without changing Estonia's political ledger.

The game still owns native rendering. These checks cover the shared-ideology
parties, party-chair/caretaker distinction and the country-context UI binding.
"""
import unittest

from script_runtime import ROOT, Runtime, parse
from patch_tfr_compatibility import DEFAULT_PARENT


PARTIES = ("reform", "centre", "ekre", "isamaa", "sde", "e200", "pp")
DEFAULTS = (
    "reform_kallas", "centre_ratas", "ekre_mart", "isamaa_seeder",
    "sde_saar", "e200_kallas", "pp_perling",
)
VARIANTS = (
    (1, "reform", "reform_michal", "TFR_EST_kallas_departed_for_europe"),
    (2, "centre", "centre_kiik", "TFR_EST_centre_leader_kiik"),
    (2, "centre", "centre_kolvart", "TFR_EST_centre_leader_kolvart"),
    (3, "ekre", "ekre_martin", "TFR_EST_martin_leads_ekre"),
    (5, "sde", "sde_laanemets", "TFR_EST_laanemets_leads_sde"),
)


def read(relative):
    return parse((ROOT / relative).read_text(encoding="utf-8-sig"), relative)


class IdeologyIconSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = read("common/scripted_localisation/TFR_EST_ideology_icons.txt")
        cls.selectors = {entry.value.get("name"): entry.value
                         for entry in tree.entries}
        cls.sprites = {
            entry.value.get("name"): entry.value.get("texturefile")
            for entry in read("interface/TFR_EST_ideology_icons.gfx").get("spriteTypes").entries
        }
        cls.diplomacy = read("common/scripted_guis/TFR_EST_ideology_icons.txt").get(
            "scripted_gui").get("TFR_EST_diplomacy_ideology_icon")

    def select(self, runtime, name):
        for selector in self.selectors[name].all("text"):
            if runtime.condition(selector.get("trigger")):
                return selector.get("localization_key")
        self.fail(f"No applicable selector in {name}")

    def expected(self, icon_id):
        return "GFX_TFR_EST_ideology_" + icon_id

    def test_every_party_has_distinct_default_art_despite_shared_native_ideologies(self):
        runtime = Runtime()
        selected = []
        for party_id, (party, icon_id) in enumerate(zip(PARTIES, DEFAULTS), 1):
            with self.subTest(party=party):
                runtime.variables["TFR_EST_pm_party"] = party_id
                party_icon = self.select(runtime, "TFR_EST_ideology_icon_" + party)
                ruling_icon = self.select(runtime, "TFR_EST_ruling_ideology_icon")
                self.assertEqual(party_icon, self.expected(icon_id))
                self.assertEqual(ruling_icon, party_icon)
                self.assertIn(party_icon, self.sprites)
                selected.append(party_icon)
        self.assertEqual(len(set(selected)), 7)

    def test_party_career_history_updates_opposition_icons_without_changing_cabinet(self):
        for party_id, party, icon_id, flag in VARIANTS:
            with self.subTest(icon=icon_id):
                runtime = Runtime()
                runtime.variables["TFR_EST_pm_party"] = 7
                runtime.flags.add(flag)
                before = (dict(runtime.variables), set(runtime.flags), runtime.leader)
                self.assertEqual(self.select(runtime, "TFR_EST_ideology_icon_" + party),
                                 self.expected(icon_id))
                self.assertEqual(self.select(runtime, "TFR_EST_ruling_ideology_icon"),
                                 self.expected("pp_perling"))
                self.assertEqual((runtime.variables, runtime.flags, runtime.leader), before)

    def test_caretaker_keeps_incumbent_portrait_until_actual_pm_identity_changes(self):
        cases = (
            (2, "centre", "centre_ratas", "centre_kiik",
             "TFR_EST_centre_leader_kiik", "TFR_EST_pm_person_tanel_kiik"),
            (2, "centre", "centre_ratas", "centre_kolvart",
             "TFR_EST_centre_leader_kolvart", "TFR_EST_pm_person_mihhail_kolvart"),
            (5, "sde", "sde_saar", "sde_laanemets",
             "TFR_EST_laanemets_leads_sde", "TFR_EST_pm_person_lauri_laanemets"),
        )
        for party_id, party, old, new, chair_flag, pm_flag in cases:
            with self.subTest(party=party, successor=new):
                runtime = Runtime()
                runtime.variables["TFR_EST_pm_party"] = party_id
                runtime.flags.update({chair_flag, "TFR_EST_caretaker"})
                self.assertEqual(self.select(runtime, "TFR_EST_ideology_icon_" + party),
                                 self.expected(new))
                self.assertEqual(self.select(runtime, "TFR_EST_ruling_ideology_icon"),
                                 self.expected(old))
                runtime.flags.discard("TFR_EST_caretaker")
                runtime.flags.add(pm_flag)
                self.assertEqual(self.select(runtime, "TFR_EST_ruling_ideology_icon"),
                                 self.expected(new))

    def test_reform_and_ekre_ruling_variants_follow_existing_career_markers(self):
        for party_id, flag, icon_id in (
            (1, "TFR_EST_kallas_departed_for_europe", "reform_michal"),
            (3, "TFR_EST_martin_leads_ekre", "ekre_martin"),
        ):
            with self.subTest(icon=icon_id):
                runtime = Runtime()
                runtime.variables["TFR_EST_pm_party"] = party_id
                runtime.flags.add(flag)
                self.assertEqual(self.select(runtime, "TFR_EST_ruling_ideology_icon"),
                                 self.expected(icon_id))

    def test_all_twelve_sprites_are_selected_and_use_expected_runtime_paths(self):
        selected = set()
        for name, definition in self.selectors.items():
            if name.startswith("TFR_EST_ideology_icon_"):
                selected.update(item.get("localization_key") for item in definition.all("text"))
        self.assertEqual(len(selected), 12)
        self.assertEqual(selected, set(self.sprites))
        for sprite, texture in self.sprites.items():
            self.assertEqual(texture, "gfx/interface/ideologies/EST/" +
                             sprite.removeprefix("GFX_TFR_EST_ideology_") + ".png")

    def test_diplomacy_uses_selected_country_context_and_releases_unsupported_countries(self):
        self.assertEqual(self.diplomacy.get("context_type"), "selected_country_context")
        self.assertEqual(self.diplomacy.get("parent_window_token"),
                         "selected_country_view_diplomacy")
        visible = self.diplomacy.get("visible")
        runtime = Runtime()
        runtime.variables["TFR_EST_pm_party"] = 2
        self.assertTrue(runtime.condition(visible))
        for prop, value in (("original_tag", "LAT"), ("is_subject", "yes")):
            with self.subTest(prop=prop):
                original = runtime.props[prop]
                runtime.props[prop] = value
                self.assertFalse(runtime.condition(visible))
                runtime.props[prop] = original
        for flag in ("TFR_EST_occupied",):
            runtime.flags.add(flag)
            self.assertFalse(runtime.condition(visible))
            runtime.flags.discard(flag)
        for party_id in (0, 8):
            runtime.variables["TFR_EST_pm_party"] = party_id
            self.assertFalse(runtime.condition(visible))
        runtime.variables["TFR_EST_pm_party"] = 2
        runtime.flags.discard("TFR_EST_initialized")
        self.assertFalse(runtime.condition(visible))

    def test_seven_parliament_images_bind_to_party_office_selectors(self):
        panel = read("common/scripted_guis/TFR_EST_parliament.txt").get(
            "scripted_gui").get("TFR_EST_parliament_panel")
        gui = read("interface/TFR_EST_parliament.gui").get("guiTypes").get("containerWindowType")
        images = {item.get("name"): item for item in gui.all("iconType")}
        for party in PARTIES:
            name = "TFR_EST_ideology_" + party
            self.assertIn(name, images)
            self.assertEqual(panel.get("properties").get(name).get("image"),
                             "[TFR_EST_ideology_icon_" + party + "]")
            self.assertIn(images[name].get("spriteType"), self.sprites)
            # The scaled 68 px icon fits inside each existing 27 px row.
            self.assertLessEqual(68 * float(images[name].get("scale")), 25)

    def test_diplomacy_backdrop_repaints_the_exact_inherited_panel_region(self):
        parent_gui = parse((DEFAULT_PARENT / "interface/countrydiplomacyview.gui").read_text(
            encoding="utf-8-sig"))
        parent_window = next(item for item in parent_gui.get("guiTypes").all("containerWindowType")
                             if item.get("name") == "countrydiplomacyview")
        country_info = next(item for item in parent_window.all("containerWindowType")
                            if item.get("name") == "country_info")
        native = {item.get("name"): item for item in country_info.all("iconType")}
        overlay = read("interface/TFR_EST_ideology_icons.gui").get("guiTypes").get("containerWindowType")
        self.assertEqual(overlay.get("clipping"), "yes")
        for axis in ("x", "y"):
            self.assertEqual(overlay.get("position").get(axis),
                             native["ideology_icon"].get("position").get(axis))
        backdrop = next(item for item in overlay.all("iconType")
                        if item.get("name") == "TFR_EST_diplomacy_ideology_backdrop")
        original = native["diplo_upper_win_bg"]
        self.assertEqual(backdrop.get("spriteType"), original.get("spriteType"))
        for axis in ("x", "y"):
            self.assertEqual(int(backdrop.get("position").get(axis)),
                             int(original.get("position").get(axis)) -
                             int(overlay.get("position").get(axis)))
        outer = overlay.get("containerWindowType")
        self.assertEqual(outer.get("background").get("spriteType"),
                         parent_window.get("background").get("spriteType"))
        self.assertEqual(outer.get("size").get("width"), parent_window.get("size").get("width"))
        for axis in ("x", "y"):
            self.assertEqual(int(outer.get("position").get(axis)),
                             -int(country_info.get("position").get(axis)) -
                             int(overlay.get("position").get(axis)))


if __name__ == "__main__":
    unittest.main()
