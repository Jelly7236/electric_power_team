from docxtpl import DocxTemplate, InlineImage 
from io import BytesIO
import pandas as pd
import numpy as np
import plotly.express as px
from docx.shared import Inches
from pathlib import Path
import warnings
import traceback
import streamlit as st
# report.py 최상단 어딘가 (streamlit import 아래 등)
import matplotlib
matplotlib.use("Agg")  # 헤드리스(배포) 환경용 백엔드
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc # 👈 폰트 관리를 위한 라이브러리 추가
import os
# report.py 상단 ---------------------------------------------------------------
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import plotly.express as px

# === 1) 프로젝트 내 TTF 경로를 절대경로로 안전하게 잡기 ===
# report.py 파일 기준으로 상대 경로를 계산
_THIS = Path(__file__).resolve()
FONT_PATH = (_THIS.parent / "data_dash" / "fonts" / "NanumGothic.ttf").resolve()

# === 2) TTF를 Matplotlib에 등록 + 기본 폰트로 지정 ===
PLOT_FONT_FAMILY = "NanumGothic"  # Plotly에도 동일 이름을 넘길 예정

def set_korean_font(ttf_path: Path):
    global PLOT_FONT_FAMILY
    try:
        if ttf_path.exists():
            # 폰트 등록
            font_manager.fontManager.addfont(str(ttf_path))
            prop = font_manager.FontProperties(fname=str(ttf_path))
            name = prop.get_name()          # 예: "NanumGothic"
            PLOT_FONT_FAMILY = name         # Plotly에서 쓸 패밀리명
            # Matplotlib 전역 설정
            import matplotlib as mpl
            mpl.rcParams["font.family"] = name
            mpl.rcParams["axes.unicode_minus"] = False
            # (선택) 캐시 리빌드
            try:
                font_manager._rebuild()
            except Exception:
                pass
            print(f"[report] ✅ 폰트 적용: {name} @ {ttf_path}")
        else:
            # 폰트 파일이 없을 때: 시스템에 설치된 나눔/맑은고딕을 시도
            import matplotlib as mpl
            # 우선순위: NanumGothic > Malgun Gothic > DejaVu Sans
            mpl.rcParams["font.family"] = ["NanumGothic", "Malgun Gothic", "DejaVu Sans"]
            mpl.rcParams["axes.unicode_minus"] = False
            print(f"[report] ⚠️ 폰트 파일 없음: {ttf_path}. 시스템 폰트로 대체.")
    except Exception as e:
        print(f"[report] ❌ 폰트 설정 실패: {e}")

set_korean_font(FONT_PATH)
# ----------------------------------------------------------------------------- 

warnings.filterwarnings("ignore")

# 요금 단가 및 설정
RATES_HIGH_B_II = {
    "봄·가을철": {"기본": 7380, "경부하": 105.6, "중간부하": 127.9, "최대부하": 158.2},
    "여름철":   {"기본": 7380, "경부하": 105.6, "중간부하": 157.9, "최대부하": 239.1},
    "겨울철":   {"기본": 7380, "경부하": 112.6, "중간부하": 157.9, "최대부하": 214.1},
}

APPLIED_POWER = 700  # 계약전력(kW)
POWER_FACTOR_RATE = 0.2  # 역률 조정 비율 (한전규정)

LOAD_COLORS = {
    'Light_Load': '#4CAF50',    # 경부하
    'Medium_Load': '#FFC107',   # 중간부하
    'Maximum_Load': '#EF5350'   # 최대부하
}

# =========================
# 안전 이미지 유틸
# =========================
def _tiny_placeholder_png() -> BytesIO:
    """1x1 투명 PNG 버퍼 생성 (Pillow 없이도 동작하는 순수 PNG 바이트)"""
    # 미니멀 투명 PNG (base64 아님, 원시 바이트)
    data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc``\x00"
        b"\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    buf = BytesIO(data)
    buf.seek(0)
    return buf

def _safe_inline_image(doc: DocxTemplate, img_buf: BytesIO | None, width_in=3.0,
                       use_placeholder=True) -> InlineImage | None:
    """
    - img_buf가 비거나 None이면:
        * use_placeholder=True: 1x1 투명 PNG로 대체 → InlineImage 반환
        * use_placeholder=False: None 반환 (템플릿에서 {% if %}로 감싸야 함)
    - 정상 버퍼면 InlineImage로 감싸서 반환
    """
    try:
        if img_buf is None:
            if use_placeholder:
                return InlineImage(doc, _tiny_placeholder_png(), width=Inches(width_in))
            return None

        # 버퍼 길이 점검
        try:
            size = img_buf.getbuffer().nbytes
        except Exception:
            # 일부 환경에서 getbuffer 불가 → 읽어서 길이 체크
            p = img_buf.tell()
            img_buf.seek(0, 2)
            size = img_buf.tell()
            img_buf.seek(p)

        if size <= 0:
            if use_placeholder:
                return InlineImage(doc, _tiny_placeholder_png(), width=Inches(width_in))
            return None

        img_buf.seek(0)
        return InlineImage(doc, img_buf, width=Inches(width_in))
    except Exception:
        if use_placeholder:
            return InlineImage(doc, _tiny_placeholder_png(), width=Inches(width_in))
        return None

