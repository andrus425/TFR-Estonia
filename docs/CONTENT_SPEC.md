# Implemented campaign content

This document records the implemented design for the development build. Balance
values are starting values; the manual campaign matrix determines public-release
acceptance. Later events are fictional developments in TFR's alternate timeline.

## Initial coalition programme

The opening has ten policy focuses in four short branches and a final marriage-referendum
focus, each lasting 35 days, built from the documented Ratas II
policies in [OPENING_POLICY_SOURCES.md](OPENING_POLICY_SOURCES.md). It replaces
the eight vague introductory nodes; party programmes and later campaign work are
hidden until the opening finishes. The ten policies require the original three
partners, a Centre prime minister and at least 51 actual coalition seats. Players
choose between the pension-reform, teacher-pay and highway roots from the start;
the COVID root additionally requires actual cases in Estonia. The branches are:

- Pension reform → extraordinary pension increase.
- Teacher pay → research funding.
- Kose–Võõbu highway → eastern-border construction and Three Seas summit as siblings.
- COVID emergency → wage compensation and excise relief as siblings.

Six terminal focuses lead to the final focus, requiring all ten policies through
their ancestor prerequisites. None of the ordinary policies has a start-date
gate. The COVID focus uses TFR's `generic_has_corona` trigger, which reads the
country's five case-severity ideas. A separate first-case event supplies Estonia's
missing parent outbreak assignment from February 27, 2020. It preserves existing
cases and does not reinfect after recovery. From 2023, it removes only its own
unchanged lowest-severity idea after the mandatory COVID focus has finished,
preserving access to that focus during delayed campaigns.

The marriage-referendum bill is the final focus. All ten policies are mandatory,
the focus cannot be canceled manually, and its December 24, 2020 gate accounts for up to 14
banked days. Investigation/response events on January 12–13 offer a retained Ratas
cabinet or resignation followed by a Reform–Centre cabinet in the same parliament.
Ordinary confidence loss cannot stop the active focus, but Ratas's resignation
automatically fails it and abandons the proposal. That outcome hides the opening
and reveals Kallas's programme. If the player delayed the choice until after the
focus completed, only this final focus is undone; the ten earlier policies and
their rewards remain. The historical April referendum never occurred; remaining
in office is an alternate-history branch.
The final focus is the only opening focus with a start-date requirement.

New opening, retained-coalition and Kallas economic and logistical bonuses use the country
dynamic modifiers. Older programme rewards await their own redesign. There is no player snap vote;
the crisis changes cabinets through explicitly authorized story effects.

## Retaining Ratas until the next election

Choosing not to resign reveals **twenty 35-day focuses** below the opening, based
on the coalition's unfinished 2019 commitments and its December 2020 COVID plans.
The reveal happens when the choice is made; the renewal focus cannot start until
the referendum finishes. Both the opening and extension remain in the same main
tree. Sources, chapters and pages appear in
[RATAS_CONTINUATION_SOURCES.md](RATAS_CONTINUATION_SOURCES.md).

**Renew the 2019 Coalition Agreement** opens these five branches. Each arrow is
a prerequisite; the player can move between branches in any valid order:

- KredEx family-home guarantees → child-based tax allowance → home nursing.
- Move 1,000 state jobs beyond Tallinn → rural broadband → regional industrial
  parks → adult retraining.
- County-hospital COVID wards → testing and contact tracing → evening/weekend
  family-doctor access → risk-group vaccination through family doctors.
- Estonian LNG connection → European-grid investment → renewable combined heat
  and power → building-renovation grants → temporary network-charge relief.
- Police/border-guard crisis reserve → conscript and Kaitseliit training.

All branch terminals are required before **Account for the Coalition's Promises**.
The full programme takes 700 days, so a 28 January 2021 start can finish on
29 December 2022, leaving 66 days before 5 March 2023. Neither the final report nor
any other new focus calls an election. Coalition breakdown, occupation and player
delays can consume the available margin.

