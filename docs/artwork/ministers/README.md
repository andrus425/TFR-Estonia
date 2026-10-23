# Minister artwork register

48 distinct people have individual artwork: all 38 portfolio nominees and ten
additional prime ministers. Mart Helme and Martin Helme share the same likeness
between their portfolio and prime-minister displays. The portfolio roster has
39 candidacies because Mart Helme can be selected for either of two offices.

The built-in **image_gen** tool produced each portrait separately from a named
photo reference. No CLI/API fallback was used. The original reference photos
were not modified. Every generated image was checked for likeness and framed
composition, then technically resized with .NET System.Drawing.

## Files and game integration

- `gfx/interface/ideas/EST/ministers/{person}.png`: 48 final 62 × 67 RGBA icons.
- `gfx/leaders/EST/ministers/{person}.png`: 12 separate 156 × 210 prime-minister
  tooltip canvases; the framed image is fitted without stretching.
- `docs/artwork/ministers/masters/{person}.png`: full-resolution generated PNGs.
- [All exact prompts](prompts.json) and [machine-readable sources](sources.json).
- [Game-size contact sheet](contact_sheet_1x.png) and [2× contact sheet](contact_sheet_2x.png).

`tools/build_ministers.py` generates both minister sprite registers. Head-minister
ideas select the `_icon` sprites. Both these aliases and the direct
`GFX_idea_TFR_EST_pm_*` sprites use the 62 × 67 icons, since the cabinet can
resolve a direct idea-ID sprite before its explicit picture alias. Shared
tooltips use separate `GFX_TFR_EST_hog_portrait_*` sprites for the 156 × 210
canvases. Appointment and cabinet logic are unaffected.

Run `./tools/export_minister_artwork.ps1` to export saved masters and refresh the
contact sheets. Run it with `-Check` to decode and verify every runtime PNG,
dimensions, transparent outside corners and opaque portrait center without
writing. Run `python tools/build_ministers.py --check` to check sprite generation.

## Style and generation prompt

The supplied TFR style guide covers focus icons and other interface assets.
The actual minister style and 62 × 67 dimensions were checked directly against
the parent mod's German minister icons, especially `Heiko Maas.png`, and other
portraits including Scholz, Seehofer and Baerbock. The targets use a thin tilted
gunmetal frame, cool silver highlights, a lavender vignette, muted photographic
color and subtle horizontal scanlines. The frame and person were generated
together with a true transparent outside margin.

The common prompt specification was: transform the named photo into one TFR
minister icon; preserve recognizable facial identity, hair, age, expression and
eyewear; use a tight head-and-shoulders crop, whole hair and chin, muted purple
background, photo-based painted treatment, fine scanlines, thin gunmetal frame
tilted about four degrees counterclockwise and transparent outside; no text,
flags, extra people or symbols. Exact per-person prompts and reference roles
are in `prompts.json`.

## Reference credits

Validation on 22 October 2026: all 48 icons and 12 tooltip canvases decoded and
passed dimension/alpha checks; all 39 candidacy mappings and 12 PM sprite pairs
resolved correctly; source, prompt and master coverage matched all 48 people;
the release inputs include the artwork and credits and exclude original photos.
The full Python suite passed 663 tests, `build_ministers.py --check` passed, and
`validate_mod.py` reported zero errors. Contact sheets were visually reviewed at
native and 2× size. A running-game visual inspection was not performed.

On 23 October 2026, the reported oversized prime-minister cabinet icon was
traced to the direct idea-ID sprite resolving the large tooltip image. All
twelve direct sprites now use 62 × 67 icons, and tooltip localization uses the
separate portrait namespace. Both lookup paths and all tooltip PNG dimensions
are covered by regressions. The 104 relevant display, minister and leadership
tests and all four affected generator checks pass; the mod validator reports
zero errors. The correction still requires visual confirmation after restarting
the game and loading the existing save.

