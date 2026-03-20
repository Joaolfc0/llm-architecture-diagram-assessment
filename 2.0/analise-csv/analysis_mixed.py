"""
Revised statistical analysis using mixed-effects models.
Addresses: non-independence of observations (nested expert × item structure),
effect sizes with confidence intervals, and proper framing.

Unit of analysis: each row is one expert's audit of one guideline-condition.
Random effects: Expert_ID (same expert rates multiple items) and
               OUT_ID (same LLM output rated by multiple experts).
"""
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
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
    df["is_SVG"] = (df["Input_Format"] == "SVG").astype(int)
    df["is_Gemini"] = (df["Model"] == "Gemini").astype(int)
    df["Agree_binary"] = (df["Agreement_Score"] >= 3).astype(int)
    df["Item_ID"] = df["OUT_ID"] + "_" + df["Guideline"]
    return df

ERR_COLS = ["Err_Hallucination", "Err_Omission", "Err_Logic",
            "Err_Contradiction", "Err_Vagueness", "Err_Other"]

def header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def sub(title):
    print(f"\n--- {title} ---")


def descriptive_summary(df):
    header("DESCRIPTIVE SUMMARY (unchanged)")
    print(f"Total observations: {len(df)}")
    print(f"Unique experts: {df['Expert_ID'].nunique()}")
    print(f"Unique items (OUT_ID x Guideline): {df['Item_ID'].nunique()}")
    print(f"Unique OUT_IDs: {df['OUT_ID'].nunique()}")

    sub("Observations per Model x Format")
    print(df.groupby(["Model", "Input_Format"]).size().unstack(fill_value=0).to_string())

    sub("Agreement rate and FC rate (descriptive, no inference)")
    for label, grp_cols in [("Overall", []),
                             ("By Model", ["Model"]),
                             ("By Format", ["Input_Format"]),
                             ("By Criterion", ["Criterion"]),
                             ("By Model x Format", ["Model", "Input_Format"])]:
        if grp_cols:
            g = df.groupby(grp_cols)
            tbl = pd.DataFrame({
                "n": g.size(),
                "agree_rate": g["Agree_binary"].mean(),
                "mean_agree": g["Agreement_Score"].mean(),
                "fc_rate": g["Is_Factual_Correct"].mean(),
            })
            print(f"\n  {label}:")
            print(tbl.round(3).to_string())
        else:
            print(f"\n  {label}: agree_rate={df['Agree_binary'].mean():.3f}, "
                  f"mean_agree={df['Agreement_Score'].mean():.3f}, "
                  f"fc_rate={df['Is_Factual_Correct'].mean():.3f}, n={len(df)}")

    sub("Direction of disagreement (descriptive)")
    disagree = df[df["Agreement_Score"] <= 2]
    df_tmp = df.copy()
    df_tmp["signed_dist"] = df_tmp["LLM_Score"] - df_tmp["Agreement_Score"]
    dis_tmp = df_tmp[df_tmp["Agreement_Score"] <= 2]
    over = (dis_tmp["signed_dist"] > 0).sum()
    under = (dis_tmp["signed_dist"] < 0).sum()
    same = (dis_tmp["signed_dist"] == 0).sum()
    print(f"  Disagreement cases: {len(disagree)} ({len(disagree)/len(df)*100:.1f}%)")
    print(f"  LLM over-scored: {over} ({over/len(disagree)*100:.1f}%)")
    print(f"  LLM under-scored: {under} ({under/len(disagree)*100:.1f}%)")
    print(f"  Same numeric score: {same} ({same/len(disagree)*100:.1f}%)")


