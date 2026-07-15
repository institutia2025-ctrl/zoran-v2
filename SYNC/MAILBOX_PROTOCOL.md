# ZORAN_MULTI_AGENT_MAILBOX_V1

## But
Canal commun durable entre CHATGPT, CODEX et CLAUDE. Le canal conserve les messages, accusés de réception, états et décisions liés à une mission et à un SHA précis.

## Lecture obligatoire
Avant toute action sur ZORAN V2, chaque agent doit lire dans cet ordre :
1. `AGENTS.md`
2. `SYNC/CURRENT_MISSION.json`
3. son état dans `SYNC/AGENT_STATE/`
4. `SYNC/mailbox/inbox.jsonl`
5. `SYNC/mailbox/acknowledgements.jsonl`
6. l'état