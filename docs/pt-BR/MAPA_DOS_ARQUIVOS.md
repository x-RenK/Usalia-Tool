# Mapa dos arquivos e suas funções

[English](../en/FILE_MAP.md)

## Arquivos que compõem o mod

| Caminho relativo ao mod | Função observada |
|---|---|
| `romfs/data/SUBDATA.DAT` | Contêiner principal de bancos textuais, scripts internos, gráficos, ANM, START, NLTX e FAD |
| `romfs/data/script.dat` | Roteiro externo usado também nas legendas das prévias; distinto do script interno de START |
| `romfs/font.bin` | Fonte externa usada por caminhos de renderização do jogo |
| `romfs/data/font.bin` | Segunda fonte externa; deve ser preservada e verificada separadamente |
| `exefs_patches/<pasta>/<BuildID>.ips` | Remapeamento de acentos e alterações do executável: interface, batalha, nomes, Enciclopédia, salvamentos e ajustes locais |
| ExeFS `main` original | Programa da edição alvo; possui strings, ponteiros, tabela CP932→Unicode e instruções de desenho |

Só SUBDATA não reproduz a tradução completa: os textos do executável, acentos e script externo dependem dos demais arquivos. O pacote v10 reuniu as antigas categorias de IPS em um patch consolidado. O nome da pasta do patch pode mudar; o nome hexadecimal do IPS e seus bytes devem corresponder ao build.

## Raiz de SUBDATA

A base NX possui 229 registros `PS_FS_V1`, com entradas repetidas `dummy.dat`. Use o índice, não só o nome, para desambiguá-las.

| Recurso | Conteúdo / uso |
|---|---|
| `start.dat` | Arquivo sem nomes internos; 107 slots na base NX. Bancos de dados, roteiro e recursos gráficos, incluindo um grande contêiner HD |
| `anm*.dat` | 48 recursos de animação legados inventariados; quadros, texturas, títulos, narrações e prévias. Não são automaticamente vídeos MP4 |
| `new_bg051.nltx` … `new_bg064.nltx` | 14 cartões da campanha de Laharl, inclusive o episódio final |
| `new_bg065.nltx` … `new_bg068.nltx` | Quatro cartões da campanha de Etna |
| `new_bg071.nltx` | Tela Next Episode / Próximo Episódio, 1920×1080 na base examinada |
| `new_bg075.nltx` | Propaganda gráfica de Thursday; exige tradução de imagem se desejado |
| `save001.tx2` … `save018.tx2` | Recursos gráficos associados aos 18 episódios/salvamentos; não substituem a tabela de títulos no main |
| `nsaveicon.tx2` | Arte de ícone de salvamento |
| `sys1.tx2` | Recurso de interface legado; função detalhada de cada recorte ainda não catalogada |
| `zz_anmdat.fad` | Layouts de animação/interface e 365 descritores de textura na base estudada |
| `dummy.dat` | Preenchimento/entradas repetidas; não remover ou renumerar |

`DATA.DAT` é outro contêiner de recursos, diferente de SUBDATA; no PC tem modificações no pacote de tradução. A análise histórica de um dump NX registrou 9.932 entradas e 1.454.896.128 bytes. Isso não prova que seus recursos coincidam com os do PC nem que um arquivo de PC possa substituí-lo.

## Bancos textuais de START

Os nomes são convenções recuperadas das ferramentas históricas; o arquivo START não contém essa tabela de nomes. Confirme o slot e o layout pelos bytes. Nomes de recursos gráficos mudam entre PC e NX; por exemplo, a tabela histórica de nomes não descreve corretamente todos os slots gráficos mais recentes.

| Slot ENG | Nome histórico | Função dos campos traduzíveis |
|---:|---|---|
| 0 | `script.dat` | Falas, eventos, tutoriais e comandos de roteiro; extração por candidatos |
| 1 | `talk.dat` | Banco de conversas/estruturas auxiliares; editor estrutural completo não implementado |
| 2–3 | `RMAPS.dat`, `RMAPS2.dat` | Dados de mapas/eventos; preservar estrutura |
| 40 | `magic.dat` | Nome e descrição de habilidades; não copiar atributos do PC |
| 41 | `HABIT.dat` | Textos de classes/títulos |
| 42–45 | `char_j/e/c/k.dat` | Bancos de personagens por idioma, conforme nomes históricos |
| 46 | `charhelp.dat` | Descrições/ajuda de personagens |
| 47 | `mitem.dat` | Nome e descrição de itens; preços, IDs e atributos ficam intactos |
| 48 | `dungeon.dat` | Nomes de destinos e áreas |
| 49 | `GE.dat` | Nomes e descrições de Geo Effects |
| 50–53 | `name_j/e/c/k.dat` | Bancos de nomes por idioma; não são necessariamente os rótulos visuais dos interlocutores |
| 54 | `WISH.dat` | Propostas e descrições de Dark Assembly |
| 55 | `HOSPITAL.dat` | Dados do hospital; layout de edição não certificado nesta versão |
| 56 | `THIEF.dat` | Mensagens de roubo |
| 57 | `zukan.dat` | Enciclopédia: título + oito campos de linha |
| 58 | `musicshop.dat` | Texto exibido na loja de música; manter BGM/preço |
| 59–62 | `geocube.dat`, `face.dat`, `mp25001.dat`, `se01.phd` | Dados auxiliares segundo a tabela histórica; não editar sem inspeção |
| 63–70 | `.pbd`, `.phd`, `voice*.phd/pbd` | Bancos de áudio segundo os nomes históricos |
| 71 | `ANM00.dat` | Recurso de animação/interface interno segundo a tabela histórica |
| 92 | atlas de nomes HD | 512×4096, TX2 indexado de 256 cores; nomes acima das falas |
| 96 | contêiner de objetos HD | 669 objetos, 1.346 folhas e 1.658 paletas na base examinada |
| 97–106 | recursos adicionais NX | Não atribuir automaticamente os nomes da tabela PC de 98 entradas |

O inventário gerável `archive-list --json` fornece nomes e posições reais da sua cópia. Nenhum offset absoluto do projeto deve ser tratado como constante para toda edição.