def mixed_agreement(df):
    """Linear mixed-effects model for Agreement_Score (treated as approx continuous).
    Fixed effects: Model (Gemini vs ChatGPT), Format (SVG vs PNG), interaction.
    Random effects: Expert_ID."""
    header("MIXED-EFFECTS MODEL: Agreement_Score")

    sub("Model 1: Model + Format + Model:Format, random=Expert_ID")
    # statsmodels MixedLM supports one grouping factor; we use Expert_ID
    # could and add Item_ID as a second variance component via nested structure (not done rn but would be a better model probably)
    # In the analysis, Item_ID had extremely low variance, so it was not considered in the paper, but it is still a good idea to consider it in a future analysis, as a crossed effect modelling scenario.
    try:
        md1 = smf.mixedlm(
            "Agreement_Score ~ is_Gemini * is_SVG",
            data=df,
            groups=df["Expert_ID"],
            re_formula="1",
        )
        mdf1 = md1.fit(reml=True)
        print(mdf1.summary())
        print("\nFixed-effect coefficients with 95% CI:")
        ci = mdf1.conf_int(alpha=0.05)
        for param in mdf1.fe_params.index:
            coef = mdf1.fe_params[param]
            lo, hi = ci.loc[param]
            p = mdf1.pvalues[param]
            print(f"  {param:30s}: coef={coef:+.3f}  95%CI=[{lo:+.3f}, {hi:+.3f}]  p={p:.4f}")
        print(f"\n  Expert_ID random intercept variance: {mdf1.cov_re.iloc[0,0]:.4f}")
        print(f"  Residual variance: {mdf1.scale:.4f}")
        icc = mdf1.cov_re.iloc[0,0] / (mdf1.cov_re.iloc[0,0] + mdf1.scale)
        print(f"  ICC (expert): {icc:.4f}")
    except Exception as e:
        print(f"  [Model 1 failed: {e}]")

    sub("Model 1b: Same but with Item_ID as group (to check item-level clustering)")
    try:
        md1b = smf.mixedlm(
            "Agreement_Score ~ is_Gemini * is_SVG",
            data=df,
            groups=df["Item_ID"],
            re_formula="1",
        )
        mdf1b = md1b.fit(reml=True)
        print(mdf1b.summary())
        ci = mdf1b.conf_int(alpha=0.05)
        print("\nFixed-effect coefficients with 95% CI:")
        for param in mdf1b.fe_params.index:
            coef = mdf1b.fe_params[param]
            lo, hi = ci.loc[param]
            p = mdf1b.pvalues[param]
            print(f"  {param:30s}: coef={coef:+.3f}  95%CI=[{lo:+.3f}, {hi:+.3f}]  p={p:.4f}")
        print(f"\n  Item_ID random intercept variance: {mdf1b.cov_re.iloc[0,0]:.4f}")
        print(f"  Residual variance: {mdf1b.scale:.4f}")
        icc_item = mdf1b.cov_re.iloc[0,0] / (mdf1b.cov_re.iloc[0,0] + mdf1b.scale)
        print(f"  ICC (item): {icc_item:.4f}")
    except Exception as e:
        print(f"  [Model 1b failed: {e}]")

    sub("Model 2: Criterion effect, random=Expert_ID")
    try:
        md2 = smf.mixedlm(
            "Agreement_Score ~ C(Criterion, Treatment(reference='clarity'))",
            data=df,
            groups=df["Expert_ID"],
            re_formula="1",
        )
        mdf2 = md2.fit(reml=True)
        print(mdf2.summary())
        ci = mdf2.conf_int(alpha=0.05)
        print("\nFixed-effect coefficients with 95% CI:")
        for param in mdf2.fe_params.index:
            coef = mdf2.fe_params[param]
            lo, hi = ci.loc[param]
            p = mdf2.pvalues[param]
            print(f"  {param:55s}: coef={coef:+.3f}  95%CI=[{lo:+.3f}, {hi:+.3f}]  p={p:.4f}")
    except Exception as e:
        print(f"  [Model 2 failed: {e}]")


