import pandas as pd
from datetime import datetime

# Lista med tillåtna tidsformat att försöka tolka
TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",   # Standard ISO-liknande format
    "%Y%m%d %H:%M:%S",     # Format som "20250125 04:48:00"
    "%y-%m-%d %H:%M:%S",   # Kort årtal, t.ex. "25-04-09 12:12:00"
]

#Försöker tolka tidsstämpeln med kända format.
#Returnerar datetime-objekt eller pd.NaT om misslyckas.
def parse_timestamp(ts_str):
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(ts_str, fmt)
        except Exception:
            continue
# Misslyckades med alla format
    return pd.NaT

"""
Normaliserar tidsstämpelkolumnen i DataFrame.
Skapar ny kolumn 'parsed_timestamp' med datetime-objekt eller NaT.
Args:
df (pd.DataFrame): Input-data.
timestamp_col (str): Namn på kolumn med tidsstämpel som sträng.
    
Returns:
df_clean (pd.DataFrame): Rader med giltiga tidsstämplar.
df_errors (pd.DataFrame): Rader med ogiltiga tidsstämplar."""

def normalize_and_flag_timestamps(df, timestamp_col='timestamp'):
    df['parsed_timestamp'] = df[timestamp_col].apply(parse_timestamp)
    df_errors = df[df['parsed_timestamp'].isna()]
    df_clean = df.dropna(subset=['parsed_timestamp']).copy()
    return df_clean, df_errors

#Loggar felaktiga rader till CSV-fil för manuell inspektion.
def log_invalid_timestamps(df_errors, log_path='invalid_timestamps.csv'):
    if not df_errors.empty:
        df_errors.to_csv(log_path, index=False)
        print(f"[Timestamp Utils] Felaktiga tidsstämplar loggade i {log_path}")
    else:
        print("[Timestamp Utils] Inga felaktiga tidsstämplar hittades.")