# Imagens, animações, capítulos e nomes

[English](../en/IMAGES_AND_SCENES.md)

## Nem todo texto de cena é legenda de vídeo

Os trechos narrativos como a introdução de Laharl são compostos por animações e texturas. Procurar apenas strings em script.dat ou arquivos de vídeo não os encontra. A análise histórica percorreu 48 ANM da raiz de SUBDATA e 379 folhas de textura legadas. Foi necessário localizar a versão HD efetivamente usada no NX.

O principal caso foi ANM31: trocar só seu recurso legado não ativou a mudança na v4. A versão HD correspondente está no contêiner de START[96]. A associação por IDs foi recuperada e revalidada nesta ferramenta; veja `docs/research/anm-hd-crosswalk.json`. Não confundir **índice do objeto**, **ID do recurso**, **índice da folha** e **índice de textura do FAD**.

## Narrações localizadas

Índices começam em zero. O objeto HD pode organizar vários quadros em uma única folha, enquanto o legado possui duas folhas/camadas.

| Cena | Recurso legado e localização | ID HD | Índice HD em START[96] |
|---|---|---:|---:|
| Introdução de Laharl / Krichevskoy | `anm31.dat`, objeto 0, folhas 0–1 | 5002 | 337 |
| Apresentação de Celestia | `anm02.dat`, objeto 1, folha 0 | 5017 | 352 |
| Lua vermelha e mãe de Laharl | `anm08.dat`, objeto 0, folhas 0–1 | 5003 | 338 |
| Canção da lua vermelha | `anm08.dat`, objeto 1, folhas 0–1 | 5004 | 339 |
| Epílogo da corte de Laharl | `anm10.dat`, objeto 0, folha 0 | 5005 | 340 |
| Decisão de ir a Celestia | `anm14.dat`, objeto 0, folha 0 | 5006 | 341 |
| Flor, silêncio e passagem de anos | `anm14.dat`, objeto 1, folha 0 | 5007 | 342 |

As sete folhas HD acima foram conferidas visualmente na base v6. São indexadas, formato HD 265; a entrada de importação aceita as cores da paleta original. As seis sequências adicionais e a introdução somaram 34 quadros gráficos na revisão do projeto.

Na comparação entre os backups original/traduzido de PC fornecidos, somente ANM31 diferia. Os outros 47 ANM eram idênticos entre essas duas fontes; após descompressão, coincidiam com os recursos correspondentes da base NX v3. Portanto, aquelas seis sequências adicionais não tinham PT-BR para copiar nesse material de PC. Foram traduzidas para o projeto de Ren com terminologia harmonizada com os diálogos. Isso não estabelece a situação de todas as traduções de PC existentes.

```sh
# Primeiro extraia start.dat do SUBDATA usando archive-extract; o nome terá prefixo do índice.
python -m usalia start-extract workspace/start.dat workspace/start-slots
python -m usalia hd-list workspace/start-slots/096.bin --json workspace/hd-index.json
python -m usalia hd-export workspace/start-slots/096.bin 337 0 workspace/intro.png
# Edite a imagem mantendo dimensões, paleta e os recortes de cada frase.
python -m usalia hd-import workspace/start-slots/096.bin 337 0 workspace/intro_editada.png workspace/096_editado.bin
python -m usalia start-replace workspace/start.dat 96 workspace/096_editado.bin workspace/start_editado.dat
python -m usalia archive-replace workspace/SUBDATA.DAT start.dat workspace/start_editado.dat workspace/SUBDATA_cenas.DAT
```

`start-extract` pode consumir memória/espaço considerável por conter centenas de MB de recursos. Não realoque os quadros da folha arbitrariamente: os comandos da animação usam seus recortes.

## Outros textos gráficos inventariados

