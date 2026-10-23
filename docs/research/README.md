# Evidence / Evidência

## PT-BR

Os arquivos desta pasta registram estruturas e achados do projeto, sem imagens nem executáveis do jogo. Offsets absolutos do v6 são históricos; o parser deve ler a tabela da cópia em uso.

- `local-validation.json`: resultados da inspeção real de NX/PC e amostras de imagens.
- `executable-validation.json`: geração de acentos comparada byte a byte com o IPS nativo histórico, usando o NSO original do mesmo Build ID.
- `anm-hd-crosswalk.json`: 48 ANM, 213 objetos legados e seus IDs associados aos objetos HD quando presentes. IDs iguais não demonstram equivalência de todos os comandos.
- `hd-objects.json`: cabeçalhos e posição estrutural dos 669 objetos HD; não contém os pixels.
- `nx-root-index-v6.json`: 229 entradas da base de pesquisa, incluindo duplicatas.
- `speaker-labels.json`: 50 rótulos gráficos de interlocutores, 49 distintos.
- `aj-history.csv`, `aj-history.json` e `AJ_INDEX.md`: 851 registros históricos. Descrições em português preservadas; nomes de plataforma normalizados para NX. O status vale para a revisão original, não certifica automaticamente a ferramenta.
- `provenance.json`: fontes técnicas usadas e política de evidência.

A suíte pública de testes usa apenas dados sintéticos. Resultados locais adicionais dependem de arquivos do próprio projeto que não são redistribuídos. O mapa de acentos está em `usalia/data/`; o perfil de edição e offsets está em `profiles/`.

## English

These files record structural findings without game artwork/executables. Absolute v6 offsets are historical; parse the directory of your own copy.

- `local-validation.json`: actual NX/PC inspection and sampled image results.
- `executable-validation.json`: generated accent patch compared byte-for-byte with the historical working patch against the matching original NSO.
- `anm-hd-crosswalk.json`: 48 ANM resources, 213 legacy objects and HD matches by resource ID where available. Matching IDs do not prove full animation-command equivalence.
- `hd-objects.json`: structural headers/positions of 669 HD objects, without pixels.
- `nx-root-index-v6.json`: 229 research-base entries, including duplicates.
- `speaker-labels.json`: 50 graphical speaker labels, 49 distinct.
- `aj-history.csv`, `aj-history.json`, `AJ_INDEX.md`: 851 historical entries. Portuguese primary descriptions retained; platform wording normalized to NX. Statuses belong to the original revision and do not certify the new toolkit.
- `provenance.json`: technical sources and evidence policy.

Public tests use synthetic fixtures only. Additional local checks rely on project files that are not redistributed. Character mappings live in `usalia/data/`; build-specific offsets live in `profiles/`.