def mixed_factual(df):
    """Logistic mixed-effects model (via GEE approximation) for Is_Factual_Correct."""
    header("MIXED/GEE MODEL: Is_Factual_Correct (binary)")

    sub("GEE logistic: Model + Format + interaction, cluster=Expert_ID")
    try:
        fam = sm.families.Binomial()
        gee1 = smf.gee(
            "Is_Factual_Correct ~ is_Gemini * is_SVG",
            groups="Expert_ID",
            data=df,
            family=fam,
            cov_struct=sm.cov_struct.Exchangeable(),
        )
        gee1_res = gee1.fit()
        print(gee1_res.summary())
        print("\nOdds ratios with 95% CI:")
        ci = gee1_res.conf_int(alpha=0.05)
        for param in gee1_res.params.index:
            coef = gee1_res.params[param]
            lo, hi = ci.loc[param]
            p = gee1_res.pvalues[param]
            or_val = np.exp(coef)
            or_lo, or_hi = np.exp(lo), np.exp(hi)
            print(f"  {param:30s}: OR={or_val:.3f}  95%CI=[{or_lo:.3f}, {or_hi:.3f}]  p={p:.4f}")
    except Exception as e:
        print(f"  [GEE 1 failed: {e}]")

    sub("GEE logistic: Criterion effect, cluster=Expert_ID")
    try:
        gee2 = smf.gee(
            "Is_Factual_Correct ~ C(Criterion, Treatment(reference='clarity'))",
            groups="Expert_ID",
            data=df,
            family=fam,
            cov_struct=sm.cov_struct.Exchangeable(),
        )
        gee2_res = gee2.fit()
        print(gee2_res.summary())
        print("\nOdds ratios with 95% CI:")
        ci = gee2_res.conf_int(alpha=0.05)
        for param in gee2_res.params.index:
            coef = gee2_res.params[param]
            lo, hi = ci.loc[param]
            p = gee2_res.pvalues[param]
            or_val = np.exp(coef)
            or_lo, or_hi = np.exp(lo), np.exp(hi)
            print(f"  {param:55s}: OR={or_val:.3f}  95%CI=[{or_lo:.3f}, {or_hi:.3f}]  p={p:.4f}")
    except Exception as e:
        print(f"  [GEE 2 failed: {e}]")


def fc_agreement_association(df):
    """Mixed model for the FC -> agreement association."""
    header("ASSOCIATION: Factual Correctness -> Agreement (mixed)")

    sub("LMM: Agreement_Score ~ Is_Factual_Correct, random=Expert_ID")
    try:
        md = smf.mixedlm(
            "Agreement_Score ~ Is_Factual_Correct",
            data=df,
            groups=df["Expert_ID"],
            re_formula="1",
        )
        mdf = md.fit(reml=True)
        ci = mdf.conf_int(alpha=0.05)
        for param in mdf.fe_params.index:
            coef = mdf.fe_params[param]
            lo, hi = ci.loc[param]
            p = mdf.pvalues[param]
            print(f"  {param:30s}: coef={coef:+.3f}  95%CI=[{lo:+.3f}, {hi:+.3f}]  p={p:.4f}")
        print(f"\n  Interpretation: factually correct justifications receive, on average,")
        print(f"  {mdf.fe_params['Is_Factual_Correct']:+.3f} higher Agreement Score (on 1-4 scale)")
    except Exception as e:
        print(f"  [Failed: {e}]")


def bootstrap_ci_rate(series, n_boot=5000, alpha=0.05):
    """Bootstrap 95% CI for a proportion."""
    rng = np.random.default_rng(42)
    vals = series.values
    n = len(vals)
    means = np.array([rng.choice(vals, size=n, replace=True).mean() for _ in range(n_boot)])
    lo = np.percentile(means, 100 * alpha / 2)
    hi = np.percentile(means, 100 * (1 - alpha / 2))
    return lo, hi


