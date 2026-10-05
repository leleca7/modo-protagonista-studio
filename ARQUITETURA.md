# Arquitetura v0.3 — free-first

## Fluxo principal

1. **Briefing** — tema, público, duração, estilo, ambiente e Hz.
2. **Texto** — Ollama local gera o pacote; fallback existe sem IA.
3. **Originalidade** — similaridade textual contra histórico; se passar do limite, uma nova geração é solicitada.
4. **Visual** — arquivo enviado, biblioteca local ou fundo procedural.
5. **Voz** — Windows SAPI local.
6. **Mix/render** — FFmpeg local.
7. **Thumbnail** — Pillow local.
8. **Registro** — SQLite.
9. **Monitor de políticas** — snapshot/hash de páginas oficiais do YouTube.
10. **Publicação** — YouTube Data API via OAuth do próprio usuário.

## Botão GERAR TUDO

Executa em sequência: pacote criativo → voz → thumbnail → render. A publicação permanece separada para permitir revisão humana.

## Dados que não vão para o Git

`config.json`, `client_secret.json`, `token.json`, `output/`, banco SQLite, snapshots de políticas e biblioteca de mídia.

## Próximas camadas

- seleção de vozes instaladas;
- múltiplos masters de áudio para reduzir repetição em vídeos longos;
- gerador local opcional de imagens/loops;
- fila de produção;
- agendamento de upload;
- painel de métricas e testes A/B de thumbnail.
