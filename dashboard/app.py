import os
import streamlit as pd_st # importing as pd_st to avoid variable name shadowing if we use standard pd for pandas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set Streamlit Page Configuration
pd_st.set_page_config(
    page_title="K-Expo LeadGen CRM 대시보드",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Premium Look
pd_st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Elegant Title Banner with Gradient */
    .title-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(30, 60, 114, 0.15);
    }
    .title-container h1 {
        font-weight: 700;
        margin: 0;
        font-size: 2.5rem;
        letter-spacing: -0.5px;
    }
    .title-container p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Beautiful KPI Cards */
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 5px solid #2a5298;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.2s ease-in-out;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
    }
    .kpi-title {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 0.5rem;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #10b981;
        font-weight: 500;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# 2. Data Loading Function with Cache
@pd_st.cache_data
def load_data():
    comp_path = os.path.join('data', 'companies.csv')
    score_path = os.path.join('data', 'lead_scores.csv')
    exh_path = os.path.join('data', 'exhibitions.csv')
    
    if not (os.path.exists(comp_path) and os.path.exists(score_path) and os.path.exists(exh_path)):
        return None
        
    df_comp = pd.read_csv(comp_path, encoding='utf-8-sig')
    df_score = pd.read_csv(score_path, encoding='utf-8-sig')
    df_exh = pd.read_csv(exh_path, encoding='utf-8-sig')
    
    # Merge datasets
    # 1) Merge companies with their lead scores
    df_merged = pd.merge(
        df_comp, 
        df_score.drop(columns=['company_name'], errors='ignore'), 
        on='company_id'
    )
    # 2) Merge with exhibition details
    df_merged = pd.merge(df_merged, df_exh, on='exhibition_id', suffixes=('', '_exh'))
    
    return df_merged, df_exh

df = load_data()

if df is None:
    pd_st.error("🚨 데이터를 불러오지 못했습니다! data/ 폴더에 샘플 데이터 파일이 정상적으로 존재하는지 확인해주세요.")
    pd_st.info("💡 1단계 및 2단계의 파이썬 파일들을 차례대로 먼저 실행해야 CSV 파일들이 완비됩니다.")
    pd_st.code("python data/generate_sample_data.py\npython scoring/lead_scoring.py")
else:
    df_merged, df_exh = df
    
    # Header Title Banner
    pd_st.markdown("""
    <div class="title-container">
        <h1>🎯 K-Expo LeadGen CRM 대시보드</h1>
        <p>전시회 참가기업 가중치 평가 기반 우선순위 리드 스코어링 분석 및 마케팅 CRM 솔루션</p>
    </div>
    """, unsafe_allow_html=True)

    # ------------------ SIDEBAR FILTERS ------------------
    pd_st.sidebar.markdown("### 🔍 리드 필터링 (Filters)")
    
    # Search by Company Name
    search_query = pd_st.sidebar.text_input("🏢 기업명 검색", "", placeholder="기업명 입력...")
    
    # Filter by Category
    all_categories = sorted(list(df_merged['category'].unique()))
    selected_categories = pd_st.sidebar.multiselect(
        "🏷️ 카테고리 선택", 
        options=all_categories, 
        default=all_categories
    )
    
    # Filter by Exhibition Name
    exh_names = sorted(list(df_merged['name'].unique()))
    selected_exhibitions = pd_st.sidebar.multiselect(
        "🎪 참가 전시회 선택", 
        options=exh_names, 
        default=exh_names
    )
    
    # Filter by Lead Score Slider
    min_score = float(df_merged['score'].min())
    max_score = float(df_merged['score'].max())
    score_range = pd_st.sidebar.slider(
        "📊 리드 스코어 구간",
        min_value=min_score,
        max_value=max_score,
        value=(min_score, max_score),
        step=1.0
    )
    
    # Filter by Export status
    export_filter = pd_st.sidebar.radio(
        "🚢 수출 가능 여부 (has_export)",
        options=["전체", "수출 가능 (Y)", "내수 전용 (N)"]
    )
    
    # Apply Filtering to DataFrame
    filtered_df = df_merged.copy()
    
    if search_query:
        filtered_df = filtered_df[filtered_df['company_name'].str.contains(search_query, case=False, na=False)]
        
    filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
    filtered_df = filtered_df[filtered_df['name'].isin(selected_exhibitions)]
    filtered_df = filtered_df[(filtered_df['score'] >= score_range[0]) & (filtered_df['score'] <= score_range[1])]
    
    if export_filter == "수출 가능 (Y)":
        filtered_df = filtered_df[filtered_df['has_export'] == 'Y']
    elif export_filter == "내수 전용 (N)":
        filtered_df = filtered_df[filtered_df['has_export'] == 'N']

    # ------------------ KPI CARDS (TOP) ------------------
    # Calculate Metrics
    total_count = len(filtered_df)
    avg_score = filtered_df['score'].mean() if total_count > 0 else 0.0
    
    # Threshold for top 20%
    if len(df_merged) > 0:
        top_20_threshold = df_merged['score'].quantile(0.80)
    else:
        top_20_threshold = 0.0
        
    # High-quality Lead Count in filtered data (>= top_20_threshold)
    high_leads_count = len(filtered_df[filtered_df['score'] >= top_20_threshold])
    
    kpi_col1, kpi_card_col2, kpi_card_col3, kpi_card_col4 = pd_st.columns(4)
    
    with kpi_col1:
        pd_st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #2563eb;">
            <div class="kpi-title">👥 분석 대상 리드 수</div>
            <div class="kpi-value">{total_count} <span style="font-size: 1.2rem; font-weight: normal; color: #64748b;">개사</span></div>
            <div class="kpi-sub" style="color: #64748b;">필터 적용 완료</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_card_col2:
        pd_st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #10b981;">
            <div class="kpi-title">⭐ 평균 리드 스코어</div>
            <div class="kpi-value">{avg_score:.1f} <span style="font-size: 1.2rem; font-weight: normal; color: #64748b;">점</span></div>
            <div class="kpi-sub">기준치: 100점 만점</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_card_col3:
        pd_st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #f59e0b;">
            <div class="kpi-title">🏆 상위 20% 스코어 기준</div>
            <div class="kpi-value">{top_20_threshold:.1f} <span style="font-size: 1.2rem; font-weight: normal; color: #64748b;">점</span></div>
            <div class="kpi-sub" style="color: #f59e0b;">이 점수 이상 우수 리드 분류</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_card_col4:
        pd_st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #8b5cf6;">
            <div class="kpi-title">🔥 고품질 리드 개수</div>
            <div class="kpi-value">{high_leads_count} <span style="font-size: 1.2rem; font-weight: normal; color: #64748b;">개사</span></div>
            <div class="kpi-sub" style="color: #8b5cf6;">전체 상위 20% 점수 이상</div>
        </div>
        """, unsafe_allow_html=True)

    pd_st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ CHARTS SECTION (MIDDLE) ------------------
    char_col1, char_col2 = pd_st.columns(2)
    
    with char_col1:
        pd_st.markdown("### 📊 리드 스코어 분포")
        if total_count > 0:
            fig_hist = px.histogram(
                filtered_df, 
                x="score", 
                nbins=15, 
                title="Lead Score Distribution",
                color_discrete_sequence=["#2a5298"],
                labels={"score": "리드 스코어 (점)", "count": "기업 수"}
            )
            fig_hist.add_vline(
                x=top_20_threshold, 
                line_dash="dash", 
                line_color="#f59e0b",
                annotation_text="우수 리드 기준선 (상위 20%)",
                annotation_position="top left"
            )
            fig_hist.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=40, b=20),
                height=350
            )
            pd_st.plotly_chart(fig_hist, use_container_width=True)
        else:
            pd_st.warning("선택 조건에 해당하는 데이터가 없어 스코어 분포를 표시할 수 없습니다.")
            
    with char_col2:
        pd_st.markdown("### 🏷️ 카테고리별 리드 분포")
        if total_count > 0:
            fig_pie = px.pie(
                filtered_df, 
                names="category", 
                values="score", 
                title="Category Share (Weighted by Score)",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=40, b=20),
                height=350
            )
            pd_st.plotly_chart(fig_pie, use_container_width=True)
        else:
            pd_st.warning("선택 조건에 해당하는 데이터가 없어 카테고리 분포를 표시할 수 없습니다.")

    pd_st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ ADVANCED BREAKDOWN & TABULATION ------------------
    pd_st.markdown("### 🏆 항목별 점수 기여도 평균")
    if total_count > 0:
        breakdown_cols = pd_st.columns(4)
        avg_web = filtered_df['score_website'].mean()
        avg_email = filtered_df['score_email'].mean()
        avg_export = filtered_df['score_export'].mean()
        avg_emp = filtered_df['score_employee'].mean()
        
        with breakdown_cols[0]:
            pd_st.metric("🌐 웹사이트 점수 기여도 (30점 만점)", f"{avg_web:.2f} 점")
        with breakdown_cols[1]:
            pd_st.metric("✉️ 이메일 신뢰 기여도 (25점 만점)", f"{avg_email:.2f} 점")
        with breakdown_cols[2]:
            pd_st.metric("🚢 수출 역량 기여도 (25점 만점)", f"{avg_export:.2f} 점")
        with breakdown_cols[3]:
            pd_st.metric("🏢 기업 규모 기여도 (20점 만점)", f"{avg_emp:.2f} 점")
            
    pd_st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ DATATABLE SECTION (BOTTOM) ------------------
    pd_st.markdown("### 📋 상세 리드 관리 테이블 (Lead Directory)")
    
    if total_count > 0:
        # Sort and Format Display Table
        display_df = filtered_df[[
            'company_id', 'company_name', 'score', 'category', 'name', 'booth_number',
            'employee_count', 'has_export', 'website_quality_score', 'email_trust_score'
        ]].copy()
        
        display_df.columns = [
            '기업 ID', '기업명', '리드 스코어', '카테고리', '전시회명', '부스 번호',
            '임직원 수', '수출 여부', '웹사이트 평점', '이메일 신뢰점수'
        ]
        
        # Enable sorting on UI
        sort_by_col = pd_st.selectbox("정렬 기준 선택", options=['리드 스코어', '기업명', '임직원 수'], index=0)
        ascending_choice = pd_st.radio("정렬 방식", options=["내림차순 (높은 순)", "오름차순 (낮은 순)"], horizontal=True)
        
        is_ascending = (ascending_choice == "오름차순 (낮은 순)")
        display_df = display_df.sort_values(by=sort_by_col, ascending=is_ascending)
        
        # Style and render
        pd_st.dataframe(
            display_df, 
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        # Export option (CSV Download)
        csv_data = display_df.to_csv(index=False, encoding='utf-8-sig') # use utf-8-sig for Excel compatibility in Korea
        pd_st.download_button(
            label="📥 필터링된 리드 결과 CSV 다운로드",
            data=csv_data,
            file_name="filtered_leads_crm.csv",
            mime="text/csv"
        )
    else:
        pd_st.info("💡 필터 조건에 부합하는 리드가 없습니다. 필터를 조정해 주시기 바랍니다.")
