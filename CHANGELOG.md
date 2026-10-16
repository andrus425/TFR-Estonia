# Changelog

## 16 October 2026 — compact focuses and visible, stronger rewards

- Compact all five focus layouts while preserving their IDs, prerequisites,
  visibility, 35-day timings and final referendum. The opening is ten grid units
  wide; both historical government programmes use five columns two units apart.
- Preserve all 235 existing focus descriptions exactly, with a hash fixture
  guarding their localized values.
- Show actual inflation-adjusted budget costs through TFR's native debt helper.
  Cohesion and readiness now show signed numerical changes without internal
  variable arithmetic in their effect tooltips.
- Give the opening and both historical cabinets stronger permanent economic and
  military rewards. Use TFR-style native "Modify ... by" previews generated from
  the same numerical model as the real modifier changes. Preview definitions
  remain display-only and never become national spirits.
- Replace the custom energy penalty with TFR's existing five Oil Crash ideas.
  Each Ratas energy policy advances recovery once; Kallas's network-charge focus
  advances it twice and her other three projects once. The full energy branch
  removes the spirit before the wider crisis ends. Shared project slots prevent
  duplicate relief across routes, and saved custom penalties migrate safely.
- Replace long historical-cabinet requirement lists with concise tooltips while
  retaining the full coalition, cabinet, programme, date and domestic-case checks.
- Add regression coverage for compact layouts, unchanged descriptions, actual
  debt costs, exact modifier previews and the real parent crisis tiers.

## 15 October 2026 — Ratas resigns and Kallas takes office

- Made Ratas's resignation automatically fail the marriage-referendum focus,
  overriding its protection against manual cancellation. Ordinary confidence loss
  still cannot cancel an already active referendum.
- Hide the opening on resignation and reveal a dedicated twenty-focus Kallas
  programme. Its first focus requires confirmation of the Reform–Centre cabinet
  after the existing thirteen-day negotiations, with no election or seat changes.
- Preserve all ten earlier policy rewards. If the player delays the resignation
  response until after native focus completion, undo only the abandoned final.
- Added five policy branches using enacted 2021–2022 policy: COVID response,
  pension/education measures, recovery investment and local services, energy bills
  and gas supply, and defence/civil protection. All twenty focuses take 35 days;
  a 26 January 2021 start can finish on 27 December 2022 before the regular vote.
- Require a confirmed Reform–Centre government and 51 actual coalition seats.
  Recorded pandemic recovery bypasses unused emergency interventions without
  rewards; certificate administration remains useful afterward.
- Reuse the existing tracked energy-crisis contribution and capped mitigation
  slots for both government routes. Relief never changes the parent's Saudi-war
  flags or stacks duplicate mitigation after a route transition.
- Keep broader domestic branches hidden until the next valid election, even if
  Reform wins again. War and restoration content uses the resolved opening and
  an earlier earned policy, so an abandoned referendum cannot block it permanently.
- Document the coalition's continuation to 2023 as alternate history; no forced
  June 2022 breakup or policies imported from the later Kallas II cabinet.

## 15 October 2026 — the retained Ratas coalition through 2023

- Added a hidden twenty-focus continuation that appears when Ratas chooses to
  remain prime minister. The first focus waits for the active referendum to finish;
  no tree replacement interrupts the crisis.
- Built five branches from the 2019 coalition agreement and December 2020
  pandemic plans: family support, regional employment and enterprise, healthcare,
  energy supply and bills, and internal/territorial security. The player can move
  between branches before the final report to voters.
- Kept every focus at 35 days and required the original three partners, Centre
  leadership and 51 actual coalition seats. Twenty focuses take 700 days, allowing
  a late-January 2021 start to finish before the March 2023 election.
- Required actual domestic COVID cases for the three pandemic interventions;
  a recorded recovered outbreak bypasses them without rewards. Added guarded
  one-tier vaccination relief using the parent's case ideas.
- Connected Estonia's dynamic economy modifier to TFR's Saudi-war supply shock.
  Funded supply, renovation and bill-relief policies mitigate its local penalties;
  crisis resolution reverses only the tracked crisis contribution.
- Hid the older domestic programmes during this coalition mandate while retaining
  world-state war/restoration branches. The next valid election ends the extension,
  including after another Centre victory; election arithmetic and dates are unchanged.
- Added primary-source references, generated localization, regression coverage and
  manual acceptance scenarios. In-game campaign and balance checks remain required.

## 15 October 2026 — branched policies and domestic COVID requirements

- Restored meaningful prerequisites within four short opening branches: pensions,
  education, infrastructure and the COVID response. Players can choose between
  branches and between sibling policies after the highway or emergency response.
- Required all six terminal policies before the referendum; their prerequisites
  cover all ten opening policies. Kept 35-day durations and the December 24 gate
  exclusively on the non-cancelable final focus.
