import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def analyze_guidelines():
    """
    Analyze the guidelines evaluation CSV.
    This is the equivalent of the G2 analysis but for guidelines.
    """
    
    # Read the CSV
    df = pd.read_csv("guidelines_evaluation.csv")
    
    # Strip whitespace from column names (in case there are spaces)
    df.columns = df.columns.str.strip()
    
    # Handle partial_agreement column (NaN means no partial agreement, so treat as 0)
    if 'partial_agreement' in df.columns:
        df['partial_agreement'] = df['partial_agreement'].fillna(0).astype(int)
    else:
        df['partial_agreement'] = 0
    
    # Ensure all numeric columns are properly typed
    df['label_correct'] = df['label_correct'].astype(int)
    df['reason_correct'] = df['reason_correct'].astype(int)
    df['full_agreement'] = df['full_agreement'].astype(int)
    
    print("="*70)
    print("GUIDELINES EVALUATION ANALYSIS")
    print("="*70)
    print(f"\nTotal cases: {len(df)}")
    
    # 1. Overall summary by model and modality (label accuracy uses all data)
    print("\n" + "="*70)
    print("OVERALL METRICS BY MODEL AND MODALITY")
    print("="*70)
    
    summary = df.groupby(["model", "modality"]).agg(
        n_cases=("label_correct", "size"),
        label_accuracy=("label_correct", "mean"),
        reason_accuracy=("reason_correct", "mean"),
        full_agreement=("full_agreement", "mean"),
        partial_agreement=("partial_agreement", "mean"),
    ).reset_index()
    
    print(summary.to_string(index=False))
    
    # 2. Breakdown by criterion
    print("\n" + "="*70)
    print("LABEL ACCURACY BY CRITERION")
    print("="*70)
    
    criterion_summary = df.groupby(["criterion", "model", "modality"]).agg(
        n_cases=("label_correct", "size"),
        label_accuracy=("label_correct", "mean"),
    ).reset_index()
    
    print(criterion_summary.to_string(index=False))
    
    # 3. Breakdown by individual guideline
    print("\n" + "="*70)
    print("LABEL ACCURACY BY GUIDELINE")
    print("="*70)
    
    guideline_summary = df.groupby(["guideline_id", "guideline_name", "model", "modality"]).agg(
        label_accuracy=("label_correct", "mean"),
    ).reset_index()
    
    print(guideline_summary.to_string(index=False))
    
    # 4. Confusion analysis (cases where label is wrong)
    print("\n" + "="*70)
    print("LABEL MISMATCHES (GT vs LLM)")
    print("="*70)
    
    mismatches = df[df["label_correct"] == 0].copy()
    if len(mismatches) > 0:
        print(f"\nTotal mismatches: {len(mismatches)} out of {len(df)} cases")
        print("\nBreakdown by model and modality:")
        mismatch_summary = mismatches.groupby(["model", "modality"]).size().reset_index(name="count")
        print(mismatch_summary.to_string(index=False))
        
        print("\nMismatch details:")
        print(mismatches[["criterion", "guideline_id", "guideline_name", "model", "modality", "gt_label", "llm_label"]].to_string(index=False))
    else:
        print("No label mismatches found!")
    
    # 5. Save detailed summary
    summary.to_csv("guidelines_summary_by_model.csv", index=False)
    criterion_summary.to_csv("guidelines_summary_by_criterion.csv", index=False)
    guideline_summary.to_csv("guidelines_summary_by_guideline.csv", index=False)
    
    print("\n" + "="*70)
    print("SUMMARY FILES CREATED:")
    print("="*70)
    print("- guidelines_summary_by_model.csv")
    print("- guidelines_summary_by_criterion.csv")
    print("- guidelines_summary_by_guideline.csv")
    
    # 6. Create visualizations
    create_visualizations(df)
    
    return df, summary