- `anm01–10`, `anm12–13`: títulos, Episode, End e To be continued repetidos nas folhas legadas.
- `anm16–19`: títulos do modo Etna em variantes ENG/JP.
- `anm12`, objeto 3, folha 0: identificação Space Battleship GARGANTUA.
- `anm20`, objeto 1, folha 0: apresentação/copyright.
- `anm21–22`: créditos gráficos.
- `anm51–60` e `anm63`: capturas usadas em prévias, com textos embutidos como nomes, indicadores de batalha e uma fala de Gordon em `anm59`, objeto 4, folha 0.
- Marcadores técnicos NO DATA em folhas de personagens não foram classificados como narração.

Traduzir uma palavra de interface ao vivo não altera a mesma palavra incorporada a uma captura de prévia. São recursos diferentes. O inventário não certifica todas as legendas de eventuais vídeos nem condições de ativação de todos os finais.

## Cartões de capítulos

Os 18 cartões usados no NX estão em `new_bg051–068.nltx`, e Next Episode em `new_bg071.nltx`. Imagens legadas com títulos também existem nos ANM, mas não substituem automaticamente os NLTX ativos. Os nomes exibidos em salvar/carregar/excluir vêm de outra tabela no main; devem seguir o mesmo glossário das artes.

Na campanha de Etna, as quatro artes correspondem a episódios 1, 2, final e continuação do final. No projeto PT-BR, a fonte textual principal foi Disgaea PC de Li Qiye. As 18 imagens e a tabela de salvamento foram comparadas na v8. Não gerar títulos novamente a partir de uma tradução literal do inglês se a comunidade já aprovou outra terminologia.

```sh
python -m usalia texture-export workspace/new_bg071.nltx workspace/next.png --format nltx
python -m usalia texture-import workspace/new_bg071.nltx workspace/next_editado.png workspace/new_bg071_editado.nltx --format nltx
python -m usalia archive-replace workspace/SUBDATA.DAT new_bg071.nltx workspace/new_bg071_editado.nltx workspace/SUBDATA_next.DAT
```

Qualidade: renderizar letras em resolução maior e reduzir com antialiasing produz contornos melhores que ampliar um recorte pequeno. Preserve forma, posição, sombra, borda, cor e entrelinhas. Não acumule uma camada nova sobre a palavra antiga. Em Próximo Episódio, preservar a inicial maior colorida e o restante branco. A v9 só suavizou recortes e não resolveu satisfatoriamente; a v10 redesenhou contornos. Sempre confira o PNG **decodificado de volta do arquivo final**, pois BC1 pode modificar bordas.

## Nomes acima dos diálogos

START[92] contém um atlas 512×4096 de 256 cores. A versão legada observada em START[25] mede 128×1024 com 16 cores; não confiar no nome histórico desse slot para deduzir a função. Os rótulos são arte, não necessariamente strings do banco `name_e.dat`.

Foram encontrados 50 rótulos, 49 distintos, incluindo Noble Demon duas vezes. A fonte PC fornecida também os mantinha em inglês. Os nomes/apelidos estão em `docs/research/speaker-labels.json`. A Usalia registra os textos originais para revisão, sem impor a tradução de nomes de personagens ou apelidos a outros idiomas.

Um PNG com novas cores é recusado pelo importador TX2 indexado. Prepare a arte usando a paleta original ou estude explicitamente a substituição de paleta. Compare todos os recortes referenciados antes de aumentar a palavra.

## Cores, transparência e margens

O projeto apresentou troca de cores na logo: confundir RGBA com ARGB é uma causa técnica possível que deve ser verificada nos bytes, não inferida só pela foto. O contêiner HD armazena ARGB; TX2/FAD observados usam RGBA. Alfa zero não é fundo preto. Compare em fundo claro, escuro e no jogo.

Barras de comandos têm variantes, ícones e recortes próprios. Restaurar só metade de `〈 〉` ou pintar por cima de A/B/Y destrói o controle. Remova a arte antiga somente na região da palavra, mantenha os pixels dos ícones e ajuste também as margens/crops quando o texto se alongar. A linha preta externa das barras da loja foi removida tornando transparentes apenas as fileiras defeituosas, sem redesenhar a moldura.
