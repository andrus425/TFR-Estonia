# Changelog

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

## 15 October 2026 — freely ordered coalition policies

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
