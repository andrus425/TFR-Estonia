# TFR Estonia

An Estonia country expansion for **The Fire Rises 1.0.9.1c / Hearts of Iron IV 1.19.\***.

This implementation includes the seven governing parties, a 101-seat Riigikogu,
national cohesion and defense readiness, both European-war campaign stages,
and playable occupation administrations. All seven parties have distinct hidden
2023 election-victory programmes. Start a **new 2020 campaign**; saves
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

Prime-minister entries remain eligible while installed, including during
caretaker government. Unappointed alternatives and manual dismissal stay
locked; only the parliamentary and story scripts change the incumbent. The
retention fix keeps the existing PM IDs and saved ledger, so an existing
submod campaign can continue after restarting HOI4 to load the updated files.

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

The opening occupies a compact ten-unit width. The two subsequent government
programmes use five closely spaced columns and one-row prerequisite steps.
Effects show TFR's actual inflation-adjusted debt cost and native numerical
changes to **Estonian Economy** or **Estonian Military**. For example, the highway
adds **5% construction speed** and reduces **supply consumption by 4%**; the
research commitment adds **5% research speed**. Permanent reforms accumulate in
the two dynamic modifiers. Requirement tooltips summarize the necessary cabinet,
51-seat majority, domestic COVID cases or completed programme. Existing focus
descriptions remain unchanged.

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

TFR's Saudi-war supply shock applies the parent's actual **Oil Crash** national
spirit (`GER_oil_crash1` through `GER_oil_crash5`). LNG, grid investment, local
generation, renovation and network-charge relief each advance recovery by one
stage. The five stages progressively reduce the parent's economic penalties;
the fifth completed project removes the spirit even if the world crisis
continues. Projects can prepare for a later shock as well as respond during it.
The end of the parent crisis removes Estonia's managed spirit, preserving
permanent reforms and other countries' crisis content. An earlier development
save's custom energy penalty is reversed once before adopting the real spirit.

Twenty focuses take **700 days**. Beginning the continuation on 28 January 2021
allows completion on 29 December 2022, with 66 days before the 5 March 2023 election
date. Delays caused by inactivity, lost coalition confidence or occupation consume
that margin. The March 2023 election date and seat-allocation rules are unchanged.
The next valid election ends this 2019 coalition programme, even if Centre wins
again. Reform, EKRE, Centre, Isamaa, SDE, Eesti 200 and Parempoolsed victories in 2023 reveal their new mandate programmes;
other results open the applicable normal domestic programmes. While a historical
government programme is active, the older party, economy and military branches remain
hidden; relevant war and restoration branches can still appear when the world
state requires them.

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
before the Saudi-war crisis or funded during it. Household bill support, the gas
reserve and LNG capability each advance Oil Crash recovery by one stage; the
electricity/gas network-charge focus advances it by two stages. Completing all
four removes the spirit. Both government routes share the same five project
slots, so repeated or inherited projects cannot stack relief.

The policies follow actual Reform–Centre decisions and enacted legislation from
2021–2022, recorded in [the Kallas source register](docs/KALLAS_GOVERNMENT_SOURCES.md).
The party partnership continuing through the election is alternate history;
the route does not force the real 2022 coalition collapse. Twenty focuses take
**700 days**: a 26 January 2021 start allows completion on **27 December 2022**,
68 days before 5 March 2023. A lost majority, occupation or player delay consumes
that margin. The next valid election ends this programme even after another
Reform victory. Reform, EKRE, Centre, Isamaa, SDE, Eesti 200 and Parempoolsed pluralities in 2023 open their new mandate
programmes; other results reveal the applicable broader domestic tree. Relevant
war and restoration branches remain governed by the world state.

War, restoration and later-term branch entries use the saved opening-resolution
state. They remain reachable after occupation and restoration even when the
engine no longer retains the earlier opening's native completion records.
Prerequisites within those branches remain in place.

## Reform wins in 2023: preparation for the European war

A validated election in 2023 gives Reform its own **32-focus programme** if it
wins the most seats. The route stays hidden before that result and does not
require the earlier Reform–Centre government to have existed. Select its focuses
under a confirmed Reform-led cabinet with **51 actual coalition seats**. The
coalition comes from the party ledger; Eesti 200 and the Social Democrats are
not forced into government. Confidence-and-supply seats do not replace the
coalition majority needed for legislation.

One root opens five compact columns, with choices between them and ordinary
prerequisites inside each:

- Three-percent defence funding, territorial-defence equipment and training,
  layered air defence, the Baltic Defence Line, Nursipalu and allied logistics.
- Defence-industry planning, ammunition and drone/repair production, European-grid
  works, wind permits and regional apartment renovation.
- Estonian-language education, Ida-Viru teacher recruitment, teachers' pay and
  careers, learning until eighteen, vocational places and Metrosert applied research.
