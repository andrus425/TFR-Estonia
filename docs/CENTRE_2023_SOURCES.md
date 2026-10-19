# Centre's conditional 2023 government programme

Research checked on 19 October 2026. This programme belongs to an alternate 2023 election in which Keskerakond wins the largest Riigikogu delegation and forms a majority cabinet. An initial March victory keeps Jüri Ratas as prime minister; a later 2023 victory preserves any Kiik/Kõlvart successor already chosen at the September congress after an earlier defeat. It is based on contemporary Centre proposals, rather than attributing the historical Reform-led government's enacted policy to Centre.

## Primary references and provenance

The original main-domain PDF link now returns 404. The [official archived platform PDF](https://vana.keskerakond.ee/files/valimisplatvorm3.pdf) remains accessible. Its cover identifies the 2023 election to the XV Riigikogu. The retrieved document has **41 pages**, **965,189 bytes**, and SHA-256 **`a13004b41b9dbcaf2b417687b881dadbc0e82f31cb705f18a12c14ce4fc77262`**. The PDF was read with `pypdf` from the public archived URL; no image or other asset was copied into the mod.

The surviving [official 2023 campaign site](https://riigikogu.keskerakond.ee/et/keskerakonna-valimisplatvorm) provides separate subject pages, allowing each branch to be checked against its own source:

- **A — [Defence policy](https://riigikogu.keskerakond.ee/et/keskerakonna-valimisplatvorm?topic_id=288):** defence funding, air defence, reservists, allied presence, community consultation and domestic industry. The relevant section begins on PDF page 7.
- **B — [Economy and energy](https://riigikogu.keskerakond.ee/et/keskerakonna-valimisplatvorm?topic_id=301):** industrial modernization, public orders, dispatchable capacity, LNG, local generation and digital connections. The economy section begins on PDF page 16.
- **C — [Regional policy](https://riigikogu.keskerakond.ee/et/keskerakonna-valimisplatvorm?topic_id=315):** guarantees, regional services, networks and renovation. The section begins on PDF page 25.
- **D — [Finance and taxation](https://riigikogu.keskerakond.ee/et/keskerakonna-valimisplatvorm?topic_id=307):** the income-tax bands and allowance, consumption-tax relief and pension objective. The section begins on PDF page 21. This is the 2023 proposal; it is not the party's older tax plan with different thresholds.
- **E — [Social policy](https://riigikogu.keskerakond.ee/et/keskerakonna-valimisplatvorm?topic_id=324):** kindergarten fees, home services and care.
- **F — [Health policy](https://riigikogu.keskerakond.ee/et/keskerakonna-valimisplatvorm?topic_id=336):** county hospitals, sick pay, medicine affordability and access. The section begins on PDF page 34.
- **G — [Education policy](https://riigikogu.keskerakond.ee/et/keskerakonna-valimisplatvorm?topic_id=285):** funded teacher pay and staffing.
- **H — [Population and minority policy](https://riigikogu.keskerakond.ee/et/keskerakonna-valimisplatvorm?topic_id=310):** language-learning access and a consultative council. The section begins on PDF page 23.

Specific legislative activity is corroborated by the Riigikogu's [account of the Centre sick-pay proposal](https://www.riigikogu.ee/pressiteated/haiguspaevade-huvitamise-korda-pikendav-eelnou-labis-teise-lugemise/), its [autumn 2023 finance-committee report](https://www.riigikogu.ee/pressiteated/rahanduskomisjoni-tegevuse-ulevaade-ii-istungjargul-11-09-2023-21-12-2023/) covering the food-VAT proposal, and [Ratas's pension-policy statement](https://www.riigikogu.ee/pressiteated/juri-ratas-pension-peab-tousma-erakorraliselt-50-eurot/). These sources establish proposals and parliamentary activity; the mod does not describe a rejected bill or an opposition pledge as historically enacted law.

## Entry, structure and timing

The programme uses `TFR_EST_centre_won_2023_election`, `TFR_EST_centre_2023_mandate` and `TFR_EST_centre_2023_mandate_ended`. Its branch is visible for an independent Estonia with an active Centre electoral mandate. It may be shown during negotiations, but every focus requires a confirmed Centre-led cabinet and **51 actual coalition seats**. Confidence-and-supply votes do not replace coalition seats. No particular coalition partner is forced.

One common root opens five parallel columns of six focuses. The final report requires all **31** other policy records. Every focus takes **35 days**; the complete programme requires **1,120 days**. An uninterrupted start on 17 April 2023 finishes on **11 May 2026**, **235 days before 2027**. Ordinary focuses have no calendar gates, and an early European war does not automatically terminate the programme. Coalition failure, delayed government formation and occupation can still interrupt it.

Defence funding is available after **70 total focus-days**, air-defence preparation after **105**, and reserve preparation after **140** along their branch. The two paid industrial facilities can be delivered after **105 and 140 days** along the industrial branch. None requires the final report or civilian-policy completion. The AI order gives these early preparations priority before the longer social programme.

## Content register

The identifiers below follow `TFR_EST_centre_2023_`. Source letters refer to the official subject pages above. Descriptions are short original summaries of implementation, and numerical effects are gameplay choices.

| Focus | Policy basis | Implementation |
|---|---|---|
| `new_mandate` | Alternate election outcome. | Agree a programme under the coalition actually confirmed. |
| `defence_commitment` | A: cross-party agreement and sustained funding. | Budget a first procurement contribution and improve organization/readiness. |
| `air_defence` | A: accelerated medium-range protection. | Fund sites, crews and procurement preparation; no free equipment. |
| `reserve_expertise` | A: reservists' skills and instruction. | Readiness, training and the existing bounded reserve-recruitment decision. |
| `allied_basing` | A: allied reception facilities and stores. | Logistics and organization; existing allied reinforcement grants remain separate. |
| `community_training` | A: local consultation and compensation. | Fund a practical training settlement and limited army experience. |
| `civil_continuity` | A: broad defence and institutional preparation. | Municipal exercises and resilience. |
| `industrial_guarantees` | A: support domestic defence industry. | Fund suppliers and unlock existing paid procurement contracts. |
| `ammunition_workshop` | A, adapted for TFR. | One funded military-factory entitlement. |
| `maintenance_workshop` | A, adapted for TFR. | A separate funded military-factory entitlement and maintenance improvements. |
| `ida_viru_innovation` | B: industrial modernization in Ida-Viru. | Assessed technology projects, research and output. |
| `regional_jobs` | C and B: guarantees and regional employment. | Fund viable investment and retraining. |
| `construction_orders` | B: public construction programme. | Tender staged projects and pay their debt-financed cost. |
| `power_reserves` | B: dispatchable capacity and LNG preparation. | Fund reserve generation and supply arrangements. |
| `local_chp` | B: local combined generation. | Finance viable projects with fuel and network arrangements. |
| `apartment_renovation` | C: regional renovation assistance. | Fund a smaller local contribution and technical supervision. |
| `weatherproof_grid` | B: resilient networks. | Finance vulnerable lines and connection bottlenecks. |
| `rural_broadband` | C: affordable last-mile access. | Fund connections and coordinate civil works. |
| `energy_cooperatives` | B: community generation and storage. | Support assessed financing and local participation. |
| `progressive_income_tax` | D: upper income band. | Add recurring income and pay an administrative cost, with political/cohesion tradeoffs. |
| `minimum_tax_allowance` | D: minimum-wage-linked exemption. | Household relief with a recurring revenue cost. |
| `food_vat` | D and parliamentary proposal 10 OE. | Reduced rate with visible lost receipts. |
| `prescription_vat` | F: prescription exemption and other medicine relief. | Affordability and service resilience, with visible lost receipts. |
| `pension_fifty` | Pension proposal and E. | Fund one extraordinary basic-component step, rather than automatically reaching the entire future objective. |
| `home_care` | E: municipal care and nursing. | Contract visits, support carers and improve resilience. |
| `county_hospitals` | F: needs-based county budgets. | Finance service availability and staffing accountability. |
| `second_day_sick_pay` | F and proposal 725 SE. | Fund the public part of a shared compensation arrangement. |
| `free_kindergarten` | E: fee relief. | Compensate councils and prepare capacity. |
| `teacher_pay` | G: negotiated pay improvements. | Fund steps and staffing alongside the longer-term salary target. |
| `language_courses` | H: instruction and paid learning time. | Improve access and participation without changing citizenship or voting rules. |
| `minorities_council` | H: advisory participation. | Convene a consultative forum and support practical service access. |
| `account_to_parliament` | Campaign conclusion. | Account for all preceding policies without calling an election. |

The two workshops are a bounded, accelerated contribution to the party's defence-industry objective. They are not a claim that the platform literally specified two military factories of HOI4 size. Force preparation does not add manpower, divisions or free equipment. Long energy, school and industrial projects are represented by funded stages rather than instant nationwide completion.

## Costs, recovery and persistence

The programme uses the parent's native inflation-adjusted debt and income helpers. Budget amounts are balance values in millions of TFR's base ledger currency; they are not conversions of the platform's historical euro figures. Every permanent economic or military reward uses an exact native preview for the existing **Estonian Economy** or **Estonian Military** dynamic modifier.

The upper income band contributes **+0.045 billion** of base recurring income. The allowance, food rate and medicine relief contribute **−0.030**, **−0.040** and **−0.012 billion**, for **−0.037 billion net** before the parent's inflation calculation. This is a game balance model, not a revenue forecast. The positive tax contribution does not silently finance all investment: procurement, buildings, services and grants still have their own explicit budget costs.

The energy-response projects share five OR-combined preparation slots with previous programmes. `power_reserves` covers slots 1–2, `local_chp` slot 3, and `apartment_renovation` slots 4–5. Equivalent older preparations count once. Those three projects can remove the actual TFR Oil Crash spirit; later grid, broadband and cooperative projects provide their stated permanent benefits without adding more recovery slots.

Factory entitlements use distinct `ammunition` and `maintenance` pending/granted flags. The grant helper checks states **13, 191, 1329 and 840**, with Estonia owning and controlling the state and an available unlocked military-factory slot. It adds no free building slots. If delivery is impossible, the paid project waits and the daily tick retries. The entitlement is consumed only after construction, so reloading or reconciling the programme cannot grant a second copy.

Persistent completion flags preserve enacted reforms. Programme refreshes do not appoint a different prime minister, change the current president, edit the 101-seat calculation, alter the postwar election controller or change EU/NATO membership. The separate Centre leadership-congress story handles a 2023 electoral defeat and is outside this victory programme.

## September leadership congress

The defeat story uses **10 September 2023**, the date of Centre's extraordinary congress. [Ratas's official congress speech](https://vana.keskerakond.ee/et/meedia/3366-j%C3%BCri-ratase-k%C3%B5ne-eesti-keskerakonna-erakorralisel-kongressil.html) identifies the date, his decision not to seek the chair, the Kiik/Kõlvart contest and his support for Kiik. The [contemporary report of Kõlvart's election](https://kesknadal.ee/2023/09/10/keskerakond-valis-oma-uueks-juhiks-mihhail-kolvarti/) records the historical winner. [The Riigikogu's April 2023 faction registration](https://www.riigikogu.ee/pressiteated/riigikogu-juhatus-registreeris-kuus-fraktsiooni/) records Kiik's role as Centre's parliamentary group chairman.

The mod retains both historical candidates and allows a Kiik victory as an alternate outcome. A March electoral defeat leaves Ratas as chair until the September event, which offers no option for him to stand again. Occupation can delay delivery until independent politics resumes. A Centre victory before the choice cancels this defeat story, while an already selected successor remains leader after a later victory. The party chair and the incumbent prime minister are separate records: this congress does not replace another party's PM, and a Centre caretaker waits for actual cabinet confirmation.
