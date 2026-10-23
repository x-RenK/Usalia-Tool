# Localization and release workflow

[Português brasileiro](../pt-BR/FLUXO.md)

## 1. Identify the target

Record region, selected language, version, Title ID, Build ID, file sizes and SHA-256 hashes. The researched target is ENG / `01004B100AF18000` / `81F7AB934AD9A6DC823F64A10E12C93C`. Do not infer an update version from the game name. JP has different structures/counts; the ENG IPS is not a JP patch.

Keep copies of SUBDATA, the external script, both fonts and main. Start a new work directory, preserve the approved previous release and track tested screens. Do not mix builds.

## 2. Inventory and export

```sh
python -m usalia archive-list workspace/SUBDATA.DAT --json workspace/subdata-index.json
python -m usalia archive-extract workspace/SUBDATA.DAT workspace/root --entry start.dat
python -m usalia text-export workspace/SUBDATA.DAT workspace/banks.csv --kind banks
python -m usalia text-export workspace/SUBDATA.DAT workspace/story.csv --kind story
python -m usalia text-export workspace/script.dat workspace/previews.csv --kind cstrings
```

Archive extraction prefixes each actual index, for example `0228_name.ext`. Use the resulting start.dat path for START commands. Do not rename resources inside the game's archive without understanding references.

Sheets store ID, resource, absolute offset, slot length, padding rule, original bytes, original text and translation. The adjacent JSON holds trusted metadata and the source hash. Keep both files. Edit `translation` only; empty means unchanged. Story/cstring records are heuristic candidates requiring contextual/control-code review.

## 3. Translate in context

Maintain consistent names, terminology, gender, pronouns, characterization and humor. Ren's PT-BR editorial policy preserved character names and terms such as Item World/Innocent. Other communities may choose their own policy; these are not toolkit requirements.

For a PC port, associate scenes/records using context and identifiers rather than copying whole archives. PC/NX have exclusive content, different commands and different gameplay parameters. The initial comparison found 285 PC versus 288 JP skills, 67 versus 68 CHARHELP records and 25 versus 31 WISH records. Equal counts still do not establish record equivalence.

Recover the PC font's carrier map: it may differ from NX. Decode to ordinary Unicode first, then encode the target mapping. Retain source translator credits and respect source terms.

## 4. Validate and build

```sh
python -m usalia text-check workspace/SUBDATA.DAT workspace/banks.csv --extra-csv workspace/story.csv
python -m usalia text-build workspace/SUBDATA.DAT workspace/banks.csv workspace/SUBDATA_text.DAT --extra-csv workspace/story.csv
```

For PT-BR with the matching IPS, add `--mapping ptbr` consistently during export/check/build. Both sheets must come from the exact same source. Overlong strings, altered metadata, duplicate IDs, deleted records, wrong bases and overlapping sheets are rejected. Text is never silently truncated to fit.

Story slots retain the original NUL position, padding with fullwidth spaces and an ASCII space if needed. Database fields receive a NUL and zero padding within the reserved slot. This removes leftover English without changing adjacent stats.

Once a file is built, old sheets no longer match its hash. Export from the new base for the next stage, or combine original-base sheets using `--extra-csv`. Preserve the stage order.

## 5. Images, executable and testing

Treat artwork and main strings using their dedicated guides. Keep chapter artwork synchronized with save/load/delete labels. Retain NX icons. Inspect images decoded from final binaries, not only editing PNGs.

Review title/options; new/continue/save/delete; buy/sell/equip; Bag/Storage; sorting/reordering/movement; Dark Assembly/creation; items/skills; Encyclopedia; battle/steal/height/targets; results; chapter cards; previews; narration; branches/endings and Etna mode. Test forward/back controls and the longest labels.

## 6. Final package

Supply final SUBDATA, external script, both fonts, consolidated IPS and readme. Packaging uses an allowlist, excluding spreadsheets, comparisons, caches, old revisions and temporary files.

```sh
python -m usalia release --subdata workspace/SUBDATA_final.DAT --script workspace/script.dat --font-root workspace/root-font.bin --font-data workspace/data-font.bin --ips workspace/81F7AB934AD9A6DC823F64A10E12C93C.ips --readme workspace/README.txt --output workspace/Localization_NX.zip
```

The six ZIP entries are the four files under `atmosphere/contents/01004B100AF18000/romfs/` (`data/SUBDATA.DAT`, `data/script.dat`, `font.bin`, `data/font.bin`), `atmosphere/exefs_patches/Usalia_Localization/81F7AB934AD9A6DC823F64A10E12C93C.ips`, and `LEIA-ME.txt`.

The IPS folder differs from the historical PT-BR release but serves the same purpose. Remove old patches **for this localization** before installing its consolidated revision; retain other games' patches. Do not combine an older modified main with a new IPS without analyzing both.

Readmes should state compatibility, installation/removal, authors, tools and actual coverage. Credit the source translator and port author. Copy the entire atmosphere tree: SUBDATA alone is insufficient for a fresh installation. Saves need not be distributed.