- Automatic business reporting, enterprise digitisation, the digital defence
  reserve, public research funding, regional exporters and civil protection.
- VAT reform and spending reviews, municipal revenue, care funding, marriage
  equality and local mental-health services.

Defence funding and industrial planning are available immediately after the root.
The ammunition and drone projects each grant **one paid military factory**, with
earliest completion after **105 and 140 total focus-days** respectively. They
require an owned and controlled Estonian core with a free unlocked building slot.
If no suitable slot exists, the funded project waits and retries; it grants no
extra slots and cannot award a duplicate factory after a reload or PM handover.
Air-defence and Baltic-line preparation are also early in their branch, rather
than depending on the final report or completed civilian policies.

All focuses take **35 days**, for **1,120 days** in total. An uninterrupted start
on the historical cabinet date of 17 April 2023 can finish on **11 May 2026**, 235
days before 2027. Delayed cabinet formation, lost majorities, occupation and player
pauses consume that margin. An early European war does not itself close the
programme. The final report requires every other policy; it starts no war and
calls no election. Older generic domestic branches stay hidden during this
mandate, while relevant war and restoration content remains available. A valid
election also retires unfinished Porto Franco choices and old cabinet callbacks;
they cannot replace the newly elected government or grant skipped policies.

The programme uses enacted policy and the 2023–2027 and 2024–2027 coalition
agreements, as recorded in [the Reform source register](docs/REFORM_2023_SOURCES.md).
Factory timing and numerical benefits are gameplay adaptations. Economic and
military rewards use the existing dynamic modifiers with native delta previews
and parent-ledger costs. The grid, wind and renovation measures fill the existing
five Oil Crash preparation slots; earlier governments' work counts once.

From late July 2024, an event can send **Kaja Kallas to Europe** and install
**Kristen Michal** as PM, provided the confirmed Reform mandate and Estonia's
actual EU membership still qualify. The delayed event rechecks those conditions.
The handover preserves the president, coalition, seats, ministers, completed
policies and election schedule. Kallas's departure is permanent career history:
future Reform-led cabinets use Michal, including after a supported occupation
and restoration, rather than bringing her back automatically.

## EKRE wins in 2023: a national conservative programme

A validated EKRE plurality in the 2023 election reveals a separate **32-focus
programme**. Its basis is the party's 2023 election, defence and population
platforms: EKRE did not lead the historical government formed after that election.
The [EKRE source register](docs/EKRE_2023_SOURCES.md) records the proposals and
their game adaptations. The coalition remains the one negotiated in parliament.
Focuses require a confirmed EKRE-led government and **51 actual coalition seats**.

One root opens five compact columns with ordinary prerequisites and choices
between them:

- Defence funding, expanded reserve preparation, air and coastal defence,
  a military border-guard reserve, and shelters and civil-protection training.
- Domestic defence contracts, ammunition and equipment-repair workshops,
  existing railways, trunk-road sections and emergency food reserves.
- Narva generating-unit overhauls, Kiisa supply arrangements, the proposed
  subsidised electricity tariff, fuel-excise relief and reduced food/medicine VAT.
- Child-linked tax relief, family-home and student-loan programmes, family-doctor
  duty hours, rural midwife cover and a thirteenth-pension supplement.
- Parliamentary scrutiny, an independent e-voting audit, citizen-initiative and
  direct-presidential-election bills, review of European measures and
  Estonian-language teaching capacity.

Defence funding can finish after **70 total focus-days**. The ammunition and
repair workshops each provide **one paid military factory**, with earliest
completion after **105 and 140 days** respectively. As on the Reform route,
delivery needs an owned and controlled Estonian core with a free unlocked slot.
Funded projects wait if necessary and cannot duplicate their factories or costs.
Reserve and air-defence preparation are also early in their branch. The expanded
reserve and domestic-contract policies unlock the existing paid recruitment and
procurement decisions rather than granting an equipped army immediately.

All **32 focuses take 35 days** each: **1,120 days**, allowing an uninterrupted
17 April 2023 start to finish on **11 May 2026**, 235 days before 2027. The final
report requires all other policies. Early war does not end the programme;
coalition loss or occupation can interrupt it, and persistent policy records
preserve enacted work. The older generic domestic branches remain hidden while
this mandate is active. A later valid election ends the programme even if EKRE
wins again; rejected election inputs do not end it.

The programme uses the existing economic and military dynamic modifiers, visible
budget costs and explicit recurring income losses for tax relief. Narva overhauls
cover two Oil Crash recovery slots, Kiisa covers one and the funded tariff covers
two. These are the same five slots used by earlier governments, so equivalent
projects count once and the full energy branch can remove the parent spirit.
Constitutional focuses prepare bills and oversight; the current president and
parliament remain governed by their established systems.

