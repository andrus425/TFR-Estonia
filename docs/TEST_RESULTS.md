# Validation results — 20 October 2026

This is an implemented **development build**, not a declaration that the public
v1 campaign matrix has passed. The pinned parent is **The Fire Rises 1.0.9.1c**.
The installed executable reports **HOI4 Operation Postern 1.19.3.0.c01a**.

## Automated source and behavior checks

| Check | Observed result |
|---|---|
| `tools/validate_mod.py` | 119 additive/override script files; 459 focuses, 62 events, 58 decisions, 2,268 English localization keys; **0 errors** |
| `python -m unittest discover -s tests -q` | **655 tests passed** in 252.589 seconds, including 500 randomized election allocations checked against an independent integer reference |
| `tools/test_occupation_compatibility.py` | **10 structural regression tests passed** |
| `tools/patch_tfr_compatibility.py --check` | **11 reproducible overrides and 632 audited changes verified**: 620 settlement safeguards and twelve head-of-government selectors |
| `tools/native_script_interface.py --check` | **0 files with legacy argument-block interfaces** |
| Opening and COVID generators | Eleven shared focuses, 22 focus localization keys, rewards/controller/events, the first-case bridge and their text reproduce exactly in `--check` mode |
| Retained-Ratas generator | Twenty shared focuses, governing/visibility/completion triggers, rewards, local crisis controller, one notice and 63 English keys reproduce exactly in `--check` mode |
| Kallas generator | Twenty shared focuses, governing/visibility/completion triggers, rewards, recovered-case bypasses and 60 English keys reproduce exactly in `--check` mode |
| Energy and preview generators | Actual parent Oil Crash integration, old-penalty migration, 260 display-only preview definitions and 520 aliases reproduce exactly in `--check` mode |
| Reform 2023 generator | Thirty-two focuses, governing/visibility/completion triggers, guarded rewards, bounded factory delivery and 70 English keys reproduce exactly in `--check` mode |
| EKRE 2023 generator | Thirty-two focuses, governing/visibility/completion triggers, paid factory projects, recurring income reductions and 70 English keys reproduce exactly in `--check` mode |
| Centre 2023 generator | Thirty-two focuses, governing/visibility/completion triggers, two bounded paid factories, native debt/income helpers and English text reproduce exactly in `--check` mode |
| Isamaa 2023 generator | Thirty-two focuses, governing/visibility/completion triggers, two bounded paid factories, visible debt/income helpers and 70 English keys reproduce exactly in `--check` mode |
| SDE 2023 generator | Thirty-two focuses, governing/visibility/completion triggers, two bounded paid factories, visible debt/income helpers and 70 English keys reproduce exactly in `--check` mode |
| Eesti 200 2023 generator | Thirty-two focuses, governing/visibility/completion triggers, two bounded paid factories, visible debt/income helpers and 70 English keys reproduce exactly in `--check` mode |
| Parempoolsed 2023 generator | Thirty-two focuses, governing/visibility/completion triggers, two bounded paid factories, visible debt/income helpers and 70 English keys reproduce exactly in `--check` mode |
| Saar–Läänemets generator | Automatic historical party succession, separate notification, persistent career/PM markers, caretaker protection and text reproduce exactly in `--check` mode |
| Centre leadership generator | September congress, exactly two guarded successor choices, persistent party leadership, caretaker protection, locked PM identities and localization reproduce exactly in `--check` mode |
| Kallas–Michal generator | Guarded, once-only succession controller, event and text reproduce exactly in `--check` mode |
| Minister generator | 39 candidacies, 38 people, 35 party/portfolio combinations, 15 professional traits, lifecycle, timed discount, localization, portrait references and sourced register reproduce exactly in `--check` mode |
| Portable packaging tests | Deterministic archive, exclusions, portable descriptors and metadata rejection passed as part of the full source suite |

The tests cover historical seats and confidence, threshold/tie behavior, invalid
poll recovery, negative and fractional inputs, inactive parties, independent
party identity, supply agreements, meter limits and tiers, economic unit conversion,
reserve authorization, programme selection, formation, initialization, campaign
stages and persistence through tree changes.

The 19 leadership-mandate regressions cover the historical Centre exception,
all seven election winners, tied largest delegations, invalid elections,
minority winners waiting for 51 confidence votes, blocked legacy nominations,
fabricated nominees, confidence recovery without replacing the incumbent,
AI preferences respecting the election result, polling without seat changes,
missing-variable repair from the saved PM, protected leader membership,
occupation/restoration continuity and explicit story authorization. The opening
revision intentionally changes the normal tree. This revision compacts the
occupation tree's horizontal coordinates; its updated hash and the unchanged
parent Soviet tree remain protected by regression checks.

Nine dynamic-modifier tests cover the two neutral containers and their 16
independent variable bindings, preservation of positive/negative authored values,
repair without reapplying present modifiers, repeated initialization, EST scope
guards, retained later reward ideas and parent modifiers, and the unchanged
occupation gameplay and parent tree. The static validator checks dynamic-modifier references,
localization and icon sprites.

The opening and branch-choice regressions comprise nine snap-election cases,
35 focus/prerequisite/branch cases, 17 story/reward cases, eight cached-visibility
cases and four event-notice cases. They cover actual coalition 50/51 thresholds
with larger supply totals, all ten required policy records, original partner
membership, December 24 and 14-day banking arithmetic, non-cancellation fields,
both political choices, 13-day caretaker succession, preserved assembly/polls/
president/calendar, ordinary and AI reconfirmation guards, dynamic reward totals,
state-change layout refresh and once-only delivered notices. The tests execute
authored control flow or inspect script structure; they do not emulate the game
focus scheduler, rendered GUI or event timing engine.

The 15 October revision verifies four short prerequisite branches, multiple valid
completion orders, blocked children, and six separate conjunctive prerequisites
for the final referendum. Their ancestor closure covers all ten policies. Recursive
checks include referenced scripted triggers and confirm that ordinary policies
have no start-date gates. The COVID response requires TFR's actual domestic-case
predicate, tested against all five inherited severity ideas. Global outbreak or
announcement flags alone cannot unlock it; the other three roots remain usable
without cases. The referendum alone retains its December 24 date gate.

The first-case bridge has 14 separate behavior tests for the February 26/27 boundary,
independent event delivery, repeated queues, existing and intervening infection at
all five severities, ownership, recovery without reseeding, guarded cleanup and
foreign-country no-ops. The delayed-response case retains this mod's owned infection
after January 2023 until response completion, accepting either the persistent
reward flag or native completed focus. An integration test delivers the authored event immediate
effect and verifies that the actual COVID focus then becomes selectable without
completing another policy. Daily-hook ordering and the response helper's own
infection guard are checked separately. These source tests manually deliver queued
events; they do not verify natural campaign scheduling or rendered focus arrows.

Executive tests cover valid confirmation of all seven PMs without changing the
president, caretaker continuity, immediate Karis succession, occupation hiding,
restoration, repeat-safe display repair, locked minister slots and explicit
ideology selection when promoting multi-role presidential characters. The shared
localization adapter preserves all 139 upstream selectors. Independent parser
tests verify all upstream script trees, retained annex actions and parent story
dispatches, including compact punctuation and late-file Estonia paths.

The retained-Ratas continuation adds 22 graph/lifecycle tests and 26 crisis tests.
They cover immediate revelation after the choice while the referendum prerequisite
still blocks selection, original partners and actual cabinet seats, five parallel
policy branches, six full completion orders, all nineteen earned-policy records
before the final report, and preservation of rewards across recreated fixtures.
Twenty 35-day focuses take 700 days: January 28, 2021 to December 29, 2022,
leaving 66 days before the earliest March 2023 election boundary. Valid elections
end the old mandate even if Centre wins again; invalid polling leaves it intact.
Old domestic branches stay hidden during that mandate while war/restoration
branches retain their existing campaign gates.

