# Contribuir / Contributing

**PT-BR:** informe edição, idioma, versão, Title ID, Build ID, comando executado, erro, tamanhos e SHA-256. Para problemas visuais, indique tela, variante e recorte. Use amostras mínimas sintéticas nos testes. Registre se um resultado foi confirmado nos bytes, por imagem ou no NX. Não transforme uma hipótese em fato. Novos layouts devem incluir limites, testes negativos e um round-trip sem alterações. Não envie dumps do jogo, executáveis, chaves ou traduções de terceiros sem autorização.

**English:** report edition, selected language, version, Title ID, Build ID, exact command/error, file sizes and SHA-256. Visual reports should identify the screen, variant and crop. Prefer minimal synthetic test fixtures. Label evidence as binary, visual or NX-confirmed; distinguish hypotheses from facts. New layouts need bounds checks, negative tests and an unchanged round-trip. Do not submit game dumps, executables, keys or unauthorized third-party scripts.

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python -m usalia --help
```

Document new findings in both `docs/pt-BR/` and `docs/en/`. Append build-specific data to a separate profile; do not replace existing offsets with those from a different build. Keep interface changes local and avoid modifying gameplay parameters while localizing text.
