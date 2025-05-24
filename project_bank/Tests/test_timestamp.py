import os
import pandas as pd
import pytest
from Utils.timestamp import parse_timestamp, normalize_and_flag_timestamps, log_invalid_timestamps

def test_parse_timestamp_valid_formats():
    # Testa olika giltiga format
    valid_samples = {
        "2025-11-16 11:26:00": True,
        "20250125 04:48:00": True,
        "25-04-09 12:12:00": True,
    }
    for ts_str in valid_samples.keys():
        result = parse_timestamp(ts_str)
        assert (result is not pd.NaT), f"Timestamp {ts_str} should parse correctly."

def test_parse_timestamp_invalid_format():
    invalid_ts = "invalid-timestamp"
    result = parse_timestamp(invalid_ts)
    assert result is pd.NaT, "Invalid timestamp should return pd.NaT"

def test_normalize_and_flag_timestamps():
    # Skapa testdata med blandade timestamps
    data = {
        "id": [1, 2, 3],
        "timestamp": ["2025-11-16 11:26:00", "invalid", "20250125 04:48:00"]
    }
    df = pd.DataFrame(data)
    
    df_clean, df_errors = normalize_and_flag_timestamps(df, timestamp_col='timestamp')
    
    # Kontrollera att df_clean har två rader (giltiga tidsstämplar)
    assert len(df_clean) == 2, "df_clean ska ha 2 rader med giltiga timestamps"
    
    # Kontrollera att df_errors har en rad (felaktig timestamp)
    assert len(df_errors) == 1, "df_errors ska ha 1 rad med ogiltig timestamp"
    
    # Kontrollera att 'parsed_timestamp' är datetime i df_clean
    assert pd.api.types.is_datetime64_any_dtype(df_clean['parsed_timestamp']), "parsed_timestamp ska vara datetime"

def test_log_invalid_timestamps_creates_file(tmp_path):
    # Skapa en DataFrame med felaktiga tidsstämplar
    data = {"id": [1], "timestamp": ["invalid"], "parsed_timestamp": [pd.NaT]}
    df_errors = pd.DataFrame(data)
    
    log_path = tmp_path / "invalid_log.csv"
    
    log_invalid_timestamps(df_errors, log_path=str(log_path))
    
    # Kontrollera att filen skapades
    assert os.path.isfile(log_path), "Loggfilen ska skapas"
    
    # Läs in filen och kontrollera innehåll
    df_logged = pd.read_csv(log_path)
    assert len(df_logged) == 1, "Loggfilen ska innehålla en rad"

def test_log_invalid_timestamps_no_file_created(tmp_path, capsys):
    # Skapa en tom DataFrame
    df_errors = pd.DataFrame(columns=["id", "timestamp", "parsed_timestamp"])
    log_path = tmp_path / "invalid_log.csv"
    
    log_invalid_timestamps(df_errors, log_path=str(log_path))
    
    # Kontrollera att fil inte skapades
    assert not os.path.exists(log_path), "Ingen fil ska skapas när df_errors är tom"
    
    # Kontrollera utskrift till konsol
    captured = capsys.readouterr()
    assert "Inga felaktiga tidsstämplar hittades" in captured.out