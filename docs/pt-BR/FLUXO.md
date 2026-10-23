# Fluxo de tradução e distribuição

[English](../en/WORKFLOW.md)

## 1. Identificar a base

Registre região, idioma selecionado, versão, Title ID, Build ID, tamanho e SHA-256 dos arquivos. O alvo estudado é ENG / `01004B100AF18000` / `81F7AB934AD9A6DC823F64A10E12C93C`. O número de atualização não deve ser deduzido só pelo nome do jogo. A edição JP possui estruturas e contagens diferentes; não reaproveitar o IPS ENG nela.

Faça cópias de SUBDATA, script externo, ambas as fontes e main. Crie uma pasta de trabalho nova. Preserve o pacote aprovado anterior e o registro de quais telas foram verificadas. Não misture arquivos de traduções de builds diferentes.

## 2. Inventariar e extrair

```sh
python -m usalia archive-list workspace/SUBDATA.DAT --json workspace/subdata-index.json
python -m usalia archive-extract workspace/SUBDATA.DAT workspace/root --entry start.dat
python -m usalia text-export workspace/SUBDATA.DAT workspace/bancos.csv --kind banks
python -m usalia text-export workspace/SUBDATA.DAT workspace/historia.csv --kind story
python -m usalia text-export workspace/script.dat workspace/previas.csv --kind cstrings
```

A extração externa cria nomes como `0228_nome.ext`, com o índice real. Localize o start.dat extraído e use esse caminho nos comandos de START. Não renomeie recursos dentro do jogo base sem compreender suas referências.

Os CSVs possuem `id`, recurso, offset absoluto, slot, regra de preenchimento, bytes anteriores, original e tradução. O JSON ao lado guarda os registros confiáveis e o SHA-256. Leve os dois juntos. Edite somente `translation`; uma célula vazia mantém o original. `story` e `cstrings` são candidatos por heurística e exigem conferir contexto e controles.

## 3. Traduzir com contexto

Mantenha glossário, nomes, gênero, pronomes, termos técnicos e humor consistentes. A política editorial PT-BR do projeto preservou nomes de personagens e termos como Item World/Innocent; isso é uma escolha de tradução, não uma limitação obrigatória da ferramenta.

Ao portar uma tradução de PC, associe cenas e registros por contexto/identificadores; não copie arquivos inteiros. PC e NX têm conteúdo exclusivo, comandos e atributos diferentes. No diagnóstico inicial, habilidades eram 285 PC contra 288 JP, CHARHELP 67 contra 68 e WISH 25 contra 31. Quantidades iguais também não provam equivalência dos registros.

Confira o mapa de acentos da fonte PC: os portadores de PC não são necessariamente os mesmos do NX. Decodifique para Unicode normal antes de converter ao mapa alvo. Respeite os créditos e as condições de uso da tradução de origem.

## 4. Validar e aplicar

```sh
python -m usalia text-check workspace/SUBDATA.DAT workspace/bancos.csv --extra-csv workspace/historia.csv
python -m usalia text-build workspace/SUBDATA.DAT workspace/bancos.csv workspace/SUBDATA_textos.DAT --extra-csv workspace/historia.csv
```

Para PT-BR com o IPS correspondente, acrescente `--mapping ptbr` na exportação, validação e geração. Os dois CSVs acima devem vir da mesma base exata. A ferramenta recusa texto longo, metadados alterados, IDs duplicados, linhas removidas, base diferente e sobreposição entre planilhas. Não trunca letras para fazer o texto caber.

Na história, a posição do NUL original é preservada: a sobra é preenchida com espaços fullwidth e, se necessário, um espaço ASCII. Nos bancos fixos, a tradução recebe NUL e preenchimento zero dentro de seu campo. Isso evita sobras de inglês sem tocar em atributos adjacentes.

Depois de gerar uma nova base, exportações antigas deixam de corresponder ao SHA-256 dela. Para outra etapa, exporte novamente a partir da nova base, ou agrupe as planilhas com `--extra-csv` antes da geração. Preserve a sequência das etapas.

## 5. Imagens, executável e revisão

Trate as imagens e as strings do main separadamente, conforme os outros guias. Atualize os títulos das artes e os rótulos de salvar/carregar/excluir de forma coerente. Mantenha os ícones NX. Compare imagens redecodificadas do binário final, não apenas PNGs de edição.

Uma revisão útil cobre: tela inicial e opções; abrir, continuar, salvar e excluir; compra/venda/equipar; Mochila/Depósito; ordenar/reorganizar e mover; Dark Assembly e criação; itens/habilidades; Enciclopédia; batalha, roubo, altura e alvos; resultados; cartões de capítulo; prévias; narrações; ramificações/finais e modo Etna. Teste também comandos de avançar/voltar e frases mais longas.

## 6. Montar o pacote final

Forneça o SUBDATA final, script externo, duas fontes, IPS consolidado e LEIA-ME. O comando usa uma lista fechada: não inclui planilhas, imagens de comparação, caches, versões antigas ou arquivos temporários.

```sh
python -m usalia release --subdata workspace/SUBDATA_final.DAT --script workspace/script.dat --font-root workspace/root-font.bin --font-data workspace/data-font.bin --ips workspace/81F7AB934AD9A6DC823F64A10E12C93C.ips --readme workspace/LEIA-ME.txt --output workspace/Traducao_NX.zip
```

Caminhos produzidos no ZIP:

- `atmosphere/contents/01004B100AF18000/romfs/data/SUBDATA.DAT`
- `atmosphere/contents/01004B100AF18000/romfs/data/script.dat`
- `atmosphere/contents/01004B100AF18000/romfs/font.bin`
- `atmosphere/contents/01004B100AF18000/romfs/data/font.bin`
- `atmosphere/exefs_patches/Usalia_Localization/81F7AB934AD9A6DC823F64A10E12C93C.ips`
- `LEIA-ME.txt`

O nome da pasta do IPS é diferente do pacote PT-BR histórico, mas tem a mesma função. Remova patches antigos **desta tradução** antes de instalar a revisão consolidada; preserve patches de outros jogos. Não deixe main modificado antigo e IPS novo alterando a mesma base sem análise.

O LEIA-ME deve indicar compatibilidade, instalação, desinstalação, autores, ferramentas e escopo real. Credite quem produziu a tradução original e o port. Copie a pasta atmosphere completa; só SUBDATA não basta para uma instalação nova. Não é necessário distribuir os saves.
