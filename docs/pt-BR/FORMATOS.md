# Formatos binários observados

[English](../en/FORMATS.md)

Todos os números multibyte abaixo são little-endian, exceto os campos de IPS. Os leitores recusam dimensões, offsets ou comprimentos fora do arquivo. Campos não compreendidos são preservados.

## PS_FS_V1 NX

Cabeçalho: assinatura de oito bytes `PS_FS_V1`, seguida por `u64 count` em `0x08`. Diretório em `0x10`, com `count` registros de 64 bytes:

| Offset no registro | Tipo | Conteúdo |
|---:|---|---|
| 0 | char[48] | Nome ASCII terminado em NUL |
| 48 | u64 | Tamanho |
| 56 | u64 | Offset absoluto no contêiner |

Ao substituir uma entrada, a Usalia acrescenta o novo recurso alinhado a 512 bytes e altera somente tamanho/offset do registro. O conteúdo antigo permanece como bytes sem referência. Isso evita reordenar recursos ou perder mudanças anteriores, mas aumenta o tamanho. Não é uma compactação do arquivo.

## PSPFS_V1 PC

Assinatura `PSPFS_V1`; contagem `u32` em `0x08`; diretório em `0x10`; registro de 52 bytes: nome[40], campo opaco `u32` em +40, tamanho `u32` em +44, offset `u32` em +48. O campo opaco fica intacto. O gravador recusa ultrapassar o endereçamento de 32 bits.

## START

Versão NX sem compressão: `u32 count` no início, seguida por `count` offsets `u32` relativos ao início de START. O fim de uma entrada é o início da próxima; a última termina no tamanho do recurso. Foram observadas 107 entradas NX contra 98 PC. START não contém os nomes apresentados por ferramentas antigas.

A variante PC estudada começa com número de blocos e tamanho de bloco, seguidos pelos offsets de blocos IMY. Foram decodificados 882 blocos de até 131.072 bytes, totalizando 115.560.064 bytes. `decompress --format imy-package` trata essa variante. A Usalia não recomprime IMY.

## YKCMP

Cabeçalho de 20 bytes: `YKCMP_V1`, tipo `u32` em +8, tamanho comprimido incluindo cabeçalho em +12, tamanho descomprimido em +16.

Tipo 7 usa zlib. Tipo 4 usa literais e referências anteriores:

| Primeiro byte c | Operação |
|---|---|
| 1–127 | Copiar c bytes literais |
| 128–191 | comprimento `(c >> 4) - 7`; distância `(c & 15) + 1` |
| 192–223 | comprimento `c - 190`; distância `próximo_byte + 1` |
| 224–255 | próximos x,y: comprimento `((c & 31)<<4)+(x>>4)+3`; distância `((x & 15)<<8)+y+1` |

Cópias sobrepostas repetem os bytes produzidos. O encoder tipo 4 desta ferramenta escreve apenas literais: é válido e sem perda, mas pode ficar muito maior. Nunca substitua um bloco comprimido maior no mesmo espaço sem corrigir seu contêiner e seus tamanhos.

## NLTX / NMPLTEX1

Na variante validada: cabeçalho de 128 bytes; largura/altura `u32` em +24/+28; comprimento do bloco YKCMP em +48; YKCMP em +128; tipo 7/zlib, com BC1 tiled descomprimido.

Dimensões físicas: `pw=ceil(w/512)*512`, `ph=ceil(h/256)*256`. Tamanho BC1 `pw*ph/2`; bloco BC1 de 4×4 pixels possui 8 bytes. O código `block_indices` registra a fórmula exata de endereçamento, recuperada e testada com os arquivos do projeto. Não presumir que todos os NMPLTEX1 usam esse formato.

Ao importar, o editor compara imagem antiga/nova, recomprime somente os blocos de 4×4 alterados e preserva os bytes BC1 dos demais. BC1 é uma compressão com perda: exportação/importação sem edição é byte a byte idêntica; edição visual passa por nova compressão local.

## TX2

Cabeçalho de 16 bytes: largura `u16`, altura `u16`, formato `u16` (+4), campo opaco (+6), quantidade de cores `u16` (+8), quantidade de paletas `u16` (+10), campos restantes preservados.

Variantes suportadas: formato 16 com uma paleta de 16 RGBA e índices de 4 bits (nibble baixo primeiro); formato 256 com uma paleta de 256 RGBA e índices de um byte; formato 3 sem paleta com RGBA direto. Outras variantes, múltiplas paletas e swizzles desconhecidos são recusados. Paleta do TX2 usa RGBA, enquanto folhas HD abaixo usam ARGB; confundir a ordem troca as cores.

## Contêiner HD de START[96]

No recurso estudado, primeiros `u32`: tamanho de metadados sem 16 bytes, campo opaco, número de folhas, número de paletas, número de objetos. Objetos começam em +32. Cada objeto começa com seu tamanho `u32`, seguido por 12 campos `u16`; `header[0]` é ID, `[4]` número de paletas, `[5]` número de folhas. O tamanho do objeto permite avançar preservando comandos desconhecidos.

Após os objetos vem a tabela de descritores de 16 bytes `<HHHHII>`: formato, campo opaco, largura, altura, campo opaco, offset relativo ao início dos pixels. Primeiro as folhas, depois as paletas. Início dos pixels = primeiro `u32` +16. Foram confirmados: 669 objetos, tabela `0x32DF80`, dados `0x339B40`, 1.346 folhas e 1.658 paletas. Esses dois offsets são relativos ao recurso HD, não ao SUBDATA inteiro.

Folha com formato 256 nesse contêiner usa ARGB direto. Outras folhas do conjunto observado usam índices de um byte e paletas ARGB; o exportador converte para RGBA. A convenção não é a mesma do TX2, apesar do número 256 aparecer nos dois.

## zz_anmdat.fad

Na base estudada, quantidade de texturas `u32` em `0x0C`; descritores a partir de `0x430`, 32 bytes `<8I>`. Campos utilizados: tamanho em posição 2, offset na posição 4, largura/altura nas posições 5/6. O recurso de textura tem cabeçalho de 48 bytes seguido de YKCMP tipo 4. Depois da descompressão, variantes observadas: 1.024 bytes de paleta RGBA + índices de um byte, ou RGBA direto.

O FAD também possui layouts e recortes. Trocar palavras sem ajustar os recortes pode cortar letras; mover recortes sem respeitar os ícones pode ocultar botões. A ferramenta exporta texturas; a interpretação integral dos comandos de layout permanece trabalho de pesquisa.
