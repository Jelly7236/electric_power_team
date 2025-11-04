import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from report import generate_report_from_template

# ============================================================================
# App config
# ============================================================================
st.set_page_config(page_title="전력 데이터 분석", page_icon="📊", layout="wide")

# ============================================================================
# 최적화된 CSS
# ============================================================================
st.markdown("""
<style>
    /* 전역 설정 */
    .main {
        background-color: #F5F7FA;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* 제목 최적화 */
    h1 {
        color: #2C3E50;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-size: 2rem;
    }
    
    h2, h3 {
        color: #34495E;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* KPI 카드 - 그라데이션 스타일 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        color: white;
        text-align: center;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    .metric-card-purple {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-card-red {
        background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
    }
    
    .metric-card-cyan {
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
    }
    
    .metric-label {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        line-height: 1.2;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        opacity: 0.85;
        font-weight: 500;
    }
    
    /* 차트 컨테이너 */
    .stPlotlyChart {
        background: white;
        border-radius: 8px;
        padding: 0.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* 사이드바 최적화 */
    [data-testid="stSidebar"] {
        background: #f1f2f6;
        border-right: 1px solid #e0e6ed;
    }
    
    [data-testid="stSidebar"] h1 {
        font-size: 1.3rem;
        color: #2C3E50;
        font-weight: 700;
        padding: 0.5rem 0;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 1rem;
        color: #34495E;
        margin-top: 1rem;
        font-weight: 600;
    }
    
    /* 버튼 최적화 */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.2rem;
        transition: all 0.2s ease;
        font-size: 0.95rem;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Expander 최적화 */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border: 1px solid #e0e6ed;
        border-radius: 6px;
        font-weight: 600;
        color: #2C3E50;
        font-size: 0.9rem;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #e9ecef;
    }
    
    /* 데이터프레임 최적화 */
    [data-testid="stDataFrame"] {
        border: 1px solid #e0e6ed;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* 구분선 */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e0e6ed;
    }
    
    /* Tabs 최적화 */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { 
        font-size: 20px; 
        font-weight: 600; 
    }
    .stTabs [data-baseweb="tab-list"] button { 
        padding-top: 10px; 
        padding-bottom: 10px; 
    }
    
    /* Insight Panel Styles */
    .insights-panel-container {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    .insight-item {
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #667eea;
        background: #f8f9fa;
        border-radius: 6px;
    }
    .insight-item:last-child {
        margin-bottom: 0;
    }
    .insight-title {
        font-weight: 600;
        color: #667eea;
        margin-bottom: 8px;
        font-size: 16px;
    }
    .insight-text {
        color: #444;
        line-height: 1.6;
        font-size: 14px;
    }
    .insight-header {
        font-size: 24px;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 20px;
    }
    
    /* Tooltip */
    .tooltip-container{position:relative;display:inline-block}
    .tooltip-icon{cursor:help;color:#1f77b4;font-size:20px;margin-left:8px;vertical-align:middle}
    .tooltip-container .tooltip-text{visibility:hidden;width:400px;background:#333;color:#fff;text-align:left;border-radius:6px;padding:15px;position:absolute;z-index:1000;top:100%;left:50%;margin-left:-200px;margin-top:10px;opacity:0;transition:opacity .3s;font-size:13px;line-height:1.6;white-space:pre-line;box-shadow:0 4px 6px rgba(0,0,0,.3)}
    .tooltip-container:hover .tooltip-text{visibility:visible;opacity:1}
    .title-with-tooltip{display:flex;align-items:center;margin-bottom:1rem}
    .title-with-tooltip h3{margin:0;display:inline}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 차트 색상 팔레트
# ============================================================================
CHART_COLORS = {
    'power': '#1f77b4',
    'cost': '#28a745',
    'carbon': '#fa709a',
    'lagging_pf': '#FF6B6B',
    'leading_pf': '#4ECDC4',
    'light_load': '#4CAF50',
    'medium_load': '#FFC107',
    'maximum_load': '#EF5350',
    'working': '#1f77b4',
    'holiday': '#ff7f0e'
}

# ============================================================================
# Paths
# ============================================================================
TRAIN_PATH = "대시보드/data_dash/train_dash_df.csv"
MONTHLY_PF_PATH =  "대시보드/data_dash/월별 역률 패널티 계산.csv"
RATE_PDF = Path("대시보드/data_dash/2024년도7월1일시행전기요금표(종합)_출력용.pdf")

TEMPLATE_PATH = Path("대시보드/data_dash/고지서_템플릿.docx")

# ============================================================================
# 유틸리티 함수
# ============================================================================
def create_metric_card(label, value, delta, card_class):
    """그라데이션 메트릭 카드 HTML 생성"""
    return f"""
    <div class="metric-card {card_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value"><strong>{value}</strong></div>
        <div class="metric-delta">{delta}</div>
    </div>
    """

# ============================================================================
# 캐싱된 데이터 로더
# ============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    """데이터 로드 및 전처리"""
    df = pd.read_csv(path)
    dt = pd.to_datetime(df["측정일시"], errors="coerce")
    df = df.assign(
        측정일시=dt,
        year=dt.dt.year,
        month=dt.dt.month,
        day=dt.dt.day,
        hour=dt.dt.hour,
        minute=dt.dt.minute,
        date=dt.dt.date.astype(str),
    )
    if "단가" in df.columns:
        df = df.dropna(subset=["단가"])
    
    # 숫자형 컬럼 최적화
    numeric_cols = ["전력사용량(kWh)", "전기요금(원)"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def load_monthly_pf(path: Path) -> pd.DataFrame:
    """역률 데이터 로드"""
    try:
        pf = pd.read_csv(path)
        pf["year"] = pf["year"].astype(int)
        pf["month"] = pf["month"].astype(int)
        return pf
    except FileNotFoundError:
        st.error(f"오류: '{path.name}' 파일을 찾을 수 없습니다. 역률 지표가 0으로 표시됩니다.")
        return pd.DataFrame(columns=["year", "month", "역률_조정금액(원)"])

@st.cache_data(show_spinner=False)
def get_pdf_bytes(path: Path):
    """PDF 바이트 로드"""
    try:
        return path.read_bytes()
    except FileNotFoundError:
        st.error(f"파일을 찾을 수 없습니다: {path}")
        return None

@st.cache_data(show_spinner=False)
def get_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """월별 요약 데이터 생성"""
    monthly = (
        df.groupby("month")
        .agg({"전력사용량(kWh)": "sum", "전기요금(원)": "mean"})
        .reset_index()
    )
    monthly = monthly[monthly["month"] <= 11]
    return monthly

@st.cache_data(show_spinner=False)
def filter_dataframe(df: pd.DataFrame, filter_unit: str, selected_value: str, 
                     work_status: str, min_date: str, max_date: str) -> tuple:
    """데이터프레임 필터링 - 캐싱"""
    if filter_unit == '월별':
        if selected_value == "전체 기간":
            filtered = df.copy()
            label = "전체 기간"
        else:
            month_num = int(selected_value.replace('월', ''))
            filtered = df[df['month'] == month_num].copy()
            label = f"2024년 {month_num}월"
    else:  # 일별
        if selected_value == "전체 기간":
            filtered = df.copy()
            label = "전체 기간"
        else:
            filtered = df[(df['date'] >= min_date) & (df['date'] <= max_date)].copy()
            label = f"{min_date} ~ {max_date}"
    
    # 작업상태 필터
    if work_status != "전체":
        filtered = filtered[filtered['작업휴무'] == work_status].copy()
    
    return filtered, label

# ============================================================================
# Load data
# ============================================================================
df = load_data(TRAIN_PATH)
monthly_summary_df = load_monthly_pf(MONTHLY_PF_PATH)
pdf_data = get_pdf_bytes(RATE_PDF)

# 전체 데이터 기반 통계 (캐싱)
monthly_totals_all = df.groupby("month")["전력사용량(kWh)"].sum()
annual_monthly_avg_power = monthly_totals_all.mean()

# ============================================================================
# 사이드바 필터 - 버튼 방식으로 변경
# ============================================================================
# 세션 상태 초기화
if 'filter_applied' not in st.session_state:
    st.session_state.filter_applied = False
if 'current_filter_unit' not in st.session_state:
    st.session_state.current_filter_unit = '월별'
if 'current_selected_period' not in st.session_state:
    st.session_state.current_selected_period = "전체 기간"
if 'current_work_status' not in st.session_state:
    st.session_state.current_work_status = "전체"
if 'current_date_start' not in st.session_state:
    st.session_state.current_date_start = str(df['측정일시'].min().date())
if 'current_date_end' not in st.session_state:
    st.session_state.current_date_end = str(df['측정일시'].max().date())

st.sidebar.markdown("**분석 단위 선택**")
temp_filter_unit = st.sidebar.radio(
    "분석 단위를 선택하세요",
    ('월별', '일별'),
    index=0 if st.session_state.current_filter_unit == '월별' else 1,
    key='temp_filter_unit'
)

st.sidebar.markdown("---")
st.sidebar.markdown("**세부 기간 선택**")

min_date = df['측정일시'].min().date()
max_date = df['측정일시'].max().date()

if temp_filter_unit == '월별':
    sorted_months = sorted(df['month'].unique().tolist())
    month_options = ["전체 기간"] + [f"{m}월" for m in sorted_months]
    temp_selected_period = st.sidebar.selectbox(
        "분석 월을 선택하세요",
        options=month_options,
        index=month_options.index(st.session_state.current_selected_period) if st.session_state.current_selected_period in month_options else 0,
        key='temp_selected_period'
    )
    temp_date_start_str = str(min_date)
    temp_date_end_str = str(max_date)
else:  # 일별
    # 현재 저장된 날짜를 기본값으로 사용
    try:
        default_start = pd.to_datetime(st.session_state.current_date_start).date()
        default_end = pd.to_datetime(st.session_state.current_date_end).date()
    except:
        default_start = min_date
        default_end = max_date
    
    date_range = st.sidebar.date_input(
        "날짜 범위를 지정하세요",
        value=(default_start, default_end),
        min_value=min_date,
        max_value=max_date,
        key='temp_date_range'
    )
    
    if len(date_range) == 2:
        temp_date_start_str = date_range[0].strftime('%Y-%m-%d')
        temp_date_end_str = date_range[1].strftime('%Y-%m-%d')
        if date_range[0] == min_date and date_range[1] == max_date:
            temp_selected_period = "전체 기간"
        else:
            temp_selected_period = f"{temp_date_start_str}~{temp_date_end_str}"
    else:
        temp_selected_period = "전체 기간"
        temp_date_start_str = str(min_date)
        temp_date_end_str = str(max_date)

st.sidebar.markdown("---")
st.sidebar.markdown("**작업 상태 선택**")

temp_work_status = st.sidebar.selectbox(
    "작업 여부 선택",
    options=["전체", "가동", "휴무"],
    index=["전체", "가동", "휴무"].index(st.session_state.current_work_status),
    key='temp_work_status'
)

# 변경 버튼
st.sidebar.markdown("---")
if st.sidebar.button("변경 적용", type="primary", use_container_width=True):
    st.session_state.current_filter_unit = temp_filter_unit
    st.session_state.current_selected_period = temp_selected_period
    st.session_state.current_work_status = temp_work_status
    st.session_state.current_date_start = temp_date_start_str
    st.session_state.current_date_end = temp_date_end_str
    st.session_state.filter_applied = True
    st.rerun()

# 적용된 필터로 데이터 필터링
filtered_df, label = filter_dataframe(
    df, 
    st.session_state.current_filter_unit, 
    st.session_state.current_selected_period, 
    st.session_state.current_work_status,
    st.session_state.current_date_start, 
    st.session_state.current_date_end
)

if filtered_df.empty:
    st.error("선택된 필터 조건에 해당하는 데이터가 없습니다. 필터를 조정해주세요.")
    st.stop()

# 작업상태 리스트 생성
if st.session_state.current_work_status == "전체":
    selected_work_status = ["가동", "휴무"]
else:
    selected_work_status = [st.session_state.current_work_status]

# 고지서 생성
word_file_data = generate_report_from_template(filtered_df, str(TEMPLATE_PATH))

# ============================================================================
# Header & downloads
# ============================================================================
st.title("LS ELECTRIC 청주 공장 전력 사용 현황")

monthly_download_data = get_monthly_summary(df)
csv_monthly = monthly_download_data.to_csv(index=False, encoding="utf-8-sig")

st.sidebar.markdown("---")
st.sidebar.markdown("### 파일 다운로드")

if word_file_data:
    try:
        mm = int(filtered_df["month"].iloc[0])
    except Exception:
        mm = 0
    st.sidebar.download_button(
        label="고지서 다운로드",
        data=word_file_data,
        file_name=f"LS일렉트릭_전기요금_고지서_{mm:02d}월.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        key="bill_sidebar_docx",
        use_container_width=True,
        help="선택 기간의 데이터가 반영된 워드 고지서입니다.",
    )
else:
    st.sidebar.warning("고지서 파일 생성 준비 중...")

if pdf_data:
    st.sidebar.download_button(
        label="요금표 다운로드",
        data=pdf_data,
        file_name="2024년_전기요금표.pdf",
        mime="application/pdf",
        key="rate_sidebar",
        use_container_width=True,
    )

# ============================================================================
# Tabs
# ============================================================================
tab1, tab2, tab3, tab4 = st.tabs(["월별 시각화", "일별 시각화", "역률 관리", "공회전 에너지 분석"])

# ============================================================================
# Tab 1. 월별 시각화
# ============================================================================
with tab1:
    # KPI 계산
    total_power = filtered_df["전력사용량(kWh)"].sum()
    total_cost = filtered_df["전기요금(원)"].sum()
    total_carbon = (filtered_df.get("탄소배출량(tCO2)", pd.Series(dtype=float)).sum()) * 1000
    total_working_days = filtered_df[filtered_df["작업휴무"] == "가동"]["date"].nunique()
    total_holiday_days = filtered_df[filtered_df["작업휴무"] == "휴무"]["date"].nunique()

    filtered_months = filtered_df[["year", "month"]].drop_duplicates()
    monthly_summary_filtered = monthly_summary_df.merge(filtered_months, on=["year", "month"], how="inner")
    total_pf_adjustment = (
        monthly_summary_filtered["역률_조정금액(원)"].sum().round(0).astype(int)
        if not monthly_summary_filtered.empty else 0
    )

    st.markdown(f"## {label} 주요 지표")
    st.markdown(
        f"**데이터 기간**: {filtered_df['측정일시'].min().strftime('%Y-%m-%d')} ~ "
        f"{filtered_df['측정일시'].max().strftime('%Y-%m-%d')}"
    )

    # KPI 카드
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.markdown(create_metric_card(
            "총 전력사용량",
            f"{total_power:,.0f} kWh",
            f"분석 기간 누적",
            "metric-card-blue"
        ), unsafe_allow_html=True)
    
    with c2:
        st.markdown(create_metric_card(
            "총 전기요금",
            f"{total_cost:,.0f} 원",
            f"분석 기간 누적",
            "metric-card-green"
        ), unsafe_allow_html=True)
    
    with c3:
        st.markdown(create_metric_card(
            "총 탄소배출량",
            f"{total_carbon:,.0f} kgCO2",
            f"분석 기간 누적",
            "metric-card-orange"
        ), unsafe_allow_html=True)
    
    with c4:
        st.markdown(create_metric_card(
            "가동일 / 휴무일",
            f"{total_working_days} / {total_holiday_days} 일",
            f"분석 기간 내",
            "metric-card-purple"
        ), unsafe_allow_html=True)

    # 역률 조정금액 카드 - 색상 변경 (cyan 사용)
    if total_pf_adjustment < 0:
        pf_card_class = "metric-card-cyan"  # 진상역률 색상으로 변경
        pf_title = "역률 감액"
        pf_value = f"{abs(total_pf_adjustment):,.0f} 원"
        pf_delta = "절감 효과"
    elif total_pf_adjustment > 0:
        pf_card_class = "metric-card-red"
        pf_title = "역률 패널티"
        pf_value = f"{total_pf_adjustment:,.0f} 원"
        pf_delta = "추가 비용"
    else:
        pf_card_class = "metric-card-blue"
        pf_title = "역률 조정금액"
        pf_value = "0 원"
        pf_delta = "조정 없음"

    with c5:
        st.markdown(create_metric_card(
            pf_title,
            pf_value,
            pf_delta,
            pf_card_class
        ), unsafe_allow_html=True)

    st.divider()

    # 차트 영역
    col_monthly_trend, col_monthly_comp = st.columns(2)
    
    # **[수정]** 폰트 크기 변수
    AXIS_FONT_SIZE = 18
    BAR_TEXT_SIZE = 16

    # 월별 추이
    with col_monthly_trend:
        st.subheader("월별 전력사용량 및 평균 요금 추이")
        
        monthly = get_monthly_summary(df)
        x_labels_kr = [f"{m}월" for m in monthly["month"]]

        # 선택된 월 확인
        if st.session_state.current_filter_unit == '월별' and st.session_state.current_selected_period != "전체 기간":
            sel_month = int(st.session_state.current_selected_period.replace('월', ''))
        else:
            sel_month = None

        bar_colors = [
            CHART_COLORS['power'] if (sel_month is not None and m == sel_month) else "lightgray"
            for m in monthly["month"]
        ]

        fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_monthly.add_trace(
            go.Bar(
                x=x_labels_kr,
                y=monthly["전력사용량(kWh)"],
                name="월별 사용량",
                marker_color=bar_colors,
                text=monthly["전력사용량(kWh)"].apply(lambda x: f"{x:,.0f}"),
                textposition='outside',
                # **[수정]** 막대 그래프 텍스트 크기
                textfont=dict(color='black', size=BAR_TEXT_SIZE),
                hovertemplate='<b>%{x}</b><br>전력: %{y:,.0f} kWh<extra></extra>'
            ),
            secondary_y=False,
        )
        
        fig_monthly.add_trace(
            go.Scatter(
                x=x_labels_kr,
                y=monthly["전기요금(원)"],
                name="월 평균 전기요금",
                mode="lines+markers",
                line=dict(color=CHART_COLORS['cost'], width=3, shape='spline'),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>요금: %{y:,.0f} 원<extra></extra>'
            ),
            secondary_y=True,
        )

        fig_monthly.update_xaxes(
            showgrid=False,
            # **[수정]** x축 눈금 레이블 및 제목 크기
            tickfont=dict(color='black', size=AXIS_FONT_SIZE),
            title_font=dict(color='black', size=AXIS_FONT_SIZE)
        )
        
        fig_monthly.update_yaxes(
            title_text="전력사용량 (kWh)",
            secondary_y=False,
            showgrid=False,
            # **[수정]** y축 눈금 레이블 및 제목 크기
            tickfont=dict(color='black', size=AXIS_FONT_SIZE),
            title_font=dict(color='black', size=AXIS_FONT_SIZE)
        )
        
        fig_monthly.update_yaxes(
            title_text="평균 전기요금 (원)",
            secondary_y=True,
            showgrid=False,
            # **[수정]** 보조 y축 눈금 레이블 및 제목 크기
            tickfont=dict(color='black', size=AXIS_FONT_SIZE),
            title_font=dict(color='black', size=AXIS_FONT_SIZE)
        )

        fig_monthly.update_layout(
            height=550,
            # **[수정]** 범례 폰트 크기
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(size=AXIS_FONT_SIZE)),
            plot_bgcolor='white',
            paper_bgcolor='white',
            uirevision='monthly_trend'
        )
        st.plotly_chart(fig_monthly, use_container_width=True, config={'displayModeBar': False})

    # 총 전력사용량 비교
    with col_monthly_comp:
        st.subheader("총 전력사용량 비교")
        
        current_total_power = total_power

        comp_labels = [label, "2024년 월평균"]
        comp_values = [current_total_power, annual_monthly_avg_power]
        comp_colors = {label: CHART_COLORS['power'], "2024년 월평균": "lightgray"}
        category_order = ["2024년 월평균"]

        if st.session_state.current_filter_unit == '월별' and st.session_state.current_selected_period != "전체 기간":
            current_month_num = int(st.session_state.current_selected_period.replace('월', ''))
            prev_month_num = current_month_num - 1
            if prev_month_num in monthly_totals_all.index:
                prev_val = monthly_totals_all.get(prev_month_num, 0)
                prev_label = f"{prev_month_num}월 (전월)"
                comp_labels.append(prev_label)
                comp_values.append(prev_val)
                comp_colors[prev_label] = CHART_COLORS['holiday']
                category_order.append(prev_label)
        
        category_order.append(label)

        comp_df = pd.DataFrame({"구분": comp_labels, "총 전력사용량 (kWh)": comp_values})
        fig_comp = px.bar(
            comp_df, x="구분", y="총 전력사용량 (kWh)",
            color="구분", color_discrete_map=comp_colors, text="총 전력사용량 (kWh)",
        )
        fig_comp.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont_color="black",
            # **[수정]** 막대 그래프 텍스트 크기
            textfont_size=BAR_TEXT_SIZE,
            hovertemplate='<b>%{x}</b><br>전력: %{y:,.0f} kWh<extra></extra>'
        )
        max_val = comp_df["총 전력사용량 (kWh)"].max() or 1

        fig_comp.update_layout(
            height=550,
            showlegend=False,
            xaxis_title="",
            yaxis_title="총 전력사용량 (kWh)",
            yaxis_range=[0, max_val * 1.2],
            xaxis=dict(
                showgrid=False,
                categoryorder="array",
                categoryarray=category_order,
                # **[수정]** x축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            yaxis=dict(
                showgrid=False,
                # **[수정]** y축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            uirevision='monthly_comp'
        )
        st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

# ============================================================================
# Tab 2. 일별 시각화
# ============================================================================
with tab2:
    st.header("일별 사용량 및 일별 전기 요금 분석")
    col_daily_power, col_daily_cost = st.columns(2)

    with col_daily_power:
        st.subheader("일별 전력량 분석")
        load_map = {"Light_Load": "경부하", "Medium_Load": "중간부하", "Maximum_Load": "최대부하"}
        
        # 데이터 전처리 최적화
        analysis_df = filtered_df[['측정일시', '작업유형', '전력사용량(kWh)']].copy()
        analysis_df["부하타입"] = analysis_df["작업유형"].map(load_map)
        analysis_df["날짜"] = analysis_df["측정일시"].dt.date

        daily = analysis_df.groupby(["날짜", "부하타입"])['전력사용량(kWh)'].sum().reset_index()
        daily_pivot = daily.pivot(index="날짜", columns="부하타입", values="전력사용량(kWh)").fillna(0).reset_index()
        daily_pivot = daily_pivot.sort_values("날짜")
        daily_pivot["날짜_str"] = pd.to_datetime(daily_pivot["날짜"]).dt.strftime("%m-%d")

        colors = {
            "경부하": CHART_COLORS['light_load'],
            "중간부하": CHART_COLORS['medium_load'],
            "최대부하": CHART_COLORS['maximum_load']
        }
        
        fig_daily = go.Figure()
        for lt in ["경부하", "중간부하", "최대부하"]:
            if lt in daily_pivot.columns:
                fig_daily.add_trace(
                    go.Bar(
                        name=lt,
                        x=daily_pivot["날짜_str"],
                        y=daily_pivot[lt],
                        marker_color=colors[lt],
                        hovertemplate='날짜: %{x}<br>' + lt + ': %{y:,.0f} kWh<extra></extra>',
                    )
                )
        fig_daily.update_layout(
            barmode="stack",
            height=550,
            xaxis_title="날짜",
            yaxis_title="전력사용량 (kWh)",
            xaxis=dict(
                showgrid=False,
                tickangle=-45,
                type="category",
                # **[수정]** x축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            yaxis=dict(
                showgrid=False,
                # **[수정]** y축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                # **[수정]** 범례 폰트 크기
                font=dict(size=AXIS_FONT_SIZE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            uirevision='daily_power'
        )
        st.plotly_chart(fig_daily, use_container_width=True, config={'displayModeBar': False})

    with col_daily_cost:
        st.subheader("일별 총 전기요금 추이 (원)")
        daily_cost = (
            filtered_df.groupby(filtered_df["측정일시"].dt.date)["전기요금(원)"].sum().reset_index()
        )
        daily_cost.columns = ["날짜", "총 전기요금(원)"]
        daily_cost["날짜_str"] = pd.to_datetime(daily_cost["날짜"]).dt.strftime("%m-%d")
        
        fig_cost = go.Figure()
        fig_cost.add_trace(
            go.Scatter(
                x=daily_cost["날짜_str"],
                y=daily_cost["총 전기요금(원)"],
                mode="lines+markers",
                line=dict(color=CHART_COLORS['cost'], width=3, shape='spline'),
                marker=dict(size=7),
                fill='tozeroy',
                fillcolor='rgba(40, 167, 69, 0.1)',
                hovertemplate='<b>%{x}</b><br>요금: %{y:,.0f} 원<extra></extra>'
            )
        )
        
        fig_cost.update_layout(
            height=550,
            xaxis_title="날짜",
            yaxis_title="총 전기요금 (원)",
            xaxis=dict(
                showgrid=False,
                tickangle=-45,
                type="category",
                # **[수정]** x축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            yaxis=dict(
                showgrid=False,
                # **[수정]** y축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False,
            uirevision='daily_cost'
        )
        st.plotly_chart(fig_cost, use_container_width=True, config={'displayModeBar': False})

    st.caption("일별 전력량은 부하 유형별 분포를, 전기요금 추이는 TOU 영향으로 비용 급증일을 식별하는 데 유용합니다.")
    st.divider()

    # 시간대 패턴
    st.header("시간대별 패턴 분석")
    col_hourly_pattern, col_hourly_load = st.columns(2)

    with col_hourly_pattern:
        st.subheader("시간대별 전력 사용량 패턴 (평균/최소/최대)")
        hourly = (
            filtered_df.groupby("hour")["전력사용량(kWh)"]
            .agg(['mean', 'min', 'max'])
            .reset_index()
        )

        time_zones = [
            {"name": "야간", "start": 0, "end": 8.25, "color": "rgba(150,150,180,0.1)"},
            {"name": "가동준비", "start": 8.25, "end": 9, "color": "rgba(255,200,100,0.15)"},
            {"name": "오전생산", "start": 9, "end": 12, "color": "rgba(100,200,150,0.15)"},
            {"name": "점심시간", "start": 12, "end": 13, "color": "rgba(255,180,150,0.15)"},
            {"name": "오후생산", "start": 13, "end": 17.25, "color": "rgba(100,200,150,0.15)"},
            {"name": "퇴근시간", "start": 17.25, "end": 18.5, "color": "rgba(255,200,100,0.15)"},
            {"name": "야간초입", "start": 18.5, "end": 21, "color": "rgba(180,180,200,0.1)"},
            {"name": "야간", "start": 21, "end": 24, "color": "rgba(150,150,180,0.1)"},
        ]

        fig_hourly = go.Figure()
        max_y = hourly["mean"].max() * 1.1
        
        for z in time_zones:
            fig_hourly.add_vrect(
                x0=z["start"],
                x1=z["end"],
                fillcolor=z["color"],
                layer="below",
                line_width=0
            )
            mid = (z["start"] + z["end"]) / 2
            fig_hourly.add_annotation(
                x=mid,
                y=max_y,
                text=z["name"],
                showarrow=False,
                font=dict(size=12, color="gray"),
                yshift=10
            )

        fig_hourly.add_trace(
            go.Scatter(
                x=hourly["hour"],
                y=hourly["mean"],
                mode="lines+markers",
                name="평균 전력사용량",
                line=dict(color=CHART_COLORS['power'], width=3, shape='spline'),
                marker=dict(size=7, color=CHART_COLORS['power']),
                customdata=list(zip(hourly["min"], hourly["max"])),
                hovertemplate="<b>%{x}:00시</b><br>평균: %{y:.1f} kWh<br>최소: %{customdata[0]:.1f} kWh<br>최대: %{customdata[1]:.1f} kWh<extra></extra>",
            )
        )
        
        fig_hourly.update_layout(
            height=550,
            xaxis_title="시간",
            yaxis_title="전력사용량 (kWh)",
            xaxis=dict(
                tickmode="array",
                tickvals=list(range(0, 25, 2)),
                ticktext=[f"{h:02d}:00" for h in range(0, 25, 2)],
                range=[-0.5, 24],
                showgrid=False,
                # **[수정]** x축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            yaxis=dict(
                range=[0, max_y * 1.15],
                showgrid=False,
                # **[수정]** y축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode="x unified",
            showlegend=False,
            uirevision='hourly_pattern'
        )
        st.plotly_chart(fig_hourly, use_container_width=True, config={'displayModeBar': False})

    with col_hourly_load:
        tooltip = (
            "[공장 부하 패턴 정의]\n"
            "1. 휴무일: 전체 시간대 경부하\n"
            "2. 가동일\n • 봄/여름/가을 최대부하: 10-12, 13-17\n • 겨울철 최대부하: 10-12, 17-20, 22-23\n • 경부하: 23-09"
        )
        st.markdown(
            f"""
            <div class="title-with-tooltip">
                <h3>시간대별 부하 발생 빈도</h3>
                <div class="tooltip-container"><span class="tooltip-icon">i</span><span class="tooltip-text">{tooltip}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        load_map2 = {"경부하": "Light_Load", "중간부하": "Medium_Load", "최대부하": "Maximum_Load"}
        polar_colors = {
            "경부하": {"line": CHART_COLORS['light_load'], "fill": f"rgba(76,175,80,.3)"},
            "중간부하": {"line": CHART_COLORS['medium_load'], "fill": f"rgba(255,193,7,.3)"},
            "최대부하": {"line": CHART_COLORS['maximum_load'], "fill": f"rgba(239,83,80,.3)"}
        }

        st.markdown("##### 부하 유형 선택")
        s1, s2, s3 = st.columns(3)
        selected = []
        if s1.checkbox("최대부하", value=True, key="p1"): selected.append("최대부하")
        if s2.checkbox("중간부하", value=True, key="p2"): selected.append("중간부하")
        if s3.checkbox("경부하", value=True, key="p3"): selected.append("경부하")

        fig_polar = go.Figure()
        all_counts, total_count = [], 0
        
        if not selected:
            st.warning("최소한 하나의 부하 유형을 선택해야 합니다.")
        else:
            for ui_name in selected:
                data_name = load_map2[ui_name]
                sub = filtered_df[filtered_df["작업유형"] == data_name]
                hour_counts = sub.groupby("hour").size().reindex(range(24), fill_value=0)
                total_count += len(sub)
                fig_polar.add_trace(
                    go.Scatterpolar(
                        r=hour_counts.values,
                        theta=[f"{h:02d}:00" for h in range(24)],
                        fill="toself",
                        fillcolor=polar_colors[ui_name]["fill"],
                        line=dict(color=polar_colors[ui_name]["line"], width=2),
                        marker=dict(size=8, color=polar_colors[ui_name]["line"]),
                        name=ui_name,
                    )
                )
            max_val = max(all_counts) if all_counts else 10
            fig_polar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max_val * 1.1],
                        # **[수정]** 방사형 축 눈금 레이블 크기
                        tickfont=dict(color='black', size=AXIS_FONT_SIZE)
                    ),
                    angularaxis=dict(
                        direction="clockwise",
                        rotation=90,
                        dtick=3,
                        # **[수정]** 각 축 눈금 레이블 크기
                        tickfont=dict(color='black', size=AXIS_FONT_SIZE)
                    ),
                ),
                height=550,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    # **[수정]** 범례 폰트 크기
                    font=dict(size=AXIS_FONT_SIZE)
                ),
                paper_bgcolor='white',
                uirevision='polar_load'
            )
            st.plotly_chart(fig_polar, use_container_width=True, config={'displayModeBar': False})
            st.caption(f"선택한 기간 내 선택 부하 유형 총 발생 건수: **{total_count:,}건**")