Crisis tests execute the authored effects against the two parent Saudi-war flags,
including stale flags after settlement, five individual mitigation projects,
preparation before onset, repeated updates/cycles and saved contribution values.
They now verify the actual parent Oil Crash tiers, removal after full preparation,
and one-time reversal of saved factory-output/consumer-goods contributions while
permanent reforms and parent flags remain intact. Pandemic tests
cover every case tier, owned-only lowest-tier removal, clean-country no-ops,
once-only vaccination rewards and no-reward recovery bypasses. Recovery bypass
requires earned coalition-agreement renewal; it cannot unlock family-doctor
reform before the continuation's root. Foreign scope, occupation, subject status,
missing initialization and recorded-outbreak guards are exercised separately.

The Kallas revision adds 21 continuation and 16 crisis tests, plus resignation
and visibility regressions. Resignation explicitly fails the referendum, rejects
its delayed completion reward and hides the opening. The active-focus availability
condition remains valid through ordinary confidence loss but becomes false on
resignation. A late choice after completion uncompletes only the referendum;
earlier policy records and rewards remain intact. These source tests model
completion records and check the authored native cancellation fields; they do not
simulate the game's active-focus validity-update timing.

The Kallas root waits for a confirmed Reform-Centre cabinet while its branch is
already visible during the caretaker handover. Six different full policy orders
finish twenty 35-day focuses on December 27, 2022 from January 26, 2021, leaving
68 days before March 5. The final report checks all nineteen earlier records.
Pandemic recovery bypasses three interventions without paying their rewards,
leaving the certificate service as a separate ordinary reform. Tests cover
actual cabinet seats, both parties, repeat-safe rewards, valid/invalid elections,
stale successor callbacks, war content and subsequent elected governments with
the referendum still uncompleted. The five shared energy-mitigation slots accept
either route's equivalent project once; all 32 mixed slot combinations are
checked against overcompensation. Visibility tests verify 256 flag combinations
without signature collisions. Parsed script definitions are cached by file
metadata while runtime catalogs and gameplay state remain independent.
The restoration regression clears all native completed-focus IDs while retaining
earned opening markers. War, restoration and a subsequent elected government
remain reachable with the failed opening hidden. Legacy phase roots use the
persistent opening-resolved availability condition; their internal branches keep
native prerequisites. They do not depend on a hidden opening focus being bypassed
again after occupation.

The tokenizer repair recovered 384 safeguards previously omitted after compact
`NOT ={` syntax. The compatibility manifest contains the expanded inventory;
live settlement acceptance remains open.

Settlement checks compare actual generated scripts with upstream semantics.
They cover guarded explicit and dynamic annexation, the retained anchor, partition
remainders, original non-Estonia annex actions, parent war flags and follow-up
events, autonomy restrictions, once-per-mandate force cleanup, all seven occupation
gates and repeat-safe repair. They do not execute combat or a live peace conference.

## Parempoolsed's conditional 2023 programme

The Parempoolsed programme contains 32 compact, 35-day focuses. A common mandate
opens five six-policy columns with ordinary internal prerequisites and choices
between columns. The final report requires all 31 preceding policy records.
An uninterrupted 1,120-day programme starting on 17 April 2023 finishes on
11 May 2026, leaving 235 days before 2027. Defence funding is reachable after
70 total focus-days, air-defence preparation after 105 and reserve preparation
after 140 along its branch. The industrial branch reaches the two paid military
factories after 105 and 140 days. These are alternative paths through one focus
queue; neither civilian completion nor the final report blocks them. Ordinary
focuses have no date gates, and early war does not close independent content.

The existing August 2022 formation makes Parempoolsed eligible without assigning
it seats or a victory. A valid ordinary 2023 election must give party 7 the
largest delegation to reveal the programme. Selection requires a confirmed
Lavly Perling cabinet, the current Parempoolsed mandate and 51 actual coalition
seats. Reform's separate ledger cannot contribute merely because it shares a
generic ideology; supply agreements cannot replace coalition membership.
Invalid, wrong-year and postwar ballots do not activate the programme. The next
valid ballot retires it even if Parempoolsed wins again. Occupation hides the
branch while retaining reforms and funded entitlements; restoration requires
cabinet confirmation and schedules a new election.

The 1,750 million in project commitments use the visible parent spending helper.
Recurring adjustments for the supplementary budget, labour taxes, employee
benefits, earmarks, university contributions and targeted support are +0.040,
−0.035, −0.015, +0.012, +0.008 and +0.010 billion respectively, a net +0.020
before inflation. These are gameplay balance amounts in TFR's base ledger,
not historical euro conversions or a revenue forecast. Spending cuts cost
three cohesion; university contributions and targeted support cost two each.
Rewards update the two persistent country modifiers with exact native previews.
Paid factories require owned, controlled Estonian cores with free unlocked
slots; blocked delivery waits without duplicating a grant or charge.

Renewable permitting, grid connections and dispatchable-capacity continuity
contribute 2 + 1 + 2 to the five recovery slots shared by all nine government
programmes. Equivalent projects count once; full preparation removes the
actual parent Oil Crash spirit. Nuclear content prepares licensing and
independent oversight without constructing a reactor. The primary programme
chapters and gameplay adaptations are recorded in the
[Parempoolsed register](PP_2023_SOURCES.md).

Thirty-eight new tests cover legitimate formation and electoral entry, no
forced seats or result, private party identity, actual coalition confirmation,
invalid/wrong-year/postwar ballots, the next mandate, randomized full completion
orders, exact budget/income values, bounded factory delivery with ownership,
control and unlocked-slot checks, restoration with an 84-day invalid-ballot
retry, all eight Parempoolsed energy combinations against mixed earlier
preparations, AI order and reproducible BOM outputs. All 427 preceding focus
descriptions are protected by captured hashes. Shared preview regressions
compare all 275 reward sources. Source execution and graph arithmetic do not
establish natural campaign scheduling, rendered layout or save serialization.

## Eesti 200's conditional 2023 programme

The Eesti 200 programme contains 32 compact, 35-day focuses. One mandate root
opens five parallel six-policy branches, with ordinary prerequisites inside
each branch. The final report requires all 31 preceding policy records. There
are no ordinary focus date gates. An uninterrupted programme takes 1,120 days:
17 April 2023 to 11 May 2026, leaving 235 days before 2027. Defence funding is
reachable after 70 focus-days, air-defence preparation after 105 and reserve
organization after 140 along that branch. Two military factories are reachable
after 105 and 140 days along the industrial branch; civilian completion and
the final report do not block these investments.

A validated ordinary 2023 election must give Eesti 200 the largest delegation.
The branch becomes visible during the caretaker handover, but focus selection
requires a confirmed Eesti 200 PM, its electoral mandate and 51 actual coalition
seats. Supply agreements do not substitute for coalition membership. Centre and
Eesti 200 remain independent in the party ledger despite their shared generic
ideology. The existing hypothetical Kristina Kallas premiership is retained.
Invalid, wrong-year and postwar ballots cannot activate the programme; the next
valid election retires it even if Eesti 200 wins again. Early war preserves an
independent mandate. Occupation hides the programme, while restoration retains
earned reforms and paid factory entitlements behind cabinet confirmation.

The 1,900 million in project commitments and five recurring income adjustments
use the parent's visible helpers. The respective adjustments are −0.020,
−0.010, +0.012, +0.025 and −0.012 billion, a net −0.005 before inflation. These
are gameplay balance amounts in TFR's base ledger, not conversions of the
historical euro pledges. The two persistent country modifiers receive the
authored buffs, and display-only previews show their exact deltas. Factory
delivery requires an owned, controlled Estonian core and a free unlocked slot;
blocked projects wait without duplicating deliveries or costs.

Renewable permits, grid connections and renovation contribute 2 + 1 + 2 to
the five shared recovery slots. Each equivalent slot counts once across all
eight programmes, and full preparation removes the actual parent Oil Crash
idea. Kalevipoja Dome is modelled as funded sites, crew preparation, communications
and compatible procurement rather than an immediately completed national shield.
The contemporary policy basis and gameplay adaptations are recorded in the
[Eesti 200 register](E200_2023_SOURCES.md).

