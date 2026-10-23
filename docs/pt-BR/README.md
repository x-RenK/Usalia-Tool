# Guia da Usalia Tool

[English](../en/README.md) · [Início](../../README.md)

## O que esta versão faz

| Área | Recurso | Limite explícito |
|---|---|---|
| Contêiner externo | Lista, valida, extrai e substitui PS_FS_V1 NX / PSPFS_V1 PC | Substituição acrescenta dados; o arquivo pode crescer |
| START | Extrai slots; substitui por outro do mesmo tamanho | Não realoca bytecode nem ponteiros internos desconhecidos |
| Textos | Exporta CSV de bancos ENG e candidatos do roteiro; valida e aplica | Roteiro usa busca heurística; não garante cobertura integral |
| CSV | Editor PT-BR/ENG, busca, contador de bytes | A atualização da linha deve ser confirmada no botão do editor |
| Acentos | 48 caracteres latinos, portadores CP932 e IPS nativo | Geração de IPS limitada ao Build ID estudado |
| Executável | NSO para imagem de análise; edições por manifesto com SHA-256 | A imagem de análise não é um main instalável |
| IPS | Inspeção, escrita, IPS32 e união com detecção de conflitos | Conflitos não são resolvidos automaticamente |
| NLTX | BC1 tiled → PNG; PNG → NLTX com blocos intactos preservados | Somente variante opaca NMPLTEX1/YKCMP observada |
| TX2 | Formatos lineares 4/8 bpp e RGBA tipo 3 | Paletado: novas cores são recusadas |
| HD de START[96] | Lista objetos, exporta folhas, substitui ARGB direto ou índices tipo 265 | Importação indexada preserva a paleta original |
| FAD | Exporta as texturas do layout observado | Reempacotamento FAD completo ainda não implementado |
| Fontes | Inspeciona metadados e exporta atlas | Não cria automaticamente fontes para alfabetos ausentes |
| Distribuição | Cinco arquivos do jogo + LEIA-ME | Fontes, script e IPS devem ser fornecidos pelo tradutor |

## Instalação

1. Extraia todo o projeto para uma pasta.
2. Instale Python 3.10+ e execute `python -m pip install -e .` nessa pasta.
3. Abra `ABRIR_USALIA.bat` no Windows, ou `python -m usalia gui` em qualquer sistema com Tkinter.
4. Para trabalhar apenas no terminal, use `python -m usalia --help`.
5. Mantenha os dumps e as imagens de trabalho em `workspace/`, ignorada pelo Git.

Pillow e NumPy são instalados pelo pacote. O módulo opcional `lz4` é necessário somente para NSO comprimido: `python -m pip install -e ".[nso]"`. A ferramenta não instala nem baixa o jogo.

## Editor

Escolha o arquivo base, o tipo `banks`, `story` ou `cstrings` e o mapa de caracteres. Extraia o CSV. Abra-o, selecione uma linha, edite a tradução e clique **Atualizar linha selecionada**. Salve e preserve o `.csv.json`. Use **Validar** antes de gerar um arquivo de saída novo.

`banks` e `story` recebem SUBDATA.DAT NX; `cstrings` examina diretamente um arquivo, como um script externo. A busca é destinada aos textos ENG identificados e pode deixar de localizar texto com controles incomuns. Não edite os identificadores, offsets, originais ou comprimentos. Uma tradução vazia mantém os bytes originais.

## Validação disponível

A suíte usa dados sintéticos distribuíveis para testar truncamento, campos longos, metadados alterados, conflitos IPS, limites, compressão e preservação de blocos. A validação local adicional usou arquivos do projeto: 229 entradas NX, 107 entradas START, 203 entradas PC, 98 entradas START PC, 669 objetos HD, 1.346 folhas e 1.658 paletas. Foram exportados 2.225 campos de bancos e 9.208 candidatos de roteiro da base v6 já modificada; essas contagens não medem a porcentagem traduzida.

A interface Tkinter não foi executada em uma sessão gráfica durante esta entrega. Os testes de formatos e arquivos não substituem testes no NX. Use a lista de telas do [fluxo de revisão](FLUXO.md).

## Organização

- `usalia/`: código reutilizável e CLI.
- `usalia/data/`: mapa de caracteres e layouts estruturais.
- `profiles/`: offsets e contagens da base estudada.
- `docs/pt-BR/` e `docs/en/`: manuais equivalentes nos dois idiomas.
- `docs/research/`: inventário, validação, histórico AJ e proveniência.
- `tests/`: testes sem recursos do jogo.

O código novo e a documentação original usam MIT. O crédito da tradução de PC permanece com seu autor; o uso do programa não concede direitos sobre textos ou artes de terceiros.
