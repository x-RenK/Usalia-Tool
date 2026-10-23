# Findings, regressions and knowledge limits

[Português brasileiro](../pt-BR/DESCOBERTAS.md)

## Preserved findings

ENG text uses CP932/fullwidth while translation sheets should remain readable Unicode. The working 48-accent solution uses native Unicode remapping; older PUA experiments are a different approach.

Text appears in databases, bytecode, external scripts, executable strings, textures, preview captures and animation layers. No single string search covers everything. PC/NX differ in container layouts, compression, counts, exclusive content, gameplay fields and controls; wholesale PC archive replacement changes more than language.

Legacy ANM resources can match HD objects by resource ID, but edits must target the active path. Chapter titles exist both in artwork and main. Pointer-table edits can be overwritten by RELA processing unless the addend is updated too. Similar command bars may be different variants. Longer text needs coordinated frame, highlight, crop and adjacent-panel changes. Approval of one screen/revision does not certify every route or ending.

## AJ cases

| Case | Finding / correction |
|---|---|
| AJ01 | Native accent conversion needs its IPS |
| AJ03 | Encyclopedia English leftovers removed by clearing the rest of each text slot, preserving names |
| AJ04 | Historical music-shop stage changed 39/41 titles, preserving BGM IDs/prices |
| AJ836–838 | Full sorting labels needed wider frame/highlight plus a local character-list shift |
| AJ841 | Restore original drawing path/position and Yes/No variant, then enlarge left margin by 20 px |
| AJ842 | Restore complete `〈 〉` icon and clear residue between it and Bag/Storage |
| AJ844 | Remove overlapping old strokes; separate text from Y; adjust margin |
| AJ846 | Initial edit targeted an inactive variant; B restored in FAD texture 298; arrows separated from Select |
| AJ847 | Move label brought 12 px closer to arrows without changing glyphs/icons |
| AJ848 | Test50Q crash: truncated SUBDATA left 20 textures pointing beyond EOF; rebuild from intact 50P and reapply intended changes |
| AJ849 | Reorder bar: right border +24 px; complete command group +12 px right |
| AJ850 | Clear only two faulty external black rows, preserving frames |
| AJ851 | Three creation-screen words copied from the Assembly reference in texture 6; icons preserved |

All 851 historical records are included as CSV/JSON. Original Portuguese descriptions remain primary historical evidence; field keys are English for tooling. Some entries were superseded or still awaited testing at that time. They are not 851 automatically applicable patches. AJ numbers are not texture indices.

## v4–v10

| Revision | Technical finding |
|---|---|
| v4 | Opening required active HD resources, not legacy ANM31 alone |
| v5 | Six additional graphical sequences translated with PC-consistent terminology |
| v6 | P052 Bold (URW Base 35) used for 34 narration frames to approximate the original style |
| v7 | 18 NLTX chapter cards and Next Episode localized |
| v8 | Save/load/delete labels synchronized; pointers and RELA addends fixed; chapter-10 punctuation reviewed |
| v9 | Artwork refined and Save? localized, but Ren still reported rough Next Episode lettering |
| v10 | Next Episode contours redrawn; Default localized; other v9 data retained |

v10 passed binary/integrity checks; final visual NX testing was still pending when Usalia was created. Historical project achievements do not imply universal automated support in the new toolkit.

## Troubleshooting

| Symptom | Check |
|---|---|
| Edit does not appear | Active HD/legacy resource, selected language, variant, install path, overlapping patch |
| Japanese glyph instead of accent | Emitted map, active IPS, Build ID and correct fonts |
| Crash when opening a screen | Every offset/size bound, FAD/HD pointers, EOF truncation, conflicting mods |
| Trailing English letters | Uncleared slot, wrong padding or overlaid artwork |
| Only editing PNG has the new title | Main's title table and RELA may still point to old data |
| Text outside a frame | Width/crop/scale and adjacent panel, not just byte count |
| Missing control icon | Artwork painted over the icon, PC controls copied into NX, wrong variant |
| Swapped colors | RGBA/ARGB order and palette index; do not infer cause from a photo alone |
| Jagged lettering | Source resolution, alpha mask, antialiasing and final BC1 encoding |
| Text search misses a phrase | It may be artwork/main text, or contain controls beyond the heuristic |

## Uncertified areas

There is no complete bytecode disassembler, full visual FAD command editor, optimized IMY encoder, automatic support for every Build ID, universal PC translation port, arbitrary-alphabet rendering, complete movie inventory or certification of every route. These boundaries identify useful areas for further community research.
