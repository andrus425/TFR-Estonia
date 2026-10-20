# Eesti 200's conditional 2023 government programme

Research checked on 20 October 2026. This is a hypothetical Eesti 200 election
victory followed by an Eesti 200-led majority cabinet. Party **6** retains its own
polling, seats and coalition membership, independently of Centre despite their
shared TFR ideology group. The existing Kristina Kallas prime-minister identity
is retained for this alternate campaign. This does not identify her as the
party's historical chair at the 2023 election or invent a historical Eesti
200-led government. No new leadership succession accompanies this programme.

## Primary reference and provenance

The source is the [party's official 2023 Riigikogu election programme](https://eesti200.ee/rk-2023/).
The surviving page explicitly identifies both the election year and its full
programme, separately from the introductory summary. The full public HTML was
retrieved with `curl` and read for this revision: **458,939 bytes**, SHA-256
**`d2af21d3c1a8392f050cb75ce7112c73832d0ea0b45f729f92c31418535a5e75`**.
The web reader received HTTP 403, while the ordinary public HTML request
succeeded. Its short-programme PDF link currently points to
`https://vana.eesti200.ee/programm/#`; no separate PDF was retrieved or treated
as evidence. The page's current navigation and crawl date are not evidence of
the platform's original publication date. No source HTML, PDF or artwork is
included in the release package.

The register below uses these sections of that single contemporary primary
source:

- **A — Security and foreign policy:** the 3% military-defence proposal,
  Kalevipoja integrated air defence, civilian crisis roles, Kaitseliit,
  domestic ammunition and drone development, Tartu disaster medicine and
  allied presence.
- **B — Economy and finance:** business research incentives, simpler companies,
  the EUR 100,000 VAT-registration threshold and zero-based expenditure review.
- **C — Energy and climate:** six-month planning procedures, unused grid
  reservations, renovation, storage guarantees, interconnectors and climate
  legislation with environmental procurement criteria.
- **D — Government and health:** once-only data, electronic invoices, personal
  health accounts, the EUR 1,200 employer allowance, care coordination and
  mental-health prevention.
- **E — Education and science:** additional EUR 250 million annual funding,
  the EUR 3,000 good-teacher objective, shared Estonian-language schools,
  compulsory learning to eighteen, EUR 6,000 student loans with up to 25-year
  repayment and an e-university.

The source supplies enough detail for the selected programme without importing
a later Riigikogu proposal. Focus wording is original. Real euro objectives
identify the proposal; the mod's costs, modifier percentages, implementation
stages and factory equivalents are game-design choices.

## Entry, priorities and timing

The branch remains hidden until a validated election in the 2023 window grants
Eesti 200 the largest delegation and sets `TFR_EST_e200_won_2023_election` and
`TFR_EST_e200_2023_mandate`. The current mandate must remain party **6** and
`TFR_EST_e200_2023_mandate_ended` must be absent. A caretaker can see the incoming
programme, but selection requires a confirmed Eesti 200 prime minister, Eesti
200 coalition membership and **51 actual coalition seats**. Supply agreements
cannot replace those coalition seats. The player negotiates the partners; no
historical coalition is forced and the seat-allocation algorithm is unchanged.

The compact layout has a root at `(4, 0)`, five six-focus columns at x
**0, 2, 4, 6, 8**, and a final report at `(4, 7)`. Ordinary internal prerequisites
give each column a progression while allowing the player to choose between
columns. The final report requires all 31 preceding policy records. All
**32 focuses take 35 days**, totalling **1,120 days**. An uninterrupted start on
**17 April 2023** finishes on **11 May 2026**, **235 days before 2027**. Cabinet
formation, lost confidence, occupation or player delay consumes that margin.
Ordinary policies have no date gates, and an early First European War does not
itself close independent content.

Defence funding can finish after **70 total focus-days**, air-defence preparation
after **105**, and reserve preparation after **140** along the defence column.
The separate industry column reaches its first and second military-factory
projects after **105 and 140 total focus-days**. These are alternative paths
through one focus queue, rather than simultaneous completion promises. No
civilian column or final report blocks them. AI order puts defence, factories
and the main energy response ahead of longer civilian reforms.

## Content register

Identifiers use `TFR_EST_e200_2023_`. Source letters refer to the sections above;
implementation details describe the authored mod content.

| Focus suffix | Basis | Implemented purpose |
|---|---|---|
| `new_mandate` | Alternate election result | Establish the programme and parliamentary accountability. |
| `defence_commitment` | A | Fund a procurement tranche with readiness, organization and supply improvements. |
| `air_defence` | A | Prepare sites, trained crews and compatible purchases; grant bounded defence and attrition improvements. |
| `reserve_muster` | A | Test assignments and unlock the existing limited reserve decision. |
| `kaitseliit_instructors` | A | Finance instruction, exercises and upkeep with training and entrenchment rewards. |
| `allied_reception` | A | Exercise existing reception arrangements and improve sustainment. |
| `civil_reserve` | A | Fund community preparation and a first Tartu training tranche. |
| `industrial_guarantees` | A | Finance assessed suppliers and unlock ordinary paid procurement. |
| `ammunition_workshop` | A; factory adaptation | Purchase one military-factory entitlement and production improvement. |
| `maintenance_workshop` | A; factory adaptation | Purchase a second entitlement and improve equipment upkeep. |
| `drone_development` | A | Commission trials with research and industrial-learning rewards. |
| `research_tax_credit` | B/E | Apply an explicit recurring revenue cost alongside research benefits. |
| `simplified_business` | B | Fund administration changes and record their recurring revenue cost. |
| `renewable_permits` | C | Finance qualified delivery and the first two shared crisis-recovery slots. |
| `grid_connection` | C | Fund bottleneck work and one shared recovery slot. |
| `renovation` | C | Finance a defined upgrade tranche and two shared recovery slots. |
| `storage_guarantees` | C | Contract assessed projects with industrial and resource rewards. |
| `interconnectors` | C | Finance design, permits and agreements with infrastructure-related benefits. |
| `climate_law` | C | Implement reviewed standards with lasting industrial-efficiency rewards. |
| `once_only_data` | D | Finance registry integration and service continuity. |
| `electronic_invoices` | D | Record audited administrative savings as an explicit recurring income change. |
| `zero_budget_review` | B | Record reviewed savings without automatically cancelling public services. |
| `health_accounts` | D | Fund rollout and record a recurring allowance cost. |
| `care_coordinators` | D | Commission integrated services with cohesion and efficiency rewards. |
| `mental_health` | D | Finance trained staff, access standards and prevention contracts. |
| `education_investment` | E | Fund an initial stage with research and cohesion rewards. |
| `teacher_careers` | E | Finance negotiated salary and workload stages. |
| `common_school` | E | Fund language staff, materials and regional delivery support. |
| `learning_to_eighteen` | E | Finance flexible places and practical completion support. |
| `student_loans` | E | Fund revised guarantees and terms. |
| `e_university` | E | Commission accessible, quality-assured digital courses. |
| `account_to_parliament` | Mandate conclusion | Report delivery after every other policy and record programme completion. |

Longer objectives are represented by funded stages. Completing a focus does not
declare that an entire air-defence shield, offshore network, education reform
or 2030 goal has already been delivered. The drone focus commissions trials
rather than supplying free aircraft. The industrial equivalents represent
domestic production and servicing investment, not literal historical promises
of two HOI4-sized factories. There are no free divisions, manpower grants,
equipment grants or instant technology unlocks. Existing paid reserve and
procurement decisions retain their own limits, while the parent's allied
reinforcements remain separate.

## Costs, dynamic modifiers and crisis recovery

Project costs total **1,900 million**, using `TFR_EST_spend_budget` and the
parent's inflation-adjusted accounting. Five policies also call
`add_income_with_inflation` with these explicit amounts:

| Policy | Recurring income change in TFR base ledger billions, before inflation |
|---|---:|
| `research_tax_credit` | −0.020 |
| `simplified_business` | −0.010 |
| `electronic_invoices` | +0.012 |
| `zero_budget_review` | +0.025 |
| `health_accounts` | −0.012 |
| **Net** | **−0.005** |

These are balance amounts in the parent economic system. They are not a
financial forecast, a conversion of real euro figures, or a claim that every
historical revenue effect has been modelled. Each focus exposes its cost and
exact numerical delta through native TFR-style previews generated from the same
values as its reward.

Permanent rewards update **Estonian Economy** and **Estonian Military**. A
persistent completion flag guards each focus so branch reconciliation cannot
replay its cost or reward. Completed reforms survive elections and the supported
occupation/restoration lifecycle.

The energy controller OR-combines equivalent preparation across governments:
`renewable_permits` fills shared slots **1–2**, `grid_connection` fills **3**, and
`renovation` fills **4–5**. Earlier work counts once, with a maximum of five
slots. Completing all three response projects removes TFR's actual **Oil Crash**
spirit, and preparation before onset still counts when the crisis starts.
Storage, interconnectors and the climate framework retain their stated rewards
without adding extra recovery slots.

The `ammunition` project checks states **13, 191, 1329, 840** in that order; the
`maintenance` project checks **191, 13, 1329, 840**. Delivery requires Estonian
ownership, control and a free unlocked military-factory slot. The helper adds
no building slots. Each paid entitlement remains pending while every eligible
state is full or unavailable, retries through the daily controller and sets its
granted flag only after delivery. Repeated ticks, occupation and restored access
cannot duplicate either project or charge its cost again.

## Lifecycle and preservation

The next valid election ends this mandate, even after another Eesti 200 win;
invalid polling preserves it. Occupation hides the constitutional programme,
while restoration retains saved reforms and entitlements and requires the
normal cabinet conditions before policies can resume. The programme does not
change the president, nominate a different prime minister, force partners,
alter elections, renew ministerial discounts or change EU/NATO membership.

The dedicated generator is `tools/build_e200_2023.py`; lifecycle registration is
in `common/scripted_effects/TFR_EST_e200_2023_lifecycle.txt`. Shared imports,
reward previews, energy recovery and the daily controller connect this route
to the established systems. The previous **395 focus descriptions** are
preserved. Test scope and observed engine results are recorded separately in
`docs/TEST_MATRIX.md` and `docs/TEST_RESULTS.md`; source documentation alone does
not establish a completed natural campaign or rendered-interface acceptance.
