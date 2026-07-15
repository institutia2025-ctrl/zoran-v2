# ZORAN_MULTI_AGENT_MAILBOX_V1

## But
Canal commun durable entre CHATGPT, CODEX et CLAUDE. Il conserve les messages, accusés de réception, états et décisions liés à une mission et à un SHA précis.

## Lecture obligatoire
Avant toute action sur ZORAN V2, chaque agent doit lire dans cet ordre :
1. `AGENTS.md`
2. `SYNC/MAILBOX_PROTOCOL.md`
3. `SYNC/CURRENT_MISSION.json`
4. son état dans `SYNC/AGENT_STATE/`
5. `SYNC/mailbox/inbox.jsonl`
6. `SYNC/mailbox/acknowledgements.jsonl`
7. l’état GitHub réel : PR, base, head SHA, diff et CI.

Aucune action ni certification depuis la mémoire seule.

## Messages obligatoires
Passent par la mailbox : mission, priorité, nouveau SHA, PR, CI, demande d’audit, finding, verdict, correction, blocage, décision Fred, merge, tag, validation post-merge et fin de mission.

Ne pas y déposer les logs complets, commandes terminal intermédiaires, raisonnements internes ou répétitions sans changement d’état.

## Invariants
- Journal append-only.
- `MESSAGE_ID` unique.
- Mission, objet et SHA obligatoires.
- ACK explicite quand `REQUIRES_ACK=true`.
- Aucun agent ne modifie ni ne remplace le verdict d’un autre.
- Tout changement de SHA annule les audits antérieurs pour la certification courante.
- Tout désaccord est tranché par les faits, la falsification, l’impact global, la cohérence, sa cinématique et le futur probable.
- Aucun merge ou mutation produit sans autorisation explicite de Fred lorsque le contrat l’exige.

## COHERENCE_PULSE_V1
Tous les **quatre échanges opérationnels inter-agents** au maximum, ou immédiatement lors d’un changement critique de SHA, PR, CI, verrou ou verdict, CHATGPT diffuse un message court `COHERENCE_PULSE` à CODEX et CLAUDE.

Le pulse rappelle uniquement :
- mission active ;
- SHA exact à utiliser ;
- état réel vérifié ;
- règle principale ;
- verrou principal ;
- prochaine action ;
- interdictions actives.

Le pulse ne crée aucune nouvelle règle et ne remplace pas les preuves GitHub.

Si CHATGPT n’est pas actif, CODEX ou CLAUDE peut émettre le pulse après quatre échanges, sans modifier les verdicts existants.

## Format minimal du pulse
```json
{
  "MESSAGE_ID": "MSG-...-COHERENCE-PULSE",
  "TIMESTAMP": "ISO-8601",
  "FROM": "CHATGPT",
  "TO": ["CODEX", "CLAUDE"],
  "MISSION_ID": "...",
  "OBJECT_ID": "...",
  "SHA": "...",
  "TYPE": "COHERENCE_PULSE",
  "PRIORITY": "P1",
  "BODY": {
    "state": "...",
    "rule": "...",
    "lock": "...",
    "next_action": "...",
    "forbidden": ["..."]
  },
  "REQUIRES_ACK": false,
  "STATUS": "BROADCAST"
}
```

## Anti-idle
À réception d’un message actionnable : ACK dès lecture, puis action ou `BLOCKED` motivé. Le silence et les instructions périmées sont interdits.
