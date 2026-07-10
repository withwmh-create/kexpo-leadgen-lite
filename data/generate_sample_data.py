import csv
import random
import os
from datetime import datetime, timedelta

def generate_data():
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # 1. Exhibition Data
    exhibitions = [
        {
            "exhibition_id": "EXH-01",
            "name": "K-Beauty Expo 2026",
            "start_date": "2026-10-15",
            "end_date": "2026-10-18",
            "venue": "KINTEX"
        },
        {
            "exhibition_id": "EXH-02",
            "name": "Seoul Food & Hotel 2026",
            "start_date": "2026-06-02",
            "end_date": "2026-06-05",
            "venue": "KINTEX"
        },
        {
            "exhibition_id": "EXH-03",
            "name": "Mega Show 2026 Season 1",
            "start_date": "2026-05-21",
            "end_date": "2026-05-24",
            "venue": "SETEC"
        },
        {
            "exhibition_id": "EXH-04",
            "name": "K-Handmade Fair 2026",
            "start_date": "2026-11-12",
            "end_date": "2026-11-15",
            "venue": "COEX"
        },
        {
            "exhibition_id": "EXH-05",
            "name": "Korea Consumer Goods Showcase 2026",
            "start_date": "2026-04-08",
            "end_date": "2026-04-09",
            "venue": "COEX"
        }
    ]
    
    exh_file_path = os.path.join('data', 'exhibitions.csv')
    with open(exh_file_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["exhibition_id", "name", "start_date", "end_date", "venue"])
        writer.writeheader()
        writer.writerows(exhibitions)
    print(f"[OK] Created: {exh_file_path} ({len(exhibitions)} entries)")

    # 2. Company Data Generation
    categories = ["Beauty", "Food", "Living", "Fashion", "Health"]
    
    # Prefix and suffix elements to construct realistic-sounding Korean business names
    prefixes = [
        "네추럴", "그린", "코리아", "한빛", "글로벌", "화인", "웰빙", "이노", "선샤인", "디지털",
        "유니온", "클린", "스마트", "미래", "제일", "에코", "클래식", "오리엔탈", "더블유", "에이치"
    ]
    suffixes = [
        "뷰티", "푸드", "인터내셔널", "코스메틱", "라이프", "코퍼레이션", "리빙", "바이오", "제약", "시스템",
        "패션", "케어", "테크", "유통", "아트", "디자인", "헬스", "컴퍼니", "인더스트리", "네트웍스"
    ]
    
    # Fixed lists of names or random generation
    company_names = set()
    while len(company_names) < 45:  # Generate 45 unique company names
        name = f"(주){random.choice(prefixes)}{random.choice(suffixes)}"
        company_names.add(name)
        
    company_names = list(company_names)
    
    companies = []
    booth_sections = ["A", "B", "C", "D", "E"]
    
    for idx, name in enumerate(company_names):
        company_id = f"COM-{idx+1:03d}"
        exh = random.choice(exhibitions)
        exh_id = exh["exhibition_id"]
        
        # Booth number e.g., A-102, C-205, etc.
        booth = f"{random.choice(booth_sections)}-{random.randint(101, 199)}"
        
        # Select category based on exhibition if possible to make it more coherent
        # (e.g. Beauty Exhibitions have higher probability of Beauty companies)
        if exh_id == "EXH-01": # K-Beauty Expo
            category = random.choices(["Beauty", "Health", "Living"], weights=[0.7, 0.2, 0.1])[0]
        elif exh_id == "EXH-02": # Seoul Food
            category = random.choices(["Food", "Health", "Living"], weights=[0.7, 0.2, 0.1])[0]
        elif exh_id == "EXH-03": # Mega Show
            category = random.choice(categories)
        elif exh_id == "EXH-04": # Handmade Fair
            category = random.choices(["Living", "Fashion", "Beauty"], weights=[0.5, 0.3, 0.2])[0]
        else: # Consumer Goods
            category = random.choice(categories)
            
        employee_count = random.randint(3, 150)
        has_export = random.choice(["Y", "N"])
        
        # Score attributes: random but some logical correlations for realistic scoring testing later
        # e.g., larger companies might have better websites or higher trust score (not strictly, but slightly correlated)
        if employee_count > 50:
            website_quality_score = random.randint(50, 100)
            email_trust_score = random.randint(40, 100)
        else:
            website_quality_score = random.randint(10, 95)
            email_trust_score = random.randint(10, 95)
            
        companies.append({
            "company_id": company_id,
            "exhibition_id": exh_id,
            "company_name": name,
            "booth_number": booth,
            "category": category,
            "employee_count": employee_count,
            "has_export": has_export,
            "website_quality_score": website_quality_score,
            "email_trust_score": email_trust_score
        })
        
    comp_file_path = os.path.join('data', 'companies.csv')
    with open(comp_file_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "company_id", "exhibition_id", "company_name", "booth_number",
            "category", "employee_count", "has_export", "website_quality_score",
            "email_trust_score"
        ])
        writer.writeheader()
        writer.writerows(companies)
    print(f"[OK] Created: {comp_file_path} ({len(companies)} entries)")

    # 3. Print evaluation summary
    print("\n" + "="*50)
    print(" EVALUATION SUMMARY")
    print("="*50)
    
    print(f"Total Exhibitions: {len(exhibitions)}")
    print(f"Total Companies: {len(companies)}")
    
    # Category Distribution Calculation
    cat_counts = {}
    for c in companies:
        cat = c["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
    print("\nCategory Distribution:")
    print("-" * 30)
    print(f"{'Category':<15} | {'Count':<5} | {'Percentage':<5}")
    print("-" * 30)
    for cat, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(companies)) * 100
        print(f"{cat:<15} | {count:<5} | {pct:.1f}%")
    print("-" * 30)

    # First 5 rows of companies
    print("\ncompanies.csv Preview (Top 5 rows):")
    print("-" * 80)
    print("company_id | exh_id | company_name | booth | category | employees | export | web_score | email_score")
    print("-" * 80)
    for c in companies[:5]:
        print(f"{c['company_id']} | {c['exhibition_id']} | {c['company_name']} | {c['booth_number']} | {c['category']} | {c['employee_count']} | {c['has_export']} | {c['website_quality_score']} | {c['email_trust_score']}")
    print("-" * 80)

if __name__ == "__main__":
    generate_data()
