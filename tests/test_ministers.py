"""Exercise the actual native cabinet definitions and Estonia's party ledger.

The small UI helper models the documented one-idea-per-native-slot replacement
and executes the candidate's authored on_add. It does not emulate the game UI,
PP spending, the intelligence DLC or the native timed-idea scheduler.
"""
from collections import defaultdict
from datetime import date
from fractions import Fraction
import importlib
import unittest

from script_runtime import ROOT, Runtime
from clausewitz import Block, parse


EXPECTED_PARTIES = ('reform', 'centre', 'ekre', 'isamaa', 'sde', 'e200', 'pp')
EXPECTED_PORTFOLIOS = {
    'foreign': 'foreign_minister',
    'economic': 'economic_minister',
    'interior': 'interior_minister',
    'intelligence': 'intelligence_minister',
    'defence': 'theorist_minister',
}
DISCOUNT = 'TFR_EST_cabinet_formation'


def walk(block):
    for entry in block.entries:
        yield entry
        if isinstance(entry.value, Block):
            yield from walk(entry.value)


class MinisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.author = importlib.import_module('build_ministers')
        cls.candidates = cls.author.CANDIDATES
        cls.candidate_id = staticmethod(cls.author.candidate_id)
        cls.native = parse((ROOT / 'common/ideas/TFR_EST_ministers.txt').read_text(
            encoding='utf-8-sig')).get('ideas')
        cls.definitions = {}
        cls.slots = {}
        for group in cls.native.entries:
            for definition in group.value.entries:
                cls.definitions[definition.key] = definition.value
                cls.slots[definition.key] = group.key
        cls.traits = parse((ROOT / 'common/country_leader/TFR_EST_ministers.txt').read_text(
            encoding='utf-8-sig')).get('leader_traits')

    def runtime(self):
        r = Runtime()
        r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
        r.call('TFR_EST_initialize_parliament')
        r.call('TFR_EST_initialize_ministers')
        return r

    def ministers(self, r):
        return {self.candidate_id(c) for c in self.candidates} & r.ideas

    def candidate(self, **fields):
        return next(c for c in self.candidates
                    if all(c[field] == value for field, value in fields.items()))

    def eligible(self, r, candidate):
        definition = self.definitions[self.candidate_id(candidate)]
        return all(r.condition(definition.get(key, Block([])))
                   for key in ('allowed', 'visible', 'available'))

    def appoint(self, r, candidate):
        """Attempt legal native appointment, preserving rejected UI state."""
        if not self.eligible(r, candidate):
            return False
        token = self.candidate_id(candidate)
        slot = EXPECTED_PORTFOLIOS[candidate['portfolio']]
        previous = {idea for idea in r.ideas if self.slots.get(idea) == slot}
        for idea in previous:
            incumbent = self.definitions[idea]
            if not r.condition(incumbent.get('allowed_to_remove', Block([]))):
                return False
        for idea in previous:
            r.ideas.discard(idea)
            r.run(self.definitions[idea].get('on_remove', Block([])))
        r.ideas.add(token)
        r.run(self.definitions[token].get('on_add', Block([])))
        return token in r.ideas

    def all_party_government(self, r, pm='centre'):
        r.flags.discard('TFR_EST_caretaker')
        for party, seats in zip(EXPECTED_PARTIES, (26, 20, 15, 12, 10, 9, 9)):
            r.variables['TFR_EST_active_' + party] = Fraction(1)
            r.variables['TFR_EST_coalition_' + party] = Fraction(1)
            r.variables['TFR_EST_supply_' + party] = Fraction(0)
            r.variables['TFR_EST_seats_' + party] = Fraction(seats)
        index = EXPECTED_PARTIES.index(pm) + 1
        r.variables['TFR_EST_pm_party'] = Fraction(index)
        r.variables['TFR_EST_mandate_party'] = Fraction(index)
        r.variables['TFR_EST_nominee_party'] = Fraction(index)
        r.call('TFR_EST_recount_confidence')
        r.call('TFR_EST_reconcile_executive_display')

    def votes(self, r, values):
        for party, value in zip(EXPECTED_PARTIES, values):
            r.variables['TFR_EST_active_' + party] = Fraction(1)
            r.variables['TFR_EST_support_' + party] = Fraction(value)
        r.variables['TFR_EST_support_other'] = Fraction(10000 - sum(values))

    def test_every_party_has_every_native_portfolio(self):
        self.assertEqual(tuple(self.author.PARTIES), EXPECTED_PARTIES)
        self.assertEqual(dict(self.author.PORTFOLIOS), EXPECTED_PORTFOLIOS)
        coverage = {(c['party'], c['portfolio']) for c in self.candidates}
        self.assertEqual(coverage, {(p, s) for p in EXPECTED_PARTIES for s in EXPECTED_PORTFOLIOS})
        ids = [self.candidate_id(c) for c in self.candidates]
        self.assertEqual(len(ids), len(set(ids)))
        for c in self.candidates:
            self.assertEqual(self.slots[self.candidate_id(c)], EXPECTED_PORTFOLIOS[c['portfolio']])

    def test_candidates_record_historical_or_inferred_appointment_basis(self):
        for c in self.candidates:
            with self.subTest(candidate=self.candidate_id(c)):
                self.assertTrue(c['person'])
                self.assertTrue(c['name'])
                self.assertTrue(c['basis'])
                self.assertTrue(c['rationale'])
                self.assertTrue(c['sources'])
                sources = (c['sources'],) if isinstance(c['sources'], str) else c['sources']
                for source in sources:
                    url = source['url'] if isinstance(source, dict) else source
                    self.assertTrue(url.startswith('https://'))

    def test_potential_prime_ministers_have_distinct_portfolio_alternatives(self):
        for party, portfolio, leader in (
            ('isamaa', 'foreign', 'urmas_reinsalu'),
            ('ekre', 'economic', 'martin_helme'),
        ):
            with self.subTest(party=party, portfolio=portfolio):
                people = {c['person'] for c in self.candidates
                          if c['party'] == party and c['portfolio'] == portfolio}
                self.assertIn(leader, people)
                self.assertGreaterEqual(len(people), 2)

    def test_potential_prime_minister_is_not_blocked_by_party_alone(self):
        # Isamaa and EKRE currently use Seeder and Mart Helme as their default
        # premiers. Reinsalu and Martin must remain appointable in those
        # cabinets unless the same person actually becomes prime minister.
        for party, person in (('isamaa', 'urmas_reinsalu'), ('ekre', 'martin_helme')):
            with self.subTest(party=party, person=person):
                r = self.runtime()
                self.all_party_government(r, party)
                candidate = self.candidate(person=person)
                self.assertTrue(self.eligible(r, candidate))

    def test_native_candidates_cost_100_and_reference_real_traits(self):
        for c in self.candidates:
            with self.subTest(candidate=self.candidate_id(c)):
                definition = self.definitions[self.candidate_id(c)]
                self.assertEqual(Fraction(definition.get('cost', '100')), 100)
                traits = definition.get('traits')
                self.assertIsInstance(traits, Block)
                self.assertTrue(traits.entries)
                for trait in traits.entries:
                    self.assertIsInstance(self.traits.get(trait.key), Block)

    def test_each_candidate_trait_has_a_country_bonus(self):
        # Positive values for these effects are beneficial; cost/time/attrition
        # reductions are also benefits. Ignore presentation and AI metadata.
        reductions = {
            'consumer_goods_factor', 'supply_consumption_factor', 'attrition',
            'training_time_army_factor', 'justify_war_goal_time', 'operation_cost',
            'required_garrison_factor', 'battalion_upkeep_factor',
            'aircraft_upkeep_factor', 'ship_upkeep_factor',
            'resistance_growth', 'resistance_damage_to_garrison',
            'industrial_refit_ic_cost_factor',
        }
        for c in self.candidates:
            bonuses = []
            for reference in self.definitions[self.candidate_id(c)].get('traits').entries:
                trait = self.traits.get(reference.key)
                for entry in trait.entries:
                    if entry.key in {'sprite', 'random', 'ai_will_do'} or isinstance(entry.value, Block):
                        continue
                    try:
                        number = Fraction(entry.value)
                    except (ValueError, TypeError):
                        continue
                    bonuses.append(number < 0 if entry.key in reductions else number > 0)
            self.assertTrue(any(bonuses), self.candidate_id(c))

    def test_historical_startup_fills_all_five_positions_once(self):
        r = self.runtime()
        selected = [c for c in self.candidates if self.candidate_id(c) in r.ideas]
        self.assertEqual(len(selected), 5)
        self.assertEqual({c['portfolio'] for c in selected}, set(EXPECTED_PORTFOLIOS))
        expected_names = {
            'foreign': 'Urmas Reinsalu', 'economic': 'Taavi Aas',
            'interior': 'Mart Helme', 'intelligence': 'Raivo Aeg', 'defence': 'Jüri Luik',
        }
        self.assertEqual({c['portfolio']: c['name'] for c in selected}, expected_names)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertIn('TFR_EST_pm_centre', r.ideas)
        self.assertNotIn(DISCOUNT, r.ideas)

    def test_repeat_initialization_and_daily_repair_preserve_player_choices(self):
        r = self.runtime()
        self.all_party_government(r)
        replacement = self.candidate(party='reform', portfolio='foreign')
        self.assertTrue(self.appoint(r, replacement))
        selected = self.ministers(r)
        variables, flags = r.variables.copy(), r.flags.copy()
        for _ in range(4):
            r.call('TFR_EST_initialize_ministers')
            r.call('TFR_EST_reconcile_ministers')
        self.assertEqual(self.ministers(r), selected)
        self.assertEqual(r.variables, variables)
        self.assertEqual(r.flags, flags)

    def test_vacant_portfolio_is_not_automatically_refilled(self):
        r = self.runtime()
        economic = self.candidate(party='centre', portfolio='economic')
        r.ideas.discard(self.candidate_id(economic))
        selected = self.ministers(r)
        r.call('TFR_EST_initialize_ministers')
        r.call('TFR_EST_reconcile_ministers')
        self.assertEqual(self.ministers(r), selected)
        self.assertEqual(len(selected), 4)

    def test_late_first_install_or_alternate_government_does_not_seed_2020_cabinet(self):
        for condition in ('late', 'alternate_pm', 'changed_coalition', 'occupied'):
            with self.subTest(condition=condition):
                r = Runtime()
                r.variables.update(TFR_EST_cohesion=55, TFR_EST_readiness=25)
                r.call('TFR_EST_initialize_parliament')
                if condition == 'late':
                    r.props['date'] = date(2024, 1, 1)
                elif condition == 'alternate_pm':
                    r.variables['TFR_EST_pm_party'] = Fraction(1)
                elif condition == 'changed_coalition':
                    r.variables['TFR_EST_coalition_ekre'] = Fraction(0)
                else:
                    r.flags.add('TFR_EST_occupied')
                r.call('TFR_EST_initialize_ministers')
                self.assertFalse(self.ministers(r))
                self.assertIn('TFR_EST_ministers_initialized', r.flags)
                # A later lifecycle repair must not interpret this as fresh
                # January 2020 and grant historical incumbents as a reward.
                r.props['date'] = date(2020, 1, 1)
                r.variables['TFR_EST_pm_party'] = Fraction(2)
                r.variables['TFR_EST_coalition_ekre'] = Fraction(1)
                r.flags.discard('TFR_EST_occupied')
                r.call('TFR_EST_initialize_ministers')
                self.assertFalse(self.ministers(r))

    def test_opposition_and_supply_only_parties_cannot_appoint(self):
        for party in EXPECTED_PARTIES:
            with self.subTest(party=party):
                r = self.runtime()
                self.all_party_government(r)
                r.variables['TFR_EST_coalition_' + party] = Fraction(0)
                r.variables['TFR_EST_supply_' + party] = Fraction(1)
                for c in self.candidates:
                    if c['party'] == party:
                        self.assertFalse(self.eligible(r, c))

    def test_shared_ideology_does_not_authorize_another_party(self):
        for governing, outsider in (('reform', 'pp'), ('pp', 'reform'),
                                    ('centre', 'e200'), ('e200', 'centre')):
            with self.subTest(governing=governing, outsider=outsider):
                r = self.runtime()
                self.all_party_government(r, governing)
                r.variables['TFR_EST_coalition_' + outsider] = Fraction(0)
                r.variables['TFR_EST_supply_' + outsider] = Fraction(1)
                for c in self.candidates:
                    if c['party'] == outsider:
                        self.assertFalse(self.eligible(r, c))

    def test_each_party_can_fill_every_position_while_holding_pm(self):
        for party in EXPECTED_PARTIES:
            for portfolio in EXPECTED_PORTFOLIOS:
                with self.subTest(party=party, portfolio=portfolio):
                    r = self.runtime()
                    self.all_party_government(r, party)
                    r.ideas.difference_update(self.ministers(r))
                    choices = [c for c in self.candidates
                               if c['party'] == party and c['portfolio'] == portfolio]
                    self.assertTrue(any(self.eligible(r, c) for c in choices))

    def test_inactive_party_and_unconfirmed_cabinet_block_appointments(self):
        for restriction in ('inactive', 'caretaker', 'minority', 'occupied', 'subject', 'foreign'):
            with self.subTest(restriction=restriction):
                r = self.runtime()
                self.all_party_government(r)
                r.ideas.difference_update(self.ministers(r))
                if restriction == 'inactive':
                    for party in EXPECTED_PARTIES:
                        r.variables['TFR_EST_active_' + party] = Fraction(0)
                elif restriction == 'caretaker': r.flags.add('TFR_EST_caretaker')
                elif restriction == 'minority': r.variables['TFR_EST_confidence_seats'] = Fraction(50)
                elif restriction == 'occupied': r.flags.add('TFR_EST_occupied')
                elif restriction == 'subject': r.props['is_subject'] = 'yes'
                elif restriction == 'foreign': r.props['tag'] = 'GER'
                self.assertFalse(any(self.eligible(r, c) for c in self.candidates))

    def test_party_withdrawal_removes_incumbents_on_confidence_recount(self):
        r = self.runtime()
        withdrawn = [c for c in self.candidates if c['party'] == 'ekre' and self.candidate_id(c) in r.ideas]
        self.assertTrue(withdrawn)
        r.variables['TFR_EST_coalition_ekre'] = Fraction(0)
        r.call('TFR_EST_recount_confidence')
        for c in withdrawn:
            self.assertNotIn(self.candidate_id(c), r.ideas)

    def test_caretaker_preserves_outgoing_ministers_but_cannot_appoint(self):
        r = self.runtime()
        before = self.ministers(r)
        r.call('TFR_EST_enter_caretaker')
        r.call('TFR_EST_clear_coalition')
        r.call('TFR_EST_reconcile_ministers')
        self.assertEqual(self.ministers(r), before)
        self.assertFalse(any(self.eligible(r, c) for c in self.candidates))

    def test_duplicate_person_cannot_hold_two_native_positions(self):
        by_person = defaultdict(list)
        for c in self.candidates:
            by_person[c['person']].append(c)
        repetitions = [choices for choices in by_person.values()
                       if len({c['portfolio'] for c in choices}) > 1]
        self.assertTrue(repetitions, 'At least one cross-portfolio candidate exercises exclusivity')
        for choices in repetitions:
            for first in choices:
                with self.subTest(person=first['person'], first=first['portfolio']):
                    r = self.runtime()
                    self.all_party_government(r)
                    r.ideas.difference_update(self.ministers(r))
                    self.assertTrue(self.appoint(r, first))
                    for second in choices:
                        if second['portfolio'] != first['portfolio']:
                            before = self.ministers(r)
                            self.assertFalse(self.appoint(r, second))
                            self.assertEqual(self.ministers(r), before)

    def test_defensive_repair_reconciles_duplicate_person_without_double_bonus(self):
        by_person = defaultdict(list)
        for c in self.candidates:
            by_person[c['person']].append(c)
        for choices in by_person.values():
            if len({c['portfolio'] for c in choices}) < 2:
                continue
            with self.subTest(person=choices[0]['person']):
                r = self.runtime()
                self.all_party_government(r)
                r.ideas.difference_update(self.ministers(r))
                for c in choices:
                    r.ideas.add(self.candidate_id(c))
                r.call('TFR_EST_reconcile_ministers')
                self.assertEqual(self.ministers(r), {self.candidate_id(choices[0])})
                before = self.ministers(r)
                r.call('TFR_EST_reconcile_ministers')
                self.assertEqual(self.ministers(r), before)

    def test_native_on_add_repairs_an_externally_forced_second_office(self):
        r = self.runtime()
        foreign = self.candidate(name='Mart Helme', portfolio='foreign')
        interior = self.candidate(name='Mart Helme', portfolio='interior')
        self.assertIn(self.candidate_id(interior), r.ideas)
        # Events and console effects bypass native purchase availability. The
        # actual on_add must still prevent both sets of trait buffs surviving.
        r.ideas.add(self.candidate_id(foreign))
        r.run(self.definitions[self.candidate_id(foreign)].get('on_add'))
        retained = {self.candidate_id(c) for c in (foreign, interior)} & r.ideas
        self.assertEqual(len(retained), 1)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)

    def test_mart_helme_cannot_simultaneously_be_pm_and_portfolio_minister(self):
        choices = [c for c in self.candidates if c['name'] == 'Mart Helme']
        self.assertGreaterEqual(len(choices), 2)
        r = self.runtime()
        self.all_party_government(r, 'ekre')
        for c in choices:
            self.assertFalse(self.eligible(r, c))
            r.ideas.add(self.candidate_id(c))
        r.call('TFR_EST_reconcile_ministers')
        self.assertTrue(all(self.candidate_id(c) not in r.ideas for c in choices))
        self.assertIn('TFR_EST_pm_ekre', r.ideas)

    def test_actual_reinsalu_or_martin_premier_keeps_alternative_appointable(self):
        for party, person, portfolio in (
            ('isamaa', 'urmas_reinsalu', 'foreign'),
            ('ekre', 'martin_helme', 'economic'),
        ):
            with self.subTest(person=person):
                r = self.runtime()
                self.all_party_government(r, party)
                r.ideas.difference_update(self.ministers(r))
                r.flags.add('TFR_EST_pm_person_' + person)
                candidate = self.candidate(person=person, portfolio=portfolio)
                self.assertTrue(r.condition(parse(
                    'TFR_EST_person_is_pm_' + person + ' = yes')))
                self.assertFalse(self.eligible(r, candidate))
                alternatives = [c for c in self.candidates
                                if c['party'] == party and c['portfolio'] == portfolio
                                and c['person'] != person]
                self.assertTrue(alternatives)
                self.assertTrue(all(self.eligible(r, c) for c in alternatives))
                self.assertTrue(self.appoint(r, alternatives[0]))
                # An authored event bypasses normal purchase availability, so
                # repeat-safe repair must also remove a forced PM appointment.
                r.ideas.add(self.candidate_id(candidate))
                r.call('TFR_EST_reconcile_ministers')
                self.assertNotIn(self.candidate_id(candidate), r.ideas)
                self.assertIn(self.candidate_id(alternatives[0]), r.ideas)

    def test_martin_identity_override_allows_mart_helme_in_the_cabinet(self):
        r = self.runtime()
        self.all_party_government(r, 'ekre')
        r.ideas.difference_update(self.ministers(r))
        r.flags.add('TFR_EST_pm_person_martin_helme')
        self.assertTrue(r.condition(parse('TFR_EST_person_is_pm_martin_helme = yes')))
        self.assertFalse(r.condition(parse('TFR_EST_person_is_pm_mart_helme = yes')))
        for candidate in (c for c in self.candidates if c['person'] == 'mart_helme'):
            self.assertTrue(self.eligible(r, candidate))

    def test_pm_person_markers_require_the_correct_party_and_clear_when_stale(self):
        for person in ('urmas_reinsalu', 'martin_helme'):
            with self.subTest(person=person):
                r = self.runtime()
                self.all_party_government(r, 'centre')
                marker = 'TFR_EST_pm_person_' + person
                r.flags.add(marker)
                self.assertFalse(r.condition(parse('TFR_EST_person_is_pm_' + person + ' = yes')))
                self.assertTrue(self.eligible(r, self.candidate(person=person)))
                r.call('TFR_EST_reconcile_ministers')
                self.assertNotIn(marker, r.flags)

    def test_caretaker_preserves_person_identity_and_occupation_clears_it(self):
        for party, person in (('isamaa', 'urmas_reinsalu'), ('ekre', 'martin_helme')):
            with self.subTest(person=person):
                r = self.runtime()
                self.all_party_government(r, party)
                marker = 'TFR_EST_pm_person_' + person
                r.flags.add(marker)
                r.call('TFR_EST_enter_caretaker')
                r.call('TFR_EST_reconcile_ministers')
                self.assertIn(marker, r.flags)
                self.assertFalse(any(self.eligible(r, c) for c in self.candidates))
                r.flags.add('TFR_EST_occupied')
                r.call('TFR_EST_reconcile_ministers')
                self.assertNotIn(marker, r.flags)

    def test_person_identity_survives_reconfirmation_until_valid_new_handover(self):
        for party, person in (('isamaa', 'urmas_reinsalu'), ('ekre', 'martin_helme')):
            for handover in ('TFR_EST_electoral_handover', 'TFR_EST_scripted_handover'):
                with self.subTest(person=person, handover=handover):
                    r = self.runtime()
                    self.all_party_government(r, party)
                    marker = 'TFR_EST_pm_person_' + person
                    r.flags.add(marker)
                    r.call('TFR_EST_confirm_cabinet')
                    self.assertIn(marker, r.flags, 'Ordinary confidence recovery keeps the same PM')
                    r.flags.add(handover)
                    r.variables['TFR_EST_confidence_seats'] = Fraction(50)
                    r.call('TFR_EST_confirm_cabinet')
                    self.assertIn(marker, r.flags, 'Failed confirmation cannot replace the PM')
                    r.call('TFR_EST_recount_confidence')
                    r.call('TFR_EST_confirm_cabinet')
                    self.assertNotIn(marker, r.flags, 'New authorized mandate resets the PM identity')

    def test_appointments_do_not_change_pm_president_mandate_or_seats(self):
        r = self.runtime()
        self.all_party_government(r)
        before = (r.leader, r.variables['TFR_EST_pm_party'], r.variables['TFR_EST_mandate_party'],
                  tuple(r.variables['TFR_EST_seats_' + p] for p in EXPECTED_PARTIES))
        for portfolio in EXPECTED_PORTFOLIOS:
            self.assertTrue(self.appoint(r, self.candidate(party='reform', portfolio=portfolio)))
        self.assertEqual((r.leader, r.variables['TFR_EST_pm_party'], r.variables['TFR_EST_mandate_party'],
                          tuple(r.variables['TFR_EST_seats_' + p] for p in EXPECTED_PARTIES)), before)
        self.assertIn('TFR_EST_pm_centre', r.ideas)

    def test_pm_native_slot_remains_locked(self):
        executives = parse((ROOT / 'common/ideas/TFR_EST_executive.txt').read_text(
            encoding='utf-8-sig')).get('ideas').get('head_minister')
        r = self.runtime()
        self.assertEqual(len(executives.entries), 7)
        for entry in executives.entries:
            self.assertFalse(r.condition(entry.value.get('available')))
            self.assertFalse(r.condition(entry.value.get('allowed_to_remove')))
        self.assertNotIn('head_minister', {self.slots[self.candidate_id(c)] for c in self.candidates})

    def test_valid_election_starts_discount_and_invalid_election_does_not(self):
        r = self.runtime()
        self.votes(r, (6000, 4000, 0, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertIn(DISCOUNT, r.ideas)
        r.ideas.discard(DISCOUNT)
        self.votes(r, (10001, 0, 0, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertNotIn(DISCOUNT, r.ideas)

    def test_election_caretaker_keeps_old_cabinet_until_new_coalition_confirmation(self):
        r = self.runtime()
        outgoing = self.ministers(r)
        self.votes(r, (6000, 4000, 0, 0, 0, 0, 0))
        r.call('TFR_EST_hold_election')
        self.assertIn('TFR_EST_caretaker', r.flags)
        self.assertIn(DISCOUNT, r.ideas)
        self.assertEqual(self.ministers(r), outgoing)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 2)
        self.assertFalse(any(self.eligible(r, c) for c in self.candidates))
        r.call('TFR_EST_confirm_cabinet')
        self.assertNotIn('TFR_EST_caretaker', r.flags)
        self.assertEqual(r.variables['TFR_EST_pm_party'], 1)
        self.assertFalse(self.ministers(r))
        # Reform's 61 seats allow a sole-party cabinet. Centre's old economic
        # minister must leave even though Centre won the remaining 40 seats.
        for portfolio in EXPECTED_PORTFOLIOS:
            self.assertTrue(self.appoint(r, self.candidate(party='reform', portfolio=portfolio)))
        self.assertEqual(len(self.ministers(r)), 5)
        self.assertTrue(all(c['party'] == 'reform' for c in self.candidates
                            if self.candidate_id(c) in r.ideas))

    def test_discount_has_five_native_cost_factors_and_no_pm_discount(self):
        definition = self.definitions[DISCOUNT]
        modifiers = {entry.key: Fraction(entry.value) for entry in definition.get('modifier').entries}
        self.assertEqual(modifiers, {slot + '_cost_factor': Fraction(-4, 5)
                                     for slot in EXPECTED_PORTFOLIOS.values()})
        r = self.runtime()
        additions = [entry.value for entry in walk(r.effects['TFR_EST_begin_minister_formation'])
                     if entry.key == 'add_timed_idea' and entry.value.get('idea') == DISCOUNT]
        self.assertEqual(len(additions), 1)
        self.assertEqual(Fraction(additions[0].get('days')), 90)

    def test_daily_repair_does_not_restart_expired_discount(self):
        r = self.runtime()
        r.call('TFR_EST_begin_minister_formation')
        r.ideas.discard(DISCOUNT)  # Expiry is handled by the native game engine.
        for _ in range(3):
            r.call('TFR_EST_reconcile_ministers')
            r.call('TFR_EST_initialize_ministers')
        self.assertNotIn(DISCOUNT, r.ideas)

    def test_occupation_clears_all_five_and_discount_without_touching_foreign_ideas(self):
        r = self.runtime()
        r.ideas.update({DISCOUNT, 'a_parent_national_spirit'})
        self.assertEqual(len(self.ministers(r)), 5)
        r.flags.add('TFR_EST_occupied')
        r.call('TFR_EST_reconcile_ministers')
        self.assertFalse(self.ministers(r))
        self.assertNotIn(DISCOUNT, r.ideas)
        self.assertIn('a_parent_national_spirit', r.ideas)
        r.flags.discard('TFR_EST_occupied')
        r.call('TFR_EST_initialize_ministers')
        r.call('TFR_EST_reconcile_ministers')
        self.assertFalse(self.ministers(r), 'Restoration must not re-seed January 2020 ministers')

    def test_suspend_ministers_is_repeat_safe(self):
        r = self.runtime()
        r.ideas.add(DISCOUNT)
        r.call('TFR_EST_suspend_ministers')
        before = (r.ideas.copy(), r.variables.copy(), r.flags.copy())
        r.call('TFR_EST_suspend_ministers')
        self.assertEqual((r.ideas, r.variables, r.flags), before)
        self.assertFalse(self.ministers(r))
        self.assertNotIn(DISCOUNT, r.ideas)

    def test_daily_and_constitutional_lifecycle_have_native_hooks(self):
        r = self.runtime()
        for effect, expected in (
            ('TFR_EST_initialize_systems', 'TFR_EST_initialize_ministers'),
            ('TFR_EST_recount_confidence', 'TFR_EST_reconcile_ministers'),
            ('TFR_EST_suspend_parliament', 'TFR_EST_suspend_ministers'),
            ('TFR_EST_assign_election_mandate', 'TFR_EST_begin_minister_formation'),
        ):
            self.assertIn(expected, {entry.key for entry in walk(r.effects[effect])}, effect)
        daily = parse((ROOT / 'common/on_actions/TFR_EST_systems.txt').read_text(
            encoding='utf-8-sig')).get('on_actions').get('on_daily_EST')
        self.assertIn('TFR_EST_reconcile_ministers', {entry.key for entry in walk(daily)})


if __name__ == '__main__':
    unittest.main()