Legislation requires Centre to retain the PM and leadership mandate, all three
original parties to remain coalition members, at least 51 actual coalition seats
and no caretaker status. Supplies from outside parties cannot replace the cabinet
majority. Costs are explicit debt-financed budgets; rewards adjust the existing
dynamic modifiers and cohesion/readiness, with persistent one-time completion.
Security programmes improve training and preparation without granting free units.

The hospital, testing/tracing and vaccination focuses require a domestic case
tier. After the country's recorded outbreak recovers, unneeded pandemic measures
are bypassed without rewards. This preserves access to ordinary family-doctor
reform and the final report. Vaccination improves one existing severity; it can
clear the lowest tier only when the submod owns that outbreak seed.

TFR's Saudi-war flags control the energy shock. Estonia receives a local −4%
factory-output and +3-point consumer-goods contribution in its economy dynamic
modifier. The LNG, grid and combined-generation focuses each mitigate one output
point; renovation and network-charge relief each mitigate 1.5 consumer-goods
points. Focuses can prepare before onset or respond during the crisis; no onset
date blocks the programme. Resolution reverses only the tracked local crisis
contribution. Permanent policy adjustments and parent global/country crisis
systems remain independent. Network-charge relief is distinct from the opening's
electricity excise cut, and infrastructure focuses finance programmes rather than
claiming complete projects in 35 days.

Older party, economy and military sections remain hidden during the retained
coalition's 2019 mandate, while war/restoration sections still follow world state.
The next valid election ends the extension and reveals the older domestic
programmes, even if Centre wins again. An invalid election leaves the current
mandate intact. The ordinary seat allocation and election calendar are unchanged.

## Kallas's Reform–Centre government until the next election

Ratas's resignation reveals **twenty 35-day focuses** and resolves the opening as
an abandoned referendum. **A Reform–Centre Government** has no prerequisite on
the failed final. It requires Kallas's confirmed cabinet after the existing
thirteen-day negotiations, using the same 60-seat parliament. The implemented
policies come from actual 2021–2022 decisions and enacted laws, with sources and
historical effective dates in
[KALLAS_GOVERNMENT_SOURCES.md](KALLAS_GOVERNMENT_SOURCES.md).

The formation root opens five branches. Each arrow is a prerequisite, while the
player chooses which branch to advance:

- Extend sick pay from day two → EUR 52 million hospital package → frontline
  vaccination → digital COVID certificates and verification.
- Legislate the EUR 20 pension increase → average-pension income-tax allowance →
  teachers' minimum EUR 1,412 → EUR 12 million for learning gaps.
- Recovery investment programme → enterprise digitisation → rural broadband →
  community mental-health services.
- Compensate eligible household energy bills → electricity/gas network-charge
  relief → procure a strategic gas reserve → fund LNG connection capability.
- The 2022 defence commitment → public shelter marking and evacuation preparation.

All five branch terminals and earlier policies are required before **Present the
Government's Record**. Legislation requires Reform PM and mandate, both Reform
and Centre in the coalition, no caretaker and at least 51 actual coalition seats.
Confidence-and-supply cannot replace that cabinet majority. Costs use the public
budget helper; persistent records prevent repeated dynamic-modifier, cohesion
and readiness rewards.

The first three COVID focuses require actual domestic cases. After an earned
formation root and recovery from a recorded outbreak, unused emergency policies
bypass without rewards. Digital certificates remain accessible afterward.
Frontline vaccination improves one existing case tier through the same guarded
ladder used by the retained-Ratas government.

The energy policies adapt contemporary measures to TFR's Saudi-war crisis. Bill
compensation mitigates 1.5 consumer-goods points; network-charge relief mitigates
one output point and 1.5 consumer-goods points; the gas reserve and LNG capability
each mitigate one output point. The two routes share five capped mitigation
slots rather than stacking duplicate projects. Completing all applicable work
reduces the local crisis from −4% output/+3 goods points to −1%/0. The source
allocations of up to EUR 170 million for gas reserves and EUR 30 million for LNG
capability fund procurement and enabling works, not instantaneous terminals.
Preparations can precede onset, and resolution preserves permanent reforms.

Twenty focuses require 700 days. A 26 January 2021 start permits completion on
27 December 2022, leaving 68 days before 5 March 2023; confidence loss, occupation
and player delays consume that margin. No programme focus calls or postpones the
regular election. The route does not force the real 2022 coalition collapse, and
its continued Reform–Centre partnership is explicit alternate history. The next
valid election ends this programme even if Reform wins again, revealing the
broader domestic sections. War and restoration access still follows world state.
The phase-entry roots use the persistent opening-resolution guard, without an
external native opening-focus prerequisite. This preserves access if occupation
and restoration remove native opening completion IDs; internal prerequisites
within each branch still apply.

## Political entry and persistence

All governing routes require an independent parliament, an electoral or explicit
story leadership mandate and at least 51 confidence votes. Centre leads the opening.
Subsequent elections automatically give coalition leadership to the party with
the most seats, with fixed party order resolving exact seat ties. The player
negotiates partners and supply agreements around that leader. Coalition members
and supply partners remain separate records. Between elections, ordinary
confidence recovery retains the incumbent; another succession requires an
explicit authored event or focus.
Outside the dedicated retained-Ratas and Kallas programmes, the current confirmed party unlocks
its programme; a caretaker cannot enact it.

Each older general party programme has ten focuses, one policy-conflict event, an active cabinet
modifier, and distinct first- and second-war response events. Completed laws and
investments persist through elections and occupation. Only the current cabinet's
programme modifier applies. Restoration resumes the saved party ledger under a
provisional caretaker and schedules an election within 90 days.

Following TFR's German model, the president occupies the main native country
portrait, while the prime minister appears in the head-minister slot and shared
head-of-government tooltip. The president remains separate through changes of
ruling party; the seven PM identities come directly from the parliamentary
ledger. Caretakers retain the incumbent PM, and occupation suspends the display.

| Party and leader | Entry and programme | Conflict and defense priorities |
|---|---|---|
| Keskerakond — Jüri Ratas | Starts as prime minister with the Centre–EKRE–Isamaa coalition. Municipal finance, regional transport, social guarantees, integration and coalition delivery. | Regional and social commitments compete for the budget. War choices emphasize municipal continuity, public support and organized reserves. |
| Reform — Kaja Kallas | Parliamentary opposition at the start. Digital administration, accountable investment, enterprise, education and European cooperation. | The fiscal debate trades the pace of consolidation against cohesion and service guarantees. War choices balance institutional continuity with interoperable procurement. |
| EKRE — Mart Helme | Coalition partner initially; can lead a cabinet after winning the most seats. Sovereignty, border security, local production, conservative policy and mobilization. | Emergency authority and coalition restraint affect legitimacy and partner relations. War choices emphasize local mobilization or support for the wider allied operation. |
| Isamaa — Helir-Valdor Seeder | Coalition partner with 12 initial seats. Family security, constitutional institutions, energy resilience and territorial defense. | A small parliamentary base requires coalition concessions. War choices fund county institutions or territorial command and logistics. |
| Social Democrats — Indrek Saar | Opposition initially. Labor agreements, regional healthcare, retraining, integration and civil resilience. | Expanded services require funded commitments. War choices distribute support between civilian relief and service families or emergency work. |
| Eesti 200 — Kristina Kallas | Active outside parliament in 2020; must enter parliament and win the most seats before leading a cabinet. Teachers, institutional redesign, university-industry cooperation and long-term planning. | Institutional reform trades speed against continuity of local services. War choices adapt planning to immediate defense while preserving schools and reconstruction capacity. |
| Parempoolsed — Lavly Perling | Formation from August 2022 when independent politics is available, then an election and valid cabinet confirmation. Administrative audit, enterprise rules, fiscal discipline, justice and procurement. | Consolidation trades savings against public confidence. War choices emphasize contract scrutiny, essential services and maintainable equipment. |

Party labels in the ledger are authoritative. Ideology popularity is a projection
for TFR compatibility: Reform/PP share market liberal; Centre/E200 share social
liberal; Isamaa is conservative, SDE social democratic and EKRE authoritarian
democratic. Sharing an ideology grants no seats or coalition membership.