# =========================

def calculate_power_factor_penalty(pf, base_pf, min_pf=60.0, max_pf=95.0):
    """역률 패널티 비율 계산 (통합 함수)"""
    if pf >= base_pf:
        # 감액: 기준 초과 시
        target_pf = min(pf, max_pf)
        pf_diff = target_pf - base_pf
        return -(pf_diff * POWER_FACTOR_RATE)  # 음수: 감액
    else:
        # 추가: 기준 미달 시
        target_pf = max(pf, min_pf)
        pf_diff = base_pf - target_pf
        return (pf_diff * POWER_FACTOR_RATE)  # 양수: 추가

def calculate_monthly_power_factor(df):
    """월평균 역률 계산 (지상/진상)"""
    # 주간 역률 (09:00~22:00)
    df_day = df[(df['hour'] >= 9) & (df['hour'] < 22)]
    total_kwh_day = df_day['전력사용량(kWh)'].sum()
    net_lag_kvarh = df_day['지상무효전력량(kVarh)'].sum() - df_day['진상무효전력량(kVarh)'].sum()
    
    pf_day = (total_kwh_day / np.sqrt(total_kwh_day**2 + net_lag_kvarh**2)) * 100 \
             if total_kwh_day > 0 and net_lag_kvarh >= 0 else 100.0
    
    # 야간 역률 (22:00~09:00)
    df_night = df[(df['hour'] >= 22) | (df['hour'] < 9)]
    total_kwh_night = df_night['전력사용량(kWh)'].sum()
    
    lag_kvarh = df_night['지상무효전력량(kVarh)'].sum()
    lead_kvarh = df_night['진상무효전력량(kVarh)'].sum()
    
    if total_kwh_night > 0:
        net_kvarh = abs(lead_kvarh - lag_kvarh)
        pf_night_lead = (total_kwh_night / np.sqrt(total_kwh_night**2 + net_kvarh**2)) * 100
    else:
        pf_night_lead = 100.0
    
    return pf_day, pf_night_lead

