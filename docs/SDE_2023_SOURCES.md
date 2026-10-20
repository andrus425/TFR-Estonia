# SDE's conditional 2023 government programme

Research checked on 20 October 2026. This is an alternate SDE election victory followed by an SDE-led majority cabinet. It does not claim that Estonia had a historical SDE-led government after the 2023 election. Party **5** retains its own parliamentary identity. The separately implemented succession makes Lauri Läänemets SDE chair from **5 February 2022**; the victory tree does not create an extra succession or allow the player to change prime minister directly.

## Primary references and provenance

The [party's contemporary programme announcement, dated 14 January 2023](https://www.sotsid.ee/sotsiaaldemokraatide-valimisprogrammi-fookuses-on-inimeste-toimetulek/) links the [official approved 2023 Riigikogu election programme](https://www.sotsid.ee/wp-content/uploads/2023/01/LO%CC%83PLIK_SDE-PROGRAMM-2023.-AASTA-RIIGIKOGU-VALIMISTEL_u%CC%88ldkogul-kinnitatud-2.pdf). Its title explicitly identifies **2023** and approval by the general assembly. The PDF was retrieved and read for this revision: **24 pages**, **555,617 bytes**, SHA-256 **`b13817c468dcab5653ce5f633f835261803032cac092e37950987651d988b556`**. Page references below use printed page numbers. Website crawl/publication metadata and the party's current front page are not used to date the platform. No source PDF or artwork is redistributed.

The following programme sections provide the content map:

- **A — Security, pages 19–20, sections 8.1–8.2:** funded military capability, reserves, voluntary defence, civil preparation, allied reception and domestic defence-sector collaboration.
- **B — Economy and regional development, pages 6–7 and 17–18, sections 1.1–1.3 and 7.1:** skills, research, industrial upgrading, digital links and regional investment.
- **C — Energy and housing, pages 9 and 16, sections 2.2 and 6.2:** generation, connections, renovation, reserves, community participation and heating.
- **D — Taxation and labour, pages 6 and 8, sections 1.1 and 1.4:** negotiated pay, collective agreements, study opportunities and revised income/dividend taxation.
- **E — Families, housing and services, pages 8–11 and 13–14, sections 2.1–3.3 and 5.1–5.2:** family support, public housing, health coverage, care, pensions and education.

For the selected air-defence implementation of the broader capability objective, the [April 2023 coalition agreement, section 1.1](https://www.sotsid.ee/wp-content/uploads/2023/04/Koalitsioonilepe-8.04.2023a.pdf) provides a supplementary contemporary primary reference. This is a capability adaptation rather than a claim that the standalone SDE election programme names that precise procurement project. The same agreement supports translating defence-sector development into ammunition production and servicing capacity. No historical coalition membership is forced by using these implementation details.

The separate chair transition follows the [official SDE announcement of 5 February 2022](https://www.sotsid.ee/sotsiaaldemokraatide-uus-esimees-on-lauri-laanemets/). It establishes Läänemets as Saar's successor independently of the hypothetical 2023 government. The party succession does not appoint a different party's prime minister or call an election.

The original focus descriptions explain commissioning and accountability rather than reproducing the programme's prose. Numerical policy identifiers are historical proposals; HOI4 modifier amounts, costs and factory equivalents are gameplay adaptations. The programme supplies sufficient domestic detail without needing to import a later Riigikogu proposal.

## Entry, priorities and timing

The branch is hidden until a validated 2023 election grants SDE the largest delegation and records `TFR_EST_sde_won_2023_election` and `TFR_EST_sde_2023_mandate`. Party **5** must remain the current mandate holder, and `TFR_EST_sde_2023_mandate_ended` must be absent. Selection requires a confirmed SDE-led cabinet, SDE coalition membership and **at least 51 actual coalition seats**. Confidence-and-supply seats do not replace coalition seats. The programme forces no partner and does not alter the seat algorithm.

One root at `(4, 0)` leads to five parallel columns at x **0, 2, 4, 6, 8**, rows **1–6**. The final report at `(4, 7)` requires every preceding policy. All **32** focuses cost **35 days**, totalling **1,120 days**. An uninterrupted start on **17 April 2023** finishes on **11 May 2026**, **235 days before 2027**. Government formation, lost confidence, interruptions or occupation may delay that schedule. No ordinary focus has a date gate, and an ongoing first European war does not itself hide this mandate.

Defence funding is reachable after **70 focus-days**, air-defence preparation after **105**, and reserve preparation after **140** along the defence branch. The separate industry branch grants military-factory projects after **105 and 140 focus-days**. These priorities do not depend on the social-service branches or final report. The AI prioritizes defence, industry and the three main energy preparations.

## Content register

Identifiers follow `TFR_EST_sde_2023_`. Source letters refer to the sections above. The register distinguishes literal policy subjects from the chosen military-game implementation.

| Focus | Basis and implemented purpose |
|---|---|
| `new_mandate` | Alternate election result; agree a funded SDE majority programme. |
| `defence_commitment` | A: fund a procurement and operating tranche toward the capability objective. |
| `air_defence` | A and supplementary agreement: prepare crews, communications and sites for layered defence. |
| `reserve_muster` | A: review reserve assignments and test rapid mobilisation. |
| `kaitseliit_instructors` | A: fund volunteer instruction, exercises and equipment upkeep. |
| `allied_reception` | A: exercise reception routes and storage with available allies. |
| `civil_protection` | A: commission warning systems, shelters and local exercises. |
| `industrial_guarantees` | A: fund assessed domestic development and supplier partnerships. |
| `ammunition_workshop` | A, capability adaptation: one paid military-factory entitlement. |
| `maintenance_workshop` | A, capability adaptation: a second paid entitlement and servicing. |
| `regional_jobs` | B: start assessed regional skilled-employment projects. |
| `applied_research` | B: finance industrial research, automation and commercialization. |
| `ultrafast_internet` | B: tender reliable connections where rollout remains incomplete. |
| `renewable_contracts` | C: fund viable additional generation with delivery obligations. |
| `grid_connection` | C: implement the proposed 30 kW household/association connection allowance. |
| `renovation` | C: finance accessible energy-saving building upgrades. |
| `strategic_reserves` | C: contract tested energy stocks and storage preparation. |
| `energy_cooperatives` | C: offer technical and financial help to viable community projects. |
| `district_heating` | C: modernize networks while preserving workable backup. |
| `progressive_tax` | D: implement the proposed 28% upper income/dividend schedules. |
| `minimum_wage` | D: negotiate funded stages toward the proposed EUR 1,200 minimum wage. |
| `collective_bargaining` | D: resource sectoral agreements, mediation and enforcement. |
| `learning_leave` | D: finance study arrangements and supported career changes. |
| `child_benefit` | E: fund the proposed indexed EUR 150 benefit level. |
| `rental_homes` | E: commission a first tranche toward the 5,000-apartment objective. |
| `universal_health` | E: finance eligibility and purchased care together. |
| `mental_health` | E: commission community services and accessible referrals. |
| `pension_base` | E: finance a step toward the EUR 1,200/50%-of-average-wage objective. |
| `care_home` | E: commission assessed care affordable on a pension. |
| `teacher_pay` | E: fund salary and career steps toward the 130%-of-average-wage objective. |
| `inclusive_schools` | E: resource staff and support for shared Estonian-language schooling. |
| `account_to_parliament` | Mandate conclusion: report delivery and outstanding obligations. |

Longer objectives are represented by funded stages, not an immediate declaration that all housing, wage, school or 2030 energy targets have been achieved. The budget covers a defined intervention, and the permanent resilience bonus abstracts its lasting benefit. The proposed five-year defence tax is not implemented as a permanent hidden receipt.

The two military-factory equivalents are the mod's bounded representation of domestic production and maintenance investment, not literal promises of two HOI4-sized factories. These focuses award no free troops, manpower, technology or equipment. Reserve and procurement flags unlock the existing limited decisions, with their normal costs and controls. Allied reinforcements remain under the parent's separate German/allied decision.

## Costs and persistent rewards

The programme incurs **2,145 million** of explicit budget costs through `TFR_EST_spend_budget`, preserving TFR's inflation-adjusted debt/accounting helper. The progressive-tax focus applies **+0.055 billion recurring income** through `add_income_with_inflation`. This is the only recurring income delta, giving **+0.055 billion net before inflation**. It represents the selected tax changes as a balance amount; it is not a financial forecast or conversion of the historical euro thresholds. Service and benefit focuses finance stages through their stated costs; they do not silently create additional tax receipts.

Permanent rewards update **Estonian Economy** and **Estonian Military**, with exact native delta previews generated from the same values. Each focus completion has a persistent once-only flag, so refreshing the programme cannot replay rewards.

The main energy projects fill five shared OR-combined recovery slots: `renewable_contracts` contributes **2**, `grid_connection` **1**, and `renovation` **2**. Equivalent preparation under an earlier government counts once. Completing all three removes TFR's actual **Oil Crash** spirit; preparations made before the crisis still count when it starts. Reserves, cooperatives and heating grant their stated rewards without adding more recovery slots.

The `ammunition` and `maintenance` projects use separate pending/granted flags. Delivery checks states **13, 191, 1329 and 840**, requiring Estonian ownership, control and an unlocked free military-factory slot. The helper creates no extra building slots. Full or unavailable states cause the paid project to wait for the daily retry, and the granted flag is set only after construction. Repeated ticks cannot duplicate either facility.

The victory programme does not change the president, the historical SDE succession schedule, cabinet appointment rules, polling, elections, EU/NATO membership or the occupation/restoration controller. Completed reforms survive government changes through the existing persistent system.
