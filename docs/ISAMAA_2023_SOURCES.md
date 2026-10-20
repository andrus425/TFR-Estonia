# Isamaa's conditional 2023 government programme

Research checked on 20 October 2026. This is a hypothetical programme for an Isamaa plurality followed by a confirmed majority cabinet in TFR's alternate timeline. Helir-Valdor Seeder remains the existing party leader and prime-minister candidate. The tree does not assume that the historical 2022 international sequence has occurred, reproduce a historical coalition, or introduce a separate leadership handover.

## Primary references and provenance

The [official 2023 campaign index](https://isamaa.ee/rk23/programm/) links the [full election programme](https://isamaa.ee/iwp/wp-content/uploads/2023/01/Isamaa-PROGRAMM-RK2023-pikk-02.pdf). The PDF was retrieved and read for this revision: **35 pages**, **364,991 bytes**, SHA-256 **`f7ca72e3dd94c156b7a8528b0b563cd4ca43b39b5a215dbae4c06a8be3d79557`**. Page numbers below are the printed PDF page numbers. No artwork or source-document asset is redistributed.

The official subject pages provide the contemporary policy basis:

- **A — [Statehood and security](https://isamaa.ee/rk23/programm-riiklus/):** independent defence, broad civil preparation and allied cooperation. The detailed defence and industry commitments are on PDF pages **13–14**.
- **B — [Economy](https://isamaa.ee/rk23/programm-majandus/):** enterprise, allowances, credit, dispatchable energy and electricity support. Credit and taxation are on pages **17–18**; the detailed energy measures are on **18–19**.
- **C — [Families and population](https://isamaa.ee/rk23/programm-rahvus/):** the proposed child allowance, joint returns, benefits, housing, care-leave calculation and maintenance assistance. Detailed measures are on pages **3–5**.
- **D — [Education and culture](https://isamaa.ee/rk23/programm-eestlus/):** the language transition, teacher-pay objective and combined research funding objective. Detailed education and research commitments begin on pages **6–7**.
- **E — [Welfare](https://isamaa.ee/rk23/programm-heaolu/):** support delivered at home and coordination with local services. The detailed welfare section begins on page **22**.
- **F — [Environment](https://isamaa.ee/rk23/programm-keskkond/):** energy efficiency and long-term stewardship, also reflected in the renovation branch. Energy-saving measures are on page **28**.
- **G — [Citizens, regions and administration](https://isamaa.ee/rk23/programm-kodanikeriik/):** county development, reliable broadband and core digital-service funding. Detailed regional and digital policy is on pages **34–35**.

The programme provides sufficient detail for this tree; it does not need a later Riigikogu proposal to fill a gap. Its language is summarized in original focus text. Historical euro thresholds are policy identifiers, while numerical gameplay costs and rewards are balance choices.

## Entry, priorities and timing

`TFR_EST_isamaa_won_2023_election`, `TFR_EST_isamaa_2023_mandate` and `TFR_EST_isamaa_2023_mandate_ended` identify the electoral mandate. The branch remains hidden until the validated 2023 vote gives party **4** the mandate. Visibility permits coalition negotiations; completing a focus requires a confirmed Isamaa-led cabinet and **51 actual coalition seats**. Confidence-and-supply votes do not replace coalition seats. The tree forces no particular partner.

The compact layout has one root at `(4, 0)`, five six-focus columns at x **0, 2, 4, 6, 8**, rows **1–6**, and a final report at `(4, 7)`. Each focus takes **35 days**. The final report requires all **31** preceding policies, giving **1,120 days** for the full programme. An uninterrupted start on **17 April 2023** finishes on **11 May 2026**, **235 days before 2027**. Government formation, confidence loss or occupation can still delay progress. No ordinary focus has a calendar gate.

Defence funding takes **70 focus-days** along its branch, air-defence preparation **105**, and reserve preparation **140**. The two paid military-factory projects take **105 and 140 days** along the separate industry branch. They do not require the civilian branches or final report. The AI takes defence, industry and energy preparation early. The outbreak of the European war does not itself hide an unfinished mandate.

## Content register

Identifiers below follow `TFR_EST_isamaa_2023_`. The source letters refer to the primary references above. The capability and factory adaptations are stated explicitly rather than attributed as literal election promises.

| Focus | Basis and implemented policy |
|---|---|
| `new_mandate` | Alternate election outcome; agree a funded majority programme. |
| `defence_commitment` | A: finance defence readiness and procurement instalments. |
| `air_defence` | A, capability adaptation: sites, crews and procurement planning for a maintainable air-defence contribution. |
| `reserve_muster` | A: exercise mobilisation, employer arrangements and stores. |
| `kaitseliit_ranges` | A: fund training facilities, instructors and local range agreements. |
| `allied_reception` | A: reception infrastructure and prepositioned stores. |
| `civil_protection` | A: fund municipal warning, evacuation and essential-service responsibilities. |
| `industrial_guarantees` | A: domestic defence research, development and supply contracts. |
| `ammunition_workshop` | A, TFR adaptation: one paid military-factory entitlement. |
| `maintenance_workshop` | A, TFR adaptation: a second paid entitlement and equipment servicing. |
| `regional_value_chains` | G and B: county-level partnerships for viable manufacturing projects. |
| `credit_register` | B: build the proposed positive lending register with data-access rules. |
| `expense_allowances` | B: revise fixed business-expense exemptions, recording lost receipts. |
| `dispatchable_reserve` | B: contract reliable domestic capacity and fuel arrangements. |
| `grid_connection` | B: finance assessed network connections and technical preparation. |
| `renovation` | B and F: fund standard designs and supervised energy-saving works. |
| `district_heating` | B: modernize viable heat networks and connections. |
| `nuclear_studies` | B: commission feasibility and safety work before a later investment decision. |
| `universal_service` | B: finance one defined electricity-support tranche. |
| `child_tax_allowance` | C: legislate the proposed annual €5,000 child-linked exemption. |
| `joint_returns` | C: permit spousal joint filing and record its revenue cost. |
| `child_benefit` | C: fund the proposed €100 first- and second-child benefit level. |
| `large_family_homes` | C: open an assessed housing grant round. |
| `care_leave` | C: update care-benefit calculations after parental leave. |
| `maintenance_support` | C: fund the proposed €200 child-maintenance assistance ceiling. |
| `estonian_schools` | D: resource staff, materials and pupil support for the language transition. |
| `teacher_pay` | D: fund negotiated steps toward the 125%-of-average-wage objective. |
| `research_compact` | D: contract public-private research towards the combined 3%-of-GDP objective. |
| `rural_internet` | G: tender reliable connections for unserved communities. |
| `digital_baseline` | G: maintain the core services, security and continuity arrangements. |
| `home_care` | E: contract municipal home support and staffing. |
| `account_to_parliament` | Campaign conclusion: report funded reforms and outstanding obligations. |

The programme's broad defence-industry objective is represented by **two bounded production facilities**. It does not literally promise two HOI4-sized military factories. Air-defence preparation is a selected use of the broader capability commitment, rather than a claimed platform quotation. Neither project grants units, manpower, weapons or a completed technology. Mobilisation and procurement use the existing limited decisions through their normal unlock flags; the separate German/allied reinforcement arrangement remains intact.

Long objectives are represented by funded stages. The programme does not declare a nuclear plant complete, all 2030 energy targets met, or every school and research target instantly fulfilled. The universal-service focus funds a tranche; its permanent economic resilience reward is a gameplay abstraction, not a promise of permanently subsidized electricity.

## Costs, recovery and persistent rewards

The tree uses **1,785 million** of explicit budget costs, applied through TFR's existing inflation-adjusted spending helper. The business-expense allowances reduce recurring income by **0.010 billion**, the child exemption by **0.035 billion**, and joint filing by **0.015 billion**: **−0.060 billion net** before inflation. These are balance values in TFR's base ledger currency, not a forecast or conversion of historical euro measures. There is no invented tax increase silently paying for the programme.

All permanent buffs update the existing **Estonian Economy** or **Estonian Military** dynamic modifier. Exact native delta previews are generated from the same reward values. Persistent completion flags guard each focus reward, preventing replay through programme refreshes or tree changes.

Energy relief shares five OR-combined preparation slots with earlier programmes: `dispatchable_reserve` covers slots **1–2**, `grid_connection` slot **3**, and `renovation` slots **4–5**. Equivalent earlier preparation counts once. Completing the three projects removes the actual TFR **Oil Crash** spirit or prepares the same relief if the crisis starts later. Heating, studies and electricity support give only their stated permanent rewards and no additional recovery slots.

The `ammunition` and `maintenance` entitlements have separate pending/granted flags. Their helper checks states **13, 191, 1329 and 840**, requiring Estonian ownership, control and a free unlocked military-factory slot. It creates no building slots. A paid project waits and the daily tick retries if delivery is currently impossible. A granted flag is set only after construction, so repeated reconciliation does not duplicate a facility.

The victory programme does not change prime-minister selection, president, cabinet nominees, party polling, the seat-allocation algorithm, EU/NATO membership or the postwar-election schedule. It follows the same mandate, coalition and occupation controller as the earlier 2023 programmes.
