from fractions import Fraction
import random
import unittest
from script_runtime import Runtime

PARTIES = ("reform", "centre", "ekre", "isamaa", "sde", "e200", "pp")
START_SEATS = (34, 26, 19, 12, 10, 0, 0)
START_SUPPORT = (2890, 2310, 1780, 1140, 980, 440, 0)


def reference(votes, active):
    eligible = [i for i in range(7) if active[i] and votes[i] >= 500]
    total = sum(votes[i] for i in eligible)
    if not total: return None
    seats = [0] * 7
    for i in eligible:
        seats[i] = 101 * votes[i] // total
    order = sorted(eligible, key=lambda i: (-(101 * votes[i] % total), i))
    for i in order[:101 - sum(seats)]: seats[i] += 1
    return seats


class ParliamentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = Runtime()

    def runtime(self, votes=START_SUPPORT, active=(1, 1, 1, 1, 1, 1, 0)):
        r = Runtime.__new__(Runtime)
        r.__dict__ = self.template.__dict__.copy()
        for key in ("variables", "temp", "flags", "global_flags", "ideas", "dynamic", "events", "messages", "characters", "templates", "calls", "politics", "props"):
            r.__dict__[key] = self.template.__dict__[key].copy()
        for i, p in enumerate(PARTIES):
            r.variables[f"TFR_EST_support_{p}"] = Fraction(votes[i])
            r.variables[f"TFR_EST_active_{p}"] = Fraction(active[i])
            r.variables[f"TFR_EST_seats_{p}"] = Fraction(START_SEATS[i])
        r.variables["TFR_EST_support_other"] = Fraction(10000 - sum(votes))
        r.variables["TFR_EST_cohesion"] = Fraction(55)
        r.variables["TFR_EST_readiness"] = Fraction(25)
        return r

    def allocation(self, votes, active=(1,) * 7):
        r = self.runtime(votes, active)
        r.call("TFR_EST_hold_election")
        seats = [r.variables[f"TFR_EST_seats_{p}"] for p in PARTIES]
        expected = reference(votes, active)
        self.assertEqual(seats, expected if expected is not None else list(START_SEATS))
        self.assertEqual(sum(seats), 101)
        self.assertTrue(all(x >= 0 and x.denominator == 1 for x in seats))
        return r

    def test_historical_initialization(self):
        r = self.runtime()
        r.call("TFR_EST_initialize_parliament")
        self.assertEqual([r.variables[f"TFR_EST_seats_{p}"] for p in PARTIES], list(START_SEATS))
        self.assertEqual(r.variables["TFR_EST_coalition_seats"], 57)
        self.assertEqual(r.variables["TFR_EST_confidence_seats"], 57)
        self.assertEqual(r.variables["TFR_EST_pm_party"], 2)

    def test_threshold_and_ties(self):
        for votes in ((500, 499, 3500, 2000, 1500, 1000, 0),
                      (5000, 5000, 0, 0, 0, 0, 0),
                      (1400, 1400, 1400, 1400, 1400, 1400, 1400),
                      (500, 500, 500, 500, 500, 500, 500),
                      (10000, 0, 0, 0, 0, 0, 0)):
            self.allocation(votes)

    def test_randomized_actual_script_matches_integer_reference(self):
        rng = random.Random(20201012)
        for _ in range(500):
            points = sorted([0, 10000] + [rng.randrange(10001) for _ in range(7)])
            buckets = [b - a for a, b in zip(points, points[1:])]
            rng.shuffle(buckets)
            self.allocation(tuple(buckets[:7]))

    def test_invalid_poll_preserves_old_assembly(self):
        cases = [(10001, 0, 0, 0, 0, 0, 0),
                 (-1, 4000, 3000, 1000, 1000, 0, 0),
                 (0, 0, 0, 0, 0, 0, 0),
                 (Fraction(5001, 2), 2500, 2000, 1000, 1000, 0, 0)]
        for votes in cases:
            r = self.runtime(votes)
            r.call("TFR_EST_hold_election")
            self.assertEqual([r.variables[f"TFR_EST_seats_{p}"] for p in PARTIES], list(START_SEATS))
            self.assertTrue(r.messages, "Invalid input must be diagnosed")

    def test_inactive_party_cannot_win_seats(self):
        r = self.runtime((2400, 2300, 1500, 1000, 1000, 1000, 600))
        r.call("TFR_EST_hold_election")
        self.assertEqual([r.variables[f"TFR_EST_seats_{p}"] for p in PARTIES], list(START_SEATS))

    def test_negative_polling_uses_invalid_sentinel_and_preserves_assembly(self):
        # Keep the total valid so the negative component itself must cause rejection.
        # Integer and fractional negatives both previously reached native modulo.
        for party in (*PARTIES, "other"):
            for negative in (Fraction(-1), Fraction(-1, 2)):
                with self.subTest(party=party, support=negative):
                    r = self.runtime()
                    support = f"TFR_EST_support_{party}"
                    compensation = "TFR_EST_support_reform" if party == "other" else "TFR_EST_support_other"
                    r.variables[compensation] += r.variables[support] - negative
                    r.variables[support] = negative
                    r.call("TFR_EST_hold_election")
                    self.assertEqual(r.variables["TFR_EST_vote_total"], 10000)
                    self.assertEqual(r.variables[f"TFR_EST_fraction_{party}"], -1)
                    self.assertEqual([r.variables[f"TFR_EST_seats_{p}"] for p in PARTIES], list(START_SEATS))
                    self.assertTrue(r.messages, "Negative polling must be diagnosed")

    def test_supply_is_not_double_counted(self):
        r = self.runtime()
        for p in PARTIES:
            r.variables[f"TFR_EST_coalition_{p}"] = Fraction(0)
            r.variables[f"TFR_EST_supply_{p}"] = Fraction(0)
        r.variables["TFR_EST_coalition_reform"] = Fraction(1)
        r.variables["TFR_EST_supply_reform"] = Fraction(1)
        r.variables["TFR_EST_supply_centre"] = Fraction(1)
        r.call("TFR_EST_recount_confidence")
        self.assertEqual(r.variables["TFR_EST_coalition_seats"], 34)
        self.assertEqual(r.variables["TFR_EST_confidence_seats"], 60)

    def test_occupied_election_does_not_change_assembly(self):
        r = self.runtime((5000, 5000, 0, 0, 0, 0, 0))
        r.flags.add("TFR_EST_occupied")
        r.call("TFR_EST_hold_election")
        self.assertEqual([r.variables[f"TFR_EST_seats_{p}"] for p in PARTIES], list(START_SEATS))

    def test_same_ideology_is_not_same_coalition(self):
        r = self.runtime((3000, 2500, 1500, 1000, 1000, 500, 500), (1,) * 7)
        for p in PARTIES:
            r.variables[f"TFR_EST_coalition_{p}"] = Fraction(0)
            r.variables[f"TFR_EST_supply_{p}"] = Fraction(0)
        r.variables["TFR_EST_seats_reform"] = Fraction(30)
        r.variables["TFR_EST_seats_pp"] = Fraction(10)
        r.variables["TFR_EST_coalition_reform"] = Fraction(1)
        r.call("TFR_EST_recount_confidence")
        self.assertEqual(r.variables["TFR_EST_coalition_seats"], 30)


if __name__ == "__main__":
    unittest.main()
