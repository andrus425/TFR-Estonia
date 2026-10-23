# Post-2023 focus artwork

The seven authored government programmes contain 224 focuses: 32 per tree.
Every focus has a separately generated composition, its own PNG texture and its
own base/shine sprite pair. No focus shares an artwork texture with another.

The icons follow the supplied TFR reference: photographic cutouts, dark
contours, metallic highlights and concentrated party-colored lighting. The
coalition leader's palette applies throughout its tree, including shared policy
subjects. Selected formation, signature-policy and accountability icons include
the programme's named politicians and party emblems.

| Programme | Main palette | Portrait subjects | Review |
| --- | --- | --- | --- |
| Reformierakond | Yellow, ultramarine | Kaja Kallas, Kristen Michal | [32 icons](reform/reform-icons-preview.png), [tree](reform/reform-tree-preview.png) |
| EKRE | Cornflower blue, silver | Martin Helme | [32 icons](ekre/ekre-icons-preview.png), [tree](ekre/ekre-tree-preview.png) |
| Keskerakond | Emerald green, silver | Jüri Ratas, Tanel Kiik, Mihhail Kõlvart | [32 icons](centre/centre-icons-preview.png), [tree](centre/centre-tree-preview.png) |
| Isamaa | Cyan blue, navy, gold | Helir-Valdor Seeder | [32 icons](isamaa/isamaa-icons-preview.png), [tree](isamaa/isamaa-tree-preview.png) |
| SDE | Red, silver | Lauri Läänemets | [32 icons](sde/sde-icons-preview.png), [tree](sde/sde-tree-preview.png) |
| Eesti 200 | Period indigo-purple, silver | Kristina Kallas | [32 icons](e200/e200-icons-preview.png), [tree](e200/e200-tree-preview.png) |
| Parempoolsed | Orange, charcoal, silver | Lavly Perling | [32 icons](pp/pp-icons-preview.png), [tree](pp/pp-tree-preview.png) |

[Selected icons from all seven programmes](seven-governments-preview.png)
are shown at their native game size. The tree previews use the authored focus
coordinates and prerequisites; they are review images, not game screenshots.
Portrait selection follows the mod's alternate political paths. In particular,
the Isamaa programme uses Seeder and Eesti 200's programme uses Kristina Kallas.

## Sources and retained work

All artwork was created with the built-in `image_gen.imagegen` tool. Each
generation request produces one complete icon. Each party directory contains:

- `manifest.json`: exact generation prompts, focus identities, palette and
  portrait choices, master/texture paths, export bounds and SHA-256 hashes.
- `masters/`: the original full-resolution generated PNGs.
- `records/`: durable per-image export and provenance records.
- The icon contact sheet and focus-tree layout preview linked above.

When review requires a correction, the selected master receives a versioned
filename. The manifest retains the exact edit prompt and previous draft's
master, runtime copy and export metadata. The current 224 runtime textures
remain one-to-one with their focuses.

[`catalog.json`](catalog.json) maps every focus to one asset. The seven programme
generators read this catalog through `tools/post2023_focus_art.py`, which rejects
shared assignments. They generate the base sprites and TFR's two-pass shine
variants together with the focus definitions.

[`reference_sources.json`](reference_sources.json) records the public party-logo
and portrait sources used for visual reference. Reference photos and assembled
research sheets stay in the ignored local cache. The shipped artwork consists
of generated compositions; original TFR icons and research photos are not
included in this set.

## Mechanical export

Runtime textures live in `gfx/interface/goals/EST/`, named
`EST_<party>_2023_<asset>.png`. They are 170 × 150 RGBA PNGs. The bottom 40 rows
are entirely transparent for the focus label. The exporter trims transparent
master padding at alpha > 1, fits the artwork within 168 × 108 using Lanczos3,
and centers it in the top 110 rows. It does not draw, recolor or compose artwork.

With Node.js and `sharp` available, run:

```text
node tools/export_post2023_focus_art.cjs --check
```

The check requires all 224 records and verifies unique texture hashes, one focus
per asset, dimensions, alpha clearance, master/texture hashes and byte-identical
exports from the retained masters. Running without `--check` also refreshes
manifest metadata and the review images. Per-image imports use `--save` with a
JSON record containing `party`, `asset_id` and the generated PNG's `source` path.
`--select-refinement` selects an inspected revision with an additional
`edit_prompt` field, checking the current draft's hashes and preserving its files.

In-game rendering, UI-scale inspection and campaign play remain separate manual
acceptance checks in the project's test matrix.
