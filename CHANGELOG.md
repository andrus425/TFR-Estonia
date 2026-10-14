# Changelog

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