def create_chart_image(df, chart_type):
    """
    그래프 이미지 생성 → PNG BytesIO 반환.
    1) 먼저 Plotly+kaleido로 시도
    2) 실패하면 matplotlib로 동일 차트를 생성
    """
    buf = BytesIO()

    if df.empty:
        # 빈 그래프라도 보여주자 (matplotlib 사용, 함수 내 import 금지!)
        fig, ax = plt.subplots(figsize=(6, 3), dpi=150)
        ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf

    # ---------- 1) Plotly (+kaleido) 시도 ----------
    try:
        import plotly.express as px
        import plotly.io as pio

        if chart_type == 'daily_usage':
            _df = df.copy()
            _df['날짜'] = _df['측정일시'].dt.date.astype(str)
            daily_usage = _df.groupby(['날짜', '작업유형'])['전력사용량(kWh)'].sum().reset_index()

            fig = px.bar(
                daily_usage, x='날짜', y='전력사용량(kWh)', color='작업유형',
                title='일별 전력사용량 (부하 유형별)', color_discrete_map=LOAD_COLORS
            )
            fig.update_layout(
                barmode='stack', height=300, margin=dict(t=50, b=50),
                font=dict(size=10, color='black'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            fig.update_xaxes(tickangle=-45, showgrid=False)
            fig.update_yaxes(showgrid=False)

        elif chart_type == 'monthly_comp':
            current_month = int(df['month'].iloc[0])
            current_usage = float(df['전력사용량(kWh)'].sum())
            prev_usage = current_usage * 0.9  # 임시
            comp_data = pd.DataFrame({
                '구분': [f'{current_month-1}월 (전월)', f'{current_month}월'],
                '총 사용량': [prev_usage, current_usage]
            })
            fig = px.bar(
                comp_data, x='구분', y='총 사용량', color='구분',
                color_discrete_map={
                    f'{current_month}월': '#1f77b4',
                    f'{current_month-1}월 (전월)': '#ffb366'
                },
                text='총 사용량'
            )
            fig.update_traces(texttemplate='%{y:,.0f} kWh', textposition='outside', textfont_color='black')
            fig.update_layout(
                title='총 전력사용량 비교', height=300, showlegend=False,
                margin=dict(t=50, b=50), font=dict(size=10, color='black')
            )
            fig.update_yaxes(title_text="총 전력사용량 (kWh)", showgrid=False)
            fig.update_xaxes(title_text="", showgrid=False)
        else:
            fig = None

        if fig is not None:
            # kaleido 필요
            png_bytes = pio.to_image(fig, format="png", width=600, height=300, scale=1)
            buf.write(png_bytes)
            buf.seek(0)
            return buf
    except Exception as e:
        print(f"[report.py] Plotly->PNG 실패: {e}")

    # ---------- 2) matplotlib 폴백 ----------
    if chart_type == 'daily_usage':
        # 1) 날짜 정렬 + 날짜형으로 그룹핑
        _df = df.copy().sort_values('측정일시')
        _df['날짜'] = _df['측정일시'].dt.normalize()  # YYYY-MM-DD 00:00:00

        daily_usage = (
            _df.groupby(['날짜', '작업유형'])['전력사용량(kWh)']
               .sum()
               .unstack(fill_value=0)
        )

        # 2) x축 라벨은 'MM-DD'만 표시
        labels = pd.to_datetime(daily_usage.index).strftime('%m-%d')
        n = len(daily_usage.index)

        # 3) 시리즈 안전 추출
        series = {
            'Light_Load':  daily_usage.get('Light_Load',  pd.Series(0, index=daily_usage.index)),
            'Medium_Load': daily_usage.get('Medium_Load', pd.Series(0, index=daily_usage.index)),
            'Maximum_Load':daily_usage.get('Maximum_Load',pd.Series(0, index=daily_usage.index)),
        }

        fig, ax = plt.subplots(figsize=(6, 3), dpi=150)
        bottom = np.zeros(n)

        for key, label, color in [
            ('Light_Load',  '경부하',   LOAD_COLORS['Light_Load']),
            ('Medium_Load', '중간부하', LOAD_COLORS['Medium_Load']),
            ('Maximum_Load','최대부하', LOAD_COLORS['Maximum_Load']),
        ]:
            vals = series[key].to_numpy() if hasattr(series[key], "to_numpy") else np.zeros(n)
            ax.bar(labels, vals, bottom=bottom, label=label, color=color)
            bottom += vals

        ax.set_title("일별 전력사용량 (부하 유형별)")
        ax.set_ylabel("kWh")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(False)

        # ✅ 범례는 하단 중앙으로 '한 번만' 표시
        leg = ax.legend(
            loc='center left',        # 축의 왼쪽 중앙을 기준으로
            bbox_to_anchor=(1.02, 0.5),  # 축 바깥 오른쪽(1.02), 수직 중앙(0.5)
            ncol=1,                   # 세로(1열)
            frameon=False,
            borderaxespad=0.0,        # 축과 범례 사이 여백 최소화
            handlelength=1.5,         # 범례 마커 길이
            labelspacing=0.6          # 라벨 간 여백
        )

        # ✅ 범례 공간 확보
        plt.subplots_adjust(bottom=0.40)

        # fig.tight_layout()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf

    elif chart_type == 'monthly_comp':
        current_month = int(df['month'].iloc[0])
        current_usage = float(df['전력사용량(kWh)'].sum())
        prev_usage = current_usage * 0.9  # 임시
        labels = [f'{current_month-1}월 (전월)', f'{current_month}월']
        values = [prev_usage, current_usage]
        colors = ['#ffb366', '#1f77b4']

        fig, ax = plt.subplots(figsize=(6, 3), dpi=150)
        ax.bar(labels, values, color=colors)
        for i, v in enumerate(values):
            ax.text(i, v, f"{v:,.0f} kWh", ha='center', va='bottom')
        ax.set_title("총 전력사용량 비교")
        ax.set_ylabel("kWh")
        ax.grid(False)
        fig.tight_layout()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf




def get_billing_data(df):
    """요금 데이터 계산 및 Context 생성"""
    if df.empty:
        return {}

    # 기간 및 계절 결정
    month = int(df['month'].iloc[0])
    season_kor = '겨울철' if month in [1, 2, 11, 12] else \
                 '여름철' if month in [6, 7, 8] else '봄·가을철'
    rate_set = RATES_HIGH_B_II[season_kor]
    
    # 시간대별 사용량
    usage_by_type = df.groupby('작업유형')['전력사용량(kWh)'].sum()
    usage = {
        '경부하': float(usage_by_type.get('Light_Load', 0.0)),
        '중간부하': float(usage_by_type.get('Medium_Load', 0.0)),
        '최대부하': float(usage_by_type.get('Maximum_Load', 0.0)),
    }
    
    # 역률 계산
    pf_day, pf_night_lead = calculate_monthly_power_factor(df)
    
    # 역률 패널티 계산
    지상패널티율_pct = calculate_power_factor_penalty(pf_day, 90.0)
    진상패널티율_pct = calculate_power_factor_penalty(pf_night_lead, 95.0)
    
    # 요금 계산
    total_basic_fee = APPLIED_POWER * rate_set['기본']
    fees = {
        '경부하': usage['경부하'] * rate_set['경부하'],
        '중간부하': usage['중간부하'] * rate_set['중간부하'],
        '최대부하': usage['최대부하'] * rate_set['최대부하']
    }
    총_전력량_요금 = sum(fees.values())
    지상역률_요금 = total_basic_fee * (지상패널티율_pct / 100.0)
    진상역률_요금 = total_basic_fee * (진상패널티율_pct / 100.0)
    모든_요금_합 = total_basic_fee + 총_전력량_요금 + 지상역률_요금 + 진상역률_요금
    부가가치세 = 모든_요금_합 * 0.1
    총_요금_세금_포함 = 모든_요금_합 + 부가가치세
    
    return {
        'month': month,
        'start': df['측정일시'].min().strftime('%Y-%m-%d'),
        'end': df['측정일시'].max().strftime('%Y-%m-%d'),
        'peak': f"{df['전력사용량(kWh)'].max():,.0f}",
        '총_요금': f"{df['전기요금(원)'].sum():,.0f}",
        'season': season_kor,
        '총_기본_요금': f"{total_basic_fee:,.0f}",
        '경부하_단가': f"{rate_set['경부하']:.1f}",
        '경부하총사용': f"{usage['경부하']:,.0f}",
        '총_경부하_요금': f"{fees['경부하']:,.0f}",
        '중간부하_단가': f"{rate_set['중간부하']:.1f}",
        '중간부하총사용': f"{usage['중간부하']:,.0f}",
        '총_중간부하_요금': f"{fees['중간부하']:,.0f}",
        '최대부하_단가': f"{rate_set['최대부하']:.1f}",
        '최대부하총사용': f"{usage['최대부하']:,.0f}",
        '총_최대부하_요금': f"{fees['최대부하']:,.0f}",
        '평균지상역률': f"{pf_day:.2f}%",
        '평균진상역률': f"{pf_night_lead:.2f}%",
        '지상패널티율': f"{지상패널티율_pct:+.2f}%",
        '진상패널티율': f"{진상패널티율_pct:+.2f}%",
        '지상역률_요금': f"{지상역률_요금:,.0f}",
        '진상역률_요금': f"{진상역률_요금:,.0f}",
        '총_전력량_요금': f"{총_전력량_요금:,.0f}",
        '모든_요금_합': f"{모든_요금_합:,.0f}",
        '총_요금_세금_포함': f"{총_요금_세금_포함:,.0f}",
        '부가가치세': f"{부가가치세:,.0f}",
        # 그래프는 generate_report_from_template에서 주입
    }

def generate_report_from_template(filtered_df, template_path):
    """최종 보고서 생성 (Bytes 반환). 이미지 안전 처리 포함."""
    try:
        tpl_path = Path(template_path).resolve()
        if (not tpl_path.exists()) or tpl_path.is_dir():
            st.error(f"템플릿 파일 누락 오류: 경로를 찾을 수 없습니다. 경로: {tpl_path}")
            return None

        doc = DocxTemplate(str(tpl_path))

        # 컨텍스트
        context = get_billing_data(filtered_df)
        if not context:
            st.warning("선택 기간 데이터가 없어 고지서를 생성할 수 없습니다.")
            return None

        # 그래프 이미지 생성 (한 번만 생성)
        image_data1 = create_chart_image(filtered_df, 'daily_usage')
        image_data2 = create_chart_image(filtered_df, 'monthly_comp')

        # 안전 삽입
        context['graph1'] = _safe_inline_image(doc, image_data1, width_in=3.0, use_placeholder=True)
        context['graph2'] = _safe_inline_image(doc, image_data2, width_in=3.0, use_placeholder=True)



        # 템플릿 렌더
        try:
            doc.render(context)
        except Exception as e:
            # 템플릿 변수명(Jinja) 오류 등
            st.error(f"고지서 렌더링 오류: {e}")
            st.exception(e)
            return None

        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream.read()

    except Exception as e:
        st.error(f"고지서 생성 중 일반 오류 발생: {e}")
        st.exception(e)
        return None
