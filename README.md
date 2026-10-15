# TFR Estonia

An Estonia country expansion for **The Fire Rises 1.0.9.1c / Hearts of Iron IV 1.19.\***.

This implementation includes the seven governing parties, a 101-seat Riigikogu,
national cohesion and defense readiness, both European-war campaign stages,
and playable occupation administrations. Start a **new 2020 campaign**; saves
created without the submod are not supported.

## Installation and first campaign

1. Keep this folder under `Documents/Paradox Interactive/Hearts of Iron IV/mod/tfr-estonia`.
2. The adjacent `tfr-estonia.mod` launcher descriptor must point to this folder.
3. Enable **The Fire Rises** and **TFR Estonia** together. For validation, use a
   clean playset with these two mods. Other overhaul/submod compatibility is not assumed.
4. Start on 1 January 2020 as Estonia. Allow one game day for the shared systems
   to initialize, then open the **Riigikogu**, **National Cohesion**, and
   **Defense Readiness** decision categories.

The opening parliament uses the real 2019 seats: Reform 34, Centre 26, EKRE 19,
Isamaa 12, and SDE 10. Jüri Ratas leads the 57-seat Centre–EKRE–Isamaa coalition.
Kersti Kaljulaid appears as the president in the main country portrait. Jüri
Ratas appears in TFR's head-minister slot and shared head-of-government tooltip,
using the same arrangement as Germany's president and chancellor. Cabinet
changes update the prime minister while preserving the constitutional president.
The existing succession event installs Alar Karis; caretaker cabinets retain
their incumbent prime minister. Occupation suspends this constitutional display
and restoration reinstates the saved presidency and cabinet ledger.

## The 2020 coalition opening

The initial focus screen contains ten policy focuses in **four short branches**,
followed by the final marriage-referendum focus. All last **35 days**. Players
can switch between branches while completing these prerequisites:

- Voluntary second-pillar reform → the €7 extraordinary pension increase.
- Teacher pay → research funding at 1% of GDP.
- Kose–Võõbu highway → eastern-border construction and the Three Seas summit,
  which are separate choices after the highway.
- COVID emergency → wage compensation and excise relief, which are separate
  choices after the emergency response.

The policies cover voluntary second-pillar reform, €1,315
teacher pay, COVID emergency measures, the €7 extraordinary pension increase,
wage compensation, diesel/electricity excise relief, the first eastern-border
section, the Kose–Võõbu highway, the Tallinn Three Seas summit and 2021 research
funding at 1% of GDP. The historical sources and writing constraints are recorded
in [the policy register](docs/OPENING_POLICY_SOURCES.md).

