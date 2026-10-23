# File map and roles

[Português brasileiro](../pt-BR/MAPA_DOS_ARQUIVOS.md)

## Mod components

| Mod-relative path | Observed role |
|---|---|
| `romfs/data/SUBDATA.DAT` | Main container for text databases, internal scripts, ANM, START, NLTX and FAD resources |
| `romfs/data/script.dat` | External script used for preview subtitles; distinct from START's internal script |
| `romfs/font.bin` | External font used by game rendering paths |
| `romfs/data/font.bin` | Second external font; preserve and verify it separately |
| `exefs_patches/<folder>/<BuildID>.ips` | Accent remapping and executable changes: interface, battle, names, Encyclopedia, save menus and local layout adjustments |
| Original ExeFS `main` | Executable strings, pointers, CP932→Unicode conversion and drawing instructions |

SUBDATA alone does not reproduce the full localization. Executable text, accents and external scripts need the other components. The v10 release consolidated the earlier IPS categories into one patch. Its folder can be renamed; the hexadecimal IPS filename and bytes must still match the build.

## SUBDATA root

The researched NX archive has 229 `PS_FS_V1` entries, including repeated `dummy.dat` names. Use entry indices to disambiguate duplicates.

| Resource | Content / use |
|---|---|
| `start.dat` | Nameless-slot archive: 107 NX slots containing databases, scripts, images and a large HD container |
| `anm*.dat` | 48 inventoried legacy animation resources with frames, textures, cards, narration and previews; not automatically MP4 movies |
| `new_bg051.nltx` … `new_bg064.nltx` | 14 Laharl campaign cards, including the final episode |
| `new_bg065.nltx` … `new_bg068.nltx` | Four Etna campaign cards |
| `new_bg071.nltx` | Next Episode card, 1920×1080 in the inspected base |
| `new_bg075.nltx` | Thursday advertisement artwork, requiring image localization |
| `save001.tx2` … `save018.tx2` | Artwork associated with the 18 episodes/save screens; does not replace main's title table |
| `nsaveicon.tx2` | Save icon artwork |
| `sys1.tx2` | Legacy interface resource; individual regions are not fully cataloged |
| `zz_anmdat.fad` | Animation/interface layouts and 365 texture descriptors in the researched base |
| `dummy.dat` | Repeated filler entries; do not remove or renumber |

`DATA.DAT` is a separate resource archive. The PC translation modifies it. A historical NX dump report recorded 9,932 entries and 1,454,896,128 bytes. This does not establish PC/NX resource equivalence or allow transplanting the PC archive.

## START databases

The following names are historical tool conventions: START itself does not store this name table. Verify each slot/layout from bytes. Some newer NX image slots differ from the historical naming list.

| ENG slot | Historical name | Localizable role |
|---:|---|---|
| 0 | `script.dat` | Dialogue, events, tutorials and script commands; candidate extraction |
| 1 | `talk.dat` | Conversation/auxiliary structures; no complete structural editor here |
| 2–3 | `RMAPS.dat`, `RMAPS2.dat` | Map/event data; retain structure |
| 40 | `magic.dat` | Skill names/descriptions; preserve NX attributes |
| 41 | `HABIT.dat` | Class/title text |
| 42–45 | `char_j/e/c/k.dat` | Language-specific character banks, historical names |
| 46 | `charhelp.dat` | Character help/descriptions |
| 47 | `mitem.dat` | Item names/descriptions; leave IDs, prices and stats intact |
| 48 | `dungeon.dat` | Destination and area names |
| 49 | `GE.dat` | Geo Effect names/descriptions |
| 50–53 | `name_j/e/c/k.dat` | Language-specific name banks; not necessarily the displayed speaker artwork |
| 54 | `WISH.dat` | Dark Assembly proposals/descriptions |
| 55 | `HOSPITAL.dat` | Hospital data; editing layout not certified in this release |
| 56 | `THIEF.dat` | Steal messages |
| 57 | `zukan.dat` | Encyclopedia: title and eight line fields |
| 58 | `musicshop.dat` | Display text; preserve BGM IDs/prices |
| 59–62 | `geocube.dat`, `face.dat`, `mp25001.dat`, `se01.phd` | Auxiliary data per historical naming; inspect before editing |
| 63–70 | `.pbd`, `.phd`, `voice*.phd/pbd` | Historical audio-bank names |
| 71 | `ANM00.dat` | Historical internal animation/interface resource |
| 92 | HD speaker-name atlas | 512×4096, 256-color indexed TX2; labels above dialogue |
| 96 | HD object container | 669 objects, 1,346 sheets and 1,658 palettes in the inspected base |
| 97–106 | NX additions | Do not blindly use names from the 98-slot PC list |

Use `archive-list --json` for actual names/positions. Project absolute offsets are evidence for one base, never universal constants.
