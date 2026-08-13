import sys
sys.path.insert(0, ".")
import pandas as pd
from app.pipeline import run_pipeline

df = pd.read_csv("data/raw/appliances_scope.csv")
df = df[df["Part_Desc"].str.contains("Dishwasher", case=False, na=False)].head(3)
# run_pipeline expects the original 6 columns
df = df[["Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf"]]

result = run_pipeline(df)
print("Rows processed:", result["rows_processed"])
print("Summary:", result["summary"])
print()
print(result["output_df"][["Mfg_Part_Num", "Part_Desc", "Classpath", "Overall_Confidence", "Needs_Review", "Flags"]].to_string(index=False))