Thirty-five new tests cover legitimate electoral entry from zero opening seats,
invalid and wrong-year ballots, postwar exclusions, private party identity,
confirmation and actual coalition seats, randomized full completion orders,
bounded factories and delayed delivery, restoration with an 84-day invalid-vote
retry, exact budget/income amounts, all eight energy-project combinations with
mixed earlier histories, AI order and reproducible BOM outputs. All 395 earlier
focus-description values are protected by captured hashes. The shared preview
regressions now compare 243 reward sources. Source execution and graph arithmetic
do not establish natural campaign scheduling, rendered focus layout or saved-game
serialization.

## SDE's conditional 2023 programme and historical party succession

The Social Democratic programme contains 32 compact, 35-day focuses. A common
root opens five parallel six-policy branches; the final report requires all
31 other policy records. The full programme takes 1,120 days. An uninterrupted
start on 17 April 2023 finishes on 11 May 2026, leaving 235 days before 2027.
Defence funding takes 70 focus-days along its branch, air-defence preparation
105 and reserves 140. The two paid military-factory projects take 105 and 140
days along their industrial branch. Ordinary focuses retain prerequisites
without calendar gates, and early military preparations do not require the
civilian programme or final report.

A valid ordinary 2023 ballot must give party 5 the largest delegation to reveal
the programme. Selection requires a confirmed SDE-led cabinet and 51 actual
coalition seats; confidence-and-supply votes cannot substitute for coalition
members. No particular partner is forced. Invalid, wrong-year and postwar
ballots cannot activate it. A subsequent valid vote retires this programme
even after another SDE victory. Early war preserves the mandate; occupation
suspends independent content while retaining earned reforms and paid projects.

The programme's 2,145 million in project-budget commitments use the visible
parent spending helper. Its upper income/dividend tax schedule contributes
0.055 billion in recurring income before inflation through the parent's
unchanged helper. These figures are gameplay balance values in TFR's base
ledger, rather than historical euro conversions or a revenue forecast. Rewards
update the two persistent country modifiers and show their exact native deltas.
Energy measures contribute 2 + 1 + 2 to the five capped recovery slots shared
with older programmes and remove the actual parent Oil Crash spirit. Funded
factory entitlements require ownership, control and an unlocked slot, wait
when delivery is impossible and cannot duplicate a grant or charge.

Lauri Läänemets succeeds Indrek Saar on the first independent daily update
from 5 February 2022. The controller applies this career change before queueing
its informational event; delaying acknowledgement cannot preserve Saar as
party chairman. Opposition and junior-partner transitions preserve another
party's PM, the president, seats, polls, coalition, portfolio ministers and
calendar. A confirmed SDE government adopts Läänemets; an outgoing Saar
caretaker waits for actual cabinet confirmation. Career history and the
caretaker guard survive occupation, while the current PM marker is cleaned up
and repaired separately. Occupation delays independent political activity.

All 363 previous focus-description values are protected by their captured
hashes. Policy sources, historical leadership references and adaptations are
recorded in [the SDE register](SDE_2023_SOURCES.md). Source and isolated native
checks do not replace natural campaign, rendered interface or saved-game
acceptance.

Thirty-two new programme tests cover legitimate electoral entry, all six
other winners, date and postwar exclusions, actual coalition seats, private
party identity, randomized full completion orders, bounded paid factories,
pending delivery and reconstructed saved state, exact parent budget/income
amounts, all eight energy-project combinations against mixed older history,
AI order and byte-reproducible BOM outputs. Native modifier previews now
compare all 211 shared reward sources. Twenty-six handover tests cover the
February 4/5 boundary, automatic application before acknowledgement, opposition
and junior coalitions, confirmed SDE leadership, outgoing and incumbent
caretakers through occupation, future cabinets, queue expiry/retry, foreign
guards, once-only notices and locked PM displays. The existing executive,
minister and Centre-leadership regressions also pass.

## Isamaa's conditional 2023 programme

Thirty-two Isamaa programme tests cover 32 compact, 35-day focuses. One root opens five
parallel six-policy branches; the final report requires the preceding 31
policies. A complete uninterrupted programme takes 1,120 days, finishing on
11 May 2026 from a 17 April 2023 start. Defence funding is available after
70 focus-days along its branch, air-defence preparation after 105, reserves
after 140, and the two paid military factories after 105 and 140 along the
industrial branch. Important preparation does not require civilian completion
or the final report. Ordinary focuses have no start-date conditions.

A valid ordinary 2023 election must give Isamaa the largest delegation to
reveal the programme. Every focus then requires a confirmed Isamaa-led cabinet
with 51 actual coalition seats; confidence-and-supply cannot replace them.
No particular coalition partner is mandatory. The route retains Seeder's
existing executive identity and the current president. A later valid vote
ends this electoral programme even if Isamaa wins again, while invalid polling
preserves it. Early war does not itself end the mandate; occupation suspends
the programme and retains its earned policies and paid entitlements.

The two funded factory projects require an owned, controlled Estonian state
with an unlocked slot. Full states preserve the pending delivery; repeated
reconciliation and reconstructed saved fixtures cannot duplicate a grant or
charge the project again. Reserve and procurement preparations unlock the
existing bounded decisions. No focus supplies free divisions or equipment.

The programme uses native economic costs, exact previews for the two existing
dynamic modifiers and three visible recurring-income reductions: -0.010,
-0.035 and -0.015 billion before inflation. The programme's 1,785 million in
budget commitments remains separate from those receipts. Energy measures
contribute 2 + 1 + 2 to the same five OR-combined recovery slots used by older
programmes, removing the actual parent Oil Crash spirit without double counting.

The policy register maps the content to Isamaa's official 2023 programme and
distinguishes proposals from gameplay adaptations. The factories are a bounded
interpretation of its defence-industry objective; nuclear policy commissions
studies rather than delivering a power station. All 331 previous focus
description values remain protected by their captured hashes. Sources and
funding choices are in [the Isamaa register](ISAMAA_2023_SOURCES.md). Tests
execute the authored election callback and rewards, all six other election
winners, invalid/wrong-year/postwar inputs, 50/51 coalition boundaries,
factories with pending delivery and reconstructed saved state, exact debt and
income helper amounts, and eight combinations of energy preparation against
mixed histories across the five older programmes. Native modifier previews
cover all 179 shared focus-reward sources. Source tests do not simulate natural
campaign scheduling, save-file serialization or the rendered focus interface.

The additional restoration regression exercises the real weekly controller.
An Isamaa electoral mandate with 61 confidence seats cannot replace the
outgoing Centre caretaker while the restoration ballot is pending. Day 77
remains pending; invalid input at day 84 preserves the assembly and schedule;
a valid ballot at day 91 ends the old programme, clears the restoration lock
and permits Seeder's confirmation. It does not manually clear the production
guard to obtain that result.

## Centre's conditional 2023 programme and September congress

Thirty-one programme/integration tests and twenty-two leadership tests cover
the new Centre route. Its 32 compact focuses each take 35 days, giving 1,120
days of content. An uninterrupted start on 17 April 2023 completes on 11 May
2026, leaving 235 days before 2027. The root opens five parallel policy branches;
only the final report requires every earlier policy. Defence funding takes 70
focus-days, air-defence preparation 105, reserve planning 140, and the two paid
military factories 105 and 140 along their respective branches.

The tests execute the actual election commit, confirmation, reward, delivery
and recovery effects. They check valid 2023 Centre pluralities, wrong parties
and years, invalid inputs, postwar ballots, next-election retirement, caretaker
restrictions and 51 actual coalition seats. Supply votes do not replace cabinet
seats and no particular partner is mandatory. An early war preserves the
programme; occupation suspends it while retaining reforms and funded projects.

Factory delivery requires ownership, control and an unlocked slot. Full states
keep the paid entitlement pending; repeated reconciliation and reconstructed
saved fixtures cannot add more than two factories or charge again. The tax
package executes native recurring-income inputs of +0.045, -0.030, -0.040 and
-0.012 billion, totaling -0.037 before inflation. Its debt-financed project
costs remain visible and separate from recurring receipts. The three energy
projects contribute 2 + 1 + 2 shared recovery slots and remove the actual parent
Oil Crash spirit without duplicating earlier governments' preparations.

