# Implementation contracts

## Ownership and data flow

The `TFR_EST_` prefix is reserved for this submod. Additive files separate the
parliament, shared systems, normal content and occupation. The parent installation
is read-only; exact-path overrides are generated and audited separately.

Party IDs are stable: Reform 1, Centre 2, EKRE 3, Isamaa 4, SDE 5, Eesti 200 6,
Parempoolsed 7. Suffixes are `reform`, `centre`, `ekre`, `isamaa`, `sde`, `e200`, `pp`.
Each has support (integer basis points), seats, active, coalition and supply
variables. Polling plus other votes totals 10,000; seats total 101 after every
valid election. Invalid inputs leave the previous assembly in place and log a
diagnostic. `TFR_EST_pm_party` is confirmed office; `TFR_EST_nominee_party` is a
proposed cabinet leader. Confidence support and actual cabinet seats are separate.

The parliament owns the election calendar. Native elections are disabled.
The first regular election is March 2023; weekly scheduling produces one election
within its window. A restoration election supersedes a same-week regular election.
Polling campaigns preserve totals through bounded transfers and never change seats.

## Public effects

- `TFR_EST_initialize_systems`: guarded first initialization, called after parent startup.
- `TFR_EST_initialize_parliament`: seed the historical assembly and Ratas cabinet.
- `TFR_EST_parliament_tick`: weekly elections, formation, confidence and leadership repair.
- `TFR_EST_suspend_parliament` / `TFR_EST_restore_parliament`: occupation and restoration.
- `TFR_EST_change_cohesion = { AMOUNT = n }` and the matching readiness effect:
  change canonical meters, clamp to 0–100 and refresh derived national spirits.
- `TFR_EST_spend_budget = { AMOUNT = n }`: millions of euros converted to the
  inflation-adjusted TFR debt ledger; callers supply the intended project cost.
- `TFR_EST_refresh_programme`: reconcile only the currently confirmed programme.
- `TFR_EST_mobilize_reserves`: one-time template authorization; normal recruitment applies.
- `TFR_EST_reconcile_occupation`: actual patron/status selects occupation or restoration.
- `TFR_EST_reconcile_campaign`: war-stage tracking and independent main-tree repair.

## Lifecycle and persistence

`TFR_EST_initialized` is set before parliament initialization. Parent startup
finishes before the day-one initialization event. A single root weekly hook runs
meter drift, parliament, normal content, and occupation weekly maintenance.
A daily hook reconciles occupation before the independent campaign tree.

Campaign stages: 0 opening, 1 first war, 2 interwar/reconstruction, 3 second war,
4 post-second-war. Seen-war flags persist even if parent global flags are cleared.
Occupation controls tree selection and suspends normal cabinet/election mechanics.

Each focus has a persistent completion flag and a bypass check. This is necessary
because `keep_completed` alone does not retain unrelated focus IDs across a
normal-to-occupation tree swap. Physical investments and political reforms remain
one-time. Occupation generations distinguish new patrons/stages and reset only
the choices that belong to a fresh occupation mandate.

Repairs do not repeat initialization, transfer territory weekly, restore enemy
control, or issue rewards. Only the actual protected settlement sets the anchor
controller. Parent delayed generic-tree changes can be repaired without preventing
combat capture in a later war.

## Compatibility boundaries

The authoritative starting political model replaces Estonia's history leadership,
while inherited technologies, influence, economic ideas, NATO/EU initialization
and DLC branches remain intact. Registration in `has_content_tag` prevents the
parent AI disable behavior at startup.

The peace patch guards annexation before execution. Other countries retain the
original annex action. Estonia keeps state 13, while the original recipient gets
the remaining intended lands. Broad country/state loops are checked as well as
literal `target = EST` statements. Russian pacification gates recognize occupied
Estonia and evaluate only territory actually owned by Russia.

The custom occupation autonomy level cannot be downgraded or integrated normally.
Explicit scripted annexation protection is still required. Debug map operations,
arbitrary console commands and other mods are outside the audited guarantee.

The parent GDP/debt/inflation and membership effects are reused. Budget values in
the authoring source are in millions, not the parent's billion-unit debt amounts.
NATO restrictions are lifted for prepared Estonia only, guarded once per campaign.

## Assets and validation

References use effective TFR/base-game sprites and portraits. Same-relative-path
TFR interface files shadow vanilla; use the effective catalog when selecting icons.
English localization is UTF-8 with BOM. New leaders currently reuse generic portraits.

The structural validator catches syntax, duplicate IDs, missing references,
localization, sprites and focus prerequisite cycles. The limited test runtime
executes actual arithmetic/control-flow scripts using exact rational arithmetic;
it does not emulate the game engine, combat, UI, scheduler or fixed-point rounding.
Engine startup and natural campaigns provide the remaining validation layers.
