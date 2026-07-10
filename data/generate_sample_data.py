import csv
import random
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_gfair_companies():
    print("[INFO] Fetching real company data from G-FAIR KOREA...")
    url = "https://gfair.or.kr/kr/online/exhibitor/exhibitorList.do"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[WARN] Failed to access G-FAIR (Status code: {response.status_code}). Using fallback mode.")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        com_list_ul = soup.find('ul', class_='com_list')
        
        if not com_list_ul:
            print("[WARN] Could not find class='com_list' on page. Using fallback mode.")
            return []
            
        li_elements = com_list_ul.find_all('li')
        crawled_companies = []
        
        for li in li_elements:
            # 1. Company Name
            name_el = li.find('span', class_='cname')
            if not name_el:
                continue
            name = name_el.text.strip()
            
            # 2. Website URL
            web_el = li.find('a', class_='webs')
            website = ""
            if web_el:
                span_el = web_el.find('span')
                if span_el:
                    website = span_el.text.strip()
                    
            # 3. Category
            category = "Living"  # Default
            ccont02_el = li.find('span', class_='ccont02')
            if ccont02_el:
                spans = ccont02_el.find_all('span')
                # Usually: [Year, Address, Category] or similar
                # Let's find spans that represent our target categories or take the last one
                if len(spans) >= 3:
                    raw_cat = spans[2].text.strip()
                    if raw_cat:
                        # Map/Clean Category
                        category = raw_cat.split(',')[0]  # Take first if comma-separated
            
            crawled_companies.append({
                "company_name": name,
                "website": website,
                "category": category
            })
            
        print(f"[OK] Successfully crawled {len(crawled_companies)} companies from G-FAIR!")
        return crawled_companies
        
    except Exception as e:
        print(f"[WARN] Crawler error: {e}. Using fallback mode.")
        return []

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
        },
        {
            "exhibition_id": "EXH-06",
            "name": "G-FAIR KOREA 2026",
            "start_date": "2026-10-22",
            "end_date": "2026-10-24",
            "venue": "KINTEX"
        }
    ]
    
    exh_file_path = os.path.join('data', 'exhibitions.csv')
    with open(exh_file_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["exhibition_id", "name", "start_date", "end_date", "venue"])
        writer.writeheader()
        writer.writerows(exhibitions)
    print(f"[OK] Created: {exh_file_path} ({len(exhibitions)} entries)")

    # 2. Company Data Generation
    categories = ["Beauty", "Food", "Living", "Fashion", "Health", "Smart", "Tech"]
    
    # Prefix and suffix elements to construct realistic-sounding Korean business names (fallback)
    prefixes = [
        "네추럴", "그린", "코리아", "한빛", "글로벌", "화인", "웰빙", "이노", "선샤인", "디지털",
        "유니온", "클린", "스마트", "미래", "제일", "에코", "클래식", "오리엔탈", "더블유", "에이치"
    ]
    suffixes = [
        "뷰티", "푸드", "인터내셔널", "코스메틱", "라이프", "코퍼레이션", "리빙", "바이오", "제약", "시스템",
        "패션", "케어", "테크", "유통", "아트", "디자인", "헬스", "컴퍼니", "인더스트리", "네트웍스"
    ]
    
    # Generate mock company names for EXH-01 to EXH-05
    company_names = set()
    while len(company_names) < 35:  # Generate 35 mock names
        name = f"(주){random.choice(prefixes)}{random.choice(suffixes)}"
        company_names.add(name)
    company_names = list(company_names)
    
    companies = []
    booth_sections = ["A", "B", "C", "D", "E", "F"]
    
    # Generate data for other exhibitions first
    for idx, name in enumerate(company_names):
        company_id = f"COM-{idx+1:03d}"
        exh = random.choice(exhibitions[:-1])  # Exclude G-FAIR (EXH-06) for mock loop
        exh_id = exh["exhibition_id"]
        booth = f"{random.choice(booth_sections[:-1])}-{random.randint(101, 199)}"
        
        # Select category based on exhibition
        if exh_id == "EXH-01":
            category = random.choices(["Beauty", "Health", "Living"], weights=[0.7, 0.2, 0.1])[0]
        elif exh_id == "EXH-02":
            category = random.choices(["Food", "Health", "Living"], weights=[0.7, 0.2, 0.1])[0]
        elif exh_id == "EXH-04":
            category = random.choices(["Living", "Fashion", "Beauty"], weights=[0.5, 0.3, 0.2])[0]
        else:
            category = random.choice(["Living", "Fashion", "Health", "Food", "Smart"])
            
        employee_count = random.randint(3, 150)
        has_export = random.choice(["Y", "N"])
        
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
        
    # Generate G-FAIR KOREA 2026 (EXH-06) companies using crawler
    gfair_crawled = fetch_gfair_companies()
    
    # Fallback to mock G-FAIR companies if crawler returned empty
    if not gfair_crawled:
        print("[INFO] Fallback: Generating 10 mock companies for G-FAIR KOREA...")
        gfair_mock_names = set()
        while len(gfair_mock_names) < 10:
            gfair_mock_names.add(f"(주){random.choice(prefixes)}테크")
        for mock_name in gfair_mock_names:
            gfair_crawled.append({
                "company_name": mock_name,
                "website": f"https://www.{random.choice(prefixes).lower()}-tech.com",
                "category": random.choice(["Tech", "Smart", "Kitchen"])
            })
            
    # Assign attributes to G-FAIR companies
    for idx, raw_comp in enumerate(gfair_crawled):
        comp_id = f"COM-{len(companies) + 1:03d}"
        
        # Booth number (using F section for G-FAIR)
        booth = f"F-{random.randint(101, 199)}"
        employee_count = random.randint(5, 180)
        has_export = random.choice(["Y", "N"])
        
        # Scoring metrics
        if employee_count > 60:
            website_quality_score = random.randint(55, 100)
            email_trust_score = random.randint(45, 100)
        else:
            website_quality_score = random.randint(15, 95)
            email_trust_score = random.randint(15, 95)
            
        companies.append({
            "company_id": comp_id,
            "exhibition_id": "EXH-06",
            "company_name": raw_comp["company_name"],
            "booth_number": booth,
            "category": raw_comp["category"],
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

if __name__ == "__main__":
    generate_data()
