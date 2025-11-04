from docxtpl import DocxTemplate, InlineImage 
from io import BytesIO
import pandas as pd
import numpy as np
import plotly.express as px
from docx.shared import Inches
import warnings
import traceback
from PIL import Image  # 🔥 추가!

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
    """그래프 이미지 생성 - Plotly → PIL Image 변환"""
    print(f"🔍 DEBUG: 차트 생성 시작 - {chart_type}")
    
    if df.empty:
        print(f"⚠️ DEBUG: 데이터프레임이 비어있음")
        return create_empty_image()

    try:
        fig = None
        
        if chart_type == 'daily_usage':
            # 일별 부하 유형별 Stack Bar Chart
            df['날짜'] = df['측정일시'].dt.date.astype(str)
            daily_usage = df.groupby(['날짜', '작업유형'])['전력사용량(kWh)'].sum().reset_index()
            
            fig = px.bar(daily_usage, x='날짜', y='전력사용량(kWh)', color='작업유형',
                         title='일별 전력사용량 (부하 유형별)', color_discrete_map=LOAD_COLORS)
            
            fig.update_layout(barmode='stack', height=400, margin=dict(t=50, b=50, l=50, r=50),
                             font=dict(size=10, color='black'),
                             legend=dict(orientation="h", yanchor="bottom", y=1.02))
            fig.update_xaxes(tickangle=-45, showgrid=False)
            fig.update_yaxes(showgrid=False)
            
        elif chart_type == 'monthly_comp':
            # 전월 대비 총 사용량 비교
            current_month = df['month'].iloc[0]
            current_usage = df['전력사용량(kWh)'].sum()
            prev_usage = current_usage * 0.9  # 임시 값
            
            comp_data = pd.DataFrame({
                '구분': [f'{current_month-1}월 (전월)', f'{current_month}월'],
                '총 사용량': [prev_usage, current_usage]
            })
            
            fig = px.bar(comp_data, x='구분', y='총 사용량', color='구분',
                         color_discrete_map={f'{current_month}월': '#1f77b4', 
                                            f'{current_month-1}월 (전월)': '#ffb366'},
                         text='총 사용량')
            
            fig.update_traces(texttemplate='%{y:,.0f} kWh', textposition='outside', 
                             textfont_color='black')
            fig.update_layout(title='총 전력사용량 비교', height=400, showlegend=False,
                             margin=dict(t=50, b=50, l=50, r=50), font=dict(size=10, color='black'))
            fig.update_yaxes(title_text="총 전력사용량 (kWh)", showgrid=False)
            fig.update_xaxes(title_text="", showgrid=False)
        
        if fig is None:
            print(f"⚠️ DEBUG: fig가 None")
            return create_empty_image()
        
        # 🔥 Plotly → PNG → PIL Image → BytesIO 변환
        img_bytes = fig.to_image(format="png", width=800, height=400, scale=2)
        img = Image.open(BytesIO(img_bytes))
        
        # BytesIO로 저장
        img_buf = BytesIO()
        img.save(img_buf, format='PNG')
        img_buf.seek(0)
        
        print(f"✅ DEBUG: 차트 생성 완료 - {chart_type}, 크기: {len(img_buf.getvalue())} bytes")
        return img_buf
        
    except Exception as e:
        print(f"❌ CHART ERROR: {chart_type} 생성 실패 - {e}")
        traceback.print_exc()
        return create_empty_image()


def create_empty_image():
    """빈 이미지 생성 (에러 대체용)"""
    from PIL import Image, ImageDraw, ImageFont
    
    # 800x400 흰색 배경
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 텍스트 추가
    text = "차트 생성 실패"
    # 기본 폰트 사용
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # 텍스트 중앙 정렬
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((800 - text_width) // 2, (400 - text_height) // 2)
    
    draw.text(position, text, fill='black', font=font)
    
    # BytesIO로 변환
    img_buf = BytesIO()
    img.save(img_buf, format='PNG')
    img_buf.seek(0)
    return img_buf


def get_billing_data(df):
    """요금 데이터 계산 및 Context 생성"""
    print(f"🔍 DEBUG: get_billing_data 시작")
    
    if df.empty:
        print(f"⚠️ DEBUG: 데이터프레임이 비어있음")
        return {}

    # 기간 및 계절 결정
    month = df['month'].iloc[0]
    season_kor = '겨울철' if month in [1, 2, 11, 12] else \
                 '여름철' if month in [6, 7, 8] else '봄·가을철'
    
    rate_set = RATES_HIGH_B_II[season_kor]
    
    # 시간대별 사용량
    usage_by_type = df.groupby('작업유형')['전력사용량(kWh)'].sum()
    usage = {
        '경부하': usage_by_type.get('Light_Load', 0),
        '중간부하': usage_by_type.get('Medium_Load', 0),
        '최대부하': usage_by_type.get('Maximum_Load', 0),
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
    
    print(f"✅ DEBUG: get_billing_data 완료")
    
    # Context 생성
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
        'graph1': "일별 사용량 이미지",
        'graph2': "월별 비교 이미지",
    }


def generate_report_from_template(filtered_df, template_path):
    """최종 보고서 생성"""
    print(f"🔍 DEBUG: 고지서 생성 시작")
    print(f"🔍 DEBUG: 템플릿 경로: {template_path}")
    print(f"🔍 DEBUG: 템플릿 존재 여부: {Path(template_path).exists()}")
    print(f"🔍 DEBUG: filtered_df 크기: {len(filtered_df)}")
    
    try:
        # 1. 템플릿 로드
        from pathlib import Path
        if not Path(template_path).exists():
            raise FileNotFoundError(f"템플릿 파일 없음: {template_path}")
        
        doc = DocxTemplate(template_path)
        print(f"✅ DEBUG: 템플릿 로드 성공")

        # 2. 컨텍스트 데이터 처리
        context = get_billing_data(filtered_df)
        print(f"✅ DEBUG: 데이터 처리 완료")
        
        # 3. 그래프 이미지 생성
        print(f"🔍 DEBUG: 그래프 1 생성 중...")
        img1 = create_chart_image(filtered_df, 'daily_usage')
        context['graph1'] = InlineImage(doc, img1, width=Inches(5))
        print(f"✅ DEBUG: 그래프 1 완료")
        
        print(f"🔍 DEBUG: 그래프 2 생성 중...")
        img2 = create_chart_image(filtered_df, 'monthly_comp')
        context['graph2'] = InlineImage(doc, img2, width=Inches(5))
        print(f"✅ DEBUG: 그래프 2 완료")
        
        # 4. 렌더링 및 저장
        print(f"🔍 DEBUG: 문서 렌더링 중...")
        doc.render(context)
        print(f"✅ DEBUG: 렌더링 완료")
        
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        result = file_stream.read()
        
        print(f"✅ DEBUG: 고지서 생성 완료 - {len(result)} bytes")
        return result
        
    except FileNotFoundError as e:
        print(f"❌ REPORT ERROR: 템플릿 파일 누락 - {e}")
        traceback.print_exc()
        return b''
        
    except Exception as e:
        print(f"❌ REPORT ERROR: 고지서 생성 실패 - {type(e).__name__}: {e}")
        traceback.print_exc()
        return b''