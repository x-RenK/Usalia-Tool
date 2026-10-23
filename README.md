# Usalia Tool

**Disgaea 1 Complete NX localization toolkit — by Ren / Disgaea Brasil**

[Português brasileiro](docs/pt-BR/README.md) · [English](docs/en/README.md)

## PT-BR

A Usalia Tool reúne as ferramentas e as descobertas do projeto PT-BR para ajudar outras comunidades a localizar **Disgaea 1 Complete NX**. Inclui editor de CSV em PT-BR/inglês, extração e aplicação de textos em campos fixos, contêineres NX/PC, imagens, acentos nativos, patches IPS e montagem de pacote.

O registro técnico cobre arquivos, funções, formatos, camadas HD/legadas, capítulos, narrações gráficas, nomes acima dos diálogos, menus do executável, problemas encontrados e validação. O catálogo histórico contém **851 ajustes AJ**. O código e os documentos são distribuídos sem arquivos do jogo ou textos integrais da tradução de PC.

### Começar

Requer Python 3.10+; Windows, Linux ou macOS. Tkinter é necessário para o editor gráfico. Em algumas distribuições Linux, instale o pacote `python3-tk` do sistema.

```sh
python -m pip install -e .
python -m usalia gui
python -m usalia --help
```

Para inspecionar um `main` NSO comprimido, instale a opção `python -m pip install -e ".[nso]"`.

```sh
python -m usalia archive-list workspace/SUBDATA.DAT
python -m usalia text-export workspace/SUBDATA.DAT workspace/bancos.csv --kind banks
python -m usalia text-export workspace/SUBDATA.DAT workspace/historia.csv --kind story
# Edite somente translation; preserve os arquivos .csv.json.
python -m usalia text-check workspace/SUBDATA.DAT workspace/bancos.csv
python -m usalia text-build workspace/SUBDATA.DAT workspace/bancos.csv workspace/SUBDATA_traduzido.DAT
```

Para acentos, leia o [guia de fontes e executável](docs/pt-BR/FONTES_E_EXECUTAVEL.md) antes de usar `--mapping ptbr`. Os comandos não traduzem automaticamente o conteúdo: extraem, validam e aplicam a tradução preparada por você.

**Base estudada:** edição ENG, Title ID `01004B100AF18000`, Build ID `81F7AB934AD9A6DC823F64A10E12C93C`. Outros idiomas, builds e regiões exigem validação. O extrator de história é heurístico; não é um desmontador completo do bytecode. A versão 1.0.0 foi validada com testes automatizados e amostras locais; o novo editor e seus resultados ainda exigem teste visual no NX.

## English

Usalia Tool consolidates the tooling and findings from the PT-BR project so other communities can localize **Disgaea 1 Complete NX**. It includes a Portuguese/English CSV editor, fixed-slot text export/import, NX/PC containers, image tools, native accented characters, IPS handling and release packaging.

The technical record covers file roles, binary layouts, HD/legacy layers, chapter cards, graphical narration, speaker labels, executable menus, failures and validation. The historical catalog contains **851 AJ adjustments**. No game binaries, game artwork or complete third-party translation scripts are included.

### Start

Python 3.10+ on Windows, Linux or macOS; Tkinter for the desktop editor. Some Linux distributions require the system `python3-tk` package.

```sh
python -m pip install -e .
python -m usalia gui
python -m usalia --help
```

Optional compressed NSO support: `python -m pip install -e ".[nso]"`.

```sh
python -m usalia archive-list workspace/SUBDATA.DAT
python -m usalia text-export workspace/SUBDATA.DAT workspace/banks.csv --kind banks
python -m usalia text-export workspace/SUBDATA.DAT workspace/story.csv --kind story
# Edit translation only; retain each .csv.json sidecar.
python -m usalia text-check workspace/SUBDATA.DAT workspace/banks.csv
python -m usalia text-build workspace/SUBDATA.DAT workspace/banks.csv workspace/SUBDATA_localized.DAT
```

Read the [font/executable guide](docs/en/FONTS_AND_EXECUTABLE.md) before using `--mapping ptbr`. These commands export, validate and apply your translation; they do not machine-translate the game.

**Research target:** ENG edition, Title ID `01004B100AF18000`, Build ID `81F7AB934AD9A6DC823F64A10E12C93C`. Other languages/builds/regions need validation. Story extraction is heuristic, not a complete bytecode disassembler. Version 1.0.0 has automated and local sample validation; its new GUI and outputs still need visual NX testing.

## Documentation / Documentação

| PT-BR | English |
|---|---|
| [Guia e recursos](docs/pt-BR/README.md) | [Guide and capabilities](docs/en/README.md) |
| [Mapa dos arquivos](docs/pt-BR/MAPA_DOS_ARQUIVOS.md) | [File map](docs/en/FILE_MAP.md) |
| [Formatos binários](docs/pt-BR/FORMATOS.md) | [Binary formats](docs/en/FORMATS.md) |
| [Fontes e executável](docs/pt-BR/FONTES_E_EXECUTAVEL.md) | [Fonts and executable](docs/en/FONTS_AND_EXECUTABLE.md) |
| [Imagens e cenas](docs/pt-BR/IMAGENS_E_CENAS.md) | [Images and scenes](docs/en/IMAGES_AND_SCENES.md) |
| [Fluxo de tradução](docs/pt-BR/FLUXO.md) | [Localization workflow](docs/en/WORKFLOW.md) |
| [Descobertas e problemas](docs/pt-BR/DESCOBERTAS.md) | [Findings and troubleshooting](docs/en/FINDINGS.md) |
| [Créditos](CREDITS.md) | [Credits](CREDITS.md) |

[AJ historical catalog / Catálogo histórico AJ](docs/research/aj-history.csv) · [Local validation / Validação local](docs/research/local-validation.json) · [Build-specific profile / Perfil por build](profiles/eng-81f7ab.json)

## Tests / Testes

```sh
python -m unittest discover -s tests -v
```

MIT for original toolkit code/documentation. Disgaea assets and third-party translations retain their respective ownership.
