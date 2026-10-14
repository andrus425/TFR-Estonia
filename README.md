# TFR Estonia

An Estonia country expansion for **The Fire Rises 1.0.9.1c / Hearts of Iron IV 1.19.\***.

This implementation includes the seven governing parties, a 101-seat Riigikogu,
national cohesion and defense readiness, both European-war campaign stages,
and playable occupation administrations. Start a **new 2020 campaign**; saves
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
- Regular elections begin in March 2023 and repeat every four years. Restored
  independence triggers an election within 90 days.
- The dedicated Riigikogu panel shows polling, seats, cabinet membership,
  supply agreements and the election calendar. TFR's ideology chart is a
  compatibility view; it is not the source of seats or confidence votes.

Government programme focuses become available to the current party in office.
An election can open a different programme. Completed policies remain recorded,
and active cabinet bonuses reconcile with the current government.

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
without resetting saved adjustments. Existing focus rewards still grant their
original ideas; their conversion will accompany a later content revision.

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
```

On this Codex host, Python is also available at:
`C:\Users\Sten\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.

`tools/build_systems.py` and `tools/build_normal_content.py` preserve the authored
sources for their generated content. Treat the parent compatibility generator
separately: `--check` verifies hashes and output; review upstream changes before
using `--write` after a TFR update.

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

The submod references installed TFR and base-game assets. The new prime ministers
and some occupation administrators currently use existing **generic portraits**;
they are named and scripted characters, but these are not custom likenesses.
No external photographs, music or TFR artwork are bundled.

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
selector and adds Estonia's seven party-ledger selectors. The shared GUI itself
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
