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
Kersti Kaljulaid is represented separately as the constitutional president.

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
- Nominate a prime minister, negotiate a coalition, and confirm the cabinet.
  A cabinet losing confidence becomes caretaker while negotiations or a snap
  election resolve the crisis.
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
```

On this Codex host, Python is also available at:
`C:\Users\Sten\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.

`tools/build_systems.py` and `tools/build_normal_content.py` preserve the authored
sources for their generated content. Treat the parent compatibility generator
separately: `--check` verifies hashes and output; review upstream changes before
using `--write` after a TFR update.

For a controlled startup parser check, close any existing HOI4 session and run:

```powershell
.\tools\run_engine_smoke.ps1 -ParentOnly -Seconds 180
.\tools\run_engine_smoke.ps1 -Seconds 180
```

This tool temporarily selects a clean mod configuration, launches only its own
game process, copies logs into ignored `test-output`, stops that process, and
restores the original mod-load configuration. It does **not** start or validate
a campaign. Do not use it while playing an existing game.

See [the architecture](docs/ARCHITECTURE.md), [manual test matrix](docs/TEST_MATRIX.md),
and [validation results](docs/TEST_RESULTS.md) for the implementation contracts
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

## Updating TFR

The parent remains untouched. Shared-file overrides are necessary to stop
destructive settlements **before** annexation occurs. Their upstream hashes and
individual protections are recorded in `docs/compatibility.json`.

After a TFR update, compare each overridden file against the new parent version,
review changed war/occupation assumptions, regenerate only after review, and rerun
the automated and settlement tests. Reusing stale overrides can discard upstream
fixes. The default supported baseline is 1.0.9.1c, not an unrestricted future version.

Credits: The Fire Rises team and Paradox Interactive for the referenced parent
content and game assets; Estonia's official election and government records for
the starting parliament and cabinet. Later paths are fictional game content.