The September story records an ordinary 2023 defeat without changing Ratas's
chairmanship in March. It rejects September 9, queues once from September 10
with a one-hour event delay, and offers exactly Tanel Kiik or Mihhail Kõlvart.
There is no retain-Ratas option. Invalid elections do not create the story;
an intervening Centre victory makes unresolved queued notices and option
effects obsolete. A choice already made persists through a later victory.

Opposition and junior-coalition choices preserve the other party's PM, seats,
polls, coalition, portfolio ministers and calendar. A Centre caretaker waits
for cabinet confirmation, including through occupation and restoration.
Confirmed or future Centre governments use the selected successor; actual PM
markers are repaired separately from persistent party leadership. The parliament
displays Centre's current party chair independently of the cabinet. Both new
native PM tokens remain locked and use existing generic TFR portraits.

All 299 pre-existing focus-description values match their byte-level fixture.
Native previews now compare all 147 shared focus-reward sources. Source tests
cover mixed energy histories across all five programmes and retain the earlier
4,096-combination check. These source cases do not emulate the natural event
scheduler, save-file serialization or rendered interface. The historical policy
and timing references are recorded in [the Centre source register](CENTRE_2023_SOURCES.md).

## EKRE's conditional 2023 programme

The EKRE addition has twenty-eight programme/integration tests, sixteen executive
identity tests and a ninth-HoG selector regression. Its 32 focuses take 35 days
each: 1,120 days in total, finishing on 11 May 2026 from an uninterrupted
17 April 2023 start. Defence funding takes 70 days along its prerequisite path;
the two paid factory projects take 105 and 140. Five compact branches give a
choice of policy priorities without placing the military preparations behind
the final report or the civilian programme.

Source tests execute the actual committed-election callback, confirmation and
completion blocks. They cover valid EKRE pluralities, wrong years and other
parties, invalid polling, postwar/restoration context, second votes, caretaker
negotiations, 50/51 actual coalition seats, confidence-and-supply differences and
single-party government without forced partners. War does not itself disable
the programme; occupation hides it and saved policy flags prevent repeat rewards.

The factory cases check ownership, control, building capacity, partial delivery,
full-state pending entitlements, reconstructed saved fixtures and the maximum
of two grants. Reserve planning and domestic contracts unlock the existing paid,
bounded recruitment/procurement decisions. The four tax-relief policies use
negative native income-helper inputs, tested at exactly -0.015, -0.04, -0.008
and -0.02 ledger units. These are ongoing revenue losses, distinct from public
investment costs charged through the unchanged debt helper.

The three EKRE energy measures contribute 2 + 1 + 2 to the existing five slots.
All eight combinations are checked against representative mixed preparations
from the three older programmes, alongside the unchanged 4,096 earlier-route
combinations. Native preview comparisons cover all 115 focus-reward sources.
A new snapshot protects the raw values of all 267 pre-existing focus descriptions.
The visible-tree matrix checks icon positions alongside first-war branches.

Martin Helme's identity becomes active only after confirmation of an independent
EKRE cabinet serving this 2023 mandate. Outgoing Centre and Mart Helme caretakers
retain their incumbent. A persistent career marker survives elections and
occupation; the personal PM marker is repaired only while EKRE supplies the PM.
Tests preserve the president, ministers, seat ledger and Reform/Michal continuity,
exclude Martin from the finance portfolio and retain Rene Kokk and Mart Helme's
ordinary candidacies. Neither the constitutional-bill focuses nor the election
audit alter the president, seat arithmetic, election calendar or alliances.

The policy source register distinguishes EKRE's contemporary proposals from
historically enacted government policy. Constitutional preparation, industrial
workshops and force planning are explicit gameplay adaptations. These checks
are not a substitute for natural campaign timing, save-file serialization or
rendered interface acceptance.

## Reform 2023, succession and postwar elections

The 19 October revision adds twenty-five programme/integration tests, twelve handover
tests, thirty-one war-election tests, an eighth-HoG selector regression and three
additional energy cases. All 32 focuses take 35 days. Random valid branch orders
complete in 1,120 days, reaching 11 May 2026 from a 17 April 2023 start; the two
paid factory projects need only 105 and 140 days along their branch. The remaining
235-day margin assumes uninterrupted focus selection and a valid majority.

Tests execute the actual committed-election mandate callback. They cover valid
Reform pluralities in 2023, confirmation and actual 50/51 coalition seats, supply
agreements, invalid polling, date boundaries, a second 2023 vote, later Reform
victories, and postwar ballots. The historical programme is initially hidden and
ends after the next valid election. Its policy records persist through Michal's
handover, war and occupation. A visibility matrix checks both Ratas histories
alongside first-war content for colliding icon coordinates. All 235 older focus
description values remain protected and unchanged.

The factory tests execute the generated numeric state scopes: each project needs
an owned, controlled state and an unlocked slot; full states preserve a paid
pending entitlement for retry. Repeated calls grant at most two factories in
total and never charge again. Exact preview comparisons now cover all 83
opening/Ratas/Kallas/Reform completion blocks, including fiscal parent-helper
calls. Energy coverage includes all 4,096 combinations of preparations across
three governments and verifies the shared five-slot ceiling.

Succession cases cover the 23 July 2024 boundary, actual EU membership, confirmed
Reform leadership, stale or invalid event delivery, repeat queues and the ended
mandate guard. Persistent career history prevents Kallas returning as PM after
Michal's appointment in later Reform cabinets, including after restoration.
Seats, ministers, coalition partners, president and earned rewards remain intact.
An opening-assembly marker retires old Porto options, queued cabinet events and
late focus completions at the first valid election. It closes the old campaign
stage without inventing a resignation/retention choice or awarding reforms;
invalid ballots leave that opening assembly intact.

Calendar cases retain March 2023, block regular 2027 ballots before and during
the first war, and require TFR's explicit completed settlement plus a winner.
A quiet declaration frame cannot count as peace. Independent Estonia votes on
the first settled daily update, even before 2027; occupation retains the 84-day
restoration process, whose vote also satisfies a pending postwar ballot. Invalid
polling retains the assembly and pending schedule. A new 1,461-day term starts
from a valid postwar election. Calendar localization displays this schedule.

These are source/control-flow checks; natural campaign event delivery, saved
native focus progress, UI rendering and war settlement interactions remain the
manual acceptance cases in `TEST_MATRIX.md`.

## Compact layouts, costs and focus-effect previews

The 16 October revision adds eight presentation tests, nine native-preview tests,
eleven cost/requirement tests, sixteen parent-crisis tests and two integrated
energy-focus progression tests. A fixture hashes all 235 existing focus description
values; all remain unchanged. Coordinate checks cover compact bounds, unique icon
positions, downward prerequisites and space for labels. A separate review evaluated
actual branch visibility for the opening, each historical cabinet, either cabinet
during the first war, and a later elected Centre cabinet; no icon positions collide.
These checks do not replace rendered UI inspection.

The preview suite executes all 51 opening/Ratas/Kallas completion blocks from
nonzero saved modifier baselines and compares every actual economic/military
change with its advertised native preview. The 49 preview definitions use TFR's
existing `effect_tooltip`/`swap_ideas` pattern; no gameplay script grants them.
The two real persistent dynamic modifiers remain the recipients of reforms.

Cost tests execute the installed parent's unchanged inflation/debt helper across
twenty combinations of budget size and inflation, including fractional amounts
and deflation. They confirm that its native numerical tooltip follows conversion
from millions to billions and inflation adjustment. A call-graph check follows
all 235 completion rewards and confirms that every reachable budget charge stays
visible. Meter tests verify signed numerical text, hidden arithmetic and clamping.
Concise requirement wrappers still enforce actual coalition seats, the correct
cabinet, occupation/caretaker restrictions and all five domestic COVID case tiers.

The energy controller now uses the parent's exact `GER_oil_crash1`–`5` modifiers.
Tests cover all 512 Ratas/Kallas project-flag combinations, progressive recovery,
final removal while the world crisis continues, preparation before onset,
weaker external tiers, missing/duplicate-tier repair, repeat updates, reconstructed
saved state, foreign/uninitialized guards and one-time reversal of the earlier
custom penalties without losing reforms. Integrated rewards verify Ratas's
1→2→3→4→5→removed progression and Kallas's 1→2→4→5→removed progression.