# ============================================================================
# Tab 3. 역률 관리
# ============================================================================
LAG_PF_THRESHOLD_PENALTY = 90
LAG_PF_THRESHOLD_INCENTIVE = 95
LEAD_PF_THRESHOLD_PENALTY = 95

@st.cache_data(show_spinner=False)
def calculate_time_based_metrics(df_subset):
    """시간 기반 역률 계산 - 캐싱"""
    lag_time_df = df_subset[(df_subset["hour"] >= 9) & (df_subset["hour"] < 22)]
    lead_time_df = df_subset[(df_subset["hour"] >= 22) | (df_subset["hour"] < 9)]
    
    valid_lag_pf = lag_time_df[lag_time_df["지상역률(%)"] > 0]["지상역률(%)"]
    avg_lag_pf_actual = valid_lag_pf.mean() if not valid_lag_pf.empty else 0
    
    valid_lead_pf = lead_time_df[lead_time_df["진상역률(%)"] > 0]["진상역률(%)"]
    avg_lead_pf_actual = valid_lead_pf.mean() if not valid_lead_pf.empty else 0
    
    return avg_lag_pf_actual, avg_lead_pf_actual

with tab3:
    if not selected_work_status:
        st.warning("사이드바에서 '작업 상태 선택'을 지정하세요.")
        st.stop()

    # KPI 계산
    total_power_usage = filtered_df["전력사용량(kWh)"].sum()
    total_lag_kvarh = filtered_df["지상무효전력량(kVarh)"].sum()
    total_lead_kvarh = filtered_df["진상무효전력량(kVarh)"].sum()

    # 필터링된 데이터의 해시로 캐싱
    cache_key = hash(tuple(filtered_df.index))
    avg_lag_pf_actual, avg_lead_pf_actual = calculate_time_based_metrics(filtered_df)

    delta_lag = (avg_lag_pf_actual - LAG_PF_THRESHOLD_PENALTY)
    delta_lead = (avg_lead_pf_actual - LEAD_PF_THRESHOLD_PENALTY)
    
    delta_lag_text = f"{delta_lag:.2f}% vs {LAG_PF_THRESHOLD_PENALTY}%"
    delta_lag_color = "metric-card-red" if delta_lag < 0 else "metric-card-green"

    delta_lead_text = f"{delta_lead:.2f}% vs {LEAD_PF_THRESHOLD_PENALTY}%"
    delta_lead_color = "metric-card-red" if delta_lead > 0 else "metric-card-green"

    st.markdown("#### 기간별 역률 관리 핵심 지표")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(create_metric_card(
            "총 전력사용량",
            f"{total_power_usage:,.0f} kWh",
            "분석 기간 누적",
            "metric-card-blue"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "총 지상 무효전력량",
            f"{total_lag_kvarh:,.0f} kVarh",
            "분석 기간 누적",
            "metric-card-orange"
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(create_metric_card(
            "총 진상 무효전력량",
            f"{total_lead_kvarh:,.0f} kVarh",
            "분석 기간 누적",
            "metric-card-purple"
        ), unsafe_allow_html=True)

    with col4:
        st.markdown(create_metric_card(
            "평균 지상 역률 (주간)",
            f"{avg_lag_pf_actual:.2f} %",
            delta_lag_text,
            delta_lag_color
        ), unsafe_allow_html=True)

    with col5:
        st.markdown(create_metric_card(
            "평균 진상 역률 (야간)",
            f"{avg_lead_pf_actual:.2f} %",
            delta_lead_text,
            delta_lead_color
        ), unsafe_allow_html=True)

    st.markdown("---")
    
    # 역률 일일 사이클
    st.subheader("역률 일일 사이클 분석")
    pf_colors = {"가동": CHART_COLORS['working'], "휴무": CHART_COLORS['holiday']}

    # 데이터 전처리 최적화
    cycle_df = filtered_df[['측정일시', '작업휴무', 'hour', 'minute', '지상역률(%)', '진상역률(%)']].copy()
    cycle_df["time_15min"] = ((cycle_df["hour"] * 60 + cycle_df["minute"]) // 15) * 15
    cycle_df["time_label"] = cycle_df["time_15min"].apply(lambda x: f"{x//60:02d}:{x%60:02d}")

    daily_cycle = (
        cycle_df.groupby(["작업휴무", "time_15min", "time_label"])
        .agg(avg_lag_pf=("지상역률(%)", "mean"), avg_lead_pf=("진상역률(%)", "mean"))
        .reset_index()
        .sort_values("time_15min")
    )

    all_time_labels = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 15, 30, 45]]
    col_lag, col_lead = st.columns(2)

    with col_lag:
        st.markdown("#### 지상역률(%) 일일 사이클")
        fig_lag = go.Figure()
        fig_lag.add_vrect(
            x0="09:00",
            x1="22:00",
            fillcolor="rgba(255,193,7,0.15)",
            layer="below",
            line_width=0
        )
        
        for status in selected_work_status:
            sub = daily_cycle[daily_cycle["작업휴무"] == status]
            fig_lag.add_trace(
                go.Scatter(
                    x=sub["time_label"],
                    y=sub["avg_lag_pf"],
                    mode="lines",
                    name=status,
                    line=dict(color=pf_colors.get(status, "gray"), width=2.5, shape='spline'),
                    hovertemplate='<b>%{x}</b><br>지상역률: %{y:.2f}%<extra></extra>'
                )
            )
        
        fig_lag.add_hline(
            y=LAG_PF_THRESHOLD_PENALTY,
            line_dash="dash",
            line_color=CHART_COLORS['lagging_pf'],
            line_width=2
        )
        
        fig_lag.update_layout(
            height=500,
            xaxis=dict(
                title="시간 (15분)",
                categoryorder="array",
                categoryarray=all_time_labels,
                tickvals=[f"{h:02d}:00" for h in range(24)],
                ticktext=[f"{h}" for h in range(24)],
                showgrid=False,
                # **[수정]** x축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            yaxis=dict(
                title="평균 지상역률(%)",
                range=[40, 102],
                showgrid=False,
                # **[수정]** y축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                # **[수정]** 범례 폰트 크기
                font=dict(size=AXIS_FONT_SIZE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=50),
            uirevision='lag_pf_cycle'
        )
        st.plotly_chart(fig_lag, use_container_width=True, config={'displayModeBar': False})

    with col_lead:
        st.markdown("#### 진상역률(%) 일일 사이클")
        fig_lead = go.Figure()
        fig_lead.add_vrect(
            x0="22:00",
            x1="23:45",
            fillcolor="rgba(78,205,196,0.15)",
            layer="below",
            line_width=0
        )
        fig_lead.add_vrect(
            x0="00:00",
            x1="09:00",
            fillcolor="rgba(78,205,196,0.15)",
            layer="below",
            line_width=0
        )
        
        for status in selected_work_status:
            sub = daily_cycle[daily_cycle["작업휴무"] == status]
            fig_lead.add_trace(
                go.Scatter(
                    x=sub["time_label"],
                    y=sub["avg_lead_pf"],
                    mode="lines",
                    name=status,
                    line=dict(color=pf_colors.get(status, "gray"), width=2.5, shape='spline'),
                    hovertemplate='<b>%{x}</b><br>진상역률: %{y:.2f}%<extra></extra>'
                )
            )
        
        fig_lead.add_hline(
            y=LEAD_PF_THRESHOLD_PENALTY,
            line_dash="dash",
            line_color=CHART_COLORS['leading_pf'],
            line_width=2
        )
        
        fig_lead.update_layout(
            height=500,
            xaxis=dict(
                title="시간 (15분)",
                categoryorder="array",
                categoryarray=all_time_labels,
                tickvals=[f"{h:02d}:00" for h in range(24)],
                ticktext=[f"{h}" for h in range(24)],
                showgrid=False,
                # **[수정]** x축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            yaxis=dict(
                title="평균 진상역률(%)",
                range=[0, 102],
                showgrid=False,
                # **[수정]** y축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                # **[수정]** 범례 폰트 크기
                font=dict(size=AXIS_FONT_SIZE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=50),
            uirevision='lead_pf_cycle'
        )
        st.plotly_chart(fig_lead, use_container_width=True, config={'displayModeBar': False})

    # 인사이트 캡션
    analysis_results = []
    
    lag_risk_data = daily_cycle[daily_cycle["avg_lag_pf"] < LAG_PF_THRESHOLD_PENALTY]
    
    if not lag_risk_data.empty:
        worst_lag = lag_risk_data["avg_lag_pf"].min()
        worst_row = lag_risk_data[lag_risk_data["avg_lag_pf"] == worst_lag].iloc[0]
        status_kr = "가동일" if worst_row["작업휴무"] == "가동" else "휴무일"
        
        analysis_results.append(
            f"① **지상역률 위험:** **{status_kr}**의 **{worst_row['time_label']}** 구간에서 평균 역률이 **{worst_lag:.2f}%**로 **90% 미달**을 기록했습니다. 이 구간의 설비 부하 패턴을 즉시 점검하여 요금 가산을 방지하세요."
        )
    else:
        analysis_results.append(
            f"① **지상역률 양호:** 주간 시간(09시~22시) 동안 지상역률이 **90%** 이상으로 잘 유지되었습니다. **95%** 초과 구간을 목표로 관리하여 감액 혜택을 극대화하세요."
        )

    lead_risk_data = daily_cycle[daily_cycle["avg_lead_pf"] < LEAD_PF_THRESHOLD_PENALTY]
    
    if not lead_risk_data.empty:
        worst_lead = lead_risk_data["avg_lead_pf"].min()
        worst_row = lead_risk_data[lag_risk_data["avg_lead_pf"] == worst_lead].iloc[0]
        status_kr = "가동일" if worst_row["작업휴무"] == "가동" else "휴무일"
        
        analysis_results.append(
            f"② **진상역률 위험:** **{status_kr}**의 **{worst_row['time_label']}** 구간에서 진상역률이 **{worst_lead:.2f}%**로 **95% 미달**을 기록했습니다. 이는 야간 시간대(22시~09시) 콘덴서 **과투입/설비 리스크**를 시사하며, 요금 가산 리스크가 있습니다."
        )
    else:
        analysis_results.append(
            "② **진상역률 양호:** 야간 시간(22시~09시) 동안 진상역률이 **95%** 이상으로 잘 유지되었습니다. 콘덴서 제어가 잘 작동 중입니다."
        )

    if "휴무" in selected_work_status:
        rest_day_data = daily_cycle[daily_cycle["작업휴무"] == "휴무"]
        rest_day_lag_risk = rest_day_data[rest_day_data["avg_lag_pf"] < 90]
        rest_day_lead_risk = rest_day_data[rest_day_data["avg_lead_pf"] < 95]
        
        if not rest_day_lag_risk.empty or not rest_day_lead_risk.empty:
            analysis_results.append(
                "③ **휴무일 특이사항:** 휴무일에도 **비정상적인 역률 변동** (90% 미만 또는 95% 미만)이 관찰되었습니다. 이는 상시 가동되는 주요 설비의 비효율적인 콘덴서 제어 또는 누설 전류로 인한 것일 수 있습니다. **설비 점검**이 필요합니다."
            )
        else:
            analysis_results.append(
                "③ **휴무일 특이사항:** 휴무일에는 역률이 안정적으로 유지되어 특별한 위험이 발견되지 않았습니다."
            )
            
    final_caption = "\n\n".join(analysis_results)
    st.caption(final_caption)

# ============================================================================
# Tab 4. 공회전 에너지 분석
# ============================================================================
@st.cache_data(show_spinner=False)
def get_idle_data(df_subset):
    """공회전 데이터 계산 - 캐싱"""
    if df_subset.empty:
        return None, None, None
    
    df_work = df_subset[df_subset["작업휴무"] == "가동"][['hour', 'date', '전력사용량(kWh)', '전기요금(원)', '작업휴무']].copy()
    df_rest = df_subset[df_subset["작업휴무"] == "휴무"][['hour', 'date', '전력사용량(kWh)', '전기요금(원)', '작업휴무']].copy()

    work_night = df_work[(df_work["hour"] >= 22) | (df_work["hour"] < 8)]
    work_baseline_val = work_night['전력사용량(kWh)'].quantile(0.3) if not work_night.empty else 0
    rest_baseline_val = df_rest['전력사용량(kWh)'].quantile(0.3) if not df_rest.empty else 0

    df_work['baseline'] = work_baseline_val
    df_work['is_idle_hour'] = (df_work['hour'] >= 22) | (df_work['hour'] < 8)
    df_work['idle_power'] = 0.0
    cond_work = (df_work['is_idle_hour']) & (df_work['전력사용량(kWh)'] > df_work['baseline'])
    df_work.loc[cond_work, 'idle_power'] = df_work['전력사용량(kWh)'] - df_work['baseline']

    df_rest['baseline'] = rest_baseline_val
    df_rest['is_idle_hour'] = True
    df_rest['idle_power'] = 0.0
    cond_rest = (df_rest['전력사용량(kWh)'] > df_rest['baseline'])
    df_rest.loc[cond_rest, 'idle_power'] = df_rest['전력사용량(kWh)'] - df_rest['baseline']

    combined = pd.concat([df_work, df_rest], ignore_index=True)
    combined['idle_cost'] = 0.0
    valid = combined['전력사용량(kWh)'] != 0
    combined.loc[valid, 'idle_cost'] = combined['전기요금(원)'] * (combined['idle_power'] / combined['전력사용량(kWh)'])

    daily_idle = (
        combined.groupby(['date', '작업휴무'])
        .agg(loss=('idle_power', 'sum'), cost=('idle_cost', 'sum'))
        .reset_index()
    )
    daily_idle = daily_idle.rename(columns={'작업휴무': 'type'})
    daily_idle['cumulative_loss'] = daily_idle['loss'].cumsum().round(1)

    kpis = {
        '가동일 야간 베이스라인': {'value': work_baseline_val, 'unit': 'kWh'},
        '휴무일 베이스라인': {'value': rest_baseline_val, 'unit': 'kWh'},
        '공회전 에너지 손실': {
            'value': daily_idle['loss'].sum().round(0),
            'unit': 'kWh',
            'details': [
                daily_idle[daily_idle['type'] == '가동']['loss'].sum().round(0),
                daily_idle[daily_idle['type'] == '휴무']['loss'].sum().round(0)
            ],
        },
        '공회전 비용 손실': {'value': daily_idle['cost'].sum().round(0), 'unit': '₩', 'details': []},
    }
    return daily_idle, kpis, combined

with tab4:
    daily_idle_summary, kpis_idle, _ = get_idle_data(filtered_df)

    if daily_idle_summary is None or daily_idle_summary.empty:
        st.warning("선택된 기간에 데이터가 없어 공회전 분석을 진행할 수 없습니다.")
    else:
        # KPI 카드
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.markdown(create_metric_card(
                "가동일 야간 베이스라인",
                f"{kpis_idle['가동일 야간 베이스라인']['value']:,.1f} kWh",
                "평균 전력 (하위 30%)",
                "metric-card-blue"
            ), unsafe_allow_html=True)
        
        with c2:
            st.markdown(create_metric_card(
                "휴무일 베이스라인",
                f"{kpis_idle['휴무일 베이스라인']['value']:,.1f} kWh",
                "평균 전력 (하위 30%)",
                "metric-card-red"
            ), unsafe_allow_html=True)
        
        with c3:
            work_loss = kpis_idle['공회전 에너지 손실']['details'][0]
            rest_loss = kpis_idle['공회전 에너지 손실']['details'][1]
            st.markdown(create_metric_card(
                "공회전 에너지 손실",
                f"{kpis_idle['공회전 에너지 손실']['value']:,.0f} kWh",
                f"가동: {work_loss:,.0f} | 휴무: {rest_loss:,.0f}",
                "metric-card-orange"
            ), unsafe_allow_html=True)
        
        with c4:
            st.markdown(create_metric_card(
                "공회전 비용 손실",
                f"₩{kpis_idle['공회전 비용 손실']['value']:,.0f}",
                "계산된 누적 요금",
                "metric-card-green"
            ), unsafe_allow_html=True)
        
        st.divider()

        # TOP 10 손실일
        st.subheader("일별 공회전 손실 TOP 10")
        
        pivot = (
            daily_idle_summary
            .pivot(index="date", columns="type", values="loss")
            .fillna(0)
        )
        pivot["total_loss"] = pivot.sum(axis=1)
        pivot["major"] = np.where(pivot.get("휴무", 0) >= pivot.get("가동", 0), "휴무", "가동")
        
        top10 = (
            pivot.sort_values("total_loss", ascending=False)
                 .head(10)
                 .reset_index()
        )
        top10["label"] = pd.to_datetime(top10["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        top10["color"] = np.where(top10["major"].eq("휴무"), CHART_COLORS['carbon'], CHART_COLORS['power'])
        
        fig_top = go.Figure(
            go.Bar(
                x=top10["total_loss"],
                y=top10["label"].astype(str),
                orientation="h",
                marker_color=top10["color"],
                text=top10["total_loss"].round(1),
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>손실: %{x:.1f} kWh<extra></extra>",
                # **[수정]** 막대 그래프 텍스트 크기
                textfont=dict(color='black', size=BAR_TEXT_SIZE)
            )
        )
        
        fig_top.update_layout(
            height=420,
            xaxis_title="손실 (kWh)",
            yaxis_title="날짜",
            xaxis=dict(
                showgrid=False,
                # **[수정]** x축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            yaxis=dict(
                type="category",
                categoryorder="array",
                categoryarray=top10["label"].tolist(),
                autorange="reversed",
                # **[수정]** y축 눈금 레이블 및 제목 크기
                tickfont=dict(color='black', size=AXIS_FONT_SIZE),
                title_font=dict(color='black', size=AXIS_FONT_SIZE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=80, r=20, t=10, b=40),
            uirevision='idle_top10'
        )
        st.plotly_chart(fig_top, use_container_width=True, config={'displayModeBar': False})
        st.divider()

        # 시간대별 손실 패턴 (사이드바 필터 사용)
        st.subheader("시간대별 손실 패턴 & 베이스라인")

        work_baseline = float(kpis_idle.get("가동일 야간 베이스라인", {}).get("value", 0) or 0.0)
        rest_baseline = float(kpis_idle.get("휴무일 베이스라인", {}).get("value", 0) or 0.0)

        # 사이드바 필터에 따라 데이터 선택
        if st.session_state.current_work_status == "가동":
            baseline = work_baseline
            status_text = "가동일"
            sel_flag = "가동"
        elif st.session_state.current_work_status == "휴무":
            baseline = rest_baseline
            status_text = "휴무일"
            sel_flag = "휴무"
        else:  # 전체
            # 전체일 경우 가동일 기준으로 표시
            baseline = work_baseline
            status_text = "전체 (가동일 기준)"
            sel_flag = "가동"

        df_sel = filtered_df.loc[filtered_df["작업휴무"].eq(sel_flag)].copy()
        df_sel["dt"] = pd.to_datetime(df_sel["측정일시"], errors="coerce")
        df_sel["hour"] = df_sel["dt"].dt.hour

        df_night = df_sel[(df_sel["hour"] >= 22) | (df_sel["hour"] < 8)].copy()

        vals = np.arange(22, 32)
        labels = [f"{(h if h < 24 else h-24):02d}:00" for h in vals]

        df_night["xnum"] = df_night["hour"].apply(lambda h: h if h >= 22 else h + 24)
        hourly = (
            df_night.groupby("xnum")["전력사용량(kWh)"]
            .mean()
            .reindex(vals, fill_value=0.0)
            .reset_index()
            .rename(columns={"전력사용량(kWh)": "power"})
        )
        hourly["loss"] = (hourly["power"] - baseline).clip(lower=0)

        fig_hour = make_subplots(specs=[[{"secondary_y": False}]])

        fig_hour.add_trace(
            go.Bar(
                x=hourly["xnum"],
                y=hourly["loss"],
                name="공회전 손실",
                marker=dict(
                    color="rgba(255,193,7,0.45)",
                    line=dict(color="rgba(255,193,7,1.0)", width=1.8)
                ),
                hovertemplate="<b>%{x}</b><br>손실: %{y:.1f} kWh<extra></extra>",
            )
        )

        fig_hour.add_trace(
            go.Scatter(
                x=hourly["xnum"],
                y=hourly["power"],
                name="실제 전력사용량 (kWh)",
                mode="lines+markers",
                line=dict(width=3, color=CHART_COLORS['power'], shape='spline'),
                marker=dict(size=7, line=dict(width=0)),
                hovertemplate="<b>%{x}</b><br>전력사용량: %{y:.1f} kWh<extra></extra>",
            )
        )

        fig_hour.add_hline(
            y=baseline,
            line_dash="dot",
            line_color="crimson",
            line_width=2,
            annotation_text="베이스라인",
            annotation_position="top right",
        )

        fig_hour.add_vrect(
            x0=22,
            x1=31,
            fillcolor="rgba(91,123,250,0.10)",
            line_width=0,
            layer="below"
        )

        fig_hour.update_xaxes(
            tickmode="array",
            tickvals=vals,
            ticktext=labels,
            title_text="야간 시간대 (22:00~08:00)",
            showgrid=False,
            range=[21.5, 31.5],
            # **[수정]** x축 눈금 레이블 및 제목 크기
            tickfont=dict(color='black', size=AXIS_FONT_SIZE),
            title_font=dict(color='black', size=AXIS_FONT_SIZE)
        )
        fig_hour.update_yaxes(
            title_text="전력사용량 (kWh)",
            rangemode="tozero",
            showgrid=False,
            # **[수정]** y축 눈금 레이블 및 제목 크기
            tickfont=dict(color='black', size=AXIS_FONT_SIZE),
            title_font=dict(color='black', size=AXIS_FONT_SIZE)
        )
        fig_hour.update_layout(
            height=460,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                # **[수정]** 범례 폰트 크기
                font=dict(size=AXIS_FONT_SIZE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=40, t=10, b=40),
            uirevision=f'idle_hour_{st.session_state.current_work_status}'
        )

        st.plotly_chart(fig_hour, use_container_width=True, config={'displayModeBar': False})
        st.caption(f"기준: {status_text} 베이스라인 {baseline:,.1f} kWh")
        st.divider()

        # 누적 추이
        st.subheader("공회전 에너지 누적 (일별 추이)")

        cum_df = daily_idle_summary.copy()
        cum_df["dt"] = pd.to_datetime(cum_df["date"], errors="coerce")
        cum_df = cum_df.sort_values("dt")
        
        if "cumulative_loss" not in cum_df.columns:
            cum_df["cumulative_loss"] = cum_df["loss"].cumsum()

        if not cum_df.empty:
            end_dt = cum_df["dt"].max()
            start_dt = end_dt - pd.Timedelta(days=6)
        else:
            end_dt = pd.Timestamp.today()
            start_dt = end_dt - pd.Timedelta(days=6)

        fig_cumul = make_subplots(specs=[[{"secondary_y": True}]])

        fig_cumul.add_trace(
            go.Bar(
                x=cum_df["dt"],
                y=cum_df["loss"],
                name="일별 공회전 (kWh)",
                marker=dict(
                    color="rgba(102,126,234,0.30)",
                    line=dict(color="rgba(102,126,234,1.0)", width=2),
                ),
                hovertemplate="<b>%{x|%m-%d}</b><br>일별: %{y:.1f} kWh<extra></extra>",
            ),
            secondary_y=False,
        )

        fig_cumul.add_trace(
            go.Scatter(
                x=cum_df["dt"],
                y=cum_df["cumulative_loss"],
                name="누적 공회전 (kWh)",
                mode="lines+markers",
                line=dict(color=CHART_COLORS['carbon'], width=3, shape='spline'),
                marker=dict(size=7, line=dict(width=0)),
                hovertemplate="<b>%{x|%m-%d}</b><br>누적: %{y:,.0f} kWh<extra></extra>",
            ),
            secondary_y=True,
        )

        fig_cumul.add_vrect(
            x0=start_dt,
            x1=end_dt,
            fillcolor="rgba(245,87,108,0.10)",
            layer="below",
            line_width=0,
        )

        fig_cumul.update_xaxes(
            title_text="날짜",
            showgrid=False,
            tickformat="%m-%d",
            # **[수정]** x축 눈금 레이블 및 제목 크기
            tickfont=dict(color='black', size=AXIS_FONT_SIZE),
            title_font=dict(color='black', size=AXIS_FONT_SIZE)
        )
        fig_cumul.update_yaxes(
            title_text="일별 (kWh)",
            secondary_y=False,
            showgrid=False,
            rangemode="tozero",
            # **[수정]** y축 눈금 레이블 및 제목 크기
            tickfont=dict(color='black', size=AXIS_FONT_SIZE),
            title_font=dict(color='black', size=AXIS_FONT_SIZE)
        )
        fig_cumul.update_yaxes(
            title_text="누적 (kWh)",
            secondary_y=True,
            showgrid=False,
            rangemode="tozero",
            # **[수정]** 보조 y축 눈금 레이블 및 제목 크기
            tickfont=dict(color='black', size=AXIS_FONT_SIZE),
            title_font=dict(color='black', size=AXIS_FONT_SIZE)
        )

        fig_cumul.update_layout(
            height=460,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                # **[수정]** 범례 폰트 크기
                font=dict(size=AXIS_FONT_SIZE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=40, t=10, b=40),
            uirevision='idle_cumul'
        )

        st.plotly_chart(fig_cumul, use_container_width=True, config={'displayModeBar': False})
        st.divider()

    # 인사이트 패널
    def render_insights_panel(kpis_idle: dict, filtered_df: pd.DataFrame):
        total_loss = float(kpis_idle.get('공회전 에너지 손실', {}).get('value', 0) or 0)
        details = kpis_idle.get('공회전 에너지 손실', {}).get('details', [0, 0]) or [0, 0]
        loss_work = float(details[0] if len(details) > 0 else 0)
        loss_rest = float(details[1] if len(details) > 1 else 0)
        work_baseline_val = float(kpis_idle.get('가동일 야간 베이스라인', {}).get('value', 0) or 0)
        total_idle_cost = float(kpis_idle.get('공회전 비용 손실', {}).get('value', 0) or 0)

        rest_percentage = (loss_rest / total_loss * 100) if total_loss > 0 else 0.0
        num_rest_days = int(filtered_df.loc[filtered_df['작업휴무'].eq('휴무'), 'date'].nunique())
        avg_daily_rest_loss = (loss_rest / num_rest_days) if num_rest_days > 0 else 0.0

        st.markdown(f"""
        <div class="insights-panel-container">
          <div class="insight-header">분석 인사이트 & 개선 제안</div>

          <div class="insight-item">
            <div class="insight-title">1. 휴무일 공회전 비중이 높습니다 ({rest_percentage:,.1f}%)</div>
            <div class="insight-text">
              선택 기간 내 전체 공회전 손실 중 <strong>{rest_percentage:,.1f}%</strong>가 휴무일에 발생했습니다.
              휴무일 일평균 불필요 소비는 <strong>{avg_daily_rest_loss:,.1f} kWh</strong>입니다.
              <br>비중이 높다면 <b>자동 차단 시스템</b> 도입을 검토하세요.
            </div>
          </div>

          <div class="insight-item">
            <div class="insight-title">2. 가동일 야간 베이스라인 개선 필요</div>
            <div class="insight-text">
              가동일 야간(22:00–08:00) 베이스라인은 <strong>{work_baseline_val:,.1f} kWh</strong>입니다.
              해당 수준을 초과해 <b>idle_power</b>가 발생한 설비(압축기/HVAC/조명 등)의
              <b>야간 가동 스케줄</b>을 재점검하세요.
            </div>
          </div>

          <div class="insight-item">
            <div class="insight-title">3. 공회전 손실 TOP Day 집중 관리</div>
            <div class="insight-text">
              TOP 10 손실일을 확인하여 휴무 전날 <b>설비 차단 체크리스트</b> 및
              <b>관리자 알림</b> 자동화를 적용하십시오.
            </div>
          </div>

          <div class="insight-item">
            <div class="insight-title">4. 단기 액션 플랜 & 예상 절감 효과</div>
            <div class="insight-text">
              공회전 비용 손실(선택 기간): <strong>₩{total_idle_cost:,.0f}</strong><br><br>
              • <b>즉시(비용 0)</b>: 휴무일 설비 수동 차단 체크리스트 → 초기 절감 효과 파악<br>
              • <b>1개월(₩500,000)</b>: 타이머/스케줄러 기반 자동 차단 시스템 구축<br>
              • <b>3개월(₩2,500,000)</b>: 스마트 EMS 알림/모니터링 시스템 구축<br><br>
              현재 공회전 손실의 50%만 개선해도 <b>약 ₩{total_idle_cost * 0.5:,.0f}</b> 절감이 가능합니다.
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    render_insights_panel(kpis_idle, filtered_df)