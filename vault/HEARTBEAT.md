# HEARTBEAT — Automações periódicas

Tarefas que o Cabeção executa automaticamente em ciclos ou horários fixos.

---

## Crons agendados

### Briefing matinal — 8h (BRT)
- Verificar tarefas pendentes em `0-Inbox/Inbox.md` (itens `- [ ]` sem data de conclusão)
- Clima atual em São Paulo
- Intenção do dia — pergunta curta e direta: *"O que precisa acontecer hoje pra o dia ter valido a pena?"*
- Tom: energético, direto, sem enrolação

### Check-in noturno — 21h (BRT)
- Perguntar como foi o dia, highlights, como Diego está se sentindo
- Se ele responder: criar ou atualizar `Journal/$(date '+%Y-%m-%d').md` com o conteúdo
- Se não responder em 30 min: não insistir

### Revisão semanal — domingo 10h (BRT)
- Compilar entradas de `Journal/` da semana
- Compilar reuniões de `Meetings/` da semana
- Gerar `Journal/weekly/YYYY-Www.md` com: resumo da semana, padrões observados, destaques, o que ficou pendente
- Enviar resumo no Telegram

---

## Heartbeat periódico (~30 min)

**Custo:** este ciclo não deve disparar RAG nem conversa longa. Preferir leitura de diretório + decisão mínima; se não houver nada novo em `Meetings/`, finalize com **`HEARTBEAT_OK` interno** sem mensagem ao Diego. Se **30 min** estiver gerando custo alto no gateway, na VPS reduza a frequência (ex.: 2–4 h) mantendo a mesma lógica — ver o guia `docs/economia-api.md` no repositório **cabecão**.

### 1. Novos arquivos em Meetings/
- Verificar se há arquivos novos desde o último ciclo
- Se houver: enriquecer com action items (se faltando) e notificar no Telegram

### 2. Sem ação necessária
- Responder `HEARTBEAT_OK` internamente (sem notificar o Diego)
