Grupp: Hanna Sjögren, Theodor Bardeman och Carl Jepsen

Git memo: hannasjogren, TBard05 och MrPhail

# Filstruktur och konfiguration för `b_projekt`

Detta projekt är en datadriven pipeline som hanterar transaktionsvalidering, valutakonvertering och databashantering med Prefect och Alembic. Nedan hittar du en översikt över filstrukturen samt instruktioner för att konfigurera databasen och filvägar. Det finns kommenterat i filerna vart man själv behöver uppdatera till sin egna databas URL och filväg.

---
## Projektets struktur

## Beskrivning av mappar och filer

## `DB_tables_data_export_to_csv_files/`  
Innehåller exporterade databas-tabeller i CSV-format.

| Fil | Beskrivning |
|------|------------|
| `accounts.csv` | Bankkonton och tillhörande IBAN-nummer. |
| `blacklist.csv` | Svartlistade konton och transaktioner. |
| `customers.csv` | Kundregister med personuppgifter. |
| `export_files.py` | Skript för att exportera tabeller till CSV-format. |
| `pending_transactions.csv` | Transaktioner som är under behandling. |
| `transactions.csv` | Fullständig transaktionshistorik. |

---

## `Data/`  
Lagrar inmatningsdata och dataset för transaktionsanalys.

| Fil | Beskrivning |
|------|------------|
| `accounts.csv` | Konto- och IBAN-data. |
| `blacklist.py` | Modul för hantering av svartlistade konton. |
| `customers.csv` | Kundregister kopplat till transaktionsdata. |
| `sebank_customers_with_accounts.csv` | Dataset med bankkunder och kontouppgifter. |
| `split_customers_account.py` | Skript för att separera kund- och konto-data. |
| `transactions.csv` | Transaktionshistorik med detaljerad information. |

---

## `Exports/`  
Innehåller exporterade transaktionsdata och analyser.

| Fil | Beskrivning |
|------|------------|
| `blacklist.csv` | Exporterad lista med svartlistade konton. |

---

## `Logs/`  
Loggar felsökning och spårning av pipelineflödet.

| Fil | Beskrivning |
|------|------------|
| `blacklist_export.log` | Loggar för export av svartlistade konton. |
| `blacklist_import.log` | Loggar för import av svartlistade konton. |
| `fraud_detection_test_logs.log` | Loggar från bedrägeridetektion. |
| `timestamp_test_logs.log` | Loggar för tidsstämplar och datavalidering. |
| `validation_test_logs.log` | Loggar för transaktionsvalidering. |

---

## `Models/`  
Databasmodeller för att hantera kund-, konto- och transaktionsdata.

| Fil | Beskrivning |
|------|------------|
| `ValidationLog.py` | Loggmodell för validering av transaktioner. |
| `account.py` | Modell för bankkonton och IBAN. |
| `blacklist.py` | Modell som hanterar svartlistade konton. |
| `customer.py` | Modell för kundinformation. |
| `exchange_rate.py` | Modell för valutakurser och konvertering. |
| `pending_transaction.py` | Modell för väntande transaktioner. |
| `transaction.py` | Modell för transaktionsdata. |

---

## `Notebook/`  
Innehåller Jupyter Notebooks för dataanalys.

| Fil | Beskrivning |
|------|------------|
| `analyse_data.ipynb` | Notebook för analys av transaktionsdata. |

---

## `Pipeline/`  
Prefect-flöde för datavalidering och transaktionshantering.

| Fil | Beskrivning |
|------|------------|
| `blacklist_ge_prefect_pipeline.py` | Pipeline med prefect -och GE för att hantera svartlistade transaktioner. |
| `database.py` | Kod för databashantering och anslutning. |
| `logging_setup.py` | Konfiguration av loggning i pipeline. |
| `main_flow.py` | Huvudflödet i pipeline som manuell hantering. |
| `prefect_pipeline.py` | Skript som kör pipeline med Prefect. |
| `validation.py` | Validering av transaktionsflödet. |

---

## `Reports/`  
Dokumentation och analyser av transaktionsdata.

| Fil | Beskrivning |
|------|------------|
| `analyse_report.md` | Rapport från dataanalysen. |
| `transaction_country_summary_2025-05-30.csv` | Sammanställning av transaktioner per land. |
| `transaction_country_summary_2025-05-30.md` | Markdown-rapport över transaktionsflöden. |

---

## `Services/`  
Funktioner för databehandling, valutakonvertering och transaktionshantering.

| Fil | Beskrivning |
|------|------------|
| `convert_currency.py` | Skript som hanterar valutakonvertering. |
| `transaction_service.py` | Huvudlogik för att bearbeta transaktioner. |
| `transfer_validation.py` | Validering av penningöverföringar. |
| `unique_transaction_countries.py` | Identifierar unika transaktionsländer. |

---

## `Tests/`  
Enhetstester för att säkerställa pipelinefunktionalitet.

| Fil | Beskrivning |
|------|------------|
| `test_datebase.py` | Testar databaskoppling och lagring. |
| `test_export.py` | Verifierar exportfunktionalitet. |
| `test_fraud_detection.py` | Testar algoritmer för bedrägeridetektion. |
| `test_timestamp.py` | Testar hantering av tidsstämplar. |
| `test_validation.py` | Säkerställer att valideringslogik fungerar korrekt. |

---

## `Utils/`  
Hjälpfunktioner och verktyg för hantering av data.

| Fil | Beskrivning |
|------|------------|
| `timestamp.py` | Modul för att hantera och konvertera tidsstämplar. |
| `validation_logs.py` | Genererar valideringsloggar för transaktionsdata. |

---

## `Alembic/`  
Databasversionering och migrationshantering med Alembic.

| Fil | Beskrivning |
|------|------------|
| `create_blacklist_pending.py` | Skript som skapar tabellen för väntande svartlistningar. |
| `migration.py` | Hantera och applicera schemaändringar. |
| `alembic.ini` | Konfigurationsfil för Alembic-miljö. |
| `env.py` | Alembic-miljökonfiguration. |
| `script.py.mako` | Template för migrationsskript. |

---