## Coalition minister behavior

Thirty-four minister tests exercise the actual generated cabinet definitions
and parliamentary lifecycle. All seven parties retain a candidate for every
portfolio even while their own leader holds the premiership. Native definitions
use the five TFR slots, the normal 100 PP price, positive country traits and
independent party membership. Tests distinguish coalition from confidence and
supply, including parties sharing an ideology, inactive parties and caretaker
governments. The existing PM tokens remain unappointable and unremovable.

The suite checks one-time historical initialization, late-install/alternate-cabinet
guards, preserving chosen ministers and empty slots, no daily reappointment,
immediate party-withdrawal cleanup, outgoing caretaker continuity and removal
after confirmation of a new coalition. A full election→caretaker→sole-Reform
confirmation sequence exercises actual hooks. Mart Helme's two portfolios have
reciprocal availability exclusions and both are removed/unavailable while he is
PM. Native `on_add` contains repeat-safe defensive repair for forced duplicates.

Valid elections grant a 90-day timed spirit with exactly five −80% minister-cost
factors. Invalid polling, ordinary government changes and repeated repairs do
not create a discount. Occupation clears every new portfolio and the window;
unrelated parent spirits survive. The small test UI helper models replacement
within one native slot and executes the authored `on_add`; it does not emulate
political-screen clicking, PP purchases or timed-idea expiration. Those remain
native engine and manual acceptance concerns.

The alternatives revision adds Trivimi Velliste and Rene Kokk and seven regressions
covering the two extra nominees, default-PM compatibility and explicit personal
identity. Reinsalu is eligible under Seeder and Martin under Mart; markers for
their own future authored premiership exclude that particular person while
preserving a suitable alternative. A Martin marker supersedes Mart's default
personal exclusion. Wrong-party markers and occupation clear personal metadata;
caretakers, ordinary confidence recovery and invalid confirmation preserve it.
Successful new electoral/scripted mandates clear outgoing metadata. No current
route sets these future markers or changes its PM identity.

## Native engine observations

The accepted Parempoolsed capture is
`test-output/engine-estonia-qa-20261020-122521/`. It reached the frontend in
approximately **297 seconds** (300 seconds including capture) and passed
**all 181 native assertions**, including the previous 167. Fourteen new cases
cover initial hiding, caretaker visibility without selection, a confirmed
Perling cabinet alongside President Karis, actual coalition seats, precise
military-variable changes, two real factory increments without repetition,
parent Oil Crash tiers through 2 + 1 + 2 recovery, occupation hiding,
restoration continuity and next-vote retirement.

The fixture remains in a **2020 frontend snapshot**. It directly activates
party eligibility and seeds the later mandate/caretaker state to exercise
native effects. Natural August 2022 formation, legitimate 2023 electoral entry,
randomized completion orders, the before-2027 schedule, delayed delivery and
restoration-election retries are source-tested. Natural campaign scheduling,
rendered focus layout and saved-game serialization remain manual checks.

This capture contains **2,032 normalized unique error-log messages** and
**zero Estonia-prefixed errors**. Relative to the pinned TFR-only and preceding
Eesti 200 captures, nine additional messages name missing foreign nationalist
medium flags (GBA, KHA, LBV, ORO, PAP, SID, SPM, TOS and VGE). They are the same
foreign asset messages already recorded in the accepted 16 October alternatives
capture, rather than new Parempoolsed script failures. No foreign asset repair
is claimed. Reports are `test-output/pp2023-final-engine-comparison.json`,
`test-output/pp2023-previous-engine-comparison.json` and
`test-output/pp2023-known-foreign-assets-comparison.json`. The owned process
stopped and the original `dlc_load.json` was verified restored byte-for-byte,
SHA-256 `767273d70e42152253bd2ad672e68f6df0a5343ffcce44d5278e81c25eeae32a`.
The temporary QA overlay is excluded from ordinary play and the package.

The accepted Eesti 200 capture is
`test-output/engine-estonia-qa-20261020-121156/`. It reached the frontend in
approximately **296 seconds** (298 seconds including capture) and passed
**all 167 native assertions**, including the previous 153. Fourteen new cases
cover initial hiding, caretaker visibility without selection, a confirmed
Eesti 200 cabinet alongside President Karis, the actual coalition-seat gate,
precise military-variable changes, two real military-factory increments and
repeat prevention, the parent's Oil Crash tiers through 2 + 1 + 2 mitigation,
occupation hiding, restoration continuity and next-vote retirement.

The fixture remains in a **2020 frontend snapshot** and explicitly seeds the
later mandate and caretaker state for these effect tests. Legitimate 2023
electoral entry, randomized completion order, the before-2027 schedule, delayed
factory delivery and restored-election retries are covered by source tests.
Natural election/focus scheduling, the rendered tree and saved-game serialization
remain manual campaign checks.

This capture contains **2,023 normalized unique error-log messages**, exactly
matching the pinned TFR-only baseline: **zero new messages, zero removed messages
and zero Estonia-prefixed errors**. Compared with the previous accepted SDE
capture, eight previously documented foreign nationalist missing-flag messages
recurred (GBA, KHA, LBV, ORO, PAP, SID, SPM and TOS); no new Estonia error or foreign
asset fix is inferred from that load variation. Reports are
`test-output/e2002023-final-engine-comparison.json` and
`test-output/e2002023-previous-engine-comparison.json`. The owned process stopped
and the original `dlc_load.json` was verified restored byte-for-byte, SHA-256
`767273d70e42152253bd2ad672e68f6df0a5343ffcce44d5278e81c25eeae32a`.
The temporary QA overlay is excluded from ordinary play and the package.

The accepted SDE capture is
`test-output/engine-estonia-qa-20261020-092235/`. It reached the frontend in
approximately **170 seconds** and passed **all 153 native assertions**, including
the previous 136. Its seventeen new cases cover initial programme hiding, the
2020 handover date guard, seeded Läänemets PM identity alongside Karis,
preservation of another party's PM, explicit caretaker gating, confirmed SDE
government, actual coalition seats, precise military-variable deltas, two real
factory increments and repeat prevention, the parent's energy tiers through
2 + 1 + 2 recovery, occupation hiding, restoration continuity and next-vote
retirement with persistent leadership history.

The native fixture remains in a **2020 frontend snapshot**. It rejects the
historical handover in 2020, then explicitly seeds the later career, mandate
and caretaker state for effect tests. Actual February 4/5 scheduling, automatic
succession before notification acknowledgement, player election entry and
outgoing-Saar caretaker protection are source-tested. Natural campaign delivery,
rendered UI and saved-game serialization remain manual acceptance cases.

This capture and the accepted Isamaa build each contain **2,015 normalized
unique error-log messages**: **zero new messages**, **zero removed messages**
and **zero Estonia-prefixed errors**. The pinned TFR-only comparison also has
zero new messages; its eight additional foreign missing-flag messages did not
occur here, and no foreign asset fix is claimed. Reports are
`test-output/sde2023-final-engine-comparison.json` and
`test-output/sde2023-previous-engine-comparison.json`. The owned game process
stopped and the original `dlc_load.json` was verified restored byte-for-byte.
The temporary QA overlay is excluded from ordinary play and the package.

The accepted Isamaa capture is
`test-output/engine-estonia-qa-20261020-090920/`. It reached the frontend in
approximately **172 seconds** and passed **all 136 native assertions**, including
the previous 122. Its fourteen new cases cover initial hiding, explicitly seeded
caretaker gating, confirmed Seeder alongside Karis, 50 actual coalition seats
despite 90 confidence votes, exact military-variable deltas, two real factory
increments and repeat prevention, the parent's energy tiers through 2 + 1 + 2
recovery, occupation hiding, restoration continuity and next-vote retirement.

The native fixture remains in a **2020 frontend snapshot** and explicitly seeds
the 2023 mandate and caretaker state. Legitimate player election entry and
pending restoration ballots are source-tested. This is not a natural 2023
campaign, rendered focus-menu inspection or saved-game serialization test.