def create_visualizations(df):
    """Create visualizations for the guidelines analysis."""
    
    # Create a figure with subplots (3x2 grid for 6 plots)
    fig, axes = plt.subplots(3, 2, figsize=(15, 18))
    fig.suptitle('Guidelines Evaluation Analysis', fontsize=16, fontweight='bold')
    
    # 1. Label accuracy by model and modality
    ax1 = axes[0, 0]
    summary = df.groupby(["model", "modality"])["label_correct"].mean().reset_index()
    summary_pivot = summary.pivot(index="model", columns="modality", values="label_correct")
    summary_pivot.plot(kind="bar", ax=ax1, rot=0)
    ax1.set_title("Label Accuracy by Model and Modality")
    ax1.set_ylabel("Accuracy")
    ax1.set_ylim([0, 1])
    ax1.legend(title="Modality")
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Label accuracy by criterion
    ax2 = axes[0, 1]
    criterion_summary = df.groupby(["criterion", "model"])["label_correct"].mean().reset_index()
    criterion_pivot = criterion_summary.pivot(index="criterion", columns="model", values="label_correct")
    criterion_pivot.plot(kind="bar", ax=ax2, rot=45)
    ax2.set_title("Label Accuracy by Criterion")
    ax2.set_ylabel("Accuracy")
    ax2.set_ylim([0, 1])
    ax2.legend(title="Model")
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Full vs Partial Agreement
    ax3 = axes[1, 0]
    agreement_summary = df.groupby(["model", "modality"]).agg({
        "full_agreement": "mean",
        "partial_agreement": "mean"
    }).reset_index()
    
    x = np.arange(len(agreement_summary))
    width = 0.35
    
    ax3.bar(x - width/2, agreement_summary["full_agreement"], width, 
            label="Full Agreement", alpha=0.8, color='#2ecc71')
    ax3.bar(x + width/2, agreement_summary["partial_agreement"], width, 
            label="Partial Agreement", alpha=0.8, color='#f39c12')
    
    ax3.set_title("Full vs Partial Agreement")
    ax3.set_ylabel("Agreement Rate")
    ax3.set_ylim([0, 1])
    ax3.set_xticks(x)
    ax3.set_xticklabels([f"{row['model']}\n{row['modality']}" for _, row in agreement_summary.iterrows()], rotation=0)
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Comparison: Label vs Reason accuracy
    ax4 = axes[1, 1]
    comparison = df.groupby(["model", "modality"]).agg({
        "label_correct": "mean",
        "reason_correct": "mean"
    }).reset_index()
    
    x = np.arange(len(comparison))
    width = 0.35
    
    ax4.bar(x - width/2, comparison["label_correct"], width, label="Label Accuracy", alpha=0.8)
    ax4.bar(x + width/2, comparison["reason_correct"], width, label="Reason Accuracy", alpha=0.8)
    
    ax4.set_title("Label vs Reason Accuracy")
    ax4.set_ylabel("Accuracy")
    ax4.set_ylim([0, 1])
    ax4.set_xticks(x)
    ax4.set_xticklabels([f"{row['model']}\n{row['modality']}" for _, row in comparison.iterrows()], rotation=0)
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    
    # 5. Stacked: Label Correct + Reason Correct + Partial + None
    ax5 = axes[2, 0]
    
    # Calculate rates for each category
    # full: label + reason correct (full_agreement = 1)
    # partial: explicitly marked as partial OR (reason correct but label wrong)
    # label_only: only label correct (reason wrong, no partial)
    # none: nothing matches (label wrong, reason wrong, no partial)
    stacked_summary = df.groupby(["model", "modality"]).apply(
        lambda x: pd.Series({
            "full": (x["full_agreement"] == 1).mean(),
            "partial": ((x["partial_agreement"] == 1) | 
                       ((x["label_correct"] == 0) & (x["reason_correct"] == 1) & (x["partial_agreement"] == 0))).mean(),
            "label_only": ((x["label_correct"] == 1) & (x["reason_correct"] == 0) & (x["partial_agreement"] == 0)).mean(),
            "none": ((x["label_correct"] == 0) & (x["reason_correct"] == 0) & (x["partial_agreement"] == 0)).mean()
        })
    ).reset_index()
    
    stacked_summary['model_modality'] = stacked_summary['model'] + '\n' + stacked_summary['modality']
    
    x = np.arange(len(stacked_summary))
    
    ax5.bar(x, stacked_summary["full"], label="Full Agreement", alpha=0.9, color='#2ecc71')
    ax5.bar(x, stacked_summary["partial"], bottom=stacked_summary["full"], 
            label="Partial Agreement", alpha=0.9, color='#f39c12')
    ax5.bar(x, stacked_summary["label_only"], 
            bottom=stacked_summary["full"] + stacked_summary["partial"],
            label="Label Only", alpha=0.9, color='#3498db')
    ax5.bar(x, stacked_summary["none"], 
            bottom=stacked_summary["full"] + stacked_summary["partial"] + stacked_summary["label_only"],
            label="No Agreement", alpha=0.9, color='#e74c3c')
    
    ax5.set_title("Agreement Distribution (Stacked)")
    ax5.set_ylabel("Proportion")
    ax5.set_ylim([0, 1])
    ax5.set_xticks(x)
    ax5.set_xticklabels(stacked_summary['model_modality'], rotation=0)
    ax5.legend(loc='upper right')
    ax5.grid(axis='y', alpha=0.3)
    
    # 6. Agreement by Criterion
    ax6 = axes[2, 1]
    criterion_agreement = df.groupby(["criterion"]).agg({
        "full_agreement": "mean",
        "partial_agreement": "mean",
        "label_correct": "mean"
    }).reset_index()
    
    x = np.arange(len(criterion_agreement))
    width = 0.25
    
    ax6.bar(x - width, criterion_agreement["label_correct"], width, 
            label="Label Correct", alpha=0.8, color='#3498db')
    ax6.bar(x, criterion_agreement["full_agreement"], width, 
            label="Full Agreement", alpha=0.8, color='#2ecc71')
    ax6.bar(x + width, criterion_agreement["partial_agreement"], width, 
            label="Partial Agreement", alpha=0.8, color='#f39c12')
    
    ax6.set_title("Agreement Rates by Criterion")
    ax6.set_ylabel("Rate")
    ax6.set_ylim([0, 1])
    ax6.set_xticks(x)
    ax6.set_xticklabels(criterion_agreement["criterion"], rotation=45, ha='right')
    ax6.legend()
    ax6.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("guidelines_analysis.png", dpi=300, bbox_inches='tight')
    print("\n✓ Visualization saved: guidelines_analysis.png")
    
    # Close the plot to free memory
    plt.close()

if __name__ == "__main__":
    df, summary = analyze_guidelines()

