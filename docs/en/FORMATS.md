# Observed binary formats

[Português brasileiro](../pt-BR/FORMATOS.md)

All multibyte fields below are little-endian except IPS. Readers reject out-of-bounds offsets, lengths and dimensions. Unknown fields are preserved.

## NX PS_FS_V1

Eight-byte signature `PS_FS_V1`, then `u64 count` at `0x08`. The directory starts at `0x10`; each 64-byte record contains a NUL-terminated ASCII name[48], `u64 size` at +48, and absolute `u64 offset` at +56.

Replacement appends a resource aligned to 512 bytes and updates only its size/offset record. Old resource bytes remain unreferenced. This avoids reordering or dropping previous edits, at the cost of growth; it is not archive compaction.

## PC PSPFS_V1

Signature `PSPFS_V1`; `u32 count` at `0x08`; directory at `0x10`; 52-byte records: name[40], opaque `u32` at +40, `u32 size` at +44, `u32 offset` at +48. The opaque field is retained. Writing beyond the 32-bit address range is rejected.

## START

Plain NX START begins with `u32 count` and an array of `u32` offsets relative to START. An entry ends at the next offset, or at resource end for the last entry. Observed counts: 107 NX versus 98 PC. START has no embedded filename list.

The studied PC variant stores a block count, block size and IMY block offsets. It decoded as 882 blocks of up to 131,072 bytes, totaling 115,560,064 bytes. Use `decompress --format imy-package`. IMY encoding is not implemented.

## YKCMP

20-byte header: `YKCMP_V1`, `u32 type` at +8, compressed size including the header at +12, uncompressed size at +16. Type 7 uses zlib. Type 4 commands are:

| First byte c | Operation |
|---|---|
| 1–127 | Copy c literal bytes |
| 128–191 | length `(c >> 4) - 7`; distance `(c & 15) + 1` |
| 192–223 | length `c - 190`; distance `next_byte + 1` |
| 224–255 | next bytes x,y: length `((c & 31)<<4)+(x>>4)+3`; distance `((x & 15)<<8)+y+1` |

Overlapping copies repeat newly produced bytes. This toolkit's type-4 encoder emits literals only: valid/lossless, potentially much larger. Never overwrite a fixed allocation with a larger compressed block without updating its container and size fields.

## NLTX / NMPLTEX1

Validated variant: 128-byte header, `u32 width/height` at +24/+28, YKCMP length at +48, YKCMP at +128, type-7 zlib payload containing tiled BC1.

Physical dimensions: `pw=ceil(w/512)*512`, `ph=ceil(h/256)*256`. BC1 storage is `pw*ph/2`; each 4×4 block occupies eight bytes. `block_indices` implements the exact address formula recovered/tested against project files. Not every NMPLTEX1 variant is assumed compatible.

Import compares old/new images, recompresses changed 4×4 blocks, and preserves all other BC1 bytes. BC1 is lossy. An unedited image round-trip is byte-identical; changed regions undergo local recompression.

## TX2

16-byte header: `u16 width`, `u16 height`, `u16 format` (+4), opaque field (+6), `u16 color count` (+8), `u16 palette count` (+10), remaining opaque fields.

Supported linear variants: format 16 with one 16-color RGBA palette and 4-bit indices (low nibble first); format 256 with one 256-color RGBA palette and byte indices; format 3 without palette and direct RGBA. Other variants, multiple palettes and unknown swizzles are rejected. TX2 palettes use RGBA, whereas the HD sheets below store ARGB; mixing these swaps colors.

## START[96] HD container

Initial `u32` fields: metadata size excluding 16 bytes, opaque field, sheet count, palette count, object count. Objects begin at +32. Each object starts with its `u32` size followed by twelve `u16` fields: `header[0]` is ID, `[4]` palette count, `[5]` sheet count. Object length skips unknown commands intact.

A descriptor table follows all objects. Each 16-byte `<HHHHII>` descriptor stores format, opaque value, width, height, opaque value, and offset relative to pixel-data start. Sheets precede palettes. Pixel-data start = first header `u32` +16. Observed: 669 objects, table `0x32DF80`, data `0x339B40`, 1,346 sheets, 1,658 palettes. These offsets are HD-resource-relative, not SUBDATA-absolute.

Format 256 in this container means direct ARGB. Other observed sheets use byte indices and ARGB palettes. The exporter converts to RGBA. Do not confuse this convention with TX2 format 256.

## zz_anmdat.fad

Observed layout: texture count `u32` at `0x0C`; 32-byte `<8I>` descriptors at `0x430`. Used fields: size at index 2, offset at index 4, width/height at indices 5/6. Each texture has a 48-byte header followed by type-4 YKCMP. Decoded variants: 1,024-byte RGBA palette plus byte indices, or direct RGBA.

FAD also contains layout/crop commands. Changing artwork without crop changes can clip letters; moving crops incorrectly can hide button icons. Texture export is implemented; complete layout-command semantics remain research work.
