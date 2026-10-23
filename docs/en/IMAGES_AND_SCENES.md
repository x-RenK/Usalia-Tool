# Images, animation, chapter cards and speaker labels

[Português brasileiro](../pt-BR/IMAGENS_E_CENAS.md)

## Graphical narration is not necessarily video subtitles

Laharl's opening narration uses animation resources and textures. Searching script strings or movie files alone misses it. Historical analysis covered 48 root ANM resources and 379 legacy texture sheets. The actively used HD counterpart also had to be located.

Changing ANM31's legacy art alone did not activate the v4 translation. Its HD counterpart is in START[96]. Resource-ID matching has been recovered and revalidated in `docs/research/anm-hd-crosswalk.json`. Distinguish **object index**, **resource ID**, **sheet index** and **FAD texture index**.

## Located narration

Indices are zero-based. One HD sheet may pack several frames that occupy multiple legacy sheets/layers.

| Scene | Legacy resource/location | HD ID | START[96] HD object index |
|---|---|---:|---:|
| Laharl/Krichevskoy introduction | `anm31.dat`, object 0, sheets 0–1 | 5002 | 337 |
| Celestia introduction | `anm02.dat`, object 1, sheet 0 | 5017 | 352 |
| Red moon and Laharl's mother | `anm08.dat`, object 0, sheets 0–1 | 5003 | 338 |
| Red moon song | `anm08.dat`, object 1, sheets 0–1 | 5004 | 339 |
| Laharl's court epilogue | `anm10.dat`, object 0, sheet 0 | 5005 | 340 |
| Decision to travel to Celestia | `anm14.dat`, object 0, sheet 0 | 5006 | 341 |
| Flower, silence and passing years | `anm14.dat`, object 1, sheet 0 | 5007 | 342 |

All seven HD sheets were visually rechecked in the v6 base. They use indexed HD format 265; imports must retain the original palette colors. The introduction plus the six additional sequences comprised 34 graphical frames in the localization project.

Only ANM31 differed between the supplied original/translated PC backups. Their other 47 ANM resources were identical; after decompression, they also matched corresponding NX v3 resources. Thus those six additional sequences had no PT-BR artwork to copy from the supplied PC material. They were translated for Ren's project using terminology aligned with the dialogue. This finding does not describe every PC fan translation ever released.

```sh
# Extract start.dat from SUBDATA with archive-extract; extraction prefixes its index.
python -m usalia start-extract workspace/start.dat workspace/start-slots
python -m usalia hd-list workspace/start-slots/096.bin --json workspace/hd-index.json
python -m usalia hd-export workspace/start-slots/096.bin 337 0 workspace/intro.png
# Keep image dimensions, palette and individual phrase crop locations.
python -m usalia hd-import workspace/start-slots/096.bin 337 0 workspace/intro_edited.png workspace/096_edited.bin
python -m usalia start-replace workspace/start.dat 96 workspace/096_edited.bin workspace/start_edited.dat
python -m usalia archive-replace workspace/SUBDATA.DAT start.dat workspace/start_edited.dat workspace/SUBDATA_scenes.DAT
```

START contains hundreds of MB of resources; extraction needs substantial disk/memory. Do not arbitrarily reposition packed phrases: animation commands reference their crops.

## Other inventoried graphical text

Legacy chapter titles, Episode, End and To be continued recur in `anm01–10` and `anm12–13`. Etna titles have ENG/JP variants in `anm16–19`. `anm12` object 3 sheet 0 contains Space Battleship GARGANTUA identification. `anm20` object 1 sheet 0 contains presentation/copyright; `anm21–22` contain graphical credits.

`anm51–60` and `anm63` include preview screenshots with embedded names and battle labels. `anm59` object 4 sheet 0 includes a Gordon dialogue capture. Technical NO DATA markers on character sheets were not classified as narration.

Translating a live interface label does not translate the same word burned into a preview screenshot. This inventory does not certify every possible movie subtitle or ending activation condition.

## Chapter cards

NX uses `new_bg051–068.nltx` for 18 cards and `new_bg071.nltx` for Next Episode. Legacy ANM title art also exists but does not automatically replace active NLTX cards. Save/load/delete chapter names come from a separate main table; keep the terminology synchronized with the artwork.

Etna's four cards represent episodes 1, 2, finale and finale continuation. The PT-BR project's primary text reference was Li Qiye's Disgaea PC translation; v8 compared all 18 cards with the save-title table. Other communities should retain their approved terminology rather than generating unrelated literal translations.

```sh
python -m usalia texture-export workspace/new_bg071.nltx workspace/next.png --format nltx
python -m usalia texture-import workspace/new_bg071.nltx workspace/next_edited.png workspace/new_bg071_edited.nltx --format nltx
python -m usalia archive-replace workspace/SUBDATA.DAT new_bg071.nltx workspace/new_bg071_edited.nltx workspace/SUBDATA_next.DAT
```

For quality, render lettering at higher resolution and downsample with antialiasing rather than enlarging small crops. Preserve shape, placement, shadows, bevel, color and line spacing. Remove old lettering before adding new glyphs. Next Episode retains its oversized colored initial and white remaining letters. The v9 crop smoothing did not adequately resolve jagged edges; v10 redrew contours. Inspect PNGs decoded **from the final encoded resource**, because BC1 can alter edges.

## Speaker labels above dialogue

START[92] contains a 512×4096, 256-color atlas. An observed legacy counterpart at START[25] is 128×1024 with 16 colors; the historical filename assigned to that slot is not reliable evidence of its function. Labels are artwork, not necessarily strings in `name_e.dat`.

50 labels were found, 49 distinct, with Noble Demon repeated. The supplied PC source also kept these in English. `docs/research/speaker-labels.json` lists the originals for review. The toolkit does not impose translated character names or nicknames.

Indexed TX2 imports reject new colors. Use the original palette or explicitly research palette replacement. Inspect every referenced crop before widening a label.

## Colors, transparency and borders

The project displayed swapped logo colors. RGBA/ARGB confusion is one technical possibility that must be checked in the bytes, not diagnosed from a photo alone. HD stores ARGB; the observed TX2/FAD variants use RGBA. Zero alpha is not a black background; inspect against light/dark backgrounds and in game.

Command bars have distinct variants, icons and crops. Replacing only half of `〈 〉`, or painting over A/B/Y, damages the controls. Limit erasure to text, preserve icon pixels, and adjust borders/crops when labels grow. Black lines outside the shop bars were removed by clearing only the faulty external rows, leaving the actual frame intact.
