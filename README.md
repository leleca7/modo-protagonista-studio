# ✨ Modo Protagonista Studio v0.3

Painel local **free-first** para centralizar a produção de vídeos do canal Modo Protagonista: briefing → texto → voz → visual → thumbnail → render → revisão → YouTube.

## Objetivo

Reduzir ao mínimo a troca entre ferramentas e evitar mensalidades desnecessárias. O núcleo funciona no próprio computador. Quando houver opção local adequada, ela é preferida a uma API paga.

## O que já funciona

- Painel local em **Streamlit**.
- Botão **GERAR TUDO** para encadear pacote criativo, voz, thumbnail e render.
- IA de texto via **Ollama local**, sem cobrança por prompt.
- Fallback local quando o Ollama estiver desligado.
- 60 afirmações organizadas em 6 blocos.
- Triagem de similaridade com projetos anteriores e regeneração local.
- Voz gratuita via **Windows SAPI**.
- Fundo procedural local e biblioteca de fundos/sons.
- Frequências geradas pelo **FFmpeg**.
- Thumbnail local.
- Render MP4 de 1 min, 11 min, 1h, 8h e 11h.
- Histórico local em SQLite.
- Monitor de mudanças em páginas oficiais do YouTube.
- Upload ao YouTube por OAuth, com `private` como padrão.
- Checagem de espaço livre em disco.

## Instalação no Windows

1. Baixe/clonar este repositório.
2. Execute `INSTALAR.bat`.
3. Para ativar IA local, instale o Ollama e rode:

```bash
ollama pull qwen3:4b
```

4. Execute `ABRIR_MODO_PROTAGONISTA.bat`.
5. Comece com **1 minuto (teste)**.

## Custos

O núcleo não exige assinatura de automação nem API paga:

- Streamlit: local/gratuito
- Ollama: local/gratuito
- Windows SAPI: local/gratuito
- FFmpeg: gratuito/open source
- SQLite: local/gratuito
- Pillow: gratuito/open source
- YouTube Data API: usa a quota da conta Google, sem cobrança por prompt

Serviços externos pagos podem ser adicionados no futuro **somente como opcionais**.

## Segurança

Nunca envie para o GitHub: `client_secret.json`, `token.json`, `config.json` com segredos, banco de projetos, renders ou biblioteca de mídia privada.

> Repositório privado é recomendado para este projeto.

## Princípio editorial

A automação não deve tentar enganar sistemas de detecção. Variação existe para oferecer conteúdo realmente distinto: texto, progressão, visual, áudio e metadados devem mudar de forma material para a pessoa que assiste.