## Shared independent campaign

The main tree contains 200 focuses: eleven opening focuses, twenty retained-Ratas
continuation focuses, twenty Kallas government focuses, 70 general programme focuses,
18 economic focuses, 21 military focuses and 40 campaign focuses. Branches are
available according to independence, government and campaign stage; they do not
lock later elected parties out permanently.

The opening implements the coalition's pension, teacher-pay, pandemic-relief,
tax, border, transport, regional-cooperation and research policies before the
referendum crisis. A retained government follows its extended coalition programme;
resignation instead opens Kallas's dedicated programme. The next parliamentary term uses the broader domestic
branches. Economic development supports education, regional investment, infrastructure,
energy, digital services and defense industry. Defense preparation covers reserve
organization, Kaitseliit, training, engineering, artillery, air defense, supply,
maintenance, procurement and allied cooperation.

Cohesion and readiness start at 55 and 25, are clamped to 0–100, and use tiers
at 25, 50 and 75. Weekly drift aggregates named sources. Decisions can fund
consultation, relief and exercises, with costs, duration and cancellation behavior.
Project spending enters TFR's inflation-adjusted debt ledger in converted units.

Reserve authorization creates a recruitable template and training support once.
It does not create a free field army. Domestic procurement has equipment limits
and cooldowns. Allied `EST_nato` reinforcements remain separate from national
reserve organization. Prepared mobilization lifts the inherited NATO restriction
for Estonia once, with readiness or war prerequisites.

TFR's first- and second-war flags and actual war state advance the campaign.
Wartime government, mobilization, territorial defense, reconstruction, renewed
preparation and constitutional restoration have dedicated content. Ordinary
independent elections continue in wartime. Normal focuses suspend under occupation.

## Occupation campaign

The occupation tree contains 35 focuses: shared municipal services, reconstruction,
employment, permitted security, accommodation, clandestine organization and
restoration, plus branches for seven administration types.

| Administration | Selection and programme |
|---|---|
| Communist Russian | Socialist Soviet patrons; municipal reconstruction, social guarantees and supervised local governance. |
| Civilian Russian | Other civilian Russian patrons, including partition outcomes; administrative recovery and a civilian governing compact. |
| Nationalist or military Russian | Nationalist/fascist patrons; controlled security institutions and a restricted local administration. |
| Eurasian | TFR's Dugin outcome; a Eurasian local mandate and political restrictions. |
| Liberal Russian/Baltic | TFR's Navalny outcome; supervised regional cooperation and a constitutional settlement. |
| European supervised | Other European patrons; reconstruction under supervision and negotiation of sovereignty guarantees. |
| European authoritarian | Authoritarian European patrons; restricted administration, security conditions and negotiated constitutional return. |

Normal parties are not assigned collaboration status from their ideology or
electorate. Occupation suspends the ordinary ledger's operation and presidency
bonuses, while retaining the data needed for restoration. Cooperation and
resistance are separate occupation meters. Decisions and events address local
forces, reconstruction, security pressure, petitions and liberation.

Protected annexation keeps EST and Northern Estonia before the original annex
can execute. Existing puppet settlements keep the parent's partition. Annex
replacements transfer intended remaining states and handle former military forces
according to the original troop-transfer policy. The special subject cannot be
integrated through normal autonomy reduction. Actual restoration content or a
supported liberation settlement returns independent politics.

A mandate generation records each genuine new patron or subsequent defeat.
Daily repair and the transition from war to peace do not charge new occupation
penalties. Material projects remain completed; a new mandate permits fresh
political choices. Delayed callbacks read the current patron before acting.

## Authored assets and remaining acceptance work

English text covers focuses, events, decisions, modifiers, the parliament and
tooltips. Installed TFR/base-game icons and event art are referenced. Several
named leaders use generic portraits, so custom likenesses remain art work for
the public release. The original package thumbnail uses geometric national colors.

Rendered UI inspection, ordinary campaigns for each party, every live peace
settlement, save/reload, DLC combinations, AI development and both-war balance
remain the manual acceptance checks. Structural and isolated native tests do not
claim those observations.
