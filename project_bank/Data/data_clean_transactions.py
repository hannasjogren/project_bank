import pandas as pd
import numpy as np
#import sqlalchemy as so

df = pd.read_csv("Data/transactions.csv")
df.head()

df.dtypes

currency_list = df["currency"].unique()
print(currency_list)

df["timestamp"] = pd.to_datetime(df["timestamp"],)

df = df.sort_values(by="timestamp", na_position= "last")
df.reset_index(drop=True, inplace=True)
df.dtypes
#df.to_csv("transaction_filtered.csv")

converter_list = pd.DataFrame({"currency": currency_list, "rate": [1, 1.45, 9.53, 10.81, 0.067, 0.35, 0.94, 0.53, 1.32, 12.87]})
converter_list.head()

df_merged = df.merge(converter_list, on="currency", how="left")
df_merged["in_sek"] = df_merged["amount"] * df_merged["rate"]
df_merged.head()

df_merged.to_csv("transaction_filtered.csv")