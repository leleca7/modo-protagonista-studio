# Changelog

## 0.3.0 — 2026-10-05

- Repositório oficial inicial do Modo Protagonista Studio.
- Novo botão **GERAR TUDO** no painel.
- Pré-checagem de espaço livre em disco.
- Confirmação adicional para renders de 8h/11h.
- `INSTALAR.bat` implementado para criar ambiente virtual e instalar dependências.
- Instalador pode oferecer FFmpeg pelo `winget` quando disponível.
- Documentação consolidada em modelo free-first.

## 0.2.0 — 2026-10-03

- Painel único com abas: Novo vídeo, Biblioteca, Histórico, Regras e Configurações.
- 60 afirmações em 6 blocos.
- Similaridade local contra projetos recentes e regeneração automática quando o limiar é ultrapassado.
- Fundo procedural automático, biblioteca local e uploads.
- Thumbnail usando o fundo do projeto.
- Pipeline separado para criação, voz, thumbnail e render.
- Banco SQLite com status, caminhos dos arquivos e ID do YouTube.
- Upload resumível ao YouTube via OAuth.
- Monitor de páginas oficiais do YouTube.
