# Party ideology artwork

Twelve original, reference-derived icons cover all seven parties and every
leader variant supported by the current political ledger. Each combines a
recognizable leader bust, the party palette and emblem, flowing fabric, charcoal
metalwork and silver edge highlights. TFR's portrait-based Argentine/Turkish
social-democracy icons and British/Ukrainian party collages guided the style.
All artwork was generated separately with the built-in **image_gen** tool on
23 October 2026. No CLI/API fallback was used.

## Runtime artwork and selection

| Party | Supported leader artwork | Palette and symbol |
|---|---|---|
| EKRE | Mart Helme; Martin Helme | Cornflower blue, black and white; blue cornflower |
| Centre | Jüri Ratas; Tanel Kiik; Mihhail Kõlvart | Emerald green and white; four-leaf clover |
| Isamaa | Helir-Valdor Seeder | Cyan blue and white; hollow eight-pointed star |
| Reform | Kaja Kallas; Kristen Michal | Yellow and ultramarine; sweeping squirrel silhouette |
| SDE | Indrek Saar; Lauri Läänemets | Red and white; angular rose with small green stem |
| Eesti 200 | Kristina Kallas | Historical indigo-purple and white; joined tilted 200 blocks |
| Parempoolsed | Lavly Perling | Orange and charcoal; two rounded right-pointing triangles |

`gfx/interface/ideologies/EST/{id}.png` contains the twelve final **66 × 68 RGBA
PNGs**. `interface/TFR_EST_ideology_icons.gfx` registers their unique sprites.
The diplomacy view displays the incumbent PM's party and likeness, including
an outgoing caretaker. The Riigikogu panel adds seven approximately 22 × 23
icons that follow each party chair, including changes in opposition. Centre
and SDE can therefore show different parliamentary-chair and serving-PM
portraits during a handover. Reform/Parempoolsed and Centre/Eesti 200 stay
visually distinct despite sharing native ideology categories.

The integration uses additive scripted GUI containers and scripted localisation.
It preserves the president, native ideology definitions and all gameplay effects.
Other countries and occupied/subject Estonia keep the inherited interface.
The diplomacy overlay redraws the installed TFR window background inside its
66 × 68 clipping area beneath the transparent artwork; no parent GUI or art
file is copied into the runtime mod.

## Masters, prompts and export

- [Native-size review sheet](contact_sheet_1x.png) and [4× review sheet](contact_sheet_4x.png).
- [Exact per-icon prompts and reference roles](prompts.json).
- [Asset mapping, sizes and SHA-256 hashes](manifest.json).
- Full-resolution generated masters: `docs/artwork/ideology/masters/{id}.png`.
- [Leader reference metadata](leader_reference_sources.json) and [party sources](party_reference_sources.json).

The shared prompt asks for one compact TFR ideology collage with a large
photo-painted leader bust, prominent party emblem, party-colored banner,
charcoal backing and silver bevels, readable at 66 × 68. It supplies the style
sheet, named portrait and, where needed, the exact party mark as reference-only
inputs. The outside is actual transparent alpha. No captions are generated;
Eesti 200 retains the identifying digits inside its emblem.

Run `python tools/export_ideology_artwork.py` to reproduce runtime PNGs and
review sheets. Run `python tools/export_ideology_artwork.py --check` to verify
all runtime pixels against the masters without writing. The only export
operations are transparent-margin trimming, proportional Lanczos resizing and
transparent padding; no creative image changes are performed by the exporter.

The original source photos, downloaded logos and copied parent style sheet
remain local research inputs. `tools/package_mod.py` excludes both minister
photo references and `docs/artwork/ideology/references/`; the ignored `.cache/`
is excluded too. Generated masters, final icons, prompts and credits are retained.
Reference sheets can be reproduced with `tools/prepare_ideology_references.py`.

## Party visual identity sources

