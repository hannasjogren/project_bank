import pandas as pd
import os
from datetime import datetime

TRANSACTIONS_CSV = r"C:\Users\hanna\PycharmProjects\b_projekt\Data\transactions.csv"
REPORTS_DIR = r"C:\Users\hanna\PycharmProjects\b_projekt\Reports"
today_str = datetime.today().strftime("%Y-%m-%d")  # t.ex. 2025-05-29

# Läs in data
try:
    df = pd.read_csv(TRANSACTIONS_CSV, encoding="utf-8")
except FileNotFoundError:
    print(f"Error: {TRANSACTIONS_CSV} not found.")
    exit()

# Hämta unika länder
sender_countries = sorted(set(df["sender_country"].dropna().unique()))
receiver_countries = sorted(set(df["receiver_country"].dropna().unique()))

# Skapa DataFrame med lika långa listor
max_len = max(len(sender_countries), len(receiver_countries))
sender_countries += [""] * (max_len - len(sender_countries))
receiver_countries += [""] * (max_len - len(receiver_countries))

df_summary = pd.DataFrame({
    "Sent From": sender_countries,
    "Sent To": receiver_countries
})

# Skapa Reports-mapp om den inte finns
os.makedirs(REPORTS_DIR, exist_ok=True)

# Filvägar med datum
csv_path = os.path.join(REPORTS_DIR, f"transaction_country_summary_{today_str}.csv")
md_path = os.path.join(REPORTS_DIR, f"transaction_country_summary_{today_str}.md")

# Terminalutskrift
print(f"\nSummary of Unique Countries in Transactions ({today_str}):\n")
print(f"Total unique sender countries: {len(set(sender_countries) - {''})}")
print(f"Total unique receiver countries: {len(set(receiver_countries) - {''})}\n")
print(df_summary.to_string(index=False))

# Spara till CSV
df_summary.to_csv(csv_path, index=False, encoding="utf-8-sig")

# Spara till Markdown
with open(md_path, "w", encoding="utf-8") as f:
    f.write(f"# Summary of Unique Countries in Transactions\n")
    f.write(f"**Date:** {today_str}\n\n")
    f.write(f"- Total unique sender countries: {len(set(sender_countries) - {''})}\n")
    f.write(f"- Total unique receiver countries: {len(set(receiver_countries) - {''})}\n\n")
    f.write(df_summary.to_markdown(index=False))

print(f"\nFiles saved to: {REPORTS_DIR}")
