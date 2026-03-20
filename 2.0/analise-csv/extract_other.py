import pandas as pd

df = pd.read_csv("Estrutura de Planilha para Análise Granular - final - Estrutura de Planilha para Anál.csv")
first_col = df.columns[0]
df = df.rename(columns={first_col: "OUT_ID"})
df = df.dropna(subset=["Expert_ID", "Model", "Criterion"])
df = df[df["Expert_ID"].str.strip() != ""]
df["Err_Other"] = pd.to_numeric(df["Err_Other"], errors="coerce")

other = df[df["Err_Other"] == 1].copy()
print(f"Total Err_Other records: {len(other)}\n")

for i, (_, row) in enumerate(other.iterrows(), 1):
    txt = str(row["Err_Other_Text"]).strip() if pd.notna(row["Err_Other_Text"]) else "(empty)"
    cmt = str(row["Expert_Comment"]).strip() if pd.notna(row["Expert_Comment"]) else "(empty)"
    print(f"--- Record {i} ---")
    print(f"  OUT_ID:         {row['OUT_ID']}")
    print(f"  Expert:         {row['Expert_ID']}")
    print(f"  Condition:      {row['Model']} / {row['Input_Format']}")
    print(f"  Criterion:      {row['Criterion']} / {row['Guideline']}")
    print(f"  LLM_Score:      {row['LLM_Score']}")
    print(f"  Agreement:      {row['Agreement_Score']}")
    print(f"  Factual Correct:{row['Is_Factual_Correct']}")
    print(f"  Err_Other_Text: {txt}")
    print(f"  Expert_Comment: {cmt}")
    print()