The accepted capture and previous Centre build each contain **2,015 normalized
unique messages**: **zero new messages**, **zero removed messages** and **zero
Estonia-prefixed errors**. The pinned TFR-only comparison also has zero new
messages; its eight additional foreign missing-flag messages did not occur in
this capture, and no foreign asset fix is claimed. Reports are
`test-output/isamaa2023-final-engine-comparison.json` and
`test-output/isamaa2023-previous-engine-comparison.json`. The owned process was
stopped and `dlc_load.json` was verified restored byte-for-byte. The QA overlay
is excluded from the portable package.

The first Isamaa capture, `test-output/engine-estonia-qa-20261020-085927/`,
reached the frontend in approximately **242 seconds** but passed only **134 of
136 assertions**. It is not an accepted run. The preceding Centre restoration
fixture left its restoration-election flag pending. The separate Isamaa
ordinary-election fixture failed to clear that test state, so the existing
confirmation guard correctly kept the outgoing Centre caretaker. The Isamaa
confirmation and later restoration assertions consequently expected the wrong
PM. The QA setup now closes that earlier fixture's pending-election state
before initializing its ordinary-election case. No gameplay guard, reward,
appointment rule or election timetable was changed to make the test pass.

The second capture, `test-output/engine-estonia-qa-20261020-090501/`, passed
**135 of 136 assertions** in approximately **168 seconds**. The confirmation
and restoration cases passed after that isolation fix. Its remaining caretaker
assertion assumed player control, while frontend Estonia is AI-controlled and
immediately confirms a majority after a valid vote. The isolated fixture now
explicitly seeds a caretaker frame, matching the older programme QA blocks.
Player entry and outgoing-PM continuity remain covered by source tests. This
second run is also retained as a failed fixture run, not an accepted result.

The Centre revision's accepted capture is
`test-output/engine-estonia-qa-20261019-132419/`. It reached the frontend in
approximately **269 seconds** and passed **all 122 native assertions**.
Its eighteen new cases verify initial hiding, confirmed Ratas/president display,
caretaker and actual-coalition gates, native military-variable deltas, two real
factory increments without repeats, the parent energy spirit's 2 + 1 + 2
recovery, next-election retirement, rejection of a congress in 2020, both
successor PM tokens, preservation of another party's PM and occupation/restoration
identity. The prior 104 assertions also pass.

The native fixture explicitly seeds the 2023 programme and completed successor
choices in a **2020 frontend snapshot**. It does not advance a natural campaign
to September. The September 9/10 boundary, event queuing, both actual option
effects, invalidated notices and caretaker congress transitions are source-tested;
natural delivery and saved-game serialization remain manual acceptance cases.

The capture contains **2,015 normalized unique messages**, with **zero new
messages** against both the pinned TFR-only baseline and the accepted EKRE build,
and **zero Estonia-prefixed errors**. Eight foreign missing-flag messages from
those baselines did not occur in this run; no foreign asset fix is claimed.
The comparison reports are `test-output/centre2023-final-engine-comparison.json`
and `test-output/centre2023-previous-engine-comparison.json`. The owned test
process stopped and the original `dlc_load.json` was verified restored
byte-for-byte. The QA overlay remains excluded from ordinary play and packaging.

The EKRE revision's accepted capture is
`test-output/engine-estonia-qa-20261019-130435/`. It reached the frontend in
approximately **204 seconds** and passed **all 104 native assertions**.
The fourteen new assertions verify initial hiding, caretaker confirmation,
Martin's PM token and minister exclusions alongside the preserved president,
actual coalition thresholds, military-variable deltas, two real factory
increments and repeat prevention, progressive parent Oil Crash tiers,
occupation/restoration identity, and retirement at the next valid vote.

These cases explicitly seed the 2023 mandate in the 2020 frontend snapshot.
They execute native effects without claiming a natural 2023 campaign, rendered
focus UI, political-screen clicks or saved-game serialization. Date boundaries,
legitimate electoral entry and all 32 completion rewards are also source-tested.

The accepted error log and pinned TFR-only baseline both contain **2,023
normalized unique messages**: **zero new messages**, **zero removed messages**
and **zero Estonia-prefixed errors**. The previous accepted Reform capture
contained nine additional foreign flag-load messages that did not occur in this
run; no foreign asset repair is claimed. Comparison reports are
`test-output/ekre2023-final-engine-comparison.json` and
`test-output/ekre2023-previous-engine-comparison.json`.
The original `dlc_load.json` was verified restored byte-for-byte after the owned
test process stopped. The isolated QA overlay is excluded from the package.

The Reform revision's final 19 October capture is
`test-output/engine-estonia-qa-20261019-124517/`. It reached the frontend in
approximately **180 seconds** and passed **all 90 native assertions**. In
addition to the programme, building, modifier, calendar and PM-display checks
below, it invokes obsolete Porto Franco options and the old cabinet controller
after an elected government has replaced the opening assembly. They preserve
the elected Reform PM and mandate and do not create a caretaker or old handover.

The final error log has **2,032 normalized unique messages**, matching the
previous accepted 16 October build exactly: **zero additional messages** and
**zero Estonia-prefixed errors**. Its nine additional messages against the pinned
TFR-only baseline are the already recorded foreign medium nationalist flag loads
for GBA, KHA, LBV, ORO, PAP, SID, SPM, TOS and VGE. Reports are
`test-output/reform2023-final-engine-comparison.json` and
`test-output/reform2023-previous-engine-comparison.json`. The original
`dlc_load.json` was verified restored byte-for-byte after the owned process
stopped. No ordinary campaign or rendered-interface acceptance is claimed.

The first 19 October Reform capture, `engine-estonia-qa-20261019-123235`,
reached the frontend but passed only 88 of 89 assertions. The country-scope
`year` lookup returned zero, producing a display year of 4. This was not accepted
as a successful run. The controller now reads `global.year`; the source runtime
also models this scope distinction so the same error cannot pass its tests.

The corrected capture, `test-output/engine-estonia-qa-20261019-123815/`,
reached the frontend in approximately **190 seconds** and passed **all 89
assertions**. The 2020 snapshot correctly produced the next display year **2024**.
It verifies the new programme's gates, exact military-variable deltas, two real
military-factory building increments, repeat prevention, removal of all parent
Oil Crash tiers, the pending/postwar election transitions and native Michal PM
ideas alongside the preserved president. Mandate flags were explicitly seeded
for history-time effect tests; the run does not simulate a 2023 or 2024 campaign.

This capture and the pinned parent baseline both contain **2,023 normalized
unique error messages**, with **zero additional messages** and **zero
Estonia-prefixed errors**. The report is
`test-output/reform2023-second-engine-comparison.json`. The original mod/DLC
configuration was restored after the owned test process stopped.

The earlier implementation run is captured locally under
`test-output/engine-estonia-qa-20261013-095041/`.
It loaded TFR, Estonia and an isolated arithmetic QA overlay, reached the frontend
in approximately **101 seconds**, and passed all seven native assertions:

1. Historical assembly and the 57-seat Ratas coalition.
2. Equal polling allocates 51/50 according to the fixed tie order.
3. Exactly 5% qualifies; 4.99% is excluded; the total is 101 seats.
4. Invalid polling preserves the prior assembly.
5. Seven equal qualifying parties allocate the remainders correctly.
6. Occupation suspends election allocation.
7. Cohesion/readiness changes clamp to 0/100 using native temporary inputs.

The TFR-only comparison run is captured under
`test-output/engine-parent-20261013-095435/` and reached the frontend in
approximately **111 seconds**. The smoke-test processes were stopped and the
original mod/DLC configuration was restored byte-for-byte after each run.

`tools/compare_engine_logs.py` compared the two captured error logs after removing
timestamps and source line numbers. Both contained **2,062 unique parent error
messages**, with **0 new unique messages**, **0 removed messages**, and **0 messages
containing the new `TFR_EST_` or `tfr_estonia` identifiers**. This establishes
startup parity with this parent build; it does not make the parent error-free.
The compact comparison is saved locally as `test-output/final-engine-comparison.json`.