- Required actual COVID cases in Estonia for the emergency focus, using TFR's
  existing severity-idea trigger. Added an independent first-case event from the
  Health Board's February 27, 2020 announcement because the parent has no Estonia
  outbreak assignment. Existing severity is preserved and recovery cannot reseed
  the outbreak. From 2023, the bridge removes only its own unchanged lowest tier
  once the mandatory COVID response is complete, so delayed play can still finish
  the opening.

## 15 October 2026 — freely ordered coalition policies (superseded)

- Made the ten opening policy focuses available in any order, without policy
  prerequisites or start-date gates, including the COVID response.
- Arranged policies in two rows of five with the final marriage-referendum focus
  centered below. All ten still must finish before that non-cancelable final.
- Retained the December 24, 2020 gate only for the referendum, along with the
  35-day durations, coalition-majority checks and Porto Franco choices.

## 14 October 2026 — historical coalition opening and Porto Franco

- Replaced the eight generic introductory focuses with eleven 35-day focuses
  covering the Ratas II coalition's documented policies and initial COVID response.
- Hid later branches during the opening. Subsequent party and war sections reveal
  through the serving government and campaign state, with guarded layout refresh.
- Required actual Centre–EKRE–Isamaa coalition membership and 51 cabinet seats
  for the ten policy focuses. Supply votes cannot substitute for coalition seats.
- Required all ten policies before the marriage-referendum bill focus, made that
  focus non-cancelable, and added a December 24 gate to account for banked progress.
- Added the January 12–13 Porto Franco sequence and a choice between retaining
  Ratas or a caretaker handover to a Reform–Centre cabinet in the same parliament.
- Removed the snap-election decision; only explicit event/focus authorization
  can call a snap vote. Regular and restoration elections continue unchanged.
- Used the two dynamic modifiers for new opening bonuses and preserved later
  content and occupation settlements. Added research notes and regression tests.

## 14 October 2026 — economy and military dynamic modifiers

- Added permanent Estonian Economy and Estonian Military dynamic modifiers,
  following TFR's variable-driven country modifiers and inherited icon assets.
- Added 16 independent backing variables with neutral initial values, guarded
  initialization, immediate refresh and daily missing-membership repair.
- Preserved existing values during repair and kept parent economic modifiers
  independent. Added source and native-engine regression coverage.
- Left all focus-tree files and existing focus rewards unchanged. Conversion of
  their individual ideas is deferred to the later content revision.

## 14 October 2026 — election-led coalition leadership

- Removed the seven player nomination decisions. Centre retains the historical
  opening leadership; later valid elections select the party with the most seats.
- Preserved coalition/supply negotiations and 51-vote cabinet confirmation,
  with the incumbent continuing as caretaker during an electoral handover.
- Locked between-election confidence recovery to the incumbent. Explicit
  event/focus hooks are the only permitted non-electoral succession mechanism.
- Made AI cabinet formation respect the stored mandate instead of overriding
  it with preferred-party game rules; those preferences now describe campaigning.
- Displayed coalition leadership separately in the parliament panel and updated
  instructions. Added leadership regressions and native-engine assertions.
- Left every focus-tree file unchanged.

## Executive display integration

- Adopted TFR's Germany-style president and head-of-government presentation.
  Kaljulaid/Karis occupy the main portrait; the parliament selects the PM in the
  locked head-minister slot and shared diplomacy tooltip.
- Updated cabinet confirmation, caretaker, succession, occupation and restoration
  handling, including prime-minister labels in the Riigikogu interface.
- Added a reproducible shared-localization adapter preserving 139 upstream selectors.
- Repaired compact punctuation parsing in the compatibility generator, recovering
  384 missed later-file safeguards; added independent parser regressions.
- Compatibility inventory now has 11 overrides, 620 settlement safeguards and
  seven head-of-government selectors.

## 1.0.0 — implementation build

- Added seven distinct governing routes and a simulated 101-seat Riigikogu.
- Established Jüri Ratas's 2020 coalition and a separate constitutional presidency.
- Added elections, cabinet negotiations, confidence-and-supply, caretaker
  transitions, campaign decisions, AI route preferences and a dedicated panel.
- Added national cohesion, defense readiness, paid preparation and reserve recruitment.
- Added shared economic, defense, first-war, reconstruction, second-war and restoration content.
- Added seven occupation mandates, protected Northern Estonia settlements,
  occupation autonomy and restoration politics.
- Registered Estonia as a TFR content country and retained inherited global systems.
- Added persistent focus completion flags across tree switches.
- Added the missing parent no-Man-the-Guns Estonian naval OOB reference.
- Added reproducible compatibility overrides, structural checks and actual-script
  election/mechanics regression tests.
- Verified native engine startup and isolated election/meter assertions; converted
  all effect inputs to HOI4's native temporary-variable interfaces.
- Preserved annex settlement force handling with once-per-mandate cleanup.

Natural campaign, graphical and balance verification remains a release gate;
see `docs/TEST_RESULTS.md`.
