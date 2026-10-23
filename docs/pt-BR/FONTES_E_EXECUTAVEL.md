# Fontes, acentos e executável

[English](../en/FONTS_AND_EXECUTABLE.md)

## A solução efetivamente confirmada

O texto ENG usa CP932/Shift-JIS e frequentemente letras ASCII convertidas para fullwidth. Uma leitura em codificação errada parece japonês sem sentido. O CSV da Usalia usa Unicode normal; a conversão ocorre apenas ao gravar.

A solução aprovada usa **48 portadores CP932 regulares**, remapeados para Unicode nativo por IPS. Os glifos necessários já estavam nas fontes originais; não foi necessário substituir o bitmap da fonte para essa solução. As tentativas antigas com PUA/fonte modificada são históricas e não devem ser confundidas com o método funcional.

Exemplo de `ã`: o CSV contém U+00E3; o gravador escreve `8B 8F`, portador CP932 `居`; a entrada da tabela de conversão em `0x20CB34` (2.149.172) da imagem de análise passa a devolver U+00E3; a fonte desenha `ã`. Não significa que todo kanji do jogo possa ser substituído sem colisão.

O campo `unicode_table_offset` do JSON é um endereço relativo à memória; some **0x100** para obter o offset IPS/imagem de análise. Essa diferença foi confirmada comparando o IPS histórico com o main original.

O mapa completo está em `usalia/data/ptbr-carriers.json`: caractere, portador, bytes CP932, offset da tabela, Unicode e GID histórico. O campo GID vem do registro de pesquisa e não é um substituto para analisar a fonte de outra edição.

```sh
python -m pip install -e ".[nso]"
python -m usalia nso-memory workspace/main workspace/main.memory.bin
python -m usalia accent-patch workspace/main.memory.bin workspace/81F7AB934AD9A6DC823F64A10E12C93C.ips
python -m usalia text-export workspace/SUBDATA.DAT workspace/bancos.csv --kind banks --mapping ptbr
# Após editar translation:
python -m usalia text-check workspace/SUBDATA.DAT workspace/bancos.csv --mapping ptbr
python -m usalia text-build workspace/SUBDATA.DAT workspace/bancos.csv workspace/SUBDATA_PT.DAT --mapping ptbr
```

O gerador verifica assinatura, Build ID, segmentos descomprimidos e os valores anteriores de cada entrada. `nso-memory` produz uma imagem de análise com cabeçalho de 0x100 bytes e segmentos nos endereços virtuais; ela **não deve ser instalada como main**. O IPS usa offsets desse espaço de análise. Não usar offsets do NSO comprimido como se fossem endereços virtuais.

A rotina CP932 foi registrada historicamente em `0x101CF8` e a região de tabela em `0x20BAE8`. Os offsets individuais do JSON são a evidência utilizada pelo gerador. Os endereços históricos da rotina/região são referências de pesquisa em memória; não misture essa convenção com os offsets de arquivo abaixo. Todos são específicos do build ENG estudado; não aplicar ao JP por semelhança.

## Outros idiomas

Para um alfabeto latino adicional, identifique glifos já presentes, caracteres portadores não utilizados e a entrada correspondente da tabela. Um mapa customizado JSON pode associar cada caractere a dois bytes CP932. O gravador pode utilizá-lo, mas você deve gerar e validar o IPS e verificar colisões com os textos que permanecem no idioma original.

Se o alfabeto não existir na fonte, apenas modificar CP932 não o cria. Será necessário estudar os registros da fonte, incluir glifos e métricas e revisar a renderização. A Usalia 1.0 não automatiza esse processo nem certifica alfabetos árabe, cirílico ou CJK completos. RTL, ligaduras e combinação de marcas exigem estudo próprio.

## font.bin

Na fonte examinada: 16.800.276 bytes; atlas 4096×4096 de um canal no fim; células 64×64; contagem em `0x18`; registros de 24 bytes a partir de `0x40`; 914 registros; atlas em `0x5A14` (23.060). Esses valores foram rechecados nos arquivos locais. Outras fontes devem ser inspecionadas separadamente.

```sh
python -m usalia font-info workspace/font.bin --atlas workspace/font-atlas.png
```

## Strings e desenho no main

Vários menus, mensagens de batalha, títulos de salvamento e opções estão no executável. Não são encontrados traduzindo apenas os bancos. A largura gráfica depende da rotina, da escala e dos recortes, além do número de bytes. Ajustes devem ser locais: uma mudança global de escala pode prejudicar telas já aprovadas.

Descobertas do build analisado, em offsets da imagem com cabeçalho de 0x100:

| Dado | Offset / observação |
|---|---|
| Pool de 18 títulos de capítulos | `[0x1BBE87, 0x1BC0E5)`, 606 bytes |
| Ponteiros dos títulos | `0x23FC40 + 8*i`, i=0..17 |
| Addend RELA de cada título | `0x169450 + 24*i` |
| Tipo de relocation observado | AArch64 RELATIVE, 1027 |
| Pergunta `Save?` | `0x1C4600`; slot fullwidth original de 11 bytes com NUL |
| Opção `Default` | `0x1BF9CF`; slot fullwidth original de 15 bytes com NUL |

A tabela de ponteiros armazena endereço de memória, por isso o valor corresponde ao offset do arquivo menos `0x100`. Alterar só o ponteiro sem o addend RELA não bastou: o carregador reescreve o destino. A correção v8 atualizou ambos e simulou a relocação antes de ler os 18 títulos.

Use `patch-manifest` para gravar alterações pesquisadas com SHA-256 e bytes anteriores. O manifesto não descobre automaticamente ponteiros nem instruções ARM64. O comando recusa strings que ultrapassem o slot e alterações sobrepostas. Modelo: `examples/binary-edit.example.json`.

## Consolidar IPS

As categorias históricas eram Unicode, Interface, Batalha, Batalha complementar, Correções, Nomes e Enciclopédia. A perda de uma delas fez reaparecer problemas já resolvidos. União por byte, com detecção de conflito, é mais confiável que escolher o arquivo mais novo pelo nome.

```sh
python -m usalia ips-info workspace/patch.ips
python -m usalia ips-merge workspace/acentos.ips workspace/interface.ips --out workspace/consolidado.ips
```

Se houver conflito, a Usalia interrompe. Compare os bytes e a finalidade de cada revisão; não usar “último vence” às cegas. Para distribuição, o IPS deve voltar ao nome do Build ID correto.