The 13 October executive-display run is captured under
`test-output/engine-estonia-qa-20261013-123825/`. It reached the frontend in about
154 seconds and passed **all 19 native assertions**, comprising the seven earlier
arithmetic cases and 12 executive cases: the opening Kaljulaid/Ratas pairing,
each of the seven PM identities across five ruling ideology groups, the Karis
handover, caretaker continuity, occupation hiding and restoration of the saved
executive. These occupation/restoration cases exercise display effects and ledger
suspension only, without invoking diplomatic settlements or unit transfers.

The successful run contains **no errors naming `TFR_EST_` or `tfr_estonia`**.
Comparison with the earlier parent baseline found eight additional missing
nationalist flag messages for GBA, KHA, LBV, ORO, PAP, SID, SPM and TOS. They
reference parent flag assets; the reason for their additional loading was not
isolated. They are recorded rather than counted as resolved or silently ignored.
The comparison is `test-output/executive-engine-comparison.json`.

An initial executive QA run failed because `promote_character` requires an
explicit ideology for characters with several leader roles. The implementation
now supplies the appropriate sub-ideology in all five government groups, and
both static checks and a regression prevent reintroducing the ambiguous call.
The later 19-case run is the accepted result.

The election-led coalition run is captured under
`test-output/engine-estonia-qa-20261014-111641/`. It reached the frontend in
approximately **192 seconds** and passed **all 26 native assertions**. It repeats
the 19 arithmetic/executive checks and adds seven leadership cases: unauthorized
nomination does nothing, a fabricated nominee is rejected, AI confidence recovery
keeps Centre, equal largest delegations use the fixed tie order, a minority winner
waits for confidence, the elected successor can be confirmed, and an invalid
subsequent election preserves the confirmed leader. The original mod/DLC
configuration was restored after the owned process stopped.

The first 14 October QA fixture passed 25 of 26 cases. During frontend history
construction Estonia is AI-controlled, so its actual election effect immediately
formed an 80-seat Reform–Centre coalition and confirmed Reform. The corrected
fixture logs `pm=1 confidence=80 centre=1` before reconstructing the pending
player cabinet from the actual elected 40/40/21 assembly. This tests native
confirmation below 51 and after adding support without mistaking automatic AI
formation for a player handover failure. The source regression separately follows
the unmodified player election effect. No gameplay exception was added for QA.

The successful 26-case log contains **no errors naming `TFR_EST_` or
`tfr_estonia`**. The same-day parent-only run,
`test-output/engine-parent-20261014-112136/`, reached the frontend in about
173 seconds with the same DLC selection. After normalization it contains 2,023
unique messages, versus 2,033 in the submod/QA run. The ten additional messages
all reference missing foreign nationalist flag assets: medium flags for GBA,
KHA, LBV, ORO, PAP, SID, SPM, TOS and VGE, plus SPM's small flag. There are no
removed messages. Their additional loading is not isolated; this is not an
error-free startup claim. The report is
`test-output/mandate-engine-comparison-current.json`. The larger asset differences
from the previous day's capture are not attributed to the parliament change.

The preceding dynamic-modifier run is captured under
`test-output/engine-estonia-qa-20261014-114230/`. It reached the frontend in
approximately **175 seconds** and passed **all 30 native assertions**: the prior
26 cases plus neutral installation, actual modifier-value application,
preservation during repeated initialization, and repair of a removed container.
Reading native `modifier@industrial_capacity_factory` before and after changing
its backing variable produced a delta of `0.03`; the corresponding supply
consumption test produced `-0.05`. Test adjustments were returned to zero after
the checks. The isolated fixture is not part of the ordinary mod.

Comparison with the same-day parent-only baseline gives **2,023 normalized unique
messages in both runs, zero new messages, zero removed messages, and zero messages
containing `TFR_EST_` or `tfr_estonia`**. The comparison report is
`test-output/dynamic-engine-comparison.json`. This establishes startup parity for
this run without claiming the parent is error-free. The original mod/DLC
configuration was restored after the owned test process stopped. It does not
verify rendered icons, natural daily scheduling or save/reload in a campaign.

The accepted opening run is captured under
`test-output/engine-estonia-qa-20261014-162010/`. It reached the frontend in about
**126 seconds** and passed **all 36 native assertions**. Six new cases verify the
initial coalition, supply votes failing to replace coalition seats, unauthorized
snap-vote rejection, resigned Ratas remaining caretaker, the Reform–Centre
successor, and retained Ratas with his original coalition. Cabinet cases invoke
story helpers directly in the isolated fixture, preserving seats, regular election
year and president. They do not run the January scheduler or select an active focus.

Comparison with the same-day parent baseline gives 2,032 normalized unique
messages against 2,023. The nine additional messages reference medium nationalist
flag assets for GBA, KHA, LBV, ORO, PAP, SID, SPM, TOS and VGE, matching the foreign
asset-loading differences recorded earlier. There are no removed messages or
messages containing `TFR_EST_`/`tfr_estonia`. The report is
`test-output/opening-engine-comparison.json`; the extra loading is not treated
as resolved or attributed to an Estonia script error.

The first 36-case attempt, `engine-estonia-qa-20261014-124250`, exited at texture
loading after 35 seconds, before reaching the frontend or any assertion. It is
not a pass and does not isolate a content fault. Windows retained an inaccessible
windowless 32 KiB child of that recorded test process. The retry exempted only
that inert recorded child from the process guard; active games remain blocked.
The accepted run stopped its owned process and restored the original playset.

The 15 October branched-opening run is captured under
`test-output/engine-estonia-qa-20261015-122811/`. It reached the frontend in about
**230 seconds** (234 seconds including capture) and passed **all 39 native
assertions**. The three new cases verify that a clean country fails TFR's
`generic_has_corona` check and cannot announce the response; each of the five
parent case ideas satisfies that check; and an active outbreak permits the guarded
response helper. The fixture restores its case ideas and announcement flag.
Its date remains January 1, 2020, so the first-case event, natural focus selection
and the 2023 cleanup guard are covered by source tests rather than this fixture.
The final delayed-response cleanup guard was applied after the engine run.

Comparison with the pinned parent-only baseline from October 14 gives 2,033
normalized unique messages against 2,023. The ten additional messages are the
nine foreign medium nationalist flags listed above plus SPM's small flag, matching
the asset differences already observed in the earlier mandate run. There are no
removed messages or messages containing `TFR_EST_`/`tfr_estonia`. The report is
`test-output/branched-opening-engine-comparison.json`. The owned test process was
stopped and the original mod/DLC configuration restored byte-for-byte.

The retained-Ratas run is captured under
`test-output/engine-estonia-qa-20261015-140432/`. It reached the frontend in about
**313 seconds** (317 seconds including capture) and passed **all 46 native
assertions**. Seven new cases verify immediate retained-choice visibility before
referendum completion, the original majority governing with legacy domestic
content suppressed, once-only energy penalties, funded mitigation, settlement
reversing only tracked contributions, owned COVID recovery bypassing emergency
policies while leaving ordinary family-doctor reform unfinished, and a valid
Centre election ending the old mandate while retaining an enacted reform.

The run has 2,032 normalized unique error messages versus 2,023 in the pinned
parent-only baseline. The nine additional messages are the previously observed
foreign medium nationalist flags. No message names `TFR_EST_` or `tfr_estonia`.
Against the earlier same-day 39-case development run, there are **zero new
messages**; SPM's small-flag message did not recur. This is not a claim that the
foreign asset issue was repaired. Reports are `test-output/ratas-engine-comparison.json`
and `test-output/ratas-previous-development-comparison.json`. The owned process
was stopped and the original mod/DLC configuration restored byte-for-byte.
The fixture invokes effects in country history; it does not select focuses,
exercise the natural election scheduler or render the hidden branches.

The Kallas-transition run is captured under
`test-output/engine-estonia-qa-20261015-142648/`. It reached the frontend in about
**212 seconds** (214 seconds including capture) and passed **all 52 native
assertions**. Six new cases verify that a delayed resignation uncompletes only
the referendum while retaining all ten earlier native completions, the confirmed
60-seat Kallas cabinet governs its own route, recovered COVID bypasses only its
emergency interventions, Kallas energy measures mitigate the same local shock,
mixed-route energy flags do not stack, and a new Reform election ends the old
Kallas mandate without a stale caretaker handover.