The period palette follows [EKRE symbolism](https://www.ekre.ee/sumboolika/),
[Centre's media register](https://keskerakond.ee/erakonnast/meediale/),
[Isamaa's 2018 logo guide](https://isamaa.ee/iwp/wp-content/uploads/2018/12/Isamaa-logo-1.pdf),
[Reform's official squirrel](https://reform.ee/wp-content/uploads/2021/11/RE_profiil_logod_orav.png),
[SDE's 2017 rose](https://www.sotsid.ee/wp-content/uploads/2017/07/logo17-sde-rbg.png),
and [Parempoolsed's 2023 style guide](https://parempoolsed.ee/stiiliraamat/).
Eesti 200 uses its [2021–2023 original party logo](https://commons.wikimedia.org/wiki/File:Eesti_200_Logo.svg)
and indigo #2F2A95, rather than the later identity on its current website.
Party emblems remain the marks of their respective parties. These generated
portraits are game artwork and do not depict an endorsement by their subjects.

## Validation

All twelve runtime exports decode and match their masters, including dimensions
and transparent corners. Native-size and 4× sheets were visually reviewed.
Eight icon selection/UI regressions, four scripted-image validation regressions
and three package regressions pass. The mod validator reports zero errors and
the pinned parent compatibility check passes. The full source-suite snapshot
had separate 2023 focus-art generator mismatches in work changing concurrently;
the details are recorded in [validation results](../../TEST_RESULTS.md).
The game was not launched to verify actual layering, tooltips or UI scaling.

## Leader photo credits

The original photos were retained unchanged as reference inputs. Imagegen
re-rendered the likenesses with party lighting, new clothing treatment,
compositing, symbols and transparent backgrounds; export adds a small resize.
These are AI-generated artworks derived from the listed references, rather
than unmodified historical photos. Attribution and any applicable share-alike
terms remain attached to the corresponding reference-derived assets. Unstated
source terms are retained as such in the register.

| Person | Reference | Photographer / credit | Date | Source license |
|---|---|---|---|---|
| Mart Helme | [Source portrait](https://commons.wikimedia.org/wiki/File:RK_Mart_Helme.jpg) | Erik Peinar | 2015-03-30 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Martin Helme | [Source portrait](https://valitsus.ee/vabariigi-valitsuse-50-koosseis) | Renee Altrov / Riigikantselei | Not stated | Reference only; rights retained by institution/photographer |
| Jüri Ratas | [Source portrait](https://commons.wikimedia.org/wiki/File:J%C3%BCri_Ratas_2017-05-25_(cropped).jpg) | 2017 Estonian Presidency of the Council of the European Union | 2017-05-25 06:20 | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0) |
| Tanel Kiik | [Source portrait](https://commons.wikimedia.org/wiki/File:Tanel_Kiik_(crop).jpg) | Renee Altrov | 2021-01-25 12:14:45 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Mihhail Kõlvart | [Source portrait](https://commons.wikimedia.org/wiki/File:Mihhail_K%C3%B5lvart_P%C3%A4tsi_monumendi_avamisel._2022_(cropped).jpg) | Jaan Künnap | 2022-10-21 14:18:41 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Helir-Valdor Seeder | [Source portrait](https://commons.wikimedia.org/wiki/File:Helir-Valdor_Seeder_2016.jpg) | Saeima | 2016-10-28 11:20 | [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0) |
| Kaja Kallas | [Source portrait](https://commons.wikimedia.org/wiki/File:Kaja_Kallas_(crop).jpg) | Renee Altrov | Taken on 25 January 2021 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Kristen Michal | [Source portrait](https://commons.wikimedia.org/wiki/File:Kristen_Michal_2023_(cropped).jpg) | Alexandros Michailidis - Council of the European Union | 2023-12-18 | Attribution |
| Indrek Saar | [Source portrait](https://www.riigikogu.ee/riigikogu/riigikogu-liikmed/58378026-b797-4bf2-89fc-31a73d9219b3/saadik/) | Chancellery of the Riigikogu | XIV Riigikogu profile, 2019-2023 | Not stated on retrieved profile; retained as visual reference |
| Lauri Läänemets | [Source portrait](https://commons.wikimedia.org/wiki/File:Lauri_L%C3%A4%C3%A4nemets_at_the_Opinion_Festival_2022_in_Paide,_Estonia_(cropped).jpg) | Sillerkiil | 2022-08-13 12:10:04 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Kristina Kallas | [Source portrait](https://commons.wikimedia.org/wiki/File:Kristina_Kallas_KF_(cropped).jpg) | Metsavend | 2018-11-06 15:04:19 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Lavly Perling | [Source portrait](https://commons.wikimedia.org/wiki/File:Lavly_Perling_2021-10-14_(cropped).jpg) | Estonian Foreign Ministry | 2021-10-14 | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0) |
