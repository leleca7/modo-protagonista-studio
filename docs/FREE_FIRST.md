# Política free-first

O Studio deve preferir uma alternativa local ou gratuita sempre que ela for tecnicamente adequada.

| Função | Padrão atual | Custo obrigatório |
|---|---|---:|
| Texto/afirmações | Ollama local | R$ 0 por prompt |
| Fallback de texto | regras/templates locais | R$ 0 |
| Voz | Windows SAPI | R$ 0 |
| Render/mix | FFmpeg | R$ 0 |
| Thumbnail | Pillow | R$ 0 |
| Banco | SQLite | R$ 0 |
| Painel | Streamlit local | R$ 0 |
| Versionamento | GitHub | conforme o plano da conta |
| Publicação | YouTube Data API/OAuth | sem cobrança por prompt |

## Regra para novas integrações

1. Procurar primeiro uma opção local/open source.
2. Se não houver qualidade suficiente, permitir serviço externo apenas como alternativa opcional.
3. Nunca tornar uma API paga requisito sem decisão explícita do usuário.
4. Nunca commitar chaves, tokens, cookies ou credenciais.
5. O ChatGPT pode alterar o código no GitHub quando solicitado, mas o programa autônomo não usa a conversa do ChatGPT como uma API gratuita.