The captured error log has 2,032 normalized unique messages, exactly matching the
preceding retained-Ratas run: **zero new messages, zero removed messages and zero
messages naming `TFR_EST_` or `tfr_estonia`**. The nine previously recorded foreign
flag differences remain against the pinned parent-only baseline. Reports are
`test-output/kallas-previous-development-comparison.json` and
`test-output/kallas-engine-comparison.json`. The owned process stopped and the
original mod/DLC configuration was restored byte-for-byte.

This run confirms the documented uncompletion effect on an already completed
referendum. Actual automatic cancellation of a running focus on the engine's
validity update, rendered branch replacement and normal campaign scheduling
remain interactive acceptance checks. The final legacy phase-root prerequisite
removal was applied after this run and is covered by the source restoration
regression and final structural validation.

The latest compact-focus run is captured under
`test-output/engine-estonia-qa-20261016-122842/`. It reached the frontend in
approximately **280 seconds** and passed **all 54 native assertions**. The
existing energy cases now exercise the real Oil Crash idea, full removal after
preparation and preservation of permanent reforms. Two additional cases execute
the highway's actual improved +5% construction/−4% supply-consumption reward and
confirm that none of the 49 display-only preview definitions becomes an idea.
The concise governing wrappers also participate in the existing native checks.

The captured log contains **2,023 normalized unique parent messages**, exactly
matching the pinned parent-only baseline: **zero new messages, zero removed
messages and zero Estonia-prefixed errors**. Comparison with the previous
development run also finds no new messages; its nine foreign missing-flag
messages did not occur in this capture. Their absence is not attributed to an
asset fix. Reports are `test-output/compact-engine-comparison.json` and
`test-output/compact-previous-development-comparison.json`. The owned process
stopped and the original mod/DLC configuration was verified restored byte-for-byte.
No normal campaign or rendered tooltip inspection was performed.

The accepted minister run is captured under
`test-output/engine-estonia-qa-20261016-131021/`. It reached the frontend in
approximately **216 seconds** and passed **all 72 native assertions**. The
eighteen new cases cover historical cabinet initialization, real coalition
eligibility, duplicate offices, user vacancies, PM/portfolio exclusion, trait
application, party withdrawal, caretaker behavior, invalid/valid election costs,
all seven parties' full cabinets and occupation cleanup. Native modifier reads
measured **+0.04 stability** from Katri Raik's trait and **−0.50** in each of the
five minister-cost factors after the valid election.

The initial minister fixture reached the frontend but passed 70/72 cases: it
read stale idea-modifier values during country-history execution and queried
unsynchronized dynamic cost tokens. The corrected fixture refreshes modifiers
before/after its comparisons and declares the five query tokens only in the
ignored QA overlay. No gameplay buff, appointment rule or discount was changed
to make the numerical tests pass. The original failed capture remains recorded
under `test-output/engine-estonia-qa-20261016-130451/` and is not an accepted run.

The accepted error log has **2,015 normalized unique parent messages**, **zero
new messages** against both the pinned parent-only baseline and the previous
development run, and **zero Estonia-prefixed errors**. Eight foreign missing-flag
messages did not appear in this capture; that absence is not attributed to an
asset fix. Reports are `test-output/ministers-engine-comparison.json` and
`test-output/ministers-previous-development-comparison.json`. The owned process
stopped and the original mod/DLC configuration was verified restored byte-for-byte.
This verifies the native cost factors and trait modifiers; political-screen
clicks, PP purchases and natural expiration of the 90-day window remain manual
campaign checks, alongside rendered portraits and tooltips.

The alternatives/80% revision is captured under
`test-output/engine-estonia-qa-20261016-133716/`. It reached the frontend in
approximately **261 seconds** and passed **all 74 native assertions**. All five
appointment-cost reads now measure **−0.80**. Two additional cases explicitly
mark Reinsalu and Martin as future authored incumbents, verify that the incumbent
cannot also hold a portfolio, and confirm that Velliste/Kokk remain eligible.
The Martin case also verifies that Mart's ordinary minister candidacy is restored
under Martin's personal identity. No current route changes PM through these tests.

The capture has **2,032 normalized unique messages** and **zero Estonia-prefixed
errors**. Nine additional messages against the pinned parent-only baseline name
the same missing foreign medium nationalist flags recorded in earlier accepted
development runs (GBA, KHA, LBV, ORO, PAP, SID, SPM, TOS and VGE). The previous
minister capture omitted several foreign-flag loads, so its direct comparison
contains seventeen additional foreign-flag messages. No candidate, trait, PM
identity or cost-factor errors occur. Reports are
`test-output/minister-alternatives-engine-comparison.json` and
`test-output/minister-alternatives-previous-comparison.json`. The original mod/DLC
configuration was verified restored byte-for-byte after the owned process stopped.

The QA overlay is not shipped or enabled in ordinary play. It executes arithmetic
within a single hidden-effect context during frontend history construction.
Temporary input and consumer statements must remain in the same context.

An earlier experiment invoking occupation/diplomatic transitions during country
history construction crashed before reaching the frontend. That fixture was
removed. A history-time crash does not establish whether a live campaign
settlement succeeds; protected occupations still require the active-campaign
checks below. Earlier failed or incomplete runs remain in ignored local test
outputs and are not counted as passes.

## Acceptance checks still open

No ordinary campaign was started by the smoke-test tool. Native application UI
control is unavailable in this environment, so rendered interface acceptance and
interactive campaign observations were not performed.

- Ordinary campaigns for all seven parties, including legitimate route entry.
- Every supported Russian and European defeat settlement in a running campaign,
  with original force handling, a second defeat and restoration.
- Parent pacification/integration and both-war progression under protected EST.
- Save/reload around elections, delayed settlements and restoration.
- AI research, production, recruitment, coalition behavior and focus progression.
- DLC combinations, UI scales, full text/tooltip display and actual focus layout.
- A natural 2020 opening through both Ratas choices, banked focus progress,
  manual cancellation attempts, delivered-event delays and post-crisis branch reveal.
- A retained-Ratas campaign through all twenty continuation focuses before the
  2023 election, with natural pandemic recovery, Saudi-war onset/settlement,
  early/late preparations, saved crisis contributions and the electoral handoff.
- Resignation during the active referendum and after delayed event response,
  native cancellation timing, Kallas's thirteen-day handover and all twenty
  successor focuses before the election, including occupation/restoration with
  native opening completion IDs lost and persistent policy markers retained.
- Long-term economy, preparation, military growth and occupation balance.
- Native minister-menu purchases, trait tooltips, generic portraits, vacancy
  selection, cost display, 90-day expiry and save/reload during cabinet formation.
- Custom portraits for characters currently using generic likenesses, plus actual
  campaign screenshots for a public Workshop release.

Use [the manual matrix](TEST_MATRIX.md) to record these observations. Public v1
acceptance requires completing that matrix; successful source, startup and
isolated arithmetic tests are the current evidence.

## Reproduction

Run the source checks in the README. Close any active HOI4 session before using
the smoke-test tool. Prepare the isolated fixture with
`python tools/prepare_engine_qa.py`, then run
`tools/run_engine_smoke.ps1 -ArithmeticQA -Seconds 600`. Use `-ParentOnly` for
the clean baseline. The tool stops early on frontend completion and checks every
expected QA assertion. Compare captured logs with `tools/compare_engine_logs.py`.

If Windows retains an inert child from an exited recorded test, the optional
`-IgnoreInertQaChildOf <recorded-parent-PID>` accepts only a matching saved exited
QA parent, no game window and a working set no greater than 1 MiB. It does not
terminate that child or exempt active/unrecorded game processes.

Rebuild the ZIP after changing documentation or source, then use
`python tools/package_mod.py --check` to verify it exactly matches current inputs.
The archive manifest records each packaged file's byte size and SHA-256 hash.
