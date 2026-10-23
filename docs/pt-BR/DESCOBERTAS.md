# Descobertas, regressões e limites de conhecimento

[English](../en/FINDINGS.md)

## Conhecimento preservado

1. O texto ENG observado é CP932/fullwidth; o CSV deve continuar legível em Unicode.
2. A solução nativa de 48 acentos foi confirmada no NX. O método antigo PUA não é o mesmo método.
3. Há texto dentro de bancos, bytecode, script externo, executável, texturas, capturas de prévia e camadas de animação. Nenhuma busca isolada cobre tudo.
4. PC e NX diferem em contêiner, compressão, contagens, conteúdo, parâmetros e controles. Copiar o SUBDATA PC inteiro altera mais que a linguagem.
5. ANM legado pode ter contraparte HD com o mesmo ID de recurso; a substituição precisa chegar ao caminho ativo.
6. O texto do título do capítulo existe em arte e no main. Corrigir só uma dessas partes deixa salvar/carregar/excluir incoerentes.
7. Em tabela realocada, corrigir apenas o ponteiro é insuficiente quando o loader reaplica o addend RELA.
8. Barras têm variantes: editar uma textura visualmente parecida pode não alterar a tela testada.
9. Maior frase requer revisar largura, seleção, crops e posição do painel vizinho. Aumentar só uma moldura pode deixar sobreposição.
10. A aprovação é por tela/revisão; não demonstra que todos os finais e contextos foram verificados.

## Casos do catálogo AJ

| Caso | Evidência / correção |
|---|---|
| AJ01 | Conversão de acentos nativos mantida; requer IPS |
| AJ03 | Enciclopédia tinha sobras ENG; limpar o restante do slot, preservar nomes |
| AJ04 | Loja de música: 39 de 41 títulos alterados na etapa registrada; IDs BGM/preços preservados |
| AJ836–838 | Opções completas de ordenação exigiram quadro/seleção maiores e deslocamento local da lista de personagens |
| AJ841 | Restaurar caminho e posição originais de desenho, usar Sim/Não; depois ampliar margem esquerda 20 px |
| AJ842 | Recuperar ícone completo `〈 〉` e limpar resíduos entre ele e Mochila/Depósito |
| AJ844 | Remover traços antigos sobrepostos; separar texto de Y; ajustar margem |
| AJ846 | A variante inicial não era a ativa; B foi recuperado na textura FAD 298; setas separadas de Selecionar |
| AJ847 | Mover aproximado 12 px das setas, mantendo letras e ícones |
| AJ848 | Crash no 50Q: SUBDATA truncado, 20 texturas apontavam além do fim; reconstrução a partir da base 50P íntegra com alterações desejadas reaplicadas |
| AJ849 | Barra de reorganização: borda direita +24 px e grupo inteiro +12 px à direita |
| AJ850 | Somente duas fileiras pretas externas tornadas transparentes; molduras preservadas |
| AJ851 | Três palavras da criação copiadas da referência da Assembleia na textura 6; ícones intactos |

Os 851 registros completos estão em `docs/research/aj-history.csv` e JSON. As descrições PT originais foram mantidas como registro primário; as chaves são em inglês para facilitar processamento. Algumas linhas são tentativas substituídas ou aguardavam teste na data do histórico. Não são uma lista de 851 patches aplicáveis automaticamente. Os números AJ não são índices de textura.

## Revisões v4–v10

| Revisão | Conhecimento técnico |
|---|---|
| v4 | Introdução exigiu o recurso HD ativo, não só ANM31 legado |
| v5 | Seis sequências gráficas adicionais traduzidas; compatibilidade de termos revisada com PC |
| v6 | Fonte P052 Bold (URW Base 35) usada nos 34 quadros narrativos para aproximar a aparência original |
| v7 | 18 cartões NLTX e Next Episode traduzidos |
| v8 | Títulos de salvar/carregar/excluir harmonizados; ponteiros + RELA atualizados; pontuação do capítulo 10 revista |
| v9 | Refinamento das artes; Save? → Salvar?; Next Episode continuou pouco satisfatório segundo Ren |
| v10 | Contornos de Próximo Episódio redesenhados; Default → Padrão; demais arquivos da v9 preservados |

A v10 tinha verificação binária e de integridade; teste visual final no NX permanecia pendente no momento da criação da Usalia. Ela não transforma automaticamente todas as etapas históricas em suporte universal da ferramenta.

## Diagnóstico rápido

| Sintoma | Verificar |
|---|---|
| Mudança não aparece | Recurso ativo HD/legado; idioma; variante; caminho de instalação; outro patch sobrescrevendo |
| Japonês no lugar de acento | Mapa gravado, IPS ativo, Build ID e fontes corretas |
| Crash ao abrir tela | Limites de todos os registros; tamanho final; ponteiros FAD/HD; truncamento; sobreposição de mods |
| Últimas letras em inglês | Campo não limpo; padding incorreto; recorte gráfico sobreposto |
| Título só muda no PNG | Tabela no main e relocação RELA ainda antigas |
| Texto fora da moldura | Largura/crop/escala e painel vizinho, além do slot em bytes |
| Ícone sumiu | Região pintada sobre botão; fonte de arte PC com controle diferente; variante errada |
| Cores trocadas | Ordem RGBA/ARGB e índice de paleta; não diagnosticar só por foto |
| Letras serrilhadas | Resolução de origem, máscara alfa, antialiasing e compressão BC1 final |
| Exportador não acha uma frase | Pode ser imagem ou main; pode haver controles fora da heurística |

## O que ainda não foi certificado

Não há disassembler completo do bytecode, editor visual completo de todos os comandos FAD, recompressor IMY otimizado, adaptação automática para outro Build ID, port automático de todas as traduções de PC, renderização de qualquer alfabeto, inventário integral de todos os vídeos ou revisão de todas as rotas do jogo. Essas limitações são registradas para que novas comunidades saibam onde continuar a pesquisa.
