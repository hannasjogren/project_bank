Grupp: Hanna Sjögren, Theodor Bardeman och Carl Jepsen

Git memo: hannasjogren, TBard05 och MrPhail

# Filstruktur och konfiguration för `b_projekt`

Detta projekt är en datadriven pipeline som hanterar transaktionsvalidering, valutakonvertering och databashantering med Prefect och Alembic. Nedan hittar du en översikt över filstrukturen samt instruktioner för att konfigurera databasen och filvägar. Det finns kommenterat i filerna vart man själv behöver uppdatera till sin egna databas URL och filväg.

---
## Projektets struktur

## Beskrivning av mappar och filer

### `alembic/` - Databasversionering med Alembic  
- `alembic_migration/migration.py` – Hanterar schemaändringar.  
- `env.py` – Konfiguration av Alembic-miljö.  
- `alembic.ini` – Konfigurationsfil för databasdialekt (PostgreSQL).  
- `script.py.mako` – Template för migrationsskript.  
- `README` – Dokumentation om migrationsprocessen.  

### `Data/` - Inmatningsdata och CSV-filer  
- `accounts.csv` – Konto- och IBAN-data.  
- `customers.csv` – Kundregister.  
- `transactions.csv` – Transaktionshistorik.  
- `sebank_customers_with_accounts.csv` – Dataset för bankkunder.  
- `split_customers_account.py` – Python-skript för dataseparation.  

### `Exports/` - Exporterade transaktionsdata  
- `transactions_export.csv` – Fil med transaktioner som har bearbetats.  

### `Logs/` - Loggfiler för felsökning och spårning  
- `pipeline.log` – Loggar hela pipelineflödet.  
- `fraud_detection_test_logs.log` – Loggar för bedrägeridetektion.  
- `validation_test_logs.log` – Loggar för transaktionsvalidering.  

### `Models/` - Databasmodeller  
- `customer.py` – Kundtabell.  
- `account.py` – Kontotabell med IBAN.  
- `blacklist.py` – Hanterar svartlistade konton.  
- `exchange_rate.py` – Lagrar valutakurser.  
- `transaction.py` – Huvudtabell för transaktioner.  
- `pending_transaction.py` – Hanterar väntande transaktioner.  
- `ValidationLog.py` – Valideringsloggar för transaktioner.  

### `Notebook/` - Dataanalys  
- `analyse_data.ipynb` – Jupyter Notebook för att analysera transaktionsdata.  

### `Pipeline/` - Prefect-flöde för datavalidering och hantering  
- `database.py` – Databasanslutning.  
- `logging_setup.py` – Konfigurerar logging i pipelinen.  
- `main_flow.py` – Huvudflödet i pipelinen.  
- `prefect_pipeline.py` – Kör pipeline med Prefect.  
- `validation.py` – Hanterar datavalidering.  

### `Reports/` - Dokumentation och analyser  
- `analyse_report.md` – Rapport från dataanalysen.  

### `Services/` - Funktioner för databehandling  
- `convert_currency.py` – Konverterar valutor.  
- `transaction_service.py` – Hanterar transaktionslogik.  
- `transfer_validation.py` – Validerar överföringar.  

### `Tests/` - Enhetstester  
- `test_database.py` – Testar databasanslutningen.  
- `test_export.py` – Testar dataexporter.  
- `test_fraud_detection.py` – Testar bedrägeridetektion.  
- `test_validation.py` – Validerar pipelineflödet.  

### `Utils/` - Hjälpfunktioner  
- `timestamp.py` – Hanterar tidsstämplar.  
- `validation_logs.py` – Genererar valideringsloggar. 
