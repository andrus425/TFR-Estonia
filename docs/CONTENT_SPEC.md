# Implemented campaign content

This document records the implemented design for the development build. Balance
values are starting values; the manual campaign matrix determines public-release
acceptance. Later events are fictional developments in TFR's alternate timeline.

## Initial coalition programme

The opening is an eleven-focus, 35-day chain built from the documented Ratas II
policies in [OPENING_POLICY_SOURCES.md](OPENING_POLICY_SOURCES.md). It replaces
the eight vague introductory nodes; party programmes and later campaign work are
hidden until the opening finishes. The ten policies require the original three
partners, a Centre prime minister and at least 51 actual coalition seats.

The marriage-referendum bill is the final focus. All ten policies are mandatory,
the focus cannot be canceled, and its December 24 gate accounts for up to 14
banked days. Investigation/response events on January 12–13 offer a retained Ratas
cabinet or resignation followed by a Reform–Centre cabinet in the same parliament.
The cabinet transition does not replace the active focus. The historical April
referendum never occurred; remaining in office is an alternate-history branch.

New opening economic and logistical bonuses use the country dynamic modifiers.
Later programme rewards await their own redesign. There is no player snap vote;
the crisis changes cabinets through explicitly authorized story effects.

## Political entry and persistence

All governing routes require an independent parliament, an electoral or explicit
story leadership mandate and at least 51 confidence votes. Centre leads the opening.
Subsequent elections automatically give coalition leadership to the party with
the most seats, with fixed party order resolving exact seat ties. The player
negotiates partners and supply agreements around that leader. Coalition members
and supply partners remain separate records. Between elections, ordinary
confidence recovery retains the incumbent; another succession requires an
explicit authored event or focus.
The current confirmed party unlocks its programme; a caretaker cannot enact it.

Each programme has ten focuses, one policy-conflict event, an active cabinet
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

The main tree contains 157 focuses: eight opening focuses, 70 programme focuses,
18 economic focuses, 21 military focuses and 40 campaign focuses. Branches are
available according to independence, government and campaign stage; they do not
lock later elected parties out permanently.

The opening establishes the coalition contract, pandemic contingencies, remote
government, livelihoods, presidency, transparency and national-security review.
Economic development then supports education, regional investment, infrastructure,
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