The table records the photo used for each likeness, rather than claiming the
generated icon is an original historical photograph. Source dates vary; the
2020–2024 alternate-history ministers use available identifiable portraits.
Where a source did not state a license, that uncertainty is retained. Downloaded
photos remain local research inputs under `references/` and are excluded from
release ZIPs by `tools/package_mod.py`; this credit register remains included.
For source photos carrying a Creative Commons license, attribution and the
license link are retained here; AI style transfer, background replacement,
crop, framing and color changes are explicitly indicated above. Share-alike
terms on source-derived artwork remain attached to the corresponding assets.

| Person | Photo source | Photographer / credit | Photo date | Source license |
|---|---|---|---|---|
| Alar Laneman | [Reference photo](https://valitsus.ee/vabariigi-valitsuse-50-koosseis) | Official institutional portrait; individual photographer not listed in page image alt text | Not stated | Reference only; rights retained by institution/photographer |
| Andres Anvelt | [Reference photo](https://commons.wikimedia.org/wiki/File:Andres_Anvelt.jpg) | Sotsiaaldemokraatlik Erakond | 2014-10-12 12:15:33 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Ants Frosch | [Reference photo](https://www.riigikogu.ee/en/parliament-of-estonia/members-of-the-riigikogu/c4e3fc0f-80fb-4a3e-b49e-80045c5253d9/ants-frosch/) | Official institutional portrait; individual photographer not listed in page image alt text | Not stated | Reference only; rights retained by institution/photographer |
| Eerik-Niiles Kross | [Reference photo](https://commons.wikimedia.org/wiki/File:RK_Eerik-Niiles_Kross.jpg) | Erik Peinar | 2015-05-06 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Enn Eesmaa | [Reference photo](https://commons.wikimedia.org/wiki/File:RK_Enn_Eesmaa.jpg) | Erik Peinar | 2015-03-30 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Hanno Pevkur | [Reference photo](https://commons.wikimedia.org/wiki/File:Hanno_Pevkur_2017.jpg) | Jarek Jõepera | 2017-05 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Helir-Valdor Seeder | [Reference photo](https://commons.wikimedia.org/wiki/File:Helir-Valdor_Seeder_2016.jpg) | Saeima | 2016-10-28 11:20 | [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0) |
| Igor Taro | [Reference photo](https://www.riigikogu.ee/riigikogu/riigikogu-liikmed/642e6a9e-8123-4b1d-bbdd-a58a4be0f1fa/igor-taro/) | Riigikogu official member portrait | Not stated | Not stated on retrieved profile; retained as visual reference |
| Ilmar Raag | [Reference photo](https://www.parempoolsed.ee/riigikogu-valimised-2023/haabersti-pohja-tallinn-ja-kristiine/) | Parempoolsed candidate portrait, January 2023 | Not stated | Not stated on retrieved profile; retained as visual reference |
| Indrek Saar | [Reference photo](https://www.riigikogu.ee/riigikogu/riigikogu-liikmed/58378026-b797-4bf2-89fc-31a73d9219b3/saadik/) | Chancellery of the Riigikogu | XIV Riigikogu profile, 2019-2023 | Not stated on retrieved profile; retained as visual reference |
| Ivari Padar | [Reference photo](https://commons.wikimedia.org/wiki/File:Ivari_Padar_MEP_01.JPG) | Bengt Oberger | 2014-02-05 18:04:29 | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |
| Jaak Aab | [Reference photo](https://commons.wikimedia.org/wiki/File:Jaak_Aab_(crop).jpg) | Renee Altrov | 2021-01-25 13:29:44 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Jaak Madison | [Reference photo](https://ecrgroup.eu/ecr/mep/jaak_madison) | European Conservatives and Reformists Group official portrait | Not stated | Not stated on retrieved profile; retained as visual reference |
| Jürgen Ligi | [Reference photo](https://commons.wikimedia.org/wiki/File:J%C3%BCrgen_Ligi.jpg) | Kaupo Kikkas | 2012-06-19 | [CC BY 3.0 ee](https://creativecommons.org/licenses/by/3.0/ee/deed.en) |
| Jüri Luik | [Reference photo](https://valitsus.ee/vabariigi-valitsuse-50-koosseis) | Renee Altrov / Riigikantselei | Not stated | Reference only; rights retained by institution/photographer |
| Jüri Ratas | [Reference photo](https://commons.wikimedia.org/wiki/File:J%C3%BCri_Ratas_2017-05-25_(cropped).jpg) | 2017 Estonian Presidency of the Council of the European Union | 2017-05-25 06:20 | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0) |
| Kaja Kallas | [Reference photo](https://commons.wikimedia.org/wiki/File:Kaja_Kallas_(crop).jpg) | Renee Altrov | Taken on 25 January 2021 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Kalev Stoicescu | [Reference photo](https://www.riigikogu.ee/riigikogu/riigikogu-liikmed/987e47c7-929b-4437-9385-fab4f4fd7824/grigore-kalev-stoicescu/) | Riigikogu official member portrait | Not stated | Not stated on retrieved profile; retained as visual reference |
| Kalle Klandorf | [Reference photo](https://commons.wikimedia.org/wiki/File:Klandorf,_Kalle.IMG_1109.JPG) | Ave Maria Mõistlik | 2013-09-25 | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |
| Kalle Laanet | [Reference photo](https://commons.wikimedia.org/wiki/File:Kalle_Laanet_2021_(crop).jpg) | Renee Altrov | 2021-01-25 18:49:26 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Katri Raik | [Reference photo](https://commons.wikimedia.org/wiki/File:Kadri_Raik_teisel_Arvamusfestivalil_Narvas.jpg) | Ülo Veldre | 2016-05-21 12:25:36 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Kristen Michal | [Reference photo](https://commons.wikimedia.org/wiki/File:Kristen_Michal_2023_(cropped).jpg) | Alexandros Michailidis - Council of the European Union | 2023-12-18 | Attribution |
| Kristina Kallas | [Reference photo](https://commons.wikimedia.org/wiki/File:Kristina_Kallas_KF_(cropped).jpg) | Metsavend | 2018-11-06 15:04:19 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Kristjan Vanaselja | [Reference photo](https://www.parempoolsed.ee/vabadust/kandidaadid/kristjan-vanaselja/) | Parempoolsed candidate portrait, April 2024 | Not stated | Not stated on retrieved profile; retained as visual reference |
| Lauri Läänemets | [Reference photo](https://commons.wikimedia.org/wiki/File:Lauri_L%C3%A4%C3%A4nemets_at_the_Opinion_Festival_2022_in_Paide,_Estonia_(cropped).jpg) | Sillerkiil | 2022-08-13 12:10:04 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Lavly Perling | [Reference photo](https://commons.wikimedia.org/wiki/File:Lavly_Perling_2021-10-14_(cropped).jpg) | Estonian Foreign Ministry | 2021-10-14 | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0) |
| Leo Kunnas | [Reference photo](https://commons.wikimedia.org/wiki/File:Leo_Kunnas.jpg) | Erik Peinar | 2019-03-19 10:33:17 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Liisa-Ly Pakosta | [Reference photo](https://www.riigikogu.ee/riigikogu/riigikogu-liikmed/289fc421-d890-4401-ba74-4dc6813f0403/saadik/) | Riigikogu official member portrait | Not stated | Not stated on retrieved profile; retained as visual reference |
| Margus Tsahkna | [Reference photo](https://www.valitsus.ee/peaminister-ministrid/valisminister-margus-tsahkna) | Government of Estonia | Not stated | Not stated on retrieved profile; retained as visual reference |
| Marina Kaljurand | [Reference photo](https://commons.wikimedia.org/wiki/File:V%C3%A4lisminister_Marina_Kaljurand_(25528444880)_(cropped2).jpg) | Estonian Foreign Ministry | 2015-07-15 12:19 | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0) |
| Marko Pomerants | [Reference photo](https://commons.wikimedia.org/wiki/File:IRL_Marko_Pomerants.jpg) | Albert Truuväärt | 2011-04-19 | [CC BY 3.0](https://creativecommons.org/licenses/by/3.0) |
| Mart Helme | [Reference photo](https://commons.wikimedia.org/wiki/File:RK_Mart_Helme.jpg) | Erik Peinar | 2015-03-30 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Martin Helme | [Reference photo](https://valitsus.ee/vabariigi-valitsuse-50-koosseis) | Renee Altrov / Riigikantselei | Not stated | Reference only; rights retained by institution/photographer |
| Mihhail Kõlvart | [Reference photo](https://commons.wikimedia.org/wiki/File:Mihhail_K%C3%B5lvart_P%C3%A4tsi_monumendi_avamisel._2022_(cropped).jpg) | Jaan Künnap | 2022-10-21 14:18:41 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Rainer Saks | [Reference photo](https://www.parempoolsed.ee/vabadust/kandidaadid/rainer-saks/) | Parempoolsed candidate portrait, April 2024 | Not stated | Not stated on retrieved profile; retained as visual reference |
| Raivo Aeg | [Reference photo](https://valitsus.ee/vabariigi-valitsuse-50-koosseis) | Official institutional portrait; individual photographer not listed in page image alt text | Not stated | Reference only; rights retained by institution/photographer |
| Rene Kokk | [Reference photo](https://www.riigikogu.ee/riigikogu/riigikogu-liikmed/694b084f-e151-4f7e-8a5c-2664a40cee7a/rene-kokk/) | Riigikogu official member portrait | Not stated | Not stated on retrieved profile; retained as visual reference |
| Siim-Valmar Kiisler | [Reference photo](https://www.parempoolsed.ee/volikogu/) | Parempoolsed council portrait, April 2022 | Not stated | Not stated on retrieved profile; retained as visual reference |
| Sven Mikser | [Reference photo](https://commons.wikimedia.org/wiki/File:Sven_Mikser_2017-05-25_(cropped).jpg) | 2017 Estonian Presidency of the Council of the European Union | 2017-05-25 06:20 | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0) |
| Sven Sester | [Reference photo](https://commons.wikimedia.org/wiki/File:IRL_Sven_Sester.jpg) | Albert Truuväärt | 2011-04-19 | [CC BY 3.0](https://creativecommons.org/licenses/by/3.0) |
| Taavi Aas | [Reference photo](https://commons.wikimedia.org/wiki/File:Taavi_Aas_2017_(cropped_2).jpg) | Aron Urb | 2017-07-03 | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0) |
| Tanel Kiik | [Reference photo](https://commons.wikimedia.org/wiki/File:Tanel_Kiik_(crop).jpg) | Renee Altrov | 2021-01-25 12:14:45 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Tiit Naber | [Reference photo](https://www.parempoolsed.ee/riigikogu-valimised-2023/haabersti-pohja-tallinn-ja-kristiine/) | Parempoolsed candidate portrait, January 2023 | Not stated | Not stated on retrieved profile; retained as visual reference |
| Tiit Riisalo | [Reference photo](https://valitsus.ee/tiit-riisalo) | Government of Estonia | Not stated | Not stated on retrieved profile; retained as visual reference |
| Tiit Terik | [Reference photo](https://commons.wikimedia.org/wiki/File:Tiit_Terik_KOV2017_(cropped).jpg) | Pealinnast | 2017-05-19 | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0) |
| Trivimi Velliste | [Reference photo](https://commons.wikimedia.org/wiki/File:2016-08-29_BSPC_Trivimi_Velliste_by_Olaf_Kosinsky-2.jpg) | Olaf Kosinsky | 2016-08-29 15:38:36 | [CC BY-SA 3.0 at](https://creativecommons.org/licenses/by-sa/3.0/at/deed.en) |
| Urmas Paet | [Reference photo](https://commons.wikimedia.org/wiki/File:Portrait_Urmas_Paet.jpg) | Kaupo Kikkas | 2012-06-19 | [CC BY 3.0 ee](https://creativecommons.org/licenses/by/3.0/ee/deed.en) |
| Urmas Reinsalu | [Reference photo](https://commons.wikimedia.org/wiki/File:Urmas_Reinsalu.jpg) | EU2017EE Estonian Presidency | 2017-07-06 13:59:33 | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0) |
