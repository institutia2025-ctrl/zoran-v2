TIMESTAMP: 2026-07-16T08:35:39.0654122+02:00

# Manifeste ordonné — ZMOS V2 Integration Contract

ID: ZMOS-V2-CONTRACT-EXPORT-MANIFEST-001  
META_ID: META-ZMOS-V2-CONTRACT-EXPORT-MANIFEST-001  
TRACE_ID: TRC-ZMOS-V2-GLOBAL-COHERENCE-20260716-001  
RUN_ID: RUN-20260716-083539  
MISSION_ID: ZMOS_V2_INTEGRATION_CONTRACT_EXPORT  
AI_ACTOR_ID: Codex-Auditeur  
GUARD_IDS: SOURCE_BYTES_UNCHANGED, ORDERED_MANIFEST, ARCHIVE_READ_ONLY, NO_REPOSITORY_TOUCH  
TARGET_AUDIT: ChatGPT / GLOBAL_COHERENCE  
STATUS: PROUVÉ

## Archive

- Chemin : `ZMOS_V2_INTEGRATION_CONTRACT_20260716_GLOBAL_COHERENCE.zip`
- Format : ZIP
- Nombre d’entrées : 14
- Taille : 20317 octets
- SHA-256 : `E1B3A795D606978CA6BC8B0CD7D6F344DC3B1EEC158BF25FC8BE5FEA8DEFB9F9`
- Protection locale : attribut Windows `ReadOnly=true`
- Portée d’immuabilité : toute altération produit un SHA différent; l’attribut local interdit l’écrasement accidentel. Aucun stockage WORM matériel n’est revendiqué.

## Inventaire contractuel ordonné

| Ordre | Chemin relatif | Taille (octets) | SHA-256 | Rôle contractuel |
|---:|---|---:|---|---|
| 1 | `EXISTING_ZMOS_ARCHITECTURE.md` | 2340 | `2BDB26B42D492F71704EBED4F10C4C8A8DA479E8D0FBA408589E80E902243325` | Figer l’architecture ZMOS existante, les flux réels et les frontières de confiance. |
| 2 | `HISTORICAL_STORE_PROTECTION_POLICY.md` | 2459 | `9807E44388B40F367EC6BE01EA27255A740006A8D19B040AC12A4E4EA8BAA267` | Interdire toute mutation runtime du store historique et encadrer la promotion supervisée. |
| 3 | `TRANSACTIONAL_STORE_CONTRACT.md` | 2549 | `76ABF98A6DD103DACFE0021D29B966272276D8595EB957A41BA599D250C99BCA` | Définir le store transactionnel distinct, ses états, invariants et interfaces. |
| 4 | `ZORAN_ZMOS_READ_BRIDGE_CONTRACT.md` | 2085 | `09F718C44856E8B717805F424DE2049BA6D3FD00B8A15337E5ADBCFD2AADB81E` | Imposer la vérification SHA, schéma, identité, provenance et le fail-closed en lecture. |
| 5 | `ZORAN_ZMOS_WRITE_BRIDGE_CONTRACT.md` | 2553 | `97E2C4827E4F6DB879597E165EDDB784C5A67C08CAA3FFDE9B03ACD17D9A7856` | Définir le writer externe unique, l’atomicité, l’idempotence et le comportement DOWN. |
| 6 | `OBJECT_AND_RELATION_SCHEMAS.md` | 2449 | `5CDEC3D1B944E9C19E91A04266130B9FB95A0E14DBECD5191AA2670B6E887EEF` | Définir les enveloppes minimales des objets moteurs et des relations scellées. |
| 7 | `IDENTITY_AND_PROVENANCE_POLICY.md` | 2216 | `141DB56D07189469AF7E882BE2698E8B0CA55EEAB10CC43EFB32FCFE75CCC4B4` | Définir identités, autorités, provenance résolue, collisions et complétude du lineage. |
| 8 | `ATOMICITY_AND_RECOVERY_MODEL.md` | 2151 | `F7F529592BA701249B585A4A2273DC987926CF9003444BB9E42B3E4B5D800D37` | Définir machine d’état, ordre de commit, recovery et menaces de corruption. |
| 9 | `RECONSTRUCTION_CONTRACT.md` | 2033 | `94D29BEEB70B005EFD56EE88B73F217B0D55405B28C6948704C17BCADC6C44EE` | Spécifier `reconstruct_run(RUN_ID)` et la preuve de complétude exacte. |
| 10 | `MIGRATION_PLAN.md` | 4063 | `82EA4DA35C171DBDC56B43A790EF40F6BE0CF229C75E22FC377649A75DBBA7E2` | Challenger et gater les LOTS 0 à 10 avec PASS/FAIL, rollback et GO Fred. |
| 11 | `RED_TEST_PLAN.json` | 3570 | `1F84BDF87799E47EBB79539E87628C7BCE7B3581CE97BF1AAAF865BF9C5502D5` | Énumérer les 20 tests rouges P0/P1/P2 exigés avant et pendant la construction. |
| 12 | `GLOBAL_IMPACT_BEFORE_BUILD.md` | 2215 | `45395B8D62871BF35B64C6219340869FFFD5E0E7473460BC798123C84759B36C` | Cartographier gains, coûts, blast radius et décisions bloquantes avant build. |
| 13 | `IMPLEMENTATION_ROADMAP.md` | 1978 | `EADD9623CCCD7E1FDEDF987B50ED54CF2D7E0D173BCEF9E6C98CD0B031B2DB9C` | Ordonner l’implémentation conditionnelle et les validations indépendantes. |
| 14 | `EXECUTIVE_SUMMARY.md` | 1717 | `8B41A69068739127DE20C1CE7294B885EA69406877ADB1325F370F187A5BFEBA` | Donner la décision exécutive, les verrous et l’ordre de construction autorisable. |

## Contrôle de remise

L’audit cible doit vérifier d’abord le SHA de l’archive, puis les 14 tailles et SHA ci-dessus. Il doit rendre `GLOBAL_COHERENCE` sans modifier l’archive, sans produire de GO implicite et sans interpréter `FIX_REQUIRED` comme autorisation de coder.

ROLLBACK: supprimer uniquement le dossier d’export après décision explicite Fred; les 14 sources restent inchangées.  
LOOP_STATUS: aucune boucle détectée; export unique fondé sur un corpus déjà scellé.