These policies require a Centre prime minister, Centre–EKRE–Isamaa coalition
membership, and **51 actual cabinet seats**. Confidence-and-supply support remains
part of parliament but does not replace this coalition requirement. The pension,
teacher-pay and highway roots are available from the start with a valid
coalition. The COVID root also requires COVID cases to be present in Estonia,
using TFR's country-level infection check. An independent first-case event supplies
the outbreak hook missing from the parent mod, from the Health Board's
[27 February 2020 announcement](https://terviseamet.ee/uudised/eestis-diagnoositi-esimene-covid-19-haigusjuhtum).
No ordinary policy focus has a start-date gate. The four branches lead to six
terminal policies, all of which must be finished before the referendum.

All ten policies must finish before **The Marriage Referendum Bill**. Its earliest
start is December 24, 2020, accounting for TFR's 14 banked focus days. This is the
only date gate in the opening. Continuous play
from the opening normally carries the final focus across January 12–13, 2021 and
finishes around January 20–21; pauses or lost majorities delay it. The final focus
cannot be canceled manually and continues through ordinary confidence loss.
Ratas's explicit resignation aborts it automatically and abandons the proposal.

While it runs, the Porto Franco investigation and Ratas's response appear as
events. Keeping Ratas renews the original 57-seat cabinet. Resigning fails the
referendum and leaves him as caretaker during 13 days of negotiations, then permits Kaja Kallas to confirm
a Reform–Centre cabinet with the original 60 seats. This does not alter polls,
seats or the next regular election date. The historical referendum was proposed
for April 2021 and never held; this focus concerns its bill and the government
crisis. Delayed campaigns receive the events after starting the final focus.

Choosing to keep Ratas reveals the continuation below, while the referendum
continues to its conclusion. Its first focus still requires the referendum to
finish. The same main tree remains loaded throughout the crisis, preserving the
non-cancelable focus. Resignation instead hides the opening and reveals Kallas's
dedicated programme immediately; its focuses wait for her cabinet's confirmation.
Earlier completed policies and rewards remain. War branches follow the campaign
stage on either route.

## Ratas remains: the programme through 2023

The retained Centre–Isamaa–EKRE cabinet receives **twenty 35-day focuses** built
around the unfinished commitments in its 2019 coalition agreement, supplemented
by pandemic plans prepared in December 2020. The continuation is hidden at the
start and appears only after the player chooses to keep Ratas. Renewing the
agreement opens five branches:

- Family-home guarantees, child-based tax relief and home nursing.
- State jobs outside Tallinn, rural broadband, regional industrial parks and
  adult retraining.
- COVID hospital capacity, testing and tracing, evening/weekend family-doctor
  access and vaccination of risk groups.
- LNG connections, European-grid investment, renewable combined heat and power,
  home renovation and temporary network-charge relief.
- Police/border-guard reserves and conscript/Kaitseliit training.

Players choose which branch to advance. Completing all five permits a final
report to voters. All legislation requires the original three partners, Centre
as the governing party, no caretaker status and **51 actual coalition seats**.
The new rewards use the existing economy and military dynamic modifiers, cohesion,
readiness and explicit budget costs. The [source register](docs/RATAS_CONTINUATION_SOURCES.md)
distinguishes the coalition's commitments from their implementation in TFR.

The three pandemic interventions require actual cases in Estonia. If its recorded
outbreak has already recovered, those emergency measures are bypassed without
their rewards so the programme can continue; the family-doctor reform remains a
normal policy. Vaccination improves an existing severity by one tier, and removes
the lowest tier only when it belongs to the submod's own outbreak bridge.

TFR's Saudi-war supply shock triggers an Estonian economy penalty of **−4% factory
output and +3 percentage points of consumer goods**. LNG, grid and generation
preparations each offset one point of the output penalty; renovation and funded
network-charge relief each offset 1.5 points of the consumer-goods penalty. These
focuses can prepare for a later shock as well as respond during it. The end of the
parent crisis removes only Estonia's tracked crisis contribution, preserving
other reforms and other countries' crisis content.

Twenty focuses take **700 days**. Beginning the continuation on 28 January 2021
allows completion on 29 December 2022, with 66 days before the 5 March 2023 election
date. Delays caused by inactivity, lost coalition confidence or occupation consume
that margin. The election calendar and seat-allocation rules are unchanged.
The next valid election ends this 2019 coalition programme, even if Centre wins
again, and reveals the normal domestic programmes. While it is active, those older
party, economy and military branches remain hidden; relevant war and restoration
branches can still appear when the world state requires them.

## Ratas steps back: Kallas's government through 2023

Resignation automatically fails **The Marriage Referendum Bill**, including if
the player delayed responding until the focus had finished. Only that final
focus is undone; the ten earlier policies retain their completion and rewards.
The opening disappears and a hidden **twenty-focus Kallas programme** appears.
**A Reform–Centre Government** can begin after confirmation of her cabinet in the
same parliament, with the original 60 seats and unchanged election calendar.

The twenty 35-day focuses open five branches:

- Sick pay from the second day, the €52 million hospital package, frontline-worker
  vaccination, and digital COVID certificates.
- Legislation for the €20 pension increase, average-pension income-tax relief,
  teachers' minimum pay of €1,412, and €12 million for learning gaps.
- The recovery investment programme, enterprise digitisation, rural broadband,
  and community mental-health services.
- Eligible household energy-bill compensation, electricity/gas network-charge
  relief, strategic gas reserves, and LNG connection capability.
- The 2022 defence funding commitment and civil protection through shelter
  marking, evacuation rehearsals, warning systems and stocks.

Each branch has prerequisites, and players can choose between branches.
**Present the Government's Record** requires the whole programme. All legislation
requires Kallas's confirmed Reform–Centre cabinet and at least **51 actual
coalition seats**. The first three COVID interventions require domestic cases;
after a recorded outbreak recovers they bypass without rewards, preserving access
to the certificate service and final report. Energy measures can be prepared
before the Saudi-war crisis or funded during it. Both government routes share
the same capped mitigation, so repeated or inherited projects cannot stack it.

The policies follow actual Reform–Centre decisions and enacted legislation from
2021–2022, recorded in [the Kallas source register](docs/KALLAS_GOVERNMENT_SOURCES.md).
The party partnership continuing through the election is alternate history;
the route does not force the real 2022 coalition collapse. Twenty focuses take
**700 days**: a 26 January 2021 start allows completion on **27 December 2022**,
68 days before 5 March 2023. A lost majority, occupation or player delay consumes
that margin. The next valid election ends this programme even after another
Reform victory, revealing the broader domestic tree. Relevant war and restoration
branches remain governed by the world state.

War, restoration and later-term branch entries use the saved opening-resolution
state. They remain reachable after occupation and restoration even when the
engine no longer retains the earlier opening's native completion records.
Prerequisites within those branches remain in place.

## Playing the political system

- Each of Reform, Centre, EKRE, Isamaa, SDE, Eesti 200 and Parempoolsed has its own
  identity, polling, seats, cabinet membership and policy programme.
- Eesti 200 begins outside parliament. Parempoolsed emerges from August 2022
  onward when independent politics is available.
- Campaign decisions move polling support; they do **not** change existing seats.
- Elections use a simplified national proportional system: 5% threshold,
  101 seats, largest remainders, and deterministic ties. The opening historical
  seats are seeded directly rather than recalculated by the simplified model.
- Cabinet confirmation requires 51 confidence votes. Cabinet members and
  confidence-and-supply partners are counted separately, with no double counting.
- Centre holds the opening coalition leadership. After each valid election, the
  party with the most seats automatically leads coalition formation. Exact seat
  ties use Reform, Centre, EKRE, Isamaa, SDE, Eesti 200, Parempoolsed order.
- Negotiate coalition partners or confidence and supply, then confirm the
  mandated cabinet with 51 votes. The incumbent remains caretaker until the
  elected successor is confirmed. There are no player nomination decisions.
- Between elections, confidence recovery reconfirms the incumbent. A different
  prime minister requires an explicit event or focus; ordinary negotiations and
  AI route preferences cannot replace the coalition leader.
- Regular elections begin in March 2023 and repeat every four years. Restored
  independence triggers an election within 90 days.
- There is no snap-election decision or automatic caretaker snap vote. Only an
  authored event or focus can authorize one.
- The dedicated Riigikogu panel shows polling, seats, cabinet membership,
  supply agreements and the election calendar. TFR's ideology chart is a
  compatibility view; it is not the source of seats or confidence votes.

Government programme focuses become available to the current party in office.
An election can open a different programme. Completed policies remain recorded,
and active cabinet bonuses reconcile with the current government.

## Cohesion, defense and the economy

Cohesion starts at **55** and readiness at **25**, both on a 0–100 scale.
Their tiers change at 25, 50 and 75. Decision descriptions show the current value,
net weekly trend, source effects and costs. Community consultation, emergency
relief and reserve exercises affect weekly trends; caretaker government and war
create strain.

Project budgets are stated in **millions of euros**, converted to the parent
mod's debt units, and applied through TFR's inflation-adjusted economic effects.
The submod retains the existing euro, EU, NATO, influence and economic setup.

**Estonian Economy** and **Estonian Military** are permanent, variable-driven
dynamic modifiers, using the same structure as TFR's country modifiers. Their
initial values are neutral. The economy container supports construction,
industrial output, production efficiency, research, resources and consumer goods;
the military container supports combat, organization, mobilization, training,
entrenchment, attrition and supply. Missing variables or modifiers are repaired
without resetting saved adjustments. New opening, retained-Ratas and Kallas bonuses use these
containers. Later programmes retain their current reward ideas pending their
own content revision.

Reserve authorization unlocks a Kaitseliit template and temporary training
support. **Recruit units normally**: the authorization does not spawn free
soldiers or equipment. Funded procurement is capped by decision cooldowns.
Prepared mobilization can lift Estonia's inherited NATO peacetime military
restrictions without changing other NATO countries.

## War, occupation and restoration

Campaign stages follow TFR's war flags and actual war state. Shared branches
cover preparation, the first war, reconstruction, the second war and restoration.
Each party has separate choices responding to the two wars.

Supported TFR settlements keep the same **EST** country playable. Existing
puppet partitions retain their intended borders. Where a settlement would remove
Estonia, a playable occupation government retains **state 13, Northern Estonia**;
other territorial transfers continue according to the parent outcome.

Occupation variants cover communist, civilian Russian, nationalist/military,
Eurasian, liberal Baltic, European supervised and European authoritarian
administrations. Normal elections and the parliamentary panel are suspended.
Local services, permitted forces, accommodation, clandestine organization and
restoration have their own content. The custom occupation autonomy level prevents
ordinary autonomy downgrade annexation.

This protection is for the audited TFR campaign and settlement paths. Arbitrary
console actions, debug map decisions and third-party modifications are outside
the guarantee. Military defeat and hostile control during a later war remain
possible; daily reconciliation does not force Tallinn back into friendly control.

Every focus records persistent completion. Tree switches therefore do not make
factory investments, equipment grants or completed reforms available repeatedly.

## Development and validation

Python 3 and Git are sufficient for the local tools. From this folder run:

```powershell
python tools/validate_mod.py
python -m unittest discover -s tests -v
python tools/patch_tfr_compatibility.py --check
python tools/test_occupation_compatibility.py
python tools/native_script_interface.py --check
```

On this Codex host, Python is also available at:
`C:\Users\Sten\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.

`tools/build_systems.py` and `tools/build_normal_content.py` preserve the authored
sources for their generated content. Treat the parent compatibility generator
separately: `--check` verifies hashes and output; review upstream changes before
using `--write` after a TFR update.

Opening content is generated by `tools/build_opening_content.py` and
`tools/build_opening_story.py`; the independent first-case hook is generated by
`tools/build_estonia_covid.py`. The retained coalition's extension is generated by
`tools/build_ratas_continuation.py`, and the Reform–Centre programme by
`tools/build_kallas_continuation.py`. All support `--check`. Use
`tools/build_normal_content.py --focus-only` for the main tree, route AI, focus
text and dependent decisions without rewriting unrelated event/idea files.

For a controlled startup parser check, close any existing HOI4 session and run:

```powershell
.\tools\run_engine_smoke.ps1 -ParentOnly -Seconds 600
.\tools\run_engine_smoke.ps1 -Seconds 600
python tools/prepare_engine_qa.py
.\tools\run_engine_smoke.ps1 -ArithmeticQA -Seconds 600
```

This tool temporarily selects a clean mod configuration, launches only its own
game process, copies logs into ignored `test-output`, stops that process, and
restores the original mod-load configuration. It does **not** start or validate
a campaign. Do not use it while playing an existing game.

The 600-second limit allows cold startup; the tool finishes early when the game
reports the frontend ready. The optional isolated QA overlay executes native
election, leadership-mandate, executive-display, meter and dynamic-modifier
assertions while constructing the initial country snapshot, and is excluded from releases. These checks do not exercise
combat, natural war progression, interface rendering or save/reload.

See [the architecture](docs/ARCHITECTURE.md), [manual test matrix](docs/TEST_MATRIX.md),
the [content specification](docs/CONTENT_SPEC.md) and
[validation results](docs/TEST_RESULTS.md) for the implementation contracts
and the distinction between automated checks and in-game verification.

## Assets and release status

The submod references installed TFR and base-game assets. The new prime ministers
and some occupation administrators currently use existing **generic portraits**;
they are named and scripted characters, but these are not custom likenesses.
No external photographs, music or TFR artwork are bundled.

The content is implemented as a development build. Natural campaigns, rendered
interface inspection, DLC combinations and balance testing are release gates
recorded in the manual matrix. A public Workshop release must not be presented
as fully playtested until those gates are completed.

## Packaging

Run `python tools/package_mod.py` to create the portable development ZIP in
`dist/`; `python tools/package_mod.py --check` verifies it against the current
sources. Identical inputs produce an identical ZIP. The package includes the
gameplay files, documentation, tools, tests, original flag thumbnail and a hash
manifest; Git data, caches, logs and test outputs are excluded.

Extract the ZIP into your HOI4 user-data `mod` directory. It contains
`tfr-estonia/` and the adjacent `tfr-estonia.mod` with portable
`path="mod/tfr-estonia"`. Enable **TFR Estonia (Development)** alongside
**The Fire Rises**. This is a development artifact, not a Workshop publication.

## Updating TFR

The parent remains untouched. Shared-file overrides are necessary to stop
destructive settlements **before** annexation occurs. Their upstream hashes and
individual changes are recorded in `docs/compatibility.json`. The additional
shared head-of-government localization adapter retains every upstream country
selector and adds Estonia's seven party-ledger selectors. The shared GUI itself
is inherited directly from TFR.

After a TFR update, compare each overridden file against the new parent version,
review changed war/occupation assumptions, regenerate only after review, and rerun
the automated and settlement tests. Reusing stale overrides can discard upstream
fixes. Generated overrides retain the upstream BOM and use canonical LF line
endings, enforced by Git attributes so output hashes survive checkout. Raw parent
hashes are recorded separately. The supported baseline is 1.0.9.1c.

Credits: The Fire Rises team and Paradox Interactive for the referenced parent
content and game assets; Estonia's official election and government records for
the starting parliament and cabinet. Later paths are fictional game content.
