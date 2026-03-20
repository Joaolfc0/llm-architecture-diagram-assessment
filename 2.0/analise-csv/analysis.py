"""
Comprehensive analysis of the AEA (Architectural Evaluation Audit) data.
Computes all metrics required for Section 4 of the paper.
"""
import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations
import warnings
warnings.filterwarnings("ignore")

CSV_PATH = "Estrutura de Planilha para Análise Granular - final - Estrutura de Planilha para Anál.csv"

def load_data():
    df = pd.read_csv(CSV_PATH)
    first_col = df.columns[0]
    df = df.rename(columns={first_col: "OUT_ID"})
    df = df.dropna(subset=["Expert_ID", "Model", "Criterion"])
    df = df[df["Expert_ID"].str.strip() != ""]
    for col in ["LLM_Score", "Agreement_Score", "Is_Factual_Correct",
                 "Err_Hallucination", "Err_Omission", "Err_Logic",
                 "Err_Contradiction", "Err_Vagueness", "Err_Other"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Condition"] = df["Model"] + "-" + df["Input_Format"]
    return df

ERR_COLS = ["Err_Hallucination", "Err_Omission", "Err_Logic",
            "Err_Contradiction", "Err_Vagueness", "Err_Other"]

def section_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def sub_header(title):
    print(f"\n--- {title} ---")

# ─────────────────────────────────────────────────────────────────────
# 0. DESCRIPTIVE STATISTICS
# ─────────────────────────────────────────────────────────────────────
def descriptive_stats(df):
    section_header("0. DESCRIPTIVE / BASELINE STATISTICS")

    print(f"\nTotal valid observations: {len(df)}")
    print(f"Unique experts: {df['Expert_ID'].nunique()}")
    print(f"Expert list: {sorted(df['Expert_ID'].unique())}")

    sub_header("Observations per Model x Format")
    print(df.groupby(["Model", "Input_Format"]).size().unstack(fill_value=0).to_string())

    sub_header("Observations per Criterion")
    print(df.groupby("Criterion").size().to_string())

    sub_header("Observations per Guideline")
    print(df.groupby(["Criterion", "Guideline"]).size().to_string())

    sub_header("Observations per Model x Format x Criterion")
    print(df.groupby(["Model", "Input_Format", "Criterion"]).size().unstack(fill_value=0).to_string())

    sub_header("Coverage matrix: experts per OUT_ID")
    coverage = df.groupby("OUT_ID")["Expert_ID"].nunique()
    print(coverage.to_string())

    sub_header("LLM_Score distribution (overall)")
    print(df["LLM_Score"].value_counts().sort_index().to_string())

    sub_header("LLM_Score distribution by Model x Format")
    print(df.groupby(["Model", "Input_Format", "LLM_Score"]).size().unstack(fill_value=0).to_string())

# ─────────────────────────────────────────────────────────────────────
# 1. RQ1  –  HUMAN-LLM AGREEMENT
# ─────────────────────────────────────────────────────────────────────
def agreement_rate(series):
    return (series >= 3).mean()

def rq1_analysis(df):
    section_header("1. RQ1: HUMAN–LLM AGREEMENT")

    # 1a  Distribution
    sub_header("1a. Agreement_Score distribution (overall)")
    print(df["Agreement_Score"].value_counts().sort_index().to_string())

    for grp in ["Model", "Input_Format", "Criterion"]:
        sub_header(f"1a. Agreement_Score distribution by {grp}")
        ct = df.groupby([grp, "Agreement_Score"]).size().unstack(fill_value=0)
        print(ct.to_string())

    # 1b  Agreement rate
    sub_header("1b. Agreement rate (Agreement_Score >= 3)")
    print(f"Overall: {agreement_rate(df['Agreement_Score']):.4f}  ({(df['Agreement_Score'] >= 3).sum()}/{len(df)})")

    for grp in ["Model", "Input_Format", "Criterion", "Guideline",
                 ["Model", "Input_Format"],
                 ["Model", "Criterion"],
                 ["Input_Format", "Criterion"],
                 ["Model", "Input_Format", "Criterion"]]:
        label = grp if isinstance(grp, str) else " x ".join(grp)
        sub_header(f"1b. Agreement rate by {label}")
        g = df.groupby(grp)["Agreement_Score"]
        tbl = pd.DataFrame({
            "n": g.count(),
            "agree_rate": g.apply(agreement_rate),
        })
        print(tbl.to_string())

    # 1c  Central tendency
    sub_header("1c. Mean / Median / SD of Agreement_Score")
    print(f"Overall  mean={df['Agreement_Score'].mean():.3f}  median={df['Agreement_Score'].median():.1f}  sd={df['Agreement_Score'].std():.3f}")

    for grp in ["Model", "Input_Format", "Criterion",
                 ["Model", "Input_Format"]]:
        label = grp if isinstance(grp, str) else " x ".join(grp)
        sub_header(f"1c. Central tendency by {label}")
        g = df.groupby(grp)["Agreement_Score"]
        tbl = pd.DataFrame({
            "mean": g.mean(),
            "median": g.median(),
            "sd": g.std(),
            "n": g.count(),
        })
        print(tbl.to_string())

    # 1d  Score distance
    df["abs_dist"] = (df["LLM_Score"] - df["Agreement_Score"]).abs()
    df["signed_dist"] = df["LLM_Score"] - df["Agreement_Score"]

    sub_header("1d. Absolute score distance |LLM_Score - Agreement_Score|")
    print(f"Overall  mean={df['abs_dist'].mean():.3f}  median={df['abs_dist'].median():.1f}")

    for grp in ["Model", "Input_Format", "Criterion",
                 ["Model", "Input_Format"]]:
        label = grp if isinstance(grp, str) else " x ".join(grp)
        sub_header(f"1d. Score distance by {label}")
        g = df.groupby(grp)["abs_dist"]
        tbl = pd.DataFrame({"mean_abs_dist": g.mean(), "median_abs_dist": g.median(), "n": g.count()})
        print(tbl.to_string())

    # 1e  Direction of disagreement
    sub_header("1e. Direction of disagreement (when Agreement_Score <= 2)")
    disagree = df[df["Agreement_Score"] <= 2]
    print(f"Total disagreement cases: {len(disagree)}  ({len(disagree)/len(df)*100:.1f}%)")
    print(f"  Strongly disagree (=1): {(disagree['Agreement_Score']==1).sum()}")
    print(f"  Disagree (=2):          {(disagree['Agreement_Score']==2).sum()}")
    over = (disagree["signed_dist"] > 0).sum()
    under = (disagree["signed_dist"] < 0).sum()
    same = (disagree["signed_dist"] == 0).sum()
    print(f"  LLM over-scored:  {over}  ({over/len(disagree)*100:.1f}%)")
    print(f"  LLM under-scored: {under}  ({under/len(disagree)*100:.1f}%)")
    print(f"  Same score:       {same}  ({same/len(disagree)*100:.1f}%)")

    sub_header("1e. Cross-tab LLM_Score vs Agreement_Score (disagreement only)")
    ct = pd.crosstab(disagree["LLM_Score"], disagree["Agreement_Score"])
    print(ct.to_string())

    # 1f  Inter-rater reliability
    sub_header("1f. Inter-rater reliability (Krippendorff's alpha)")
    compute_irr(df)

    # 1g  Statistical tests
    sub_header("1g. Statistical tests")
    stat_tests_rq1(df)

def compute_irr(df):
    """Krippendorff's alpha for ordinal data (simplified bootstrap-free)."""
    try:
        from krippendorff import alpha as kripp_alpha
        has_kripp = True
    except ImportError:
        has_kripp = False

    grouped = df.groupby(["OUT_ID", "Guideline"])
    items = []
    for (out_id, guideline), grp in grouped:
        if len(grp) >= 2:
            items.append({
                "item": f"{out_id}_{guideline}",
                "scores": grp["Agreement_Score"].tolist(),
                "raters": grp["Expert_ID"].tolist(),
                "model": grp["Model"].iloc[0],
                "fmt": grp["Input_Format"].iloc[0],
            })

    if not has_kripp:
        print("[krippendorff package not installed – computing pairwise agreement instead]")
        all_pairs_agree = []
        for it in items:
            scores = it["scores"]
            for i in range(len(scores)):
                for j in range(i + 1, len(scores)):
                    all_pairs_agree.append(1 if scores[i] == scores[j] else 0)
        if all_pairs_agree:
            print(f"  Overall pairwise exact agreement: {np.mean(all_pairs_agree):.3f} ({sum(all_pairs_agree)}/{len(all_pairs_agree)})")
            within1 = []
            for it in items:
                scores = it["scores"]
                for i in range(len(scores)):
                    for j in range(i + 1, len(scores)):
                        within1.append(1 if abs(scores[i] - scores[j]) <= 1 else 0)
            print(f"  Overall pairwise within-1 agreement: {np.mean(within1):.3f} ({sum(within1)}/{len(within1)})")

        for cond_key in ["model", "fmt"]:
            sub_vals = {}
            for it in items:
                k = it[cond_key]
                if k not in sub_vals:
                    sub_vals[k] = []
                for i in range(len(it["scores"])):
                    for j in range(i + 1, len(it["scores"])):
                        sub_vals[k].append(1 if it["scores"][i] == it["scores"][j] else 0)
            for k, v in sub_vals.items():
                print(f"  Pairwise exact agreement ({cond_key}={k}): {np.mean(v):.3f} ({sum(v)}/{len(v)})")
        return

    all_raters = sorted(df["Expert_ID"].unique())
    rater_idx = {r: i for i, r in enumerate(all_raters)}
    item_labels = [it["item"] for it in items]
    matrix = np.full((len(all_raters), len(items)), np.nan)
    for j, it in enumerate(items):
        for rater, score in zip(it["raters"], it["scores"]):
            matrix[rater_idx[rater], j] = score

    alpha_val = kripp_alpha(matrix, level_of_measurement="ordinal")
    print(f"  Overall Krippendorff's alpha (ordinal): {alpha_val:.4f}")

    for cond_key in ["model", "fmt"]:
        cond_vals = set(it[cond_key] for it in items)
        for cv in sorted(cond_vals):
            idxs = [j for j, it in enumerate(items) if it[cond_key] == cv]
            if len(idxs) >= 2:
                sub_matrix = matrix[:, idxs]
                a = kripp_alpha(sub_matrix, level_of_measurement="ordinal")
                print(f"  Krippendorff's alpha ({cond_key}={cv}): {a:.4f}")

def stat_tests_rq1(df):
    chatgpt = df[df["Model"] == "ChatGPT"]["Agreement_Score"].dropna()
    gemini = df[df["Model"] == "Gemini"]["Agreement_Score"].dropna()
    u, p = stats.mannwhitneyu(chatgpt, gemini, alternative="two-sided")
    n = len(chatgpt) + len(gemini)
    r_rb = 1 - (2 * u) / (len(chatgpt) * len(gemini))
    print(f"Mann-Whitney (ChatGPT vs Gemini): U={u:.1f}, p={p:.4f}, r={r_rb:.3f}, n_chatgpt={len(chatgpt)}, n_gemini={len(gemini)}")

    png = df[df["Input_Format"] == "PNG"]["Agreement_Score"].dropna()
    svg = df[df["Input_Format"] == "SVG"]["Agreement_Score"].dropna()
    u, p = stats.mannwhitneyu(png, svg, alternative="two-sided")
    r_rb = 1 - (2 * u) / (len(png) * len(svg))
    print(f"Mann-Whitney (PNG vs SVG): U={u:.1f}, p={p:.4f}, r={r_rb:.3f}, n_png={len(png)}, n_svg={len(svg)}")

    groups = [g["Agreement_Score"].dropna().values for _, g in df.groupby("Criterion")]
    h, p = stats.kruskal(*groups)
    print(f"Kruskal-Wallis (across 5 criteria): H={h:.3f}, p={p:.4f}")

    crit_names = sorted(df["Criterion"].unique())
    if p < 0.05:
        print("  Post-hoc pairwise Mann-Whitney (Bonferroni-corrected):")
        pairs = list(combinations(crit_names, 2))
        for c1, c2 in pairs:
            g1 = df[df["Criterion"] == c1]["Agreement_Score"].dropna()
            g2 = df[df["Criterion"] == c2]["Agreement_Score"].dropna()
            u_val, p_val = stats.mannwhitneyu(g1, g2, alternative="two-sided")
            p_corr = min(p_val * len(pairs), 1.0)
            flag = "*" if p_corr < 0.05 else ""
            print(f"    {c1} vs {c2}: U={u_val:.1f}, p_raw={p_val:.4f}, p_corr={p_corr:.4f} {flag}")

# ─────────────────────────────────────────────────────────────────────
# 2. RQ2  –  FACTUAL CORRECTNESS & ERROR TYPES
# ─────────────────────────────────────────────────────────────────────
def rq2_analysis(df):
    section_header("2. RQ2: FACTUAL CORRECTNESS AND ERROR TYPES")

    # 2a  Factual correctness rate
    sub_header("2a. Factual correctness rate")
    fc = df["Is_Factual_Correct"]
    print(f"Overall: {fc.mean():.4f}  ({int(fc.sum())}/{len(fc)})")

    for grp in ["Model", "Input_Format", "Criterion", "Guideline",
                 ["Model", "Input_Format"],
                 ["Model", "Criterion"],
                 ["Input_Format", "Criterion"]]:
        label = grp if isinstance(grp, str) else " x ".join(grp)
        sub_header(f"2a. Factual correctness by {label}")
        g = df.groupby(grp)["Is_Factual_Correct"]
        tbl = pd.DataFrame({"n": g.count(), "fc_rate": g.mean(), "fc_count": g.sum().astype(int)})
        print(tbl.to_string())

    # 2b  Error type frequencies
    sub_header("2b. Error type frequencies (overall)")
    n_total = len(df)
    n_incorrect = (df["Is_Factual_Correct"] == 0).sum()
    for col in ERR_COLS:
        cnt = int(df[col].sum())
        pct_all = cnt / n_total * 100
        pct_inc = cnt / n_incorrect * 100 if n_incorrect > 0 else 0
        print(f"  {col:25s}: {cnt:4d} ({pct_all:5.1f}% of all, {pct_inc:5.1f}% of incorrect)")

    # 2c  Error types by condition
    for grp in ["Model", "Input_Format", "Criterion",
                 ["Model", "Input_Format"]]:
        label = grp if isinstance(grp, str) else " x ".join(grp)
        sub_header(f"2c. Error type rates by {label}")
        g = df.groupby(grp)
        tbl = g[ERR_COLS].mean()
        tbl.insert(0, "n", g.size())
        print(tbl.round(4).to_string())

    # 2d  Error co-occurrence
    sub_header("2d. Error co-occurrence")
    df["n_errors"] = df[ERR_COLS].sum(axis=1)
    print("Number of error types flagged per record:")
    print(df["n_errors"].value_counts().sort_index().to_string())
    multi = df[df["n_errors"] >= 2]
    if len(multi) > 0:
        print(f"\nRecords with 2+ error types: {len(multi)}")
        print("Most common error-type pairs:")
        pair_counts = {}
        for _, row in multi.iterrows():
            flagged = [c for c in ERR_COLS if row[c] == 1]
            for a, b in combinations(flagged, 2):
                pair = (a, b)
                pair_counts[pair] = pair_counts.get(pair, 0) + 1
        for pair, cnt in sorted(pair_counts.items(), key=lambda x: -x[1]):
            print(f"  {pair[0]} + {pair[1]}: {cnt}")

    # 2e  Relationship factual correctness <-> agreement
    sub_header("2e. Factual correctness vs Agreement_Score")
    correct = df[df["Is_Factual_Correct"] == 1]["Agreement_Score"].dropna()
    incorrect = df[df["Is_Factual_Correct"] == 0]["Agreement_Score"].dropna()
    print(f"  Correct   – mean={correct.mean():.3f}, median={correct.median():.1f}, n={len(correct)}")
    print(f"  Incorrect – mean={incorrect.mean():.3f}, median={incorrect.median():.1f}, n={len(incorrect)}")
    if len(correct) > 0 and len(incorrect) > 0:
        u, p = stats.mannwhitneyu(correct, incorrect, alternative="two-sided")
        print(f"  Mann-Whitney U={u:.1f}, p={p:.4f}")

    agree_rate_correct = agreement_rate(correct)
    agree_rate_incorrect = agreement_rate(incorrect)
    print(f"  Agreement rate (correct):   {agree_rate_correct:.4f}")
    print(f"  Agreement rate (incorrect): {agree_rate_incorrect:.4f}")

    # 2f  Error types in disagreement cases
    sub_header("2f. Error types in disagreement cases (Agreement_Score <= 2)")
    disagree = df[df["Agreement_Score"] <= 2]
    agree = df[df["Agreement_Score"] >= 3]
    print(f"  Disagreement records: {len(disagree)}   Agreement records: {len(agree)}")
    for col in ERR_COLS:
        rate_dis = disagree[col].mean() if len(disagree) > 0 else 0
        rate_agr = agree[col].mean() if len(agree) > 0 else 0
        print(f"  {col:25s}: disagree={rate_dis:.3f}  agree={rate_agr:.3f}  ratio={rate_dis/rate_agr:.2f}" if rate_agr > 0 else f"  {col:25s}: disagree={rate_dis:.3f}  agree={rate_agr:.3f}")

    # 2g  Qualitative analysis of expert comments
    sub_header("2g. Expert comments (non-empty)")
    comments = df[df["Expert_Comment"].notna() & (df["Expert_Comment"].str.strip() != "")]
    print(f"  Records with comments: {len(comments)} ({len(comments)/len(df)*100:.1f}%)")
    print(f"  Comments by condition:")
    print(comments.groupby(["Model", "Input_Format"]).size().to_string())
    print(f"\n  Comments by criterion:")
    print(comments.groupby("Criterion").size().to_string())
    print(f"\n  All comments:")
    for _, row in comments.iterrows():
        print(f"    [{row['Model']}-{row['Input_Format']}] {row['Criterion']}/{row['Guideline']} "
              f"(Agr={int(row['Agreement_Score'])}, FC={int(row['Is_Factual_Correct'])}): "
              f"{row['Expert_Comment'][:200]}")

# ─────────────────────────────────────────────────────────────────────
# 3. RQ3  –  EFFECTS OF MODEL AND REPRESENTATION
# ─────────────────────────────────────────────────────────────────────
def rq3_analysis(df):
    section_header("3. RQ3: EFFECTS OF MODEL AND REPRESENTATION")

    # 3a  Full 2x2 summary
    sub_header("3a. Full 2x2 summary table (Model x Format)")
    summary_rows = []
    for (model, fmt), grp in df.groupby(["Model", "Input_Format"]):
        row = {
            "Model": model, "Format": fmt,
            "n": len(grp),
            "agree_rate": agreement_rate(grp["Agreement_Score"]),
            "mean_agree": grp["Agreement_Score"].mean(),
            "median_agree": grp["Agreement_Score"].median(),
            "fc_rate": grp["Is_Factual_Correct"].mean(),
        }
        for col in ERR_COLS:
            row[col] = grp[col].mean()
        summary_rows.append(row)
    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.round(4).to_string(index=False))

    # 3b  Model effect
    sub_header("3b. Model effect (ChatGPT vs Gemini)")
    for metric_name, col in [("Agreement_Score", "Agreement_Score"), ("Is_Factual_Correct", "Is_Factual_Correct")]:
        c = df[df["Model"] == "ChatGPT"][col].dropna()
        g = df[df["Model"] == "Gemini"][col].dropna()
        print(f"  {metric_name}: ChatGPT mean={c.mean():.3f} (n={len(c)}), Gemini mean={g.mean():.3f} (n={len(g)})")
        if col == "Agreement_Score":
            u, p = stats.mannwhitneyu(c, g, alternative="two-sided")
            print(f"    Mann-Whitney U={u:.1f}, p={p:.4f}")
        else:
            ct = pd.crosstab(df["Model"], df[col])
            chi2, p, dof, _ = stats.chi2_contingency(ct)
            print(f"    Chi-squared={chi2:.3f}, p={p:.4f}, dof={dof}")

    for col in ERR_COLS:
        c_rate = df[df["Model"] == "ChatGPT"][col].mean()
        g_rate = df[df["Model"] == "Gemini"][col].mean()
        print(f"  {col}: ChatGPT={c_rate:.3f}, Gemini={g_rate:.3f}")

    # 3c  Format effect
    sub_header("3c. Format effect (PNG vs SVG)")
    for metric_name, col in [("Agreement_Score", "Agreement_Score"), ("Is_Factual_Correct", "Is_Factual_Correct")]:
        p_val = df[df["Input_Format"] == "PNG"][col].dropna()
        s_val = df[df["Input_Format"] == "SVG"][col].dropna()
        print(f"  {metric_name}: PNG mean={p_val.mean():.3f} (n={len(p_val)}), SVG mean={s_val.mean():.3f} (n={len(s_val)})")
        if col == "Agreement_Score":
            u, p = stats.mannwhitneyu(p_val, s_val, alternative="two-sided")
            print(f"    Mann-Whitney U={u:.1f}, p={p:.4f}")
        else:
            ct = pd.crosstab(df["Input_Format"], df[col])
            chi2, p, dof, _ = stats.chi2_contingency(ct)
            print(f"    Chi-squared={chi2:.3f}, p={p:.4f}, dof={dof}")

    for col in ERR_COLS:
        p_rate = df[df["Input_Format"] == "PNG"][col].mean()
        s_rate = df[df["Input_Format"] == "SVG"][col].mean()
        print(f"  {col}: PNG={p_rate:.3f}, SVG={s_rate:.3f}")

    # 3d  Interaction effect
    sub_header("3d. Interaction effect (Model x Format)")
    print("  Delta (SVG - PNG) in agreement rate per model:")
    for model in ["ChatGPT", "Gemini"]:
        png_rate = agreement_rate(df[(df["Model"] == model) & (df["Input_Format"] == "PNG")]["Agreement_Score"])
        svg_rate = agreement_rate(df[(df["Model"] == model) & (df["Input_Format"] == "SVG")]["Agreement_Score"])
        print(f"    {model}: PNG={png_rate:.3f}, SVG={svg_rate:.3f}, delta={svg_rate - png_rate:+.3f}")

    print("  Delta (SVG - PNG) in factual correctness per model:")
    for model in ["ChatGPT", "Gemini"]:
        png_fc = df[(df["Model"] == model) & (df["Input_Format"] == "PNG")]["Is_Factual_Correct"].mean()
        svg_fc = df[(df["Model"] == model) & (df["Input_Format"] == "SVG")]["Is_Factual_Correct"].mean()
        print(f"    {model}: PNG={png_fc:.3f}, SVG={svg_fc:.3f}, delta={svg_fc - png_fc:+.3f}")

    # 3e  Per-criterion breakdown
    sub_header("3e. Agreement rate by Criterion within each Condition")
    tbl = df.groupby(["Model", "Input_Format", "Criterion"])["Agreement_Score"].apply(agreement_rate).unstack(fill_value=0)
    print(tbl.round(4).to_string())

    sub_header("3e. Factual correctness by Criterion within each Condition")
    tbl = df.groupby(["Model", "Input_Format", "Criterion"])["Is_Factual_Correct"].mean().unstack(fill_value=0)
    print(tbl.round(4).to_string())

    sub_header("3e. Mean Agreement_Score by Criterion within each Condition")
    tbl = df.groupby(["Model", "Input_Format", "Criterion"])["Agreement_Score"].mean().unstack(fill_value=0)
    print(tbl.round(3).to_string())

    # 3f  Guideline-level heat map
    sub_header("3f. Agreement rate by Guideline within each Condition")
    tbl = df.groupby(["Guideline", "Model", "Input_Format"])["Agreement_Score"].apply(agreement_rate)
    tbl = tbl.unstack(["Model", "Input_Format"])
    print(tbl.round(3).to_string())

    sub_header("3f. Factual correctness by Guideline within each Condition")
    tbl = df.groupby(["Guideline", "Model", "Input_Format"])["Is_Factual_Correct"].mean()
    tbl = tbl.unstack(["Model", "Input_Format"])
    print(tbl.round(3).to_string())

    sub_header("3f. Mean Agreement_Score by Guideline within each Condition")
    tbl = df.groupby(["Guideline", "Model", "Input_Format"])["Agreement_Score"].mean()
    tbl = tbl.unstack(["Model", "Input_Format"])
    print(tbl.round(3).to_string())

    sub_header("3f. N observations by Guideline within each Condition")
    tbl = df.groupby(["Guideline", "Model", "Input_Format"])["Agreement_Score"].count()
    tbl = tbl.unstack(["Model", "Input_Format"])
    print(tbl.to_string())


def main():
    df = load_data()
    descriptive_stats(df)
    rq1_analysis(df)
    rq2_analysis(df)
    rq3_analysis(df)

if __name__ == "__main__":
    main()
