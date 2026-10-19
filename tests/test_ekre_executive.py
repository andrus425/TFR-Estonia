"""Keep the 2023 EKRE prime minister distinct from cabinet candidates.

Primary historical anchors:
https://www.ekre.ee/martin-helme-ekre-programmi-esitlusel-valimiste-pohikusimus-on-kas-eesti-jaab-meie-rahvuskoduks/
https://www.riigikogu.ee/pressiteated/muu-pressiteade-et/riigikogu-juhatus-registreeris-kuus-fraktsiooni/

EKRE identified Martin as chairman at its January 2023 programme launch, and
the Riigikogu registered him as its faction chair in April. Becoming PM is the
mod's alternate election outcome, not a claim that EKRE formed that government.
"""
from copy import deepcopy
from datetime import date
import unittest

from script_runtime import ROOT, Runtime, parse


CAREER = 'TFR_EST_martin_leads_ekre'
PERSON = 'TFR_EST_pm_person_martin_helme'
MART = 'TFR_EST_pm_ekre'
MARTIN = 'TFR_EST_pm_ekre_martin'
ACTIVE = 'TFR_EST_ekre_2023_mandate'
ENDED = 'TFR_EST_ekre_2023_mandate_ended'
PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')


class EkreExecutiveTests(unittest.TestCase):
    def fresh(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        return r

    def elect(self, r, party='ekre', election_date=date(2023, 3, 5)):
        r.props['date'] = election_date
        for p in PARTIES:
            r.variables['TFR_EST_active_' + p] = 1
            r.variables['TFR_EST_support_' + p] = 10000 if p == party else 0
        r.variables['TFR_EST_support_other'] = 0
        r.call('TFR_EST_hold_election')

    def runtime(self, confirmed=True):
        r = self.fresh()
        self.elect(r)
        # This fixture consumes the election controller's public metadata. The
        # separate programme suite verifies its actual historical vote hook.
        r.flags.update({ACTIVE, 'TFR_EST_ekre_won_2023_election'})
        r.flags.discard(ENDED)
        if confirmed:
            r.call('TFR_EST_confirm_cabinet')
        return r

    def named_pm(self, r):
        texts = parse((ROOT / 'common/scripted_localisation/TFR_EST_executive.txt').read_text()).get('defined_text')
        return next(e.value.get('localization_key') for e in texts.entries
                    if e.key == 'text' and r.condition(e.value.get('trigger')))

    def eligible(self, r, person, portfolio):
        return r.test(f'TFR_EST_can_appoint_{person}_{portfolio}', '=', 'yes')

    def test_opening_centre_cabinet_and_mart_helme_minister_are_preserved(self):
        r = self.fresh()
        r.call('TFR_EST_initialize_ministers')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertIn('TFR_EST_pm_centre', r.ideas)
        self.assertIn('TFR_EST_minister_mart_helme_interior', r.ideas)
        self.assertNotIn(CAREER, r.flags)
        self.assertNotIn(PERSON, r.flags)
        self.assertTrue(self.eligible(r, 'martin_helme', 'economic'))

    def test_ekre_government_before2023_keeps_mart_as_default(self):
        r = self.fresh()
        self.elect(r, election_date=date(2022, 10, 1))
        r.call('TFR_EST_confirm_cabinet')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 3)
        self.assertIn(MART, r.ideas)
        self.assertNotIn(MARTIN, r.ideas)
        self.assertNotIn(CAREER, r.flags)
        self.assertEqual(self.named_pm(r), 'TFR_EST_mart_helme')
        self.assertTrue(self.eligible(r, 'martin_helme', 'economic'))

    def test_2023_caretaker_keeps_outgoing_pm_until_confirmation(self):
        r = self.runtime(confirmed=False)
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        r.call('TFR_EST_reconcile_executive_display')
        r.call('TFR_EST_reconcile_ministers')
        self.assertNotIn(CAREER, r.flags)
        self.assertNotIn(PERSON, r.flags)
        self.assertIn('TFR_EST_pm_centre', r.ideas)
        self.assertNotIn(MARTIN, r.ideas)

    def test_outgoing_ekre_caretaker_is_not_prematurely_replaced(self):
        r = self.fresh()
        self.elect(r, election_date=date(2022, 10, 1))
        r.call('TFR_EST_confirm_cabinet')
        self.elect(r)
        r.flags.update({ACTIVE, 'TFR_EST_ekre_won_2023_election'})
        r.flags.discard(ENDED)
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn(MART, r.ideas)
        self.assertNotIn(MARTIN, r.ideas)
        self.assertNotIn(CAREER, r.flags)
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(MARTIN, r.ideas)
        self.assertNotIn(MART, r.ideas)

    def test_confirmed2023_cabinet_selects_martin_without_changing_president(self):
        r = self.runtime(confirmed=False)
        president = r.leader
        seats = tuple(r.variables['TFR_EST_seats_' + p] for p in PARTIES)
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(CAREER, r.flags)
        self.assertIn(PERSON, r.flags)
        self.assertIn(MARTIN, r.ideas)
        self.assertNotIn(MART, r.ideas)
        self.assertEqual(self.named_pm(r), 'TFR_EST_martin_helme')
        self.assertEqual(r.variables['TFR_EST_pm_party'], 3)
        self.assertEqual(r.variables['TFR_EST_mandate_party'], 3)
        self.assertEqual(tuple(r.variables['TFR_EST_seats_' + p] for p in PARTIES), seats)
        self.assertEqual(r.leader, president)

    def test_other_party_wrong_mandate_and_ended_metadata_do_not_create_career(self):
        for case in ('other_party', 'wrong_mandate', 'ended'):
            with self.subTest(case=case):
                r = self.runtime(confirmed=False)
                r.flags.discard('TFR_EST_caretaker')
                r.variables['TFR_EST_pm_party'] = 3
                if case == 'other_party': r.variables['TFR_EST_pm_party'] = 2
                if case == 'wrong_mandate': r.variables['TFR_EST_mandate_party'] = 2
                if case == 'ended': r.flags.add(ENDED)
                r.call('TFR_EST_reconcile_ekre_pm_identity')
                self.assertNotIn(CAREER, r.flags)
                self.assertNotIn(PERSON, r.flags)

    def test_finance_minister_excluded_and_rene_kokk_remains_eligible(self):
        r = self.runtime()
        self.assertFalse(self.eligible(r, 'martin_helme', 'economic'))
        self.assertTrue(self.eligible(r, 'rene_kokk', 'economic'))
        self.assertTrue(self.eligible(r, 'mart_helme', 'foreign'))
        self.assertTrue(self.eligible(r, 'mart_helme', 'interior'))
        r.ideas.add('TFR_EST_minister_mart_helme_foreign')
        self.assertFalse(self.eligible(r, 'mart_helme', 'interior'))

    def test_minister_reconciliation_derives_pm_before_candidate_exclusions(self):
        r = self.runtime(confirmed=False)
        r.variables['TFR_EST_pm_party'] = 3
        r.flags.discard('TFR_EST_caretaker')
        r.ideas.discard('TFR_EST_minister_mart_helme_interior')
        r.ideas.update({'TFR_EST_minister_martin_helme_economic',
                        'TFR_EST_minister_mart_helme_foreign'})
        r.call('TFR_EST_reconcile_ministers')
        self.assertIn(CAREER, r.flags)
        self.assertIn(PERSON, r.flags)
        self.assertNotIn('TFR_EST_minister_martin_helme_economic', r.ideas)
        self.assertIn('TFR_EST_minister_mart_helme_foreign', r.ideas)

    def test_confirmation_keeps_mart_portfolio_when_martin_becomes_pm(self):
        r = self.fresh()
        r.call('TFR_EST_initialize_ministers')
        self.elect(r)
        r.flags.update({ACTIVE, 'TFR_EST_ekre_won_2023_election'})
        r.flags.discard(ENDED)
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(MARTIN, r.ideas)
        self.assertIn('TFR_EST_minister_mart_helme_interior', r.ideas)
        self.assertFalse(self.eligible(r, 'mart_helme', 'foreign'))
        self.assertTrue(self.eligible(r, 'rene_kokk', 'economic'))

    def test_ordinary_caretaker_keeps_already_confirmed_martin(self):
        r = self.runtime()
        r.call('TFR_EST_enter_caretaker')
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn(CAREER, r.flags)
        self.assertIn(PERSON, r.flags)
        self.assertIn(MARTIN, r.ideas)
        self.assertFalse(self.eligible(r, 'rene_kokk', 'economic'))

    def test_future_ekre_election_and_person_marker_repair_keep_martin(self):
        r = self.runtime()
        self.elect(r, election_date=date(2028, 3, 5))
        r.flags.add(ENDED)
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(CAREER, r.flags)
        self.assertIn(MARTIN, r.ideas)
        r.flags.discard(PERSON)
        r.call('TFR_EST_reconcile_ministers')
        self.assertIn(PERSON, r.flags)
        self.assertFalse(self.eligible(r, 'martin_helme', 'economic'))

    def test_other_party_replaces_personal_marker_but_not_ekre_career(self):
        r = self.runtime()
        self.elect(r, 'centre', date(2028, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(CAREER, r.flags)
        self.assertNotIn(PERSON, r.flags)
        self.assertNotIn(MARTIN, r.ideas)
        self.assertIn('TFR_EST_pm_centre', r.ideas)
        self.assertEqual(self.named_pm(r), 'TFR_EST_juri_ratas')
        self.elect(r, election_date=date(2032, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(MARTIN, r.ideas)
        self.assertIn(PERSON, r.flags)

    def test_occupation_preserves_career_and_restoration_repairs_martin(self):
        r = self.runtime()
        r.flags.add('TFR_EST_occupied')
        r.props['is_subject'] = 'yes'
        r.leader = 'EST_yana_toom_char'
        r.call('TFR_EST_reconcile_executive_display')
        r.call('TFR_EST_reconcile_ministers')
        self.assertIn(CAREER, r.flags)
        self.assertNotIn(PERSON, r.flags)
        self.assertNotIn(MARTIN, r.ideas)
        self.assertEqual(r.leader, 'EST_yana_toom_char')
        r.flags.discard('TFR_EST_occupied')
        r.props['is_subject'] = 'no'
        r.call('TFR_EST_reconcile_executive_display')
        self.assertIn(MARTIN, r.ideas)
        self.assertIn(PERSON, r.flags)

    def test_reform_michal_succession_and_martin_career_can_coexist(self):
        r = self.runtime()
        r.flags.add('TFR_EST_kallas_departed_for_europe')
        self.elect(r, 'reform', date(2028, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn('TFR_EST_pm_reform_michal', r.ideas)
        self.assertNotIn(MARTIN, r.ideas)
        self.assertIn(CAREER, r.flags)
        self.elect(r, election_date=date(2032, 3, 5))
        r.call('TFR_EST_confirm_cabinet')
        self.assertIn(MARTIN, r.ideas)
        self.assertNotIn('TFR_EST_pm_reform_michal', r.ideas)
        self.assertIn('TFR_EST_kallas_departed_for_europe', r.flags)

    def test_repair_has_no_political_cost_rewards_or_duplicate_state_changes(self):
        r = self.runtime()
        before = deepcopy((r.variables, r.flags, r.ideas, r.calls, r.props, r.politics))
        for _ in range(3):
            r.call('TFR_EST_reconcile_ekre_pm_identity')
            r.call('TFR_EST_reconcile_executive_display')
            r.call('TFR_EST_reconcile_ministers')
        self.assertEqual((r.variables, r.flags, r.ideas, r.calls, r.props, r.politics), before)

    def test_native_martin_idea_cannot_be_appointed_or_removed_by_player(self):
        ideas = parse((ROOT / 'common/ideas/TFR_EST_executive.txt').read_text()).get('ideas').get('head_minister')
        idea = ideas.get(MARTIN)
        self.assertEqual(idea.get('available').get('always'), 'no')
        self.assertEqual(idea.get('allowed_to_remove').get('always'), 'no')
        self.assertEqual(idea.get('removal_cost'), '-1')
        self.assertEqual(idea.get('modifier').entries, [])
        r = self.runtime()
        self.assertTrue(r.condition(idea.get('visible')))
        self.assertFalse(r.condition(ideas.get(MART).get('visible')))


if __name__ == '__main__':
    unittest.main()