After confirmation of the elected EKRE government, **Martin Helme** takes the
locked PM position. The outgoing caretaker keeps its incumbent during coalition
talks. Martin's leadership persists for later EKRE cabinets across elections and
supported occupation/restoration. His economic-minister appointment is excluded
while he is PM, leaving Rene Kokk as the party's economic candidate; Mart Helme
remains eligible for an ordinary portfolio.

## Centre wins in 2023: public services and national preparation

A validated Centre plurality in the 2023 election opens its own **32-focus
programme**. An initial March victory keeps Jüri Ratas as PM after cabinet
confirmation; a later 2023 victory preserves any successor already chosen at
the September congress. The programme adapts Centre's contemporary election
platform; it represents a
hypothetical government rather than the historical Reform-led cabinet's actions.
The [Centre source register](docs/CENTRE_2023_SOURCES.md) records the original
platform and each policy's implementation. A confirmed Centre-led government and
**51 actual coalition seats** are required, with partners chosen through the
party ledger.

One root opens five compact columns with choices between them:

- A cross-party defence commitment, air-defence preparation, reservists'
  civilian expertise, allied reception facilities, training-area compensation
  and municipal civil protection.
- Domestic defence suppliers, ammunition and equipment-maintenance workshops,
  Ida-Viru industrial technology, regional investment guarantees and funded
  public construction.
- Dispatchable generation and LNG preparation, local heat-and-power projects,
  rural apartment renovation, weatherproof networks, last-mile broadband and
  community energy cooperatives.
- A higher income-tax band, a minimum-wage-linked allowance, reduced food and
  prescription-medicine VAT, a funded pension increase and care at home.
- Predictable county-hospital funding, sick pay from the second day, free
  kindergarten places, teachers' pay negotiations, free Estonian courses and a
  national-minorities advisory council.

Defence funding is available after **70 total focus-days**, air defence after
**105**, and reserve preparation after **140** along their branch. The industrial
column provides **two paid military factories** after **105 and 140 days**.
Each needs an owned and controlled Estonian core with an unlocked free building
slot; funded projects wait when necessary and grant each facility once. Neither
the factories nor the early defence policies require completed civilian branches
or the final report. Reserve and domestic-supplier policies also unlock the
existing paid recruitment and procurement decisions.

All focuses take **35 days**, totaling **1,120 days**. An uninterrupted
17 April 2023 start can finish on **11 May 2026**, 235 days before 2027. The final
report requires all other policies. The programme remains available during an
early European war while the government still qualifies; occupation or loss of
the coalition majority can interrupt it. Older generic domestic branches remain
hidden during the mandate. A later valid election ends this programme even after
another Centre victory, while invalid ballots preserve it.

Native effect tooltips show the actual budget charges, dynamic-modifier deltas
and recurring revenue changes. The higher income-tax band raises receipts;
the allowance and consumption-tax relief reduce them. The energy programme
shares the existing five Oil Crash recovery slots: reserve-generation/LNG work
covers two, local heat and power one, and apartment renovation two. Earlier
equivalent preparations count once. Completing all three can remove the crisis
spirit without duplicating another cabinet's work.

If Centre instead loses the 2023 election, Ratas remains party chair through the
summer. From **10 September 2023**, an independent Estonia receives the party's
extraordinary-congress event with **Tanel Kiik** and **Mihhail Kõlvart** as its two
candidates. The choice changes Centre's chair and its future PM identity. It
preserves another party's incumbent PM, the president, parliamentary seats,
coalition agreements and election schedule, including when Centre is a junior
coalition partner. An outgoing Ratas caretaker stays until cabinet confirmation.
The selected leader persists across future Centre governments and supported
occupation/restoration. Centre's 2023 victory path does not hold this defeat
congress.

## Isamaa wins in 2023: national resilience and family policy

A validated Isamaa plurality in the 2023 election reveals a **32-focus
programme** based on its contemporary election platform. This is a hypothetical
Isamaa-led cabinet; the party did not win the historical election. The
[Isamaa source register](docs/ISAMAA_2023_SOURCES.md) records the proposals and
their game adaptations. The programme keeps **Helir-Valdor Seeder** as the
party's existing PM identity and preserves the coalition negotiated in the
parliament system. Focuses need a confirmed Isamaa PM and **51 actual coalition
seats**; confidence-and-supply partners cannot replace that legislative majority.

The compact layout has one root, five six-focus columns with internal
prerequisites, and a final report requiring all 31 earlier policies. Choices
between columns let the player prioritize preparation without completing all
civilian policies first. All focuses take **35 days**, totaling **1,120 days**.
An uninterrupted 17 April 2023 start can finish on **11 May 2026**, 235 days
before 2027. Delayed confirmation, a lost majority or occupation consumes that
margin. An early European war does not itself end the programme.

