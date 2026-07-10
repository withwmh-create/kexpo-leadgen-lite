import os
import pandas as pd
import numpy as np

# 1. Config Dictionary for Scoring Weights and Rules
# Weights must sum to 1.0
SCORING_CONFIG = {
    "weights": {
        "website_quality_score": 0.30,  # Website quality (0~100)
        "email_trust_score": 0.25,      # Email trust (0~100)
        "has_export_score": 0.25,       # Export capability (Y/N)
        "employee_size_score": 0.20     # Company scale (based on employee count)
    },
    "rules": {
        "export_scores": {
            "Y": 100.0,
            "N": 30.0  # Give a minor baseline score even without export
        },
        "employee_brackets": [
            {"min_limit": 50, "score": 100.0},
            {"min_limit": 10, "score": 70.0},
            {"min_limit": 0, "score": 40.0}
        ]
    }
}

def calculate_employee_score(employee_count):
    for bracket in SCORING_CONFIG["rules"]["employee_brackets"]:
        if employee_count >= bracket["min_limit"]:
            return bracket["score"]
    return 0.0

def run_lead_scoring():
    # File Paths
    input_path = os.path.join('data', 'companies.csv')
    output_path = os.path.join('data', 'lead_scores.csv')
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found! Please run generate_sample_data.py first.")
        return
    
    # Read companies CSV
    df = pd.read_csv(input_path, encoding='utf-8-sig')
    
    # Raw Score Breakdown Calculations
    df['raw_website_score'] = df['website_quality_score'].astype(float)
    df['raw_email_score'] = df['email_trust_score'].astype(float)
    df['raw_export_score'] = df['has_export'].map(SCORING_CONFIG["rules"]["export_scores"])
    df['raw_employee_score'] = df['employee_count'].apply(calculate_employee_score)
    
    # Weighted Score Contributions (Breakdown)
    w = SCORING_CONFIG["weights"]
    df['contrib_website'] = df['raw_website_score'] * w['website_quality_score']
    df['contrib_email'] = df['raw_email_score'] * w['email_trust_score']
    df['contrib_export'] = df['raw_export_score'] * w['has_export_score']
    df['contrib_employee'] = df['raw_employee_score'] * w['employee_size_score']
    
    # Total Score
    df['score'] = (
        df['contrib_website'] + 
        df['contrib_email'] + 
        df['contrib_export'] + 
        df['contrib_employee']
    ).round(1)
    
    # Clean up and select output columns
    output_df = df[[
        'company_id', 'company_name', 'score',
        'contrib_website', 'contrib_email', 'contrib_export', 'contrib_employee',
        'raw_website_score', 'raw_email_score', 'raw_export_score', 'raw_employee_score'
    ]].copy()
    
    # Rename columns for clarity in output
    output_df.columns = [
        'company_id', 'company_name', 'score',
        'score_website', 'score_email', 'score_export', 'score_employee',
        'raw_website', 'raw_email', 'raw_export', 'raw_employee'
    ]
    
    # Save to CSV
    output_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"[OK] Lead Scoring Completed! Result saved to: {output_path}")
    
    # --- EVALUATION SUMMARY ---
    print("\n" + "="*70)
    print(" LEAD SCORING EVALUATION SUMMARY")
    print("="*70)
    
    # 1. Top 10 Leads
    top_10 = output_df.sort_values(by='score', ascending=False).head(10)
    print("\nTop 10 High-Quality Leads:")
    print("-" * 115)
    print(f"{'Rank':<4} | {'ID':<7} | {'Company Name':<16} | {'Total Score':<11} | {'Website (30)':<12} | {'Email (25)':<10} | {'Export (25)':<11} | {'Employee (20)':<13}")
    print("-" * 115)
    for rank, (_, row) in enumerate(top_10.iterrows(), 1):
        print(f"#{rank:<2} | {row['company_id']:<7} | {row['company_name']:<16} | {row['score']:<11} | {row['score_website']:<12.1f} | {row['score_email']:<10.1f} | {row['score_export']:<11.1f} | {row['score_employee']:<13.1f}")
    print("-" * 115)
    
    # 2. Score Distribution (Text-based Histogram)
    print("\nScore Distribution (Histogram):")
    print("-" * 50)
    bins = [0, 40, 50, 60, 70, 80, 90, 100]
    bin_labels = [" <40 ", "40-49", "50-59", "60-69", "70-79", "80-89", "90-100"]
    
    distribution = pd.cut(output_df['score'], bins=bins, labels=bin_labels, right=False)
    counts = distribution.value_counts().sort_index()
    
    max_count = counts.max()
    scale = 20  # Scale factor for display
    
    for label, count in counts.items():
        bar = "■" * int((count / max_count) * scale) if max_count > 0 else ""
        print(f"{label} : {count:<3} {bar}")
    print("-" * 50)
    print(f"Mean Score   : {output_df['score'].mean():.2f}")
    print(f"Median Score : {output_df['score'].median():.2f}")
    print(f"Min / Max    : {output_df['score'].min()} / {output_df['score'].max()}")
    print("-" * 50)

if __name__ == "__main__":
    run_lead_scoring()