def confidence_intervals(df):
    """Bootstrap CIs for key proportions."""
    # Esse BOOTSTRAP está impreciso agora que analiso melhor, pois não considera a estrutura correlacionada dos dados 
    #Tratando todas linhas como eventos independentes, o que não é o caso.
    #That means two rows from the same expert are more similar than two arbitrary rows, and two rows about the same item may also be more similar than arbitrary rows.
    header("BOOTSTRAP 95% CONFIDENCE INTERVALS")

    sub("Agreement rate (Agree >= 3)")
    for label, subset in [("Overall", df),
                           ("ChatGPT", df[df["Model"]=="ChatGPT"]),
                           ("Gemini", df[df["Model"]=="Gemini"]),
                           ("PNG", df[df["Input_Format"]=="PNG"]),
                           ("SVG", df[df["Input_Format"]=="SVG"])]:
        rate = subset["Agree_binary"].mean()
        lo, hi = bootstrap_ci_rate(subset["Agree_binary"])
        print(f"  {label:12s}: {rate:.3f}  95%CI=[{lo:.3f}, {hi:.3f}]  n={len(subset)}")

    sub("Agreement rate by Model x Format")
    for (m, f), grp in df.groupby(["Model", "Input_Format"]):
        rate = grp["Agree_binary"].mean()
        lo, hi = bootstrap_ci_rate(grp["Agree_binary"])
        print(f"  {m}-{f:3s}: {rate:.3f}  95%CI=[{lo:.3f}, {hi:.3f}]  n={len(grp)}")

    sub("Factual correctness rate")
    for label, subset in [("Overall", df),
                           ("ChatGPT", df[df["Model"]=="ChatGPT"]),
                           ("Gemini", df[df["Model"]=="Gemini"]),
                           ("PNG", df[df["Input_Format"]=="PNG"]),
                           ("SVG", df[df["Input_Format"]=="SVG"])]:
        rate = subset["Is_Factual_Correct"].mean()
        lo, hi = bootstrap_ci_rate(subset["Is_Factual_Correct"])
        print(f"  {label:12s}: {rate:.3f}  95%CI=[{lo:.3f}, {hi:.3f}]  n={len(subset)}")

    sub("Factual correctness by Model x Format")
    for (m, f), grp in df.groupby(["Model", "Input_Format"]):
        rate = grp["Is_Factual_Correct"].mean()
        lo, hi = bootstrap_ci_rate(grp["Is_Factual_Correct"])
        print(f"  {m}-{f:3s}: {rate:.3f}  95%CI=[{lo:.3f}, {hi:.3f}]  n={len(grp)}")

    sub("Agreement rate by Criterion")
    for crit, grp in df.groupby("Criterion"):
        rate = grp["Agree_binary"].mean()
        lo, hi = bootstrap_ci_rate(grp["Agree_binary"])
        print(f"  {crit:20s}: {rate:.3f}  95%CI=[{lo:.3f}, {hi:.3f}]  n={len(grp)}")

    sub("Factual correctness by Criterion")
    for crit, grp in df.groupby("Criterion"):
        rate = grp["Is_Factual_Correct"].mean()
        lo, hi = bootstrap_ci_rate(grp["Is_Factual_Correct"])
        print(f"  {crit:20s}: {rate:.3f}  95%CI=[{lo:.3f}, {hi:.3f}]  n={len(grp)}")


def error_descriptives(df):
    """Error types - purely descriptive, no inference."""
    header("ERROR TYPE DESCRIPTIVES (no inference)")
    n_total = len(df)
    n_incorrect = (df["Is_Factual_Correct"] == 0).sum()
    print(f"Incorrect justifications: {n_incorrect}/{n_total} ({n_incorrect/n_total*100:.1f}%)\n")
    for col in ERR_COLS:
        cnt = int(df[col].sum())
        pct_all = cnt / n_total * 100
        pct_inc = cnt / n_incorrect * 100 if n_incorrect > 0 else 0
        print(f"  {col:25s}: {cnt:4d} ({pct_all:5.1f}% of all, {pct_inc:5.1f}% of incorrect)")

    sub("Error rates by Model x Format (descriptive)")
    tbl = df.groupby(["Model", "Input_Format"])[ERR_COLS].mean()
    tbl.insert(0, "n", df.groupby(["Model", "Input_Format"]).size())
    print(tbl.round(3).to_string())

    sub("Error rates in disagreement vs agreement (descriptive)")
    disagree = df[df["Agreement_Score"] <= 2]
    agree = df[df["Agreement_Score"] >= 3]
    print(f"  {'Error type':25s}  {'Disagree':>10s}  {'Agree':>10s}  {'Ratio':>8s}")
    for col in ERR_COLS:
        rd = disagree[col].mean() if len(disagree) > 0 else 0
        ra = agree[col].mean() if len(agree) > 0 else 0
        ratio = f"{rd/ra:.1f}x" if ra > 0 else "n/a"
        print(f"  {col:25s}  {rd:10.3f}  {ra:10.3f}  {ratio:>8s}")


def main():
    df = load_data()
    descriptive_summary(df)
    confidence_intervals(df)
    mixed_agreement(df)
    mixed_factual(df)
    fc_agreement_association(df)
    error_descriptives(df)

if __name__ == "__main__":
    main()