The five policy branches cover:

- Funded independent defence, integrated air-defence sites, reserve muster,
  Kaitseliit training areas, allied reception and legally funded civil protection.
- Defence-industry contracts, ammunition and maintenance workshops, regional
  manufacturing, a positive credit register and updated business-expense allowances.
- Dispatchable power reserves, secure grid connections, renovation, district
  heating, nuclear feasibility studies and electricity universal-service support.
- A €5,000 child-linked tax allowance, joint returns for spouses, €100 first-
  and second-child benefits, large-family housing grants, care-leave protection
  and €200 child-maintenance assistance.
- Estonian-language schools, teachers' pay, public-private research cooperation,
  rural broadband, maintained digital services and care at home.

Defence funding opens immediately after the root and can finish after **70 total
focus-days**. Ammunition and maintenance
projects each provide **one paid military factory**, after **105 and 140 total
focus-days** along their branch. Delivery requires an owned and controlled
Estonian core with a free unlocked building slot. A funded project waits when
no suitable slot exists, charges only once and cannot duplicate the factory on
later ticks, reload or restoration. Reserve and domestic-procurement preparation
use the existing bounded, paid decisions.

Economic and military policies update the two persistent dynamic modifiers,
with exact native previews and TFR-ledger costs. The full programme carries
**1,785 million in project-budget commitments** before TFR's inflation adjustment.
The child-linked tax
allowance, joint returns and business-expense exemptions also reduce recurring
receipts by **0.060 billion in TFR's base ledger before inflation**. These are
gameplay balance values. Dispatchable generating reserve,
grid connection and renovation fill the shared Oil Crash recovery slots in
steps of **two, one and two**. Equivalent preparations by earlier cabinets count
once, and all three can remove the parent crisis spirit. Older generic domestic
branches stay hidden during this mandate, while relevant war and restoration
content remains accessible. The next valid election ends the programme even if
Isamaa wins again; invalid polling preserves it and enacted reforms remain saved.

## SDE wins in 2023: social protection and credible defence

A validated SDE plurality in the 2023 election reveals a **32-focus programme**
based on the party's contemporary election platform. This represents a
hypothetical SDE-led cabinet, using the coalition the player actually negotiates.
The [SDE source register](docs/SDE_2023_SOURCES.md) distinguishes platform
proposals from their TFR adaptations. Legislation requires a confirmed SDE
prime minister and **51 actual coalition seats**; confidence-and-supply votes
cannot replace that majority.

The compact tree has a root, five six-focus policy columns with internal
prerequisites, and an all-policy final report. The player can choose which
column to prioritize. Every focus takes **35 days**, totaling **1,120 days**.
An uninterrupted 17 April 2023 start finishes on **11 May 2026**, 235 days before
2027. Delayed cabinet confirmation, a lost majority or occupation consumes this
margin; the First European War starting early does not itself close the tree.

The five branches cover:

- Funded defence capabilities, layered air-defence preparation, reserve
  mobilisation, Kaitseliit instructors, allied reception, shelters and sirens.
- Domestic defence development, ammunition and maintenance workshops, regional
  skilled jobs, applied research and unserved ultrafast-internet connections.
- Renewable-power contracts, household grid connections up to 30 kW, inclusive
  renovation grants, strategic reserves, energy cooperatives and district heating.
- The proposed 28% upper income-tax band, negotiated steps toward a €1,200
  minimum wage, collective bargaining, learning leave, a €150 child benefit
  with indexation, and public rental housing.
- Universal health-insurance access, community mental-health services, a funded
  pension increase, affordable assessed residential care, teacher pay and shared
  Estonian-language schooling.

Defence funding opens directly after the root and can finish after **70 total
focus-days** along its branch; air defence follows at **105**, reserves at **140**.
The two industrial projects each provide **one paid military factory**, after
**105 and 140 total focus-days** along the industrial column. They require an
owned and controlled Estonian core with a free unlocked building slot. Funded
projects wait for space and deliver once, without repeat charges. Existing paid
procurement and reserve decisions remain the route to equipment and manpower.

The programme uses the persistent economy and military dynamic modifiers,
visible native delta previews and TFR budget helpers. Project commitments total
**2,145 million**, and the tax package adds **0.055 billion in recurring receipts**
in TFR's base ledger before inflation. These are gameplay balance values.
Renewable contracts, grid connections and renovation fill the shared Oil Crash
recovery slots in steps of **two, one and two**. Equivalent earlier preparations
count once, and completing all three removes the actual parent crisis spirit.
A later valid election ends the programme even after another SDE victory;
invalid polling preserves it, and completed reforms and paid entitlements persist.

