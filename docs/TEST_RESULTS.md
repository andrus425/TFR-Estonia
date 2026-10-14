# Validation results — 14 October 2026

This is an implemented **development build**, not a declaration that the public
v1 campaign matrix has passed. The pinned parent is **The Fire Rises 1.0.9.1c**.
The installed executable reports **HOI4 Operation Postern 1.19.3.0.c01a**.

## Automated source and behavior checks

| Check | Observed result |
|---|---|
| `tools/validate_mod.py` | 56 additive/override script files; 192 focuses, 53 events, 59 decisions, 921 English localization keys; **0 errors** |
| `python -m unittest discover -s tests -v` | **69 tests passed**, including 500 randomized election allocations checked against an independent integer reference |
| `tools/test_occupation_compatibility.py` | **10 structural regression tests passed** |
| `tools/patch_tfr_compatibility.py --check` | **11 reproducible overrides and 627 audited changes verified**: 620 settlement safeguards and seven head-of-government selectors |
| `tools/native_script_interface.py --check` | **0 files with legacy argument-block interfaces** |
| Portable packaging tests | Deterministic archive, exclusions, portable descriptors and metadata rejection passed as part of the 69-test suite |

The tests cover historical seats and confidence, threshold/tie behavior, invalid
poll recovery, negative and fractional inputs, inactive parties, independent
party identity, supply agreements, meter limits and tiers, economic unit conversion,
reserve authorization, programme selection, formation, initialization, campaign
stages and persistence through tree changes.

The 19 leadership-mandate regressions cover the historical Centre exception,
all seven election winners, tied largest delegations, invalid elections,
minority winners waiting for 51 confidence votes, blocked legacy nominations,
fabricated nominees, confidence recovery without replacing the incumbent,
AI preferences respecting the election result, polling without seat changes,
missing-variable repair from the saved PM, protected leader membership,
occupation/restoration continuity and explicit story authorization. All three
focus-tree files retain their pre-revision SHA-256 hashes; the two Estonia
trees also have an automated preservation check.

Nine dynamic-modifier tests cover the two neutral containers and their 16
independent variable bindings, preservation of positive/negative authored values,
repair without reapplying present modifiers, repeated initialization, EST scope
guards, unchanged existing idea rewards, retained parent modifiers and all three
focus-tree hashes. The static validator now checks dynamic-modifier references,
localization and icon sprites.

Executive tests cover valid confirmation of all seven PMs without changing the
president, caretaker continuity, immediate Karis succession, occupation hiding,
restoration, repeat-safe display repair, locked minister slots and explicit
ideology selection when promoting multi-role presidential characters. The shared
localization adapter preserves all 139 upstream selectors. Independent parser
tests verify all upstream script trees, retained annex actions and parent story
dispatches, including compact punctuation and late-file Estonia paths.

The tokenizer repair recovered 384 safeguards previously omitted after compact
`NOT ={` syntax. The compatibility manifest contains the expanded inventory;
live settlement acceptance remains open.

Settlement checks compare actual generated scripts with upstream semantics.
They cover guarded explicit and dynamic annexation, the retained anchor, partition
remainders, original non-Estonia annex actions, parent war flags and follow-up
events, autonomy restrictions, once-per-mandate force cleanup, all seven occupation
gates and repeat-safe repair. They do not execute combat or a live peace conference.

## Native engine observations

The earlier implementation run is captured locally under
`test-output/engine-estonia-qa-20261013-095041/`.
It loaded TFR, Estonia and an isolated arithmetic QA overlay, reached the frontend
in approximately **101 seconds**, and passed all seven native assertions:

1. Historical assembly and the 57-seat Ratas coalition.
2. Equal polling allocates 51/50 according to the fixed tie order.
3. Exactly 5% qualifies; 4.99% is excluded; the total is 101 seats.
4. Invalid polling preserves the prior assembly.
5. Seven equal qualifying parties allocate the remainders correctly.
6. Occupation suspends election allocation.
7. Cohesion/readiness changes clamp to 0/100 using native temporary inputs.

The TFR-only comparison run is captured under
`test-output/engine-parent-20261013-095435/` and reached the frontend in
approximately **111 seconds**. The smoke-test processes were stopped and the
original mod/DLC configuration was restored byte-for-byte after each run.

`tools/compare_engine_logs.py` compared the two captured error logs after removing
timestamps and source line numbers. Both contained **2,062 unique parent error
messages**, with **0 new unique messages**, **0 removed messages**, and **0 messages
containing the new `TFR_EST_` or `tfr_estonia` identifiers**. This establishes
startup parity with this parent build; it does not make the parent error-free.
The compact comparison is saved locally as `test-output/final-engine-comparison.json`.

The 13 October executive-display run is captured under
`test-output/engine-estonia-qa-20261013-123825/`. It reached the frontend in about
154 seconds and passed **all 19 native assertions**, comprising the seven earlier
arithmetic cases and 12 executive cases: the opening Kaljulaid/Ratas pairing,
each of the seven PM identities across five ruling ideology groups, the Karis
handover, caretaker continuity, occupation hiding and restoration of the saved
executive. These occupation/restoration cases exercise display effects and ledger
suspension only, without invoking diplomatic settlements or unit transfers.

The successful run contains **no errors naming `TFR_EST_` or `tfr_estonia`**.
Comparison with the earlier parent baseline found eight additional missing
nationalist flag messages for GBA, KHA, LBV, ORO, PAP, SID, SPM and TOS. They
reference parent flag assets; the reason for their additional loading was not
isolated. They are recorded rather than counted as resolved or silently ignored.
The comparison is `test-output/executive-engine-comparison.json`.

