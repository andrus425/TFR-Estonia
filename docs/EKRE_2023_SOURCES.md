# EKRE's conditional 2023 programme

Research checked on 19 October 2026. EKRE did not lead Estonia's historical post-election government. This tree represents a hypothetical government formed after an EKRE plurality in the submod's valid 2023 election. Its priorities come from the party's contemporary proposals, rather than attributing Reform's enacted policies to EKRE.

## Primary references

- **A — Full 2023 platform:** [EKRE's published election programme](https://www.ekre.ee/ekre_2023_aasta_riigikogu_valimiste_programm/) and its [campaign-site version](https://rk.ekre.ee/programm). The energy, tax, transport, health and constitutional priorities used below are stated there.
- **B — Contemporary summary:** [Official 21-page election presentation](https://rk.ekre.ee/public/image/program/EKRE_R2023_Valimisprogramm.pdf). This independently preserves the principal campaign pledges in an accessible party PDF. Relevant pages are 4–5 for prices and pensions, 7–8 for families and education, 10–11 for care, 13–14 for defence, and 16–19 for institutions.
- **C — Defence:** [EKRE's 2023 defence programme](https://www.ekre.ee/riigikaitseprogramm-2023-aasta-valimisteks/), published 27 December 2022, and the party's [accompanying presentation](https://www.ekre.ee/ekre-riigikaitseprogramm-keskendub-iseseisva-kaitsevoime-tugevdamisele-ja-elanikkonnakaitsele/). The programme includes domestic defence-industry support, equipment, reserves, coastal protection, civil protection and border-service proposals.
- **D — Families:** [Population programme](https://ekre.ee/ekre-rahvastikuprogramm-paastame-eesti-rahvusriigi/) and the [10 January 2023 presentation](https://www.ekre.ee/ekre-uus-rahvastikuprogramm-naeb-ette-tulumaksu-pensioni-ning-oppe-ja-kodulaenu-sidumist-laste-arvuga/). The loan and tax nodes adapt the child-linked proposals.
- **E — Legislative follow-through on tax:** The [Riigikogu finance committee's autumn 2023 report](https://www.riigikogu.ee/wpcms/wp-content/uploads/2023/12/RAHK-II-istungj%C3%A4rgul-11.09-21.12.23-kontrollitud-21.12.23.pdf) records EKRE's food-VAT proposal, 272 OE. The [277 OE bill record](https://www.riigikogu.ee/tegevus/eelnoud/eelnou/d0839eb9-4bad-4eb2-9ee6-accc477b8e97/riigikogu-otsuse-ettepaneku-tegemine-vabariigi-valitsusele-langetada-vahiravimite-kaibemaksumaara-eelnou-277-oe-i-riigikogu-koosseisu-haalteenamus/) documents a narrower cancer-medicine initiative. The mod uses the broader medicine-rate pledge in the election platform and does not misdescribe the rejected bill as enacted law.
- **F — Constitutional procedure:** The [Riigikogu's account of the 2021 direct-election proposal](https://www.riigikogu.ee/pressiteated/riigikogu-ei-toetanud-rahvahaaletuse-korraldamist-presidendi-otsevalimise-kusimuses/) establishes earlier legislative activity. Its [constitutional committee account of citizen initiatives](https://www.riigikogu.ee/pressiteated/pohiseaduskomisjon-toetab-rahvaalgatuse-seadustamist/) supplies procedural context. The 2023 platform remains the source of the renewed pledges.

The party's HTML pages sometimes returned HTTP 403 to the browsing fetcher. The text was checked through indexed results on the same official domains and against the official PDF. No secondary site's characterization of EKRE is used as a substitute platform. The descriptions are original short implementation summaries, without reproducing campaign rhetoric or treating contested party claims as established fact.

## Entry and timing

The branch requires the persistent `TFR_EST_ekre_won_2023_election` and `TFR_EST_ekre_2023_mandate` markers, with no ended mandate, independence, and electoral mandate party 3. It can be shown during coalition talks. Focus selection additionally requires a confirmed EKRE prime minister, EKRE in the coalition, and **51 actual coalition seats**. Confidence-and-supply votes do not substitute for those coalition seats. The coalition's other parties remain those negotiated through the ledger.

There are **32 focuses of 35 days**, totaling **1,120 days**: one common root, five parallel six-focus columns, and one final report. Starting on 17 April 2023 gives an uninterrupted completion date of **11 May 2026**, leaving **235 days before 2027**. There are no calendar requirements on ordinary policies and no blanket wartime prohibition. Defeat, coalition failure and a deliberately delayed government can still interrupt the schedule.

Defence spending is available after **70 total focus-days**. The industrial column's second and third nodes provide the two paid military factories after **105 and 140 days**. Reserve preparation and air-defence planning are accessible after **105 and 140 days** along their own branch. These measures require neither civilian reforms nor the final report. AI priorities put the two factories, defence preparations and energy security before later civilian policy.

## Focus register

Identifiers below follow `TFR_EST_ekre_2023_`. References identify the policy basis; numerical rewards, costs and the division of work into focuses are game design.

| Focus | Policy basis | In-game implementation |
|---|---|---|
| `new_mandate` | Hypothetical election outcome. | Agree a programme under the actual parliamentary coalition. |
| `defence_commitment` | C: defence funding. | Pay an initial procurement contribution; improve organization, logistics and readiness. |
| `reserve_training` | C: larger reserve and training establishment. | Call-up preparation and training bonuses; unlock the existing bounded reserve-recruitment decision. |
| `air_defence` | C: medium- and short-range protection. | Fund preparatory procurement, crews and resilience; no free missile systems. |
| `coastal_defence` | C: coastal and mine capability. | Prepared shore positions; no fleet or free weapons. |
| `military_border_guard` | C: proposed military border service. | Crisis command, communications and reserve organization. |
| `shelters` | C: civil protection. | Building preparation, exercises and resilience. |
| `defence_contracts` | C: domestic industry, growth capital and development cooperation. | Fund maintainable contracts and unlock existing paid domestic procurement. |
| `ammunition_workshop` | C, adapted to TFR. | One paid factory project, subject to ownership, control and building slots. |
| `repair_workshop` | C, adapted to TFR. | A distinct second paid factory project; maintenance and efficiency. |
| `existing_railways` | A: existing railway links instead of Rail Baltic. | A funded domestic investment package with a cohesion cost for disputed redirection. No automatic destruction of existing infrastructure. |
| `trunk_roads` | A: four-lane trunk routes. | Fund sections, represented by construction and supply bonuses. |
| `food_reserves` | C: emergency supplies. | Fund contracted domestic stores; no perpetual free food or equipment. |
| `narva_blocks` | A: idle Narva units. | Overhaul funding and dependable production; political and environmental friction affects cohesion. |
| `kiisa_reserve` | A: Kiisa's market role. | Fund fuel, company and dispatch arrangements. |
| `regulated_power` | A: three-cent electricity proposal. | A funded supply/subsidy reserve with political and cohesion costs. No assertion that the quoted tariff is permanently sustainable. |
| `fuel_excise` | A: lower fuel duties. | Lower household/production burdens and recurring public income. |
| `food_vat` | E and A: five-percent food rate. | Household relief with explicit recurring revenue loss. |
| `medicine_vat` | B and A: five-percent medicine rate. | Relief and service resilience with explicit recurring revenue loss. |
| `child_tax_relief` | D: child-linked allowance. | Relief, administrative funding and a recurring revenue loss. |
| `family_home_loans` | D: loan relief linked to children. | Fund a limited pilot with assessed borrowers. |
| `student_loan_relief` | D: parents' education debt. | Fund applications and first claims. |
| `family_doctors` | B: primary-care and pharmacy access. | Pay for dependable duty arrangements and productive resilience. |
| `rural_maternity` | B: local midwife cover. | Fund staffing and referral arrangements. |
| `thirteenth_pension` | B: additional pension payment. | Fund an initial supplement, distinct from a promise to raise every pension to a specified future level. |
| `parliamentary_scrutiny` | B and A: institutional oversight. | Committee expertise, accountability and political capacity. |
| `e_vote_audit` | B: electoral-system scrutiny. | A funded technical audit; it does not presume wrongdoing or change the assembly. |
| `citizens_initiative` | F and A: direct-democracy proposals. | Draft verification and constitutional safeguards; preparation only. |
| `presidential_election_bill` | F and B: presidential selection proposal. | Prepare a constitutional bill; the current president and succession system remain in place. |
| `constitutional_review` | A: scrutiny of European obligations. | Resource the Riigikogu's review, with cohesion and political tradeoffs. |
| `estonian_education` | B: language of instruction. | Pay for staff and materials; no population, citizenship or state-culture changes. |
| `account_to_parliament` | Campaign conclusion. | Require the other 31 records, then grant political and cohesion rewards. |

The party's ambitious force-establishment figures are not implemented as free manpower, divisions, tank units or equipment. The two workshops are an explicitly accelerated first industrial contribution, supported by the platform's domestic-industry commitment. The focus names and descriptions distinguish planning, funding and legislation from completed long-term capability.

## Budget, energy and continuity

Amounts use the existing TFR economic ledger and its native inflation-adjusted debt or income tooltips. Focus budget amounts are game values in millions of the ledger's base currency; they are not purported conversions of historical appropriations. Fuel, food, medicine and child-tax relief visibly reduce recurring income. Public construction, loans and services add public debt through the existing spending helper. Benefits appear as exact changes to **Estonian Economy** or **Estonian Military**, plus explicit cohesion, readiness and political costs where applicable.

Energy preparation shares the existing five recovery slots with the earlier cabinet programmes. `narva_blocks` covers slots 1–2, `kiisa_reserve` covers slot 3, and `regulated_power` covers slots 4–5. Equivalent older preparations count once; completing these three projects can remove the parent's Oil Crash spirit. The following tax nodes are not required to remove it. None of these projects changes another country's energy crisis or rewrites TFR's European institutions.

The ammunition and repair entitlements use their own pending and granted flags. Only states **13, 191, 1329 and 840** are eligible, with Estonia owning and controlling the state and an available unlocked military-factory slot. No extra slots are granted. If no eligible slot exists, the funded project waits and the daily tick retries; successful delivery consumes that project's entitlement. Reloading the tree or changing the cabinet cannot grant another copy.

All policy rewards have persistent completion records. Constitutional preparation and the e-voting audit do not change the 101-seat election calculation, call a snap election, alter the regular/postwar calendar, appoint a president, or remove the requirement for coalition confidence. European scrutiny does not automatically leave the EU or NATO. Those systems continue to follow the submod's existing lifecycle rules.