SDE begins with **Indrek Saar** as party chair. From **5 February 2022**, the first
independent daily update records **Lauri Läänemets** as his successor, matching
[the party's leadership election](https://www.sotsid.ee/sotsiaaldemokraatide-uus-esimees-on-lauri-laanemets/).
The party row shows the chair independently of the incumbent government. An SDE
prime minister updates to Läänemets through the authored handover, while another
party's prime minister, the president, parliamentary seats and coalition remain
unchanged. An outgoing Saar caretaker remains until cabinet confirmation;
occupation postpones independent leadership activity, and the selected career
persists through restoration and later SDE governments. The notice acknowledges
the succession and provides no option to keep Saar.

## Eesti 200 wins in 2023: long-term reform and preparedness

A validated Eesti 200 plurality in the 2023 election reveals a **32-focus
programme** for a hypothetical Eesti 200-led cabinet. The
[Eesti 200 source register](docs/E200_2023_SOURCES.md) records the contemporary
platform and its TFR adaptations. The existing Kristina Kallas PM identity is
retained for this alternate outcome; this does not identify her as the party's
historical chair at the 2023 election. Focuses require a confirmed Eesti 200 PM,
the current electoral mandate and **51 actual coalition seats**. The player
negotiates the partners; confidence-and-supply votes cannot substitute.

The compact tree has a root, five six-focus columns with internal prerequisites,
and an all-policy final report. The player can choose which policy column to
prioritize. All focuses take **35 days**, totaling **1,120 days**. An uninterrupted
17 April 2023 start finishes on **11 May 2026**, 235 days before 2027. Delayed
cabinet confirmation, majority loss or occupation consumes this margin; an
early First European War does not itself close independent content.

The five branches cover:

- The proposed 3% defence commitment, the Kalevipoja air-defence programme,
  assigned civilian crisis roles, Kaitseliit instruction, allied reception and
  Tartu military/disaster-medicine training.
- Domestic defence suppliers, ammunition and equipment-servicing workshops,
  dual-use drone trials, business research incentives, simpler companies and
  the proposed €100,000 VAT-registration threshold.
- Six-month renewable-permit procedures, unused grid reservations, housing
  renovation, storage and microgrids, offshore connections and a climate law.
- Once-only state data, public electronic invoices, zero-based budget review,
  personal health accounts with the proposed €1,200 employer allowance, care
  coordinators and first-line mental-health services.
- Investment toward the proposed €250 million annual education increase,
  teacher careers toward the €3,000 salary objective, shared Estonian-language
  schools, compulsory learning to eighteen, €6,000 student loans with longer
  repayment, and the shared e-university platform.

Defence funding can finish after **70 total focus-days** along its branch, air
defence after **105**, and reserve preparation after **140**. The two industrial
projects each provide **one paid military factory**, after **105 and 140 total
focus-days** along their column. No civilian branch or final report blocks these
preparations. Factories require an owned and controlled Estonian core with a
free unlocked slot; funded projects wait for space and deliver once, without
repeat charges. Normal paid recruitment and procurement remain necessary.

Rewards use the persistent economic and military dynamic modifiers, native
numerical previews and TFR's budget helpers. Project commitments total
**1,900 million** in TFR's base ledger. The research incentive, business
simplification, electronic-invoice savings, budget review and health allowance
change recurring income by **−0.020, −0.010, +0.012, +0.025 and −0.012 billion**,
respectively, for a net **−0.005 billion before inflation**. These are game
balance values; the programme's real currency objectives above are policy
sources rather than a conversion of game-ledger units.

Renewable permits fill two shared
Oil Crash recovery slots, grid connections one, and renovation two. Equivalent
preparation by earlier cabinets counts once; full preparation removes the actual
parent crisis spirit. A later valid election ends the programme even if Eesti
200 wins again. Invalid input preserves it, while completed reforms and funded
factory entitlements remain saved through occupation and restoration.

## Parempoolsed wins in 2023: enterprise, a lean state and preparedness

A validated Parempoolsed plurality in the 2023 election reveals a **32-focus
programme** based on the party's own contemporary platform. The
[Parempoolsed source register](docs/PP_2023_SOURCES.md) records the original
programme and separates its proposals from funded TFR adaptations. Parempoolsed
must already have formed, and a confirmed Lavly Perling government needs the
current electoral mandate and **51 actual coalition seats**. Reform's seats and
polling remain separate despite the parties sharing a generic ideology;
confidence-and-supply votes cannot replace the governing majority.

The compact tree has a root, five six-focus columns with ordinary prerequisites,
and a final parliamentary report requiring all preceding policies. Players
choose which branch to prioritize. Every focus takes **35 days**, for a total
of **1,120 days**: an uninterrupted 17 April 2023 start finishes on **11 May
2026**, 235 days before 2027. Ordinary focuses have no date gates, and an early
First European War does not itself close independent content. Cabinet talks,
majority loss or occupation can consume that completion margin.

The five branches cover:

- A cross-party 3% defence investment agreement, air-defence crews and
  communications, broader service roles, a 10,000-person civilian reserve,
  allied reception funded outside the baseline, and essential-service exercises.
- Private suppliers' access to loan and equity capital, contracted ammunition
  and military servicing capacity, the proposed 3% public-private research
  agreement, university knowledge transfer and skilled-worker admission points.
- Simpler planning for private renewable projects, offshore-wind connections,
  dependable generation during the transition, independent nuclear licensing,
  renovation procedures and timber use in public construction. The licensing
  focus prepares rules and supervision; it does not build a reactor.
- State expenditure and agency audits, a negative supplementary budget,
  understandable public accounts, the proposed 18% income tax and social-tax
  ceiling at three average wages, employee-benefit tax relief, and transparent
  appropriations replacing discretionary political earmarks.
- The proposed 70% teaching share of education spending, shared
  Estonian-language schooling, vocational and adult retraining, partial
  university tuition with student assistance, needs-based support, and more
  competitive care contracts with less medical paperwork.

Defence funding can finish after **70 total focus-days**, air-defence preparation
after **105**, and reserves after **140** along the military branch. The two
industrial projects each provide **one paid military factory**, finishable after
**105 and 140 total focus-days** along their column. No civilian branch or final
report blocks these preparations. Each project requires an owned and controlled
Estonian core with a free unlocked slot; the funded entitlement waits when no
slot qualifies and delivers once. Existing recruitment and equipment procurement
remain paid and bounded.

Project commitments total **1,750 million** in TFR's base ledger. The
supplementary-budget savings, labour-tax changes, employee-benefit relief,
removed earmarks, tuition contributions and targeted support respectively change
recurring income by **+0.040, −0.035, −0.015, +0.012, +0.008 and +0.010 billion**:
a net **+0.020 billion before inflation**. These are game-balance amounts,
separate from the programme's real percentage objectives. The expenditure cuts
cost three cohesion, and tuition and targeted benefits each cost two; the wider
programme can rebuild trust, but these reforms do not automatically balance
Estonia's budget.

Renewable permits fill two shared Oil Crash recovery slots, grid connections
one, and continuity capacity two. Equivalent earlier governments' work counts
each slot once across all nine programmes; completing the preparations removes
the actual parent crisis spirit. Rewards use the persistent economic and
military modifiers with native numerical previews and TFR budget costs. The
next valid election ends the programme even if Parempoolsed wins again; invalid
input preserves it. Completed reforms and funded factory entitlements survive
supported occupation and restoration. All **427 preceding focus descriptions**
remain unchanged.

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
- The March 2023 election remains scheduled. Its successor waits for the First
  European War to finish: no fixed 2027 election takes place before or during
  that war. An independent survivor votes on the first daily update after the
  actual settlement, even if peace comes before 2027. Active war, capitulation
  and occupation defer that vote. A fresh four-year term (1,461 days) then begins.
- Restored independence retains its 84-day election period. When a postwar vote
  is also pending, the restoration ballot waits for a settled war and satisfies
  both schedules without a second immediate election. Invalid polling preserves
  the assembly and retries the pending election instead of consuming its schedule.
- There is no snap-election decision or automatic caretaker snap vote. Only an
  authored event or focus can authorize one.
- The dedicated Riigikogu panel shows polling, seats, cabinet membership,
  supply agreements and the election calendar. TFR's ideology chart is a
  compatibility view; it is not the source of seats or confidence votes.

Government programme focuses become available to the current party in office.
An election can open a different programme. Completed policies remain recorded,
and active cabinet bonuses reconcile with the current government.

## Appointing coalition ministers

Use TFR's existing cabinet slots to appoint the **foreign, economic, interior,
intelligence and defence ministers**. Each of the seven parties has at least
one nominee for every portfolio: 38 people provide 39 candidacies. Active parties'
nominees remain visible, but appointments require that party in the actual
coalition and a confirmed independent government with 51 confidence votes.
Confidence-and-supply agreements do not provide cabinet appointment rights.
Parempoolsed nominees appear after the party forms.

Appointments normally cost **100 political power**. For **90 days after each
valid election**, a timed cabinet-formation spirit reduces all five appointment
costs by **80%**, normally to **20 PP**, before other modifiers. The displayed
native price includes the discount. Invalid elections, ordinary coalition
negotiations and the Ratas–Kallas handover do not start a discount window.

Minister traits provide national benefits, including construction and output,
fiscal efficiency, diplomatic relations, stability, intelligence capabilities,
army organization, training and supply. The prime minister remains locked to the
parliamentary mandate and scripted government changes. A person cannot hold two
cabinet offices: Mart Helme's foreign/interior candidacies exclude one another,
and both become unavailable when he is prime minister. Vacate his current
portfolio through TFR's empty-slot choice before appointing him to the other.
EKRE has alternatives for both positions.
Trivimi Velliste provides an Isamaa foreign-affairs alternative to Urmas Reinsalu,
and Rene Kokk provides an EKRE economic alternative to Martin Helme. Person-aware
exclusions support future authored premierships without blocking Reinsalu under
Seeder or Martin under Mart Helme.

The day-one initialization appoints Urmas Reinsalu, Taavi Aas, Mart Helme,
Raivo Aeg and Jüri Luik. Aeg represents security oversight in TFR's intelligence
slot. Coalition withdrawal removes the departing party's ministers; outgoing
caretakers retain their ministers during negotiations but cannot appoint new
ones. Confirmation removes ministers outside the new coalition. Occupation
clears all five portfolios and the discount. Deliberately vacant portfolios and
player choices are never overwritten by daily repair.

The [candidate register](docs/MINISTER_ROSTER.md) records the complete roster and
primary sources. It distinguishes historical portfolio holders from inferred
appointments and later-party recruitment in the alternate timeline. Minister
portraits use individual **62 × 67 pixel TFR-style icons**, generated from photo
references with the native tilted metal frame, purple background and muted
portrait treatment. The [artwork register](docs/artwork/ministers/README.md)
records the photo sources, credits and generation prompts.

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
without resetting saved adjustments. Opening, retained-Ratas, pre-election
Kallas and the Reform/EKRE/Centre/Isamaa/SDE/Eesti 200/Parempoolsed 2023 mandate bonuses use these
containers. Older generic
programmes retain their current reward ideas pending their own content revision.

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
python tools/build_energy_crisis.py --check
python tools/build_focus_tooltips.py --check
python tools/build_ministers.py --check
python tools/build_reform_2023.py --check
python tools/build_reform_handover.py --check
python tools/build_ekre_2023.py --check
python tools/build_centre_2023.py --check
python tools/build_centre_leadership.py --check
python tools/build_isamaa_2023.py --check
python tools/build_sde_2023.py --check
python tools/build_sde_handover.py --check
python tools/build_e200_2023.py --check
python tools/build_pp_2023.py --check
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
`tools/focus_reward_model.py` holds the historical cabinets' numerical balance;
`tools/build_focus_tooltips.py` generates native previews from those same values.
`tools/build_energy_crisis.py` generates the parent Oil Crash integration and
safe migration of the earlier custom penalty. Both generators support `--check`.
`tools/build_ministers.py` builds the native cabinet candidates, traits,
eligibility, lifecycle helpers, portrait sprite mappings, localization and sourced roster from
the two `tools/minister_roster_*.json` research files; it also supports `--check`.
`tools/export_minister_artwork.ps1` exports the saved imagegen masters as 62 × 67
cabinet icons and separate 156 × 210 prime-minister tooltip images; `-Check`
verifies dimensions, transparency and readable portrait centers without writing.
`tools/build_reform_2023.py` generates the elected 2023 programme, rewards and
localization. `tools/build_reform_handover.py` generates the Kallas–Michal event
and guarded career transition. Both support `--check`. Election scheduling and
the validated 2023 mandate lifecycle are authored in the dedicated
`TFR_EST_elections_war.txt` and `TFR_EST_reform_2023_lifecycle.txt` helpers.
`tools/build_ekre_2023.py` generates the alternative elected EKRE programme,
rewards and localization, with its own `--check`. The elected programmes feed
the shared main-tree imports, AI priorities, modifier previews and capped energy
recovery slots; regenerate the shared main tree and check those outputs after a
policy change. The EKRE election hook is in `TFR_EST_ekre_2023_lifecycle.txt`.
`tools/build_centre_2023.py` generates Centre's elected programme, rewards and
localization and also supports `--check`. Its validated mandate and party-defeat
history are maintained in `TFR_EST_centre_2023_lifecycle.txt`.
`tools/build_centre_leadership.py` generates the guarded September congress,
party-leader labels and persistent leadership helpers, with its own `--check`.
`tools/build_isamaa_2023.py` generates Isamaa's elected programme, rewards and
localization, with its own `--check`. Its validated mandate lifecycle is authored
in `TFR_EST_isamaa_2023_lifecycle.txt`; its policies feed the same shared imports,
party-first AI ordering, modifier previews and five energy-recovery slots.
`tools/build_sde_2023.py` generates the alternative SDE programme, rewards and
localization with `--check`; its validated election hook is authored in
`TFR_EST_sde_2023_lifecycle.txt`. It uses the same shared imports, party-first AI,
modifier previews and capped energy slots. `tools/build_sde_handover.py` generates
the historical Saar–Läänemets career transition, notification and independent
party-leader labels; it also supports `--check`.
`tools/build_e200_2023.py` generates Eesti 200's alternative programme, rewards
and localization, with `--check`. Its validated mandate lifecycle is authored in
`TFR_EST_e200_2023_lifecycle.txt`; its policies feed the shared main-tree imports,
party-first AI, modifier previews and five capped energy-recovery slots.

`tools/build_pp_2023.py` generates Parempoolsed's alternative programme, rewards
and localization, with `--check`. Its validated mandate lifecycle is authored in
`TFR_EST_pp_2023_lifecycle.txt`; its policies feed the same main-tree imports,
party-first AI, exact modifier previews and five capped energy-recovery slots.

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

The submod references installed TFR and base-game assets. All 38 portfolio
nominees and all 12 prime-minister displays now use individual TFR-style artwork
for **48 distinct people**, with shared portraits for people who can hold either
office. Some occupation administrators still use generic leader portraits.
The [minister artwork register](docs/artwork/ministers/README.md) contains source
credits and prompts. Downloaded research photos are excluded from release ZIPs.
All seven parties also have original TFR-inspired ideology artwork: twelve
leader variants combine recognizable portraits, party colors and party symbols
in transparent 66 × 68 PNGs. The diplomacy icon follows the serving prime
minister, including caretakers; seven smaller icons in the Riigikogu ledger
follow each party's leadership, including changes in opposition. The
[ideology artwork register](docs/artwork/ideology/README.md) records the supported
leaders, source credits, exact imagegen prompts and export procedure. Review the
[native-size sheet](docs/artwork/ideology/contact_sheet_1x.png) or
[4× sheet](docs/artwork/ideology/contact_sheet_4x.png). The integration adds no
ideologies or gameplay effects and leaves parent TFR interface files inherited.
The eleven opening focuses have original AI-generated TFR-style collage icons,
with Centre emerald, Isamaa blue/gold and EKRE cornflower-blue accents. The
Three Seas summit uses nonpartisan Estonian colors. Seeder, Ratas, Martin Helme
and Kaljulaid appear in the relevant policy icons. Each runtime texture is a
170 × 150 RGBA PNG with the bottom 40 pixels fully transparent for the label.
The [preview sheet](docs/artwork/opening/opening-icons-preview.png),
[native-size sheet](docs/artwork/opening/opening-icons-native-size.png),
high-resolution masters and full generation prompts are retained under
`docs/artwork/opening/`; `manifest.json` maps them to focus IDs and records
party associations, export bounds and SHA-256 hashes. The opening generator
also maintains all eleven base sprites and their TFR-style shine variants.
The twenty-focus retained-Ratas continuation has a matching complete icon set,
including Ratas on coalition renewal and the final public report, Seeder on
child-based tax relief, Martin Helme on electricity-charge relief and Jüri Luik
on territorial training. Its [preview sheet](docs/artwork/ratas/ratas-icons-preview.png),
[native-size sheet](docs/artwork/ratas/ratas-icons-native-size.png),
[tree layout preview](docs/artwork/ratas/ratas-tree-preview.png), masters and
full prompt/asset manifest are retained under `docs/artwork/ratas/`. Its generator
maintains twenty base sprites and twenty matching shine variants. All textures
use the same 170 × 150 canvas and transparent bottom 40 pixels.
The twenty-focus Kallas Reform–Centre programme also has a complete matching
set, with Reform yellow/gold and Centre emerald accents. Kallas appears on the
formation and public-report icons; Kiik, Kersna and Laanet illustrate frontline
vaccination, teacher pay and defence funding. Official period cabinet photos
guided the minister likenesses; the reference photos remain outside the package.
The [preview sheet](docs/artwork/kallas/kallas-icons-preview.png),
[native-size sheet](docs/artwork/kallas/kallas-icons-native-size.png),
[tree layout preview](docs/artwork/kallas/kallas-tree-preview.png), masters and
exact prompts are in `docs/artwork/kallas/`. Its generator maintains twenty base
and twenty shine sprites, using the same 170 × 150 RGBA/40-pixel-clearance format.
The seven post-2023 government programmes each have 32 separately generated
icons: 224 unique textures and 224 matching base/shine sprite pairs. Every focus
has its own composition. The coalition leader's palette runs through each tree,
with selected leader portraits and party emblems. The
[seven-government overview](docs/artwork/post2023/seven-governments-preview.png)
and [artwork guide](docs/artwork/post2023/README.md) link all seven icon sheets and
tree previews. Exact built-in imagegen prompts, original masters, reference
credits and one-to-one focus mappings are retained in `docs/artwork/post2023/`.
The generators reject shared artwork assignments; the export check also rejects
duplicate texture hashes and verifies the transparent label space.
No external photographs, music or copied TFR artwork are bundled.

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
selector and adds Estonia's seven party selectors and persistent named PM successors. The shared GUI itself
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