An initial executive QA run failed because `promote_character` requires an
explicit ideology for characters with several leader roles. The implementation
now supplies the appropriate sub-ideology in all five government groups, and
both static checks and a regression prevent reintroducing the ambiguous call.
The later 19-case run is the accepted result.

The election-led coalition run is captured under
`test-output/engine-estonia-qa-20261014-111641/`. It reached the frontend in
approximately **192 seconds** and passed **all 26 native assertions**. It repeats
the 19 arithmetic/executive checks and adds seven leadership cases: unauthorized
nomination does nothing, a fabricated nominee is rejected, AI confidence recovery
keeps Centre, equal largest delegations use the fixed tie order, a minority winner
waits for confidence, the elected successor can be confirmed, and an invalid
subsequent election preserves the confirmed leader. The original mod/DLC
configuration was restored after the owned process stopped.

The first 14 October QA fixture passed 25 of 26 cases. During frontend history
construction Estonia is AI-controlled, so its actual election effect immediately
formed an 80-seat Reform–Centre coalition and confirmed Reform. The corrected
fixture logs `pm=1 confidence=80 centre=1` before reconstructing the pending
player cabinet from the actual elected 40/40/21 assembly. This tests native
confirmation below 51 and after adding support without mistaking automatic AI
formation for a player handover failure. The source regression separately follows
the unmodified player election effect. No gameplay exception was added for QA.

The successful 26-case log contains **no errors naming `TFR_EST_` or
`tfr_estonia`**. The same-day parent-only run,
`test-output/engine-parent-20261014-112136/`, reached the frontend in about
173 seconds with the same DLC selection. After normalization it contains 2,023
unique messages, versus 2,033 in the submod/QA run. The ten additional messages
all reference missing foreign nationalist flag assets: medium flags for GBA,
KHA, LBV, ORO, PAP, SID, SPM, TOS and VGE, plus SPM's small flag. There are no
removed messages. Their additional loading is not isolated; this is not an
error-free startup claim. The report is
`test-output/mandate-engine-comparison-current.json`. The larger asset differences
from the previous day's capture are not attributed to the parliament change.

The latest dynamic-modifier run is captured under
`test-output/engine-estonia-qa-20261014-114230/`. It reached the frontend in
approximately **175 seconds** and passed **all 30 native assertions**: the prior
26 cases plus neutral installation, actual modifier-value application,
preservation during repeated initialization, and repair of a removed container.
Reading native `modifier@industrial_capacity_factory` before and after changing
its backing variable produced a delta of `0.03`; the corresponding supply
consumption test produced `-0.05`. Test adjustments were returned to zero after
the checks. The isolated fixture is not part of the ordinary mod.

Comparison with the same-day parent-only baseline gives **2,023 normalized unique
messages in both runs, zero new messages, zero removed messages, and zero messages
containing `TFR_EST_` or `tfr_estonia`**. The comparison report is
`test-output/dynamic-engine-comparison.json`. This establishes startup parity for
this run without claiming the parent is error-free. The original mod/DLC
configuration was restored after the owned test process stopped. It does not
verify rendered icons, natural daily scheduling or save/reload in a campaign.

The QA overlay is not shipped or enabled in ordinary play. It executes arithmetic
within a single hidden-effect context during frontend history construction.
Temporary input and consumer statements must remain in the same context.

An earlier experiment invoking occupation/diplomatic transitions during country
history construction crashed before reaching the frontend. That fixture was
removed. A history-time crash does not establish whether a live campaign
settlement succeeds; protected occupations still require the active-campaign
checks below. Earlier failed or incomplete runs remain in ignored local test
outputs and are not counted as passes.

## Acceptance checks still open

No ordinary campaign was started by the smoke-test tool. Native application UI
control is unavailable in this environment, so rendered interface acceptance and
interactive campaign observations were not performed.

- Ordinary campaigns for all seven parties, including legitimate route entry.
- Every supported Russian and European defeat settlement in a running campaign,
  with original force handling, a second defeat and restoration.
- Parent pacification/integration and both-war progression under protected EST.
- Save/reload around elections, delayed settlements and restoration.
- AI research, production, recruitment, coalition behavior and focus progression.
- DLC combinations, UI scales, full text/tooltip display and actual focus layout.
- Long-term economy, preparation, military growth and occupation balance.
- Custom portraits for characters currently using generic likenesses, plus actual
  campaign screenshots for a public Workshop release.

Use [the manual matrix](TEST_MATRIX.md) to record these observations. Public v1
acceptance requires completing that matrix; successful source, startup and
isolated arithmetic tests are the current evidence.

## Reproduction

Run the source checks in the README. Close any active HOI4 session before using
the smoke-test tool. Prepare the isolated fixture with
`python tools/prepare_engine_qa.py`, then run
`tools/run_engine_smoke.ps1 -ArithmeticQA -Seconds 600`. Use `-ParentOnly` for
the clean baseline. The tool stops early on frontend completion and checks every
expected QA assertion. Compare captured logs with `tools/compare_engine_logs.py`.

Rebuild the ZIP after changing documentation or source, then use
`python tools/package_mod.py --check` to verify it exactly matches current inputs.
The archive manifest records each packaged file's byte size and SHA-256 hash.
