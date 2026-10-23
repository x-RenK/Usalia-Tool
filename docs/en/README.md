# Usalia Tool guide

[Português brasileiro](../pt-BR/README.md) · [Home](../../README.md)

## Capabilities

| Area | Feature | Explicit limit |
|---|---|---|
| Outer archive | List, validate, extract and replace NX PS_FS_V1 / PC PSPFS_V1 | Replacement appends data, increasing archive size |
| START | Extract slots; replace equal-size slots | No automatic relocation of bytecode or unknown pointers |
| Text | Export ENG database fields and story candidates; validate/import | Story scanning is heuristic, not exhaustive |
| CSV | PT-BR/ENG editor, search and byte counter | Commit each edited row with the Update button |
| Accents | 48 Latin characters, CP932 carriers and native Unicode IPS | IPS generation is restricted to the researched build |
| Executable | NSO to analysis image; SHA-256-bound edit manifests | Analysis image is not an installable main |
| IPS | Inspection, writing, IPS32 and conflict-aware merge | Conflicting edits are not resolved automatically |
| NLTX | Tiled BC1 to PNG and back; untouched blocks preserved | Observed opaque NMPLTEX1/YKCMP variant only |
| TX2 | Linear 4/8-bpp indexed and type-3 RGBA | Indexed imports reject colors outside the palette |
| START[96] HD archive | Object listing, sheet export, direct ARGB or type-265 indexed replacement | Indexed imports must use the original palette |
| FAD | Export textures from the observed layout | Full FAD repacking is not implemented |
| Fonts | Metadata inspection and atlas export | No automatic creation of missing alphabets |
| Distribution | Five game files plus readme | Translator supplies the fonts, script and IPS |

## Installation

Extract the complete project, install Python 3.10+, and run `python -m pip install -e .` in the project directory. Open `ABRIR_USALIA.bat` on Windows or run `python -m usalia gui` with Tkinter. Command-line users can start with `python -m usalia --help`. Keep dumps and working artwork under the Git-ignored `workspace/` directory.

The package installs Pillow and NumPy. Only compressed NSO support needs optional `lz4`: `python -m pip install -e ".[nso]"`. The toolkit does not download or install the game.

## Editor

Choose the source, extraction kind (`banks`, `story` or `cstrings`) and character mapping. Export and open the CSV, select a row, edit its translation, then click **Update selected row**. Save the CSV together with its `.csv.json` sidecar. Validate before building a new output file.

`banks` and `story` take an NX SUBDATA.DAT; `cstrings` scans a standalone file, including an external script. The heuristic targets identified ENG text and may miss unusual controls. Do not change IDs, offsets, originals or slot sizes. An empty translation preserves the original bytes.

## Validation

The distributable test suite uses synthetic fixtures to cover truncation, overlong text, metadata tampering, conflicting IPS edits, bounds, compression and block preservation. Additional local checks used project files: 229 NX entries, 107 NX START entries, 203 PC entries, 98 PC START entries, 669 HD objects, 1,346 sheets and 1,658 palettes. The modified v6 baseline yielded 2,225 database fields and 9,208 story candidates; these figures are not translation coverage percentages.

The Tkinter interface was not run in a graphical desktop during this delivery. Binary validation does not replace NX testing. Follow the [review workflow](WORKFLOW.md).

## Layout

`usalia/` contains reusable code and the CLI. `usalia/data/` holds structural layouts and character mappings. `profiles/` stores build-specific offsets/counts. Both documentation directories provide equivalent manuals. `docs/research/` holds the inventory, validation, historical AJ catalog and provenance; `tests/` contains fixtures without game assets.

Original code/documentation is MIT. The original PC translator retains credit; using this toolkit does not grant rights to third-party scripts or artwork.
