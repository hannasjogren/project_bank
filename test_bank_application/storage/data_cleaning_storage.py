converted_dates = []
invalid_dates = []

try:
    with open ("C:/Users/theod/PycharmProjects/test_bank_application/logging_folder/timestamp_logs", "r", encoding="utf-8") as file:
        for line in file:
            date_str = line.strip()

            if not date_str:
                continue

            dt_obj = None
            original_date_str = date_str

            next_day_adjustment = False
            if " 24" in date_str:
                date_str = date_str.replace(" 24", "00:", 1)
                next_day_adjustment = True

            if "." in date_str.split(" ")[-1] and ":" not in date_str.split(" ")[-1]:
                date_str = date_str.split(".")(":")

            for formats in expected_formats:
                try:
                    dt_obj = datetime.strptime(date_str, formats)
                    break
                except ValueError:
                    continue

            if dt_obj is None:
                try:
                    dt_obj = pd.to_datetime(date_str, errors="raise")
                except ValueError as e:
                    invalid_dates.append(f"{original_date_str} - pandas hanterar inte detta {e}")
                    continue

            if dt_obj and next_day_adjustment:
                dt_obj += pd.Timedelta(days=1)

            if dt_obj:
                converted_dates.append(dt_obj.strftime("%Y-%m-%d %H:%M:%S"))

except FileNotFoundError:
    print("File not found, Check so your file name matches the file you chose")
except Exception as e:
    print(f"A mysterious interaction occurred, you role the dice and get 1")

print("Converted dates (YYYY-MM-DD HH:MM:SS)")
for d in converted_dates:
    print(d)

print("Unknown dates och thay error")
for d in invalid_dates:
    print(d)

#----------------------------------------------------------------------------------------------------#
expected_formats = [
    "%Y%m%d %H:%M:%S",   # 20250125 04:48:00
    "%y-%m-%d %H:%M:%S", # 25-04-09 12:12:00
    "%Y-%m-%d %H:%M",    # 2025-01-18 16:14
    "%Y-%m-%d %H.%M",    # 2025-01-30 23.30
    "%Y-%m-%d %H.%M:%S"  # 2025-04-01 09.15:00
]
converted_data_with_ids = []
invalid_data_with_ids = []

try:
    with open ("logging_folder/timestamp_logs_with_ids", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            parts = line.split(',', 1)
            if len(parts) < 2:
                invalid_data_with_ids.append((None, f"Formatfel i loggfilen: {line}"))
                continue

            original_id = parts[0]
            date_str = parts[1]

            dt_obj = None
            original_date_str_from_log = date_str

            next_day_adjustment = False
            if " 24" in date_str:
                date_str = date_str.replace(" 24", " 00", 1)
                next_day_adjustment = True

            if dt_obj and next_day_adjustment:
                dt_obj += pd.Timedelta(days=1)

            if "." in date_str.split(" ")[-1] and ":" not in date_str.split(" ")[-1]:
                 time_part = date_str.split(" ")[-1]
                 if len(time_part.split('.')) == 2: # Ex: 12.30
                     date_str = date_str.replace(time_part, time_part.replace('.', ':'))

            for formats in expected_formats:
                try:
                    dt_obj = datetime.strptime(date_str, formats)
                    break
                except ValueError:
                    continue

            if dt_obj is None:
                try:
                    dt_obj = pd.to_datetime(date_str, errors="raise")
                except ValueError as e:
                    invalid_data_with_ids.append((original_id, f"{original_date_str_from_log} - pandas hanterar inte detta: {e}"))
                    continue

            if dt_obj and next_day_adjustment:
                dt_obj += pd.Timedelta(days=1)

            if dt_obj:
                converted_data_with_ids.append((original_id, dt_obj.strftime("%Y-%m-%d %H:%M:%S")))

except FileNotFoundError:
    print("I searched for the file: 'timestamp_logs_with_ids' but it remains hidden")
except Exception as e:
    print(f"An error occurred: {e}")

print("\nIts converted! (YYYY-MM-DD HH:MM:SS):")
for original_id, converted_date in converted_data_with_ids:
    print(f"ID: {original_id}, Datum: {converted_date}")

print("\nUnknown error amongst id, file import or convertion error")
for original_id, error_msg in invalid_data_with_ids:
    print(f"ID: {original_id}, Fel: {error_msg}")

#-------------------------------------------------------------------------------------------------------
df_transaction["amount"] = df_transaction["amount"].str.replace(" ", "").str.replace(",", ".")
df_transaction["amount"] = df_transaction["amount"].astype(float)

df_transaction["currency"] = df_transaction["currency"].astype(str)
df_transaction["currency"] = df_transaction["currency"].str.replace(" ", "").str.replace(",", ".")
df_transaction["currency"] = df_transaction["currency"].replace("SKR", "SEK")

#----------------------------------------------------------------------------------
if "id" in df_transaction.columns:
    original_ids = df_transaction["id"].copy()
else:
    original_ids = df_transaction.index.copy()

original_timestamps = df_transaction["timestamp"].copy()
df_transaction["timestamp"] = pd.to_datetime(df_transaction["timestamp"], errors="coerce")

df_valid_timestamps = df_transaction[df_transaction["timestamp"].notna()]
df_pending = df_transaction[df_transaction["timestamp"].isna()]

pending_data_to_log = []
for idx in df_pending.index:
    item_id = original_ids[idx] if "id" in df_transaction.columns else idx
    pending_data_to_log.append((item_id, original_timestamps[idx]))

print(f"Pending data to log: {pending_data_to_log}")
#%%
if not df_pending.empty:
    with open("logging_folder/timestamp_logs_with_ids", "a", encoding="utf-8") as f:
        for item_id, val in pending_data_to_log:
            f.write(f"{item_id},{val}\n")
    print("timestamp_logs_with_ids.txt har uppdaterats med ID:n.")
else:
    print("Inga felaktiga datum att logga.")

#%%
id_to_converted_datetime = {item_id: dt_obj for item_id, dt_obj in converted_data_with_ids}

for idx in df_pending.index:
    current_id = original_ids[idx]

    if current_id in id_to_converted_datetime:
        df_transaction.loc[idx, "timestamp"] = id_to_converted_datetime[current_id]

print(df_transaction["timestamp"])

