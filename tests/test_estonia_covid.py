"""Exercise the first-case bridge against TFR's actual infection trigger."""
from datetime import date
import unittest

from script_runtime import ROOT, Runtime, parse
from build_estonia_covid import build_effects, build_events, build_localisation


RECORDED = "TFR_EST_covid_first_case_recorded"
PENDING = "TFR_EST_covid_first_case_pending"
OWNED = "TFR_EST_covid_seed_owned"
EVENT = "tfr_estonia_covid.1"
TIERS = (
    "lower_covid_cases", "low_covid_cases", "medium_covid_cases",
    "high_covid_cases", "higher_covid_cases",
)


class EstoniaCovidTests(unittest.TestCase):
    def runtime(self, when=date(2020, 2, 27)):
        r = Runtime()
        # Import the real inherited trigger, never replace it with a test boolean.
        path = ROOT / "common/scripted_triggers/00_TFR_scripted_triggers_ZZZ_generic.txt"
        parent = parse(path.read_text(encoding="utf-8-sig"), str(path))
        r.triggers["generic_has_corona"] = parent.get("generic_has_corona")
        r.props["date"] = when
        return r

    def event(self):
        path = ROOT / "events/TFR_EST_covid.txt"
        tree = parse(path.read_text(encoding="utf-8-sig"), str(path))
        return next(e.value for e in tree.entries
                    if e.key == "country_event" and e.value.get("id") == EVENT)

    def deliver(self, r):
        self.assertTrue(r.condition(self.event().get("trigger")))
        r.run(self.event().get("immediate"))

    def test_no_outbreak_or_queue_before_first_case_announcement(self):
        for when in (date(2020, 1, 1), date(2020, 2, 26)):
            with self.subTest(when=when):
                r = self.runtime(when)
                r.call("TFR_EST_covid_tick")
                self.assertFalse(r.ideas)
                self.assertFalse(r.events)
                self.assertNotIn(RECORDED, r.flags)
                self.assertFalse(r.condition(self.event().get("trigger")))
                r.call("TFR_EST_register_covid_first_case")
                self.assertFalse(r.ideas)
                self.assertNotIn(RECORDED, r.flags)

    def test_country_event_seeds_actual_parent_presence_independently_of_focus(self):
        r = self.runtime()
        r.call("TFR_EST_covid_tick")
        self.assertEqual(r.events, [EVENT])
        self.assertIn(PENDING, r.flags)
        self.assertFalse(r.ideas, "Queuing a notice does not yet manufacture infection")
        self.deliver(r)
        self.assertEqual(r.ideas, {TIERS[0]})
        self.assertTrue(r.condition(r.triggers["generic_has_corona"]))
        self.assertIn(RECORDED, r.flags)
        self.assertIn(OWNED, r.flags)
        self.assertNotIn(PENDING, r.flags)
        self.assertFalse(r.props["completed_focuses"])
        self.assertNotIn("TFR_EST_opening_covid_announced", r.flags)

    def test_queued_notice_and_delivery_are_one_time(self):
        r = self.runtime()
        r.call("TFR_EST_covid_tick")
        r.call("TFR_EST_covid_tick")
        self.assertEqual(r.events.count(EVENT), 1)
        self.deliver(r)
        r.call("TFR_EST_register_covid_first_case")
        r.call("TFR_EST_covid_tick")
        self.assertEqual(r.events.count(EVENT), 1)
        self.assertEqual(r.messages.count("TFR_EST_COVID_FIRST_CASE_RECORDED"), 1)
        self.assertFalse(r.condition(self.event().get("trigger")))
        queue = next(entry.value for _, entry in r.effects["TFR_EST_covid_tick"].walk()
                     if entry.key == "country_event")
        self.assertEqual(queue.get("hours"), "1")
        pending = next(entry.value for _, entry in r.effects["TFR_EST_covid_tick"].walk()
                       if entry.key == "set_country_flag" and hasattr(entry.value, "get"))
        self.assertEqual(pending.get("days"), "2")

    def test_existing_parent_infection_at_any_tier_is_preserved(self):
        for tier in TIERS:
            with self.subTest(tier=tier):
                r = self.runtime()
                r.ideas.add(tier)
                r.call("TFR_EST_covid_tick")
                self.assertEqual(r.ideas, {tier})
                self.assertIn(RECORDED, r.flags)
                self.assertNotIn(OWNED, r.flags)
                self.assertFalse(r.events)

    def test_external_infection_arriving_between_queue_and_delivery_is_preserved(self):
        for tier in TIERS:
            with self.subTest(tier=tier):
                r = self.runtime()
                r.call("TFR_EST_covid_tick")
                r.ideas.add(tier)
                self.deliver(r)
                self.assertEqual(r.ideas, {tier})
                self.assertIn(RECORDED, r.flags)
                self.assertNotIn(OWNED, r.flags)

    def test_external_infection_before_delivery_suppresses_obsolete_notice(self):
        r = self.runtime()
        r.call("TFR_EST_covid_tick")
        r.ideas.add("medium_covid_cases")
        r.call("TFR_EST_covid_tick")
        self.assertIn(RECORDED, r.flags)
        self.assertNotIn(PENDING, r.flags)
        self.assertFalse(r.condition(self.event().get("trigger")))
        self.assertEqual(r.ideas, {"medium_covid_cases"})

    def test_recovery_never_reseeds_an_already_recorded_outbreak(self):
        for origin in ("bridge", "external"):
            with self.subTest(origin=origin):
                r = self.runtime()
                if origin == "bridge":
                    r.call("TFR_EST_register_covid_first_case")
                else:
                    r.ideas.add("high_covid_cases")
                    r.call("TFR_EST_covid_tick")
                r.ideas.clear()
                r.props["date"] = date(2021, 1, 1)
                r.call("TFR_EST_covid_tick")
                r.call("TFR_EST_register_covid_first_case")
                self.assertFalse(r.ideas)
                self.assertFalse(r.events)
                self.assertIn(RECORDED, r.flags)
                self.assertNotIn(OWNED, r.flags)

    def test_severity_change_relinquishes_seed_ownership(self):
        r = self.runtime()
        r.call("TFR_EST_register_covid_first_case")
        r.ideas = {"medium_covid_cases"}
        r.call("TFR_EST_covid_tick")
        self.assertNotIn(OWNED, r.flags)
        r.props["date"] = date(2023, 1, 1)
        r.call("TFR_EST_covid_tick")
        self.assertEqual(r.ideas, {"medium_covid_cases"})

    def test_january_2023_cleans_only_the_owned_lowest_tier(self):
        r = self.runtime()
        r.call("TFR_EST_register_covid_first_case")
        r.flags.add("TFR_EST_done_opening_covid_emergency")
        r.props["date"] = date(2022, 12, 31)
        r.call("TFR_EST_covid_tick")
        self.assertEqual(r.ideas, {TIERS[0]})
        r.props["date"] = date(2023, 1, 1)
        r.call("TFR_EST_covid_tick")
        self.assertFalse(r.ideas)
        self.assertIn(RECORDED, r.flags)
        self.assertNotIn(OWNED, r.flags)
        r.call("TFR_EST_covid_tick")
        self.assertFalse(r.ideas)
        self.assertFalse(r.events)

    def test_delayed_mandatory_response_keeps_owned_infection_until_completed(self):
        for completion in ("reward_flag", "completed_focus"):
            with self.subTest(completion=completion):
                r = self.runtime()
                r.call("TFR_EST_register_covid_first_case")
                r.props["date"] = date(2023, 1, 1)
                r.call("TFR_EST_covid_tick")
                self.assertEqual(r.ideas, {TIERS[0]})
                self.assertIn(OWNED, r.flags)
                self.assertIn(RECORDED, r.flags)
                self.assertFalse(r.events)
                self.assertTrue(r.condition(r.triggers["generic_has_corona"]))
                if completion == "reward_flag":
                    r.flags.add("TFR_EST_done_opening_covid_emergency")
                else:
                    r.props["completed_focuses"].add("TFR_EST_opening_covid_emergency")
                r.call("TFR_EST_covid_tick")
                self.assertFalse(r.ideas)
                self.assertNotIn(OWNED, r.flags)
                self.assertIn(RECORDED, r.flags)
                r.call("TFR_EST_covid_tick")
                self.assertFalse(r.ideas)
                self.assertFalse(r.events)

    def test_january_2023_preserves_externally_owned_tiers(self):
        for tier in TIERS:
            with self.subTest(tier=tier):
                r = self.runtime(date(2023, 1, 1))
                r.ideas.add(tier)
                r.flags.add("TFR_EST_done_opening_covid_emergency")
                r.call("TFR_EST_covid_tick")
                self.assertEqual(r.ideas, {tier})
                self.assertNotIn(OWNED, r.flags)
                self.assertFalse(r.events)

    def test_no_first_case_seed_or_event_in_2023_and_later(self):
        for when in (date(2023, 1, 1), date(2024, 2, 27)):
            with self.subTest(when=when):
                r = self.runtime(when)
                r.call("TFR_EST_covid_tick")
                r.call("TFR_EST_register_covid_first_case")
                self.assertFalse(r.ideas)
                self.assertFalse(r.events)
                self.assertNotIn(RECORDED, r.flags)
                self.assertFalse(r.condition(self.event().get("trigger")))

    def test_other_countries_are_untouched_by_helpers_or_event(self):
        for helper in ("TFR_EST_covid_tick", "TFR_EST_register_covid_first_case"):
            with self.subTest(helper=helper):
                r = self.runtime()
                r.props["tag"] = "GER"
                r.flags.add(OWNED)
                r.ideas.add("low_covid_cases")
                before = (r.flags.copy(), r.ideas.copy())
                r.call(helper)
                self.assertEqual((r.flags, r.ideas), before)
                self.assertFalse(r.events)
                self.assertFalse(r.condition(self.event().get("trigger")))

    def test_generated_files_are_current_and_localisation_has_bom(self):
        outputs = {
            "common/scripted_effects/TFR_EST_covid.txt": build_effects().encode("utf-8"),
            "events/TFR_EST_covid.txt": build_events().encode("utf-8"),
            "localisation/english/TFR_EST_covid_l_english.yml": build_localisation().encode("utf-8-sig"),
        }
        for relative, expected in outputs.items():
            with self.subTest(path=relative):
                self.assertEqual((ROOT / relative).read_bytes(), expected)
        self.assertTrue((ROOT / "localisation/english/TFR_EST_covid_l_english.yml").read_bytes().startswith(b"\xef\xbb\xbf"))


if __name__ == "__main__":
    unittest.main()
