# Fonts, accented characters and executable

[Português brasileiro](../pt-BR/FONTES_E_EXECUTAVEL.md)

## Confirmed working approach

ENG text uses CP932/Shift-JIS, often with ASCII converted to fullwidth. Mis-decoding it can look like meaningless Japanese. Usalia sheets contain ordinary Unicode; conversion happens when writing the game file.

The approved solution uses **48 regular CP932 carriers**, remapped to native Unicode through IPS. Required glyphs already existed in the original fonts. The working solution did not need bitmap replacement. Earlier PUA/modified-font attempts are historical and must not be confused with this method.

Example: CSV `ã` is U+00E3. The writer emits CP932 `8B 8F`, whose carrier is `居`. The conversion entry at analysis-image offset `0x20CB34` (2,149,172) is patched to return U+00E3, and the font draws `ã`. This does not make arbitrary kanji safe to replace without collision checks.

The JSON `unicode_table_offset` field is memory-relative; add **0x100** for IPS/analysis-image offsets. This was verified against the historical IPS and original main.

`usalia/data/ptbr-carriers.json` contains all 48 characters, carriers, CP932 bytes, table offsets, Unicode values and historical GIDs. The GID field is research metadata, not a replacement for inspecting another edition's font.

```sh
python -m pip install -e ".[nso]"
python -m usalia nso-memory workspace/main workspace/main.memory.bin
python -m usalia accent-patch workspace/main.memory.bin workspace/81F7AB934AD9A6DC823F64A10E12C93C.ips
python -m usalia text-export workspace/SUBDATA.DAT workspace/banks.csv --kind banks --mapping ptbr
# Edit translation, then:
python -m usalia text-check workspace/SUBDATA.DAT workspace/banks.csv --mapping ptbr
python -m usalia text-build workspace/SUBDATA.DAT workspace/banks.csv workspace/SUBDATA_PT.DAT --mapping ptbr
```

Generation checks signature, Build ID, decompressed flags and the old values of every conversion entry. `nso-memory` produces an analysis image with a 0x100-byte header and segments at virtual addresses; **do not install it as main**. IPS offsets use this analysis convention. Compressed NSO file offsets are not virtual addresses.

Historical research recorded the CP932 routine at `0x101CF8` and a table region at `0x20BAE8`. The JSON's individual offsets drive the generator. The historical routine/region values are memory research references; do not mix them with the file offsets below. Every value is specific to the researched ENG build, not a JP-compatible constant.

## Other languages

For additional Latin characters, identify existing glyphs, unused CP932 carriers and their conversion entries. A custom JSON mapping can assign one character to two CP932 bytes. The text writer accepts it, but you must generate/validate the corresponding executable patch and check for collisions with untranslated source text.

If the font lacks an alphabet, CP932 remapping cannot create it. Font records, bitmaps, metrics and rendering must be extended separately. Usalia 1.0 does not automate this or certify full Arabic, Cyrillic or CJK alphabets. RTL, ligatures and combining marks require further research.

## font.bin

Inspected font: 16,800,276 bytes; one-channel 4096×4096 atlas at file end; 64×64 cells; count at `0x18`; 24-byte records starting at `0x40`; 914 records; atlas offset `0x5A14` (23,060). These values were rechecked locally. Inspect each other font separately.

```sh
python -m usalia font-info workspace/font.bin --atlas workspace/font-atlas.png
```

## Main strings and drawing

Many menus, battle messages, save titles and options live in the executable. Database translation alone will not find them. Visual fit depends on drawing paths, scale and crops as well as byte length. Keep adjustments local: global scale changes can regress approved screens.

Build-specific findings, in the analysis image including its 0x100-byte header:

| Data | Offset / observation |
|---|---|
| 18 chapter-title pool | `[0x1BBE87, 0x1BC0E5)`, 606 bytes |
| Title pointers | `0x23FC40 + 8*i`, i=0..17 |
| Title RELA addends | `0x169450 + 24*i` |
| Observed relocation type | AArch64 RELATIVE, 1027 |
| `Save?` prompt | `0x1C4600`; original fullwidth slot is 11 bytes including NUL |
| `Default` option | `0x1BF9CF`; original fullwidth slot is 15 bytes including NUL |

Pointers store memory addresses, corresponding here to file offsets minus `0x100`. Updating the pointer alone failed because the loader reapplied the RELA addend. The v8 fix updated both and simulated relocation before reading all 18 titles.

Use `patch-manifest` for researched edits bound to SHA-256 and expected old bytes. It does not discover pointers or ARM64 instructions. It rejects overlong strings and overlapping edits. See `examples/binary-edit.example.json`.

## Consolidating IPS

Historical categories were Unicode, Interface, Battle, complementary Battle, Corrections, Names and Encyclopedia. Omitting one revived previously fixed issues. Merge by byte with conflict detection rather than selecting the newest filename.

```sh
python -m usalia ips-info workspace/patch.ips
python -m usalia ips-merge workspace/accents.ips workspace/interface.ips --out workspace/consolidated.ips
```

Conflicts stop the merge. Compare the purpose and bytes of both revisions rather than blindly using last-writer-wins. Rename the finished release patch to the correct Build ID.
