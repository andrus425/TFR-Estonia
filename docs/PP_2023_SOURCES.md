# Parempoolsed's conditional 2023 government programme

Research checked on **20 October 2026**. The tree represents a hypothetical
Parempoolsed election victory and majority government under the campaign's
existing **Lavly Perling** identity. Party **7** keeps its own polls, seats and
coalition membership even though Reform and Parempoolsed share TFR's
`market_liberal` ideology. The programme neither awards election support nor
changes the seat-allocation algorithm. No new leadership succession is added.

## Primary references

The source is the party's [official 2023 Riigikogu programme index](https://parempoolsed.ee/riigikogu-valimised-2023/programm/)
and the complete relevant chapter text linked from it. All links below retain
the explicit `riigikogu-valimised-2023` path. They were read directly through
the web reader; later menu items, site copyright dates and current navigation
are not treated as evidence of the historical publication date. No third-party
summary, later programme, source HTML or artwork is included in the package.

| Code | Official chapter | Selected basis |
|---|---|---|
| A | [Kaitstud piiririik](https://parempoolsed.ee/riigikogu-valimised-2023/programm/kaitstud-piiririik/) | Long-term defence investment, military spending of at least 3% plus host-nation support, society-wide participation and essential-service continuity. |
| B | [Kiire majanduskasv](https://parempoolsed.ee/riigikogu-valimised-2023/programm/kiire-majanduskasv/) | Loan and equity capital rather than routine grants, joint 3% research investment and university-industry knowledge transfer. |
| C | [Mõistlik kliimapoliitika](https://parempoolsed.ee/riigikogu-valimised-2023/programm/moistlik-kliimapoliitika/) | Competition, faster planning, grid connections, dispatchable supply during transition, nuclear regulation, renovation and timber construction. |
| D | [Korras riigirahandus](https://parempoolsed.ee/riigikogu-valimised-2023/programm/korras-riigirahandus/) | Expenditure review, a negative supplementary budget, understandable accounts, an 18% income-tax objective and employee-benefit exemptions. |
| E | [Nõudlik riigijuhtimine](https://parempoolsed.ee/riigikogu-valimised-2023/programm/noudlik-riigijuhtimine/) | Traceable services, transparent appropriations and removal of discretionary political earmarks. |
| F | [Tark rahvas](https://parempoolsed.ee/riigikogu-valimised-2023/programm/tark-rahvas/) | Teacher-focused spending, common Estonian-language schools, vocational and adult training, and university contributions paired with assistance. |
| G | [Õiglane sotsiaalpoliitika](https://parempoolsed.ee/riigikogu-valimised-2023/programm/oiglane-sotsiaalpoliitika/) | Needs-based support, competitive care provision and reduced medical paperwork. |
| H | [Positiivne rahvuslus](https://parempoolsed.ee/riigikogu-valimised-2023/programm/positiivne-rahvuslus/) | A qualification-based immigration points system and language integration. |

These contemporary chapters provide sufficient detail without adding later
parliamentary proposals. Real percentage objectives identify the proposals;
focus costs, reward percentages, recovery slots and implementation stages are
authored game balance. Wording is original rather than a translation of long
programme passages.

The security chapter refers to the real 2022 invasion and contemporary NATO
accessions. The implementation instead uses the allies and crisis conditions
actually present in TFR. It does not trigger a historical invasion, force a
particular NATO membership change or grant automatic diplomatic membership.

## Entry and timing

The programme is hidden until a validated election within the supported 2023
window gives Parempoolsed the largest delegation. Its visibility uses
`TFR_EST_pp_won_2023_election`, `TFR_EST_pp_2023_mandate`, mandate party **7**,
independent parliamentary status and the absence of
`TFR_EST_pp_2023_mandate_ended`. A caretaker can inspect the incoming programme;
selection requires a confirmed Parempoolsed prime minister, Parempoolsed
coalition membership and **51 actual coalition seats**. Confidence-and-supply
agreements do not substitute for those coalition seats. No coalition partners
are forced.

There are **32 focuses of 35 days**, totalling **1,120 days**. An uninterrupted
start on **17 April 2023** finishes on **11 May 2026**, leaving **235 days before
2027**. Government formation, lost confidence, occupation and player delays
use that margin. Ordinary policies have no date gates and a war does not
automatically close an independent cabinet's programme.

The compact layout uses a root at `(4, 0)`, five six-focus columns at x
**0, 2, 4, 6, 8**, and a final account at `(4, 7)`. Column prerequisites preserve
progression while allowing choice between branches. The final account requires
all 31 prior policies.

The military column can deliver defence funding at **70 total focus-days**,
air-defence preparation at **105**, and reserve preparation at **140**. The
separate industrial column can deliver its two factory projects after **105**
and **140 total focus-days**. These are alternative paths through one focus
queue, not simultaneous deliveries. No civilian branch or final account
blocks them. AI order prioritizes defence, industry and the early energy
response before longer civilian reforms.

## Content register

IDs use `TFR_EST_pp_2023_`; cost amounts are in the mod's millions before the
parent's inflation adjustment. Source letters refer to the chapter table.

| Focus suffix | Basis | Cost | Implementation |
|---|---|---:|---|
| `new_mandate` | Alternate result | 0 | Establish parliamentary accountability. |
| `defence_commitment` | A | 125 | Fund an initial military investment tranche. |
| `air_defence` | A; capability adaptation | 105 | Train crews and equip communications. |
| `reserve_muster` | A | 50 | Exercise call-up plans and unlock the limited reserve decision. |
| `civil_reserve` | A | 60 | Begin civilian registration and training toward the 10,000-person objective. |
| `allied_reception` | A | 80 | Resource existing reception arrangements separately. |
| `service_continuity` | A | 70 | Exercise ministries, stocks and essential suppliers. |
| `industrial_guarantees` | B/A | 50 | Improve assessed private supplier financing and unlock paid procurement. |
| `ammunition_workshop` | B/A; factory adaptation | 140 | Contract one production-capacity entitlement. |
| `maintenance_workshop` | B/A; factory adaptation | 115 | Contract one servicing-capacity entitlement. |
| `research_agreement` | B | 65 | Start the joint research investment agreement. |
| `knowledge_transfer` | B | 80 | Commission applied university-industry development. |
| `skilled_migration` | H/B | 35 | Implement the qualification-based admission system. |
| `renewable_permits` | C | 65 | Resource planning reform; fill two shared recovery slots. |
| `grid_connection` | C | 70 | Co-finance assessed connection work; fill one recovery slot. |
| `continuity_capacity` | C | 70 | Maintain dependable supply; fill two recovery slots. |
| `nuclear_framework` | C | 35 | Prepare licensing and independent supervision. |
| `renovation` | C | 40 | Simplify procedures and provide technical advice. |
| `timber_construction` | C | 55 | Qualify durable materials for public contracts. |
| `expenditure_audit` | D | 25 | Review duplication and publish service costs. |
| `supplementary_budget` | D | 20 | Apply reviewed savings with a cohesion cost. |
| `transparent_budget` | D/E | 15 | Publish comprehensible accounts and service progress. |
| `labour_taxes` | D | 20 | Stage the tax reduction and social-tax ceiling with an explicit revenue cost. |
| `fringe_benefits` | D | 20 | Implement specified employee-cost exemptions with a revenue cost. |
| `no_earmarks` | E | 15 | Replace discretionary grants with accountable appropriations. |
| `teaching_priority` | F | 65 | Rebalance spending toward the 70% teacher-pay objective. |
| `common_school` | F/H | 70 | Fund language materials and classroom support. |
| `vocational_training` | F | 55 | Commission accessible vocational and adult training places. |
| `university_contribution` | F | 40 | Pair partial tuition with revised loans and grants; apply a cohesion cost. |
| `targeted_support` | G | 50 | Reassess blanket entitlements with a cohesion cost. |
| `patient_choice` | G | 45 | Improve competitive care contracts and electronic referrals. |
| `account_to_parliament` | Mandate conclusion | 0 | Account for every preceding policy. |

The two industrial projects are requested campaign content adapted from the
platform's security and private-investment policies. The platform does not
literally promise these two HOI4-sized factories. Their representation is
paid procurement tooling and contracted domestic capacity, not a claim that
Parempoolsed proposed expanding state ownership of ordinary firms. The general
capital policy uses the platform's loan/equity approach rather than inventing
a blanket business-subsidy law.

The air-defence project is an implementation choice within the proposed
long-term investment plan, not a separately named party air-defence scheme.
The civilian-reserve objective adds no 10,000-person manpower grant. Nuclear
licensing creates neither a reactor nor a nuclear technology or weapons unlock.
All longer objectives are funded stages; there are no new free divisions,
equipment grants or unlimited manpower. Existing reserve and procurement
decisions retain their costs and caps, and parent allied reinforcements stay
separate.

## Costs and lasting effects

One-off project costs total **1,750 million** through `TFR_EST_spend_budget`.
Six policies call the parent's `add_income_with_inflation` using these explicit
base-ledger amounts:

| Policy | Recurring income change, TFR billions before inflation |
|---|---:|
| `supplementary_budget` | +0.040 |
| `labour_taxes` | -0.035 |
| `fringe_benefits` | -0.015 |
| `no_earmarks` | +0.012 |
| `university_contribution` | +0.008 |
| `targeted_support` | +0.010 |
| **Net** | **+0.020** |

These are balance values, not euro conversions or a financial forecast. Savings
and tax costs accumulate only when their individual policies are completed.
The programme does not automatically erase debt, guarantee a balanced national
budget or assume tax cuts instantly pay for themselves. Implemented tradeoffs
include **-3 cohesion** from expenditure cuts and **-2 each** from tuition and
targeted-benefit changes, alongside other funded cohesion improvements.

Permanent rewards update **Estonian Economy** and **Estonian Military** through
the shared modifier system. Numerical previews and visible costs derive from
the same values as the actual rewards. Persistent completion flags guard
each reward and preserve reforms across government changes.

The energy projects fill **2 + 1 + 2** shared preparation slots. Equivalent
preparations across all nine supported government programmes use OR conditions
and cap the recovery at five slots, preventing duplicate recovery from a
government change. They reduce and ultimately remove TFR's actual Oil Crash
idea, and can be prepared before it appears. The later nuclear, renovation and
timber policies provide their own lasting effects without inventing extra
recovery stages.

Each military-factory project grants one factory at most, in an owned and
controlled Estonian core with an unlocked free building slot. A funded project
waits when no eligible state has space and retries through the existing daily
controller. Occupation suspends delivery. Pending projects do not consume their
delivery flag until actual construction succeeds.

## Implementation and verification boundaries

`tools/build_pp_2023.py` deterministically generates the four gameplay files
and English UTF-8 BOM localization. The lifecycle callback, controller hooks,
shared imports, AI plan, effect previews and crisis helpers integrate it with
the existing campaign. Old descriptions and unrelated country content remain
outside this builder.

The route uses existing icons and character assets. This source register
records policy provenance and intended behaviour; test results, native-engine
coverage and remaining playtest limits are recorded in `docs/TEST_RESULTS.md`.
It does not claim that a natural campaign, rendered layout or save/reload test
has been completed merely because a generated file exists.
