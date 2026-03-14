# HEARTBEAT — Automações a cada 30 min

Tarefas que o Cabeção (OpenClaw) executa a cada ciclo de heartbeat (~30 min).

---

## 1. Novos arquivos em Meetings/

- Verificar se há novos arquivos em `Meetings/` (ex.: export do Granola via sync).
- Se houver arquivo novo: enriquecer com action items se estiver faltando e notificar no Telegram.

## 2. (Opcional) Voice Memos / outra pasta de sync

- Se no futuro houver upload automático de áudio para uma pasta na VPS, verificar essa pasta e processar (transcrever → classificar → salvar no vault).

## 3. Resposta padrão

- Se não houver nada a fazer neste ciclo: responder `HEARTBEAT_OK`.
