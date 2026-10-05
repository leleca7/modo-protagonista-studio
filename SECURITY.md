# Segurança

Nunca faça commit dos seguintes arquivos:

- `client_secret.json`
- `token.json`
- `.env`
- configurações com chaves privadas
- cookies de navegador
- arquivos do banco local
- renders e mídia privada do canal

O projeto foi desenhado para manter credenciais no computador do usuário. Se uma credencial for publicada por engano, revogue-a imediatamente no provedor correspondente e gere uma nova.
