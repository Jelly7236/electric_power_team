import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\train_df.csv")
df.info()




# 시간대별 평균 역률을 계산합니다.
hourly_pf_analysis = df.groupby(['작업휴무', 'hour']).agg(
    avg_lagging_pf=('지상역률(%)', 'mean'),
    avg_leading_pf=('진상역률(%)', 'mean')
).reset_index()

# 시각화 설정을 합니다.
sns.set_theme(style="whitegrid")
# 한글 폰트 설정 (사용자 환경에 따라 'Malgun Gothic'이 없을 경우 다른 폰트로 대체 필요)
plt.rcParams['font.family'] = 'Malgun Gothic'
# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False


# --- 1. 지상역률(%) (Lagging Power Factor) 일별 사이클 그래프 ---

plt.figure(figsize=(12, 6))

# 라인 플롯을 그립니다.
sns.lineplot(data=hourly_pf_analysis, x='hour', y='avg_lagging_pf', hue='작업휴무', marker='o')

# KEPCO 규정 기준선 (90%)을 표시합니다.
plt.axhline(y=90, color='r', linestyle='--', label='요금제 기준선 (90%)')

# KEPCO 규제 시간 (09시 ~ 22시)을 강조합니다.
plt.axvspan(9, 22, color='yellow', alpha=0.3, label='KEPCO 지상역률 규제 시간 (09시~22시)')

# 제목과 라벨 설정
plt.title('작업휴무 별 시간대별 평균 지상역률(%)', fontsize=16)
plt.xlabel('시간 (Hour)', fontsize=12)
plt.ylabel('평균 지상역률(%)', fontsize=12)
plt.xticks(range(0, 24))
plt.ylim(50, 105)
plt.legend(title='작업휴무', loc='lower right')
plt.tight_layout()
plt.savefig('lagging_pf_daily_cycle.png')
plt.close()

# --- 2. 진상역률(%) (Leading Power Factor) 일별 사이클 그래프 ---

plt.figure(figsize=(12, 6))

# 라인 플롯을 그립니다.
sns.lineplot(data=hourly_pf_analysis, x='hour', y='avg_leading_pf', hue='작업휴무', marker='o')

# KEPCO 규정 기준선 (95%)을 표시합니다.
plt.axhline(y=95, color='r', linestyle='--', label='요금제 기준선 (95%)')

# KEPCO 규제 시간 (22시 ~ 09시)을 강조합니다.
# 22시~23시59분
plt.axvspan(22, 24, color='orange', alpha=0.3, label='KEPCO 진상역률 규제 시간 (22시~09시)')
# 0시~9시
plt.axvspan(0, 9, color='orange', alpha=0.3)

# 제목과 라벨 설정
plt.title('작업휴무 별 시간대별 평균 진상역률(%)', fontsize=16)
plt.xlabel('시간 (Hour)', fontsize=12)
plt.ylabel('평균 진상역률(%)', fontsize=12)
plt.xticks(range(0, 24))
plt.ylim(50, 105)
plt.legend(title='작업휴무', loc='lower right')
plt.tight_layout()
plt.savefig('leading_pf_daily_cycle.png')
plt.close()


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 데이터 로드
# 파일 경로를 'train_df.csv'로 설정합니다.
df = pd.read_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\train_df.csv")

# 2. 15분 단위(시간분) 평균 지상역률 및 진상역률을 작업휴무 별로 계산합니다.
analysis_15min = df.groupby(['작업휴무', '시간분']).agg(
    avg_lagging_pf=('지상역률(%)', 'mean'), # 지상역률 평균
    avg_leading_pf=('진상역률(%)', 'mean')  # 진상역률 평균
).reset_index()

# 시각화 설정을 합니다.
sns.set_theme(style="whitegrid")
# 한글 폰트 설정 (사용자 환경에 따라 'Malgun Gothic'이 없을 경우 다른 폰트로 대체 필요)
plt.rcParams['font.family'] = 'Malgun Gothic'
# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False 

# ----------------------------------------------------------------------
# --- 1. 15분 단위 평균 지상역률(%) 일일 사이클 그래프 (규제: 09시~22시, 90%) ---
# ----------------------------------------------------------------------

plt.figure(figsize=(12, 6))

# 라인 플롯 생성
sns.lineplot(data=analysis_15min, x='시간분', y='avg_lagging_pf', hue='작업휴무', linewidth=2)

# KEPCO 규정 기준선 (90%) 및 규제 시간 (09시 ~ 22시) 표시
plt.axhline(y=90, color='r', linestyle='--', label='요금제 기준선 (90%)')
plt.axvspan(9, 22, color='yellow', alpha=0.3, label='KEPCO 규제 시간 (09시~22시)')

# 제목 및 축 설정
plt.title('작업휴무 별 15분 단위 평균 지상역률(%) 일일 사이클', fontsize=16)
plt.xlabel('시간 (Hour, 15분 단위)', fontsize=12)
plt.ylabel('평균 지상역률(%)', fontsize=12)
plt.xticks(range(0, 24, 1)) # X축 눈금 1시간 단위
plt.xlim(0, 24)
plt.ylim(0, 105)
plt.legend(title='작업휴무', loc='lower right')
plt.grid(True, axis='x', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig('15min_avg_lagging_pf_cycle.png')
plt.close()


# ----------------------------------------------------------------------
# --- 2. 15분 단위 평균 진상역률(%) 일일 사이클 그래프 (규제: 22시~09시, 95%) ---
# ----------------------------------------------------------------------

plt.figure(figsize=(12, 6))

# 라인 플롯 생성
sns.lineplot(data=analysis_15min, x='시간분', y='avg_leading_pf', hue='작업휴무', linewidth=2)

# KEPCO 규정 기준선 (95%) 표시
plt.axhline(y=95, color='r', linestyle='--', label='요금제 기준선 (95%)')

# KEPCO 규제 시간 (22시 ~ 다음날 09시) 강조
# 22시부터 24시까지
plt.axvspan(22, 24, color='orange', alpha=0.3, label='KEPCO 규제 시간 (22시~09시)')
# 0시부터 9시까지
plt.axvspan(0, 9, color='orange', alpha=0.3)

# 제목 및 축 설정
plt.title('작업휴무 별 15분 단위 평균 진상역률(%) 일일 사이클', fontsize=16)
plt.xlabel('시간 (Hour, 15분 단위)', fontsize=12)
plt.ylabel('평균 진상역률(%)', fontsize=12)
plt.xticks(range(0, 24, 1)) # X축 눈금 1시간 단위
plt.xlim(0, 24)
plt.ylim(0, 105)
plt.legend(title='작업휴무', loc='lower right')
plt.grid(True, axis='x', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig('15min_avg_leading_pf_cycle.png')
plt.close()


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 데이터 로드


# 2. 15분 단위(시간분) 평균 지상역률 및 진상역률을 작업휴무 별로 계산합니다.
analysis_15min = df.groupby(['작업휴무', '시간분']).agg(
    avg_lagging_pf=('지상역률(%)', 'mean'),  # 지상역률 평균
    avg_leading_pf=('진상역률(%)', 'mean')   # 진상역률 평균
).reset_index()

# 시각화 설정을 합니다.
sns.set_theme(style="whitegrid")
# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False 

# '가동'과 '휴무' 데이터 분리
df_on = analysis_15min[analysis_15min['작업휴무'] == '가동']
df_off = analysis_15min[analysis_15min['작업휴무'] == '휴무']

# 플로팅 함수 정의 (코드 반복을 줄이기 위해)
def plot_pf_cycle(data, status, filename):
    plt.figure(figsize=(12, 6))
    
    # 지상역률(%) 플롯 (파란색)
    plt.plot(data['시간분'], data['avg_lagging_pf'], label='지상역률(%) (Lagging PF)', color='blue', linewidth=2)
    # 진상역률(%) 플롯 (녹색)
    plt.plot(data['시간분'], data['avg_leading_pf'], label='진상역률(%) (Leading PF)', color='green', linewidth=2)

    # --- KEPCO 규정 기준선 및 규제 시간 표시 ---
    
    # 1. 지상역률 규정 (09시~22시, 90%)
    plt.axhline(y=90, color='blue', linestyle='--', alpha=0.7, label='지상역률 기준선 (90%)')
    plt.axvspan(9, 22, color='lightblue', alpha=0.2, label='지상역률 규제 시간 (09시~22시)')
    
    # 2. 진상역률 규정 (22시~09시, 95%)
    plt.axhline(y=95, color='green', linestyle=':', alpha=0.7, label='진상역률 기준선 (95%)')
    # 22시부터 24시까지
    plt.axvspan(22, 24, color='lightgreen', alpha=0.2, label='진상역률 규제 시간 (22시~09시)')
    # 0시부터 9시까지
    plt.axvspan(0, 9, color='lightgreen', alpha=0.2)

    # 제목 및 축 설정
    plt.title(f'작업휴무 "{status}" 시 15분 단위 평균 역률 비교', fontsize=16)
    plt.xlabel('시간 (Hour, 15분 단위)', fontsize=12)
    plt.ylabel('평균 역률(%)', fontsize=12)
    plt.xticks(range(0, 24, 1)) # X축 눈금 1시간 단위
    plt.xlim(0, 24)
    plt.ylim(0, 105)
    plt.legend(title='역률 종류 및 규정', loc='lower right')
    plt.grid(True, axis='x', linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# 3. '가동' 데이터 플롯 및 저장
plot_pf_cycle(df_on, '가동', '15min_pf_cycle_on.png')

# 4. '휴무' 데이터 플롯 및 저장
plot_pf_cycle(df_off, '휴무', '15min_pf_cycle_off.png')



import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 분석에 사용할 월 정의: 1월, 2월, 3월, 11월
target_months = [1, 2, 3, 10, 11]

# 1. 데이터 로드 및 필터링

df = df[df['month'].isin(target_months)].copy() # 타겟 월만 필터링합니다.

# 2. 월(month), 작업휴무, 시간분 별로 그룹화하여 평균 역률을 계산합니다.
monthly_15min_pf = df.groupby(['month', '작업휴무', '시간분']).agg(
    avg_lagging_pf=('지상역률(%)', 'mean'),  # 평균 지상역률
    avg_leading_pf=('진상역률(%)', 'mean')   # 평균 진상역률
).reset_index()

# 'month'를 문자열로 변환하여 시각화의 색상(hue)으로 사용합니다.
monthly_15min_pf['month'] = monthly_15min_pf['month'].astype(str)

# '가동'과 '휴무' 데이터 분리
df_on = monthly_15min_pf[monthly_15min_pf['작업휴무'] == '가동']
df_off = monthly_15min_pf[monthly_15min_pf['작업휴무'] == '휴무']

# 시각화 설정을 합니다.
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False 

# --- 플로팅 함수 정의: 4개의 그래프 생성을 자동화합니다. ---
def plot_monthly_15min_cycle(data, status, pf_type, pf_col, filename, criterion, regulation_start, regulation_end):
    plt.figure(figsize=(14, 7))
    
    # 월별 추이를 라인 플롯으로 그립니다.
    sns.lineplot(data=data, x='시간분', y=pf_col, hue='month', palette='tab10', linewidth=1.5)

    # KEPCO 요금제 기준선 표시
    plt.axhline(y=criterion, color='r', linestyle='--', label=f'요금제 기준선 ({criterion}%)')

    # KEPCO 규제 시간 영역 강조
    if pf_type == '지상역률(%)':
        # 09시 ~ 22시 규제
        plt.axvspan(regulation_start, regulation_end, color='yellow', alpha=0.15, label='KEPCO 규제 시간 (09시~22시)')
    elif pf_type == '진상역률(%)':
        # 22시 ~ 09시 규제
        plt.axvspan(22, 24, color='orange', alpha=0.15, label='KEPCO 규제 시간 (22시~09시)')
        plt.axvspan(0, 9, color='orange', alpha=0.15)
    
    # 제목 및 축 설정
    plt.title(f'작업휴무 "{status}" 시 1, 2, 3, 11월 15분 단위 평균 {pf_type}', fontsize=16)
    plt.xlabel('시간 (Hour, 15분 단위)', fontsize=12)
    plt.ylabel(f'평균 {pf_type}', fontsize=12)
    plt.xticks(range(0, 24, 1))
    plt.xlim(0, 24)
    # Y축 범위는 기준선 근처에 집중되도록 설정합니다.
    y_min = data[pf_col].min()
    plt.ylim(y_min - 5 if y_min < criterion else criterion - 5, 105)
    plt.legend(title='월 (Month)', loc='lower right')
    plt.grid(True, axis='x', linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# ----------------------------------------------------------------------
# --- 3. '가동' 시, 월별 15분 단위 역률 그래프 생성 ---
# ----------------------------------------------------------------------

# 3-1. 지상역률 (규제: 09시~22시, 90%)
plot_monthly_15min_cycle(
    df_on, '가동', '지상역률(%)', 'avg_lagging_pf', '15min_pf_cycle_on_lagging_1_2_3_11.png', 
    criterion=90, regulation_start=9, regulation_end=22
)

# 3-2. 진상역률 (규제: 22시~09시, 95%)
plot_monthly_15min_cycle(
    df_on, '가동', '진상역률(%)', 'avg_leading_pf', '15min_pf_cycle_on_leading_1_2_3_11.png', 
    criterion=95, regulation_start=22, regulation_end=9
)

# ----------------------------------------------------------------------
# --- 4. '휴무' 시, 월별 15분 단위 역률 그래프 생성 ---
# ----------------------------------------------------------------------

# 4-1. 지상역률 (규제: 09시~22시, 90%)
plot_monthly_15min_cycle(
    df_off, '휴무', '지상역률(%)', 'avg_lagging_pf', '15min_pf_cycle_off_lagging_1_2_3_11.png', 
    criterion=90, regulation_start=9, regulation_end=22
)

# 4-2. 진상역률 (규제: 22시~09시, 95%)
plot_monthly_15min_cycle(
    df_off, '휴무', '진상역률(%)', 'avg_leading_pf', '15min_pf_cycle_off_leading_1_2_3_11.png', 
    criterion=95, regulation_start=22, regulation_end=9
)



import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# 2. 그룹화 및 평균 계산 (1차 매핑 패턴 구축)
# 작업휴무 x 작업유형 x 시간분 별 평균 역률 계산
pf_cycle_full = df.groupby(['작업휴무', '작업유형', '시간분']).agg(
    avg_lagging_pf=('지상역률(%)', 'mean'),
    avg_leading_pf=('진상역률(%)', 'mean')
).reset_index()

# 3. 데이터 분리
df_on = pf_cycle_full[pf_cycle_full['작업휴무'] == '가동'].copy()
df_off = pf_cycle_full[pf_cycle_full['작업휴무'] == '휴무'].copy()

# 4. 시각화 설정
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False 

# 5. 2x2 서브플롯 생성
fig, axes = plt.subplots(2, 2, figsize=(18, 12), sharex=True, sharey=True)
fig.suptitle('작업휴무 및 작업유형별 15분 단위 평균 역률 패턴', fontsize=20, y=1.02)

# 공통 기준선 및 규제 시간 정의
LAGGING_CRITERION = 90
LEADING_CRITERION = 95
LAGGING_REG_START = 9
LAGGING_REG_END = 22

# --- 5-1. Top Left: 지상역률 (가동) ---
sns.lineplot(data=df_on, x='시간분', y='avg_lagging_pf', hue='작업유형', 
             ax=axes[0, 0], palette='Set1', linewidth=2, legend=False)
axes[0, 0].axhline(y=LAGGING_CRITERION, color='r', linestyle='--', alpha=0.7)
axes[0, 0].axvspan(LAGGING_REG_START, LAGGING_REG_END, color='yellow', alpha=0.15)
axes[0, 0].set_title('① 지상역률 (%) - 가동', fontsize=16)
axes[0, 0].set_ylabel('평균 지상역률(%)', fontsize=12)
axes[0, 0].set_xlabel('')
axes[0, 0].set_ylim(50, 105)

# --- 5-2. Top Right: 진상역률 (가동) ---
sns.lineplot(data=df_on, x='시간분', y='avg_leading_pf', hue='작업유형', 
             ax=axes[0, 1], palette='Set1', linewidth=2)
axes[0, 1].axhline(y=LEADING_CRITERION, color='g', linestyle='--', alpha=0.7)
# 진상역률 규제 시간 (22시~09시)
axes[0, 1].axvspan(22, 24, color='lightgreen', alpha=0.15)
axes[0, 1].axvspan(0, 9, color='lightgreen', alpha=0.15)
axes[0, 1].set_title('② 진상역률 (%) - 가동', fontsize=16)
axes[0, 1].set_ylabel('평균 진상역률(%)', fontsize=12)
axes[0, 1].set_xlabel('')
axes[0, 1].legend(title='작업유형', loc='lower right')

# --- 5-3. Bottom Left: 지상역률 (휴무) ---
sns.lineplot(data=df_off, x='시간분', y='avg_lagging_pf', hue='작업유형', 
             ax=axes[1, 0], palette='Set1', linewidth=2, legend=False)
axes[1, 0].axhline(y=LAGGING_CRITERION, color='r', linestyle='--', alpha=0.7)
axes[1, 0].axvspan(LAGGING_REG_START, LAGGING_REG_END, color='yellow', alpha=0.15)
axes[1, 0].set_title('③ 지상역률 (%) - 휴무', fontsize=16)
axes[1, 0].set_ylabel('평균 지상역률(%)', fontsize=12)
axes[1, 0].set_xlabel('시간 (Hour, 15분 단위)', fontsize=12)
axes[1, 0].set_xticks(range(0, 24, 2))

# --- 5-4. Bottom Right: 진상역률 (휴무) ---
sns.lineplot(data=df_off, x='시간분', y='avg_leading_pf', hue='작업유형', 
             ax=axes[1, 1], palette='Set1', linewidth=2, legend=False)
axes[1, 1].axhline(y=LEADING_CRITERION, color='g', linestyle='--', alpha=0.7)
axes[1, 1].axvspan(22, 24, color='lightgreen', alpha=0.15)
axes[1, 1].axvspan(0, 9, color='lightgreen', alpha=0.15)
axes[1, 1].set_title('④ 진상역률 (%) - 휴무', fontsize=16)
axes[1, 1].set_ylabel('평균 진상역률(%)', fontsize=12)
axes[1, 1].set_xlabel('시간 (Hour, 15분 단위)', fontsize=12)
axes[1, 1].set_xticks(range(0, 24, 2))

plt.tight_layout()
plt.savefig('pf_cycle_4_way_comparison.png')
plt.close()


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 데이터 로드

# 2. 시각화 설정
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False 

# 공통 기준선 및 규제 시간 정의
LAGGING_CRITERION = 90
LEADING_CRITERION = 95
LAGGING_REG_START = 9
LAGGING_REG_END = 22

# --- 플로팅 함수 정의: 계절별 4가지 패턴 비교 그래프 생성 ---
def plot_monthly_pf_comparison(target_months, title_suffix, filename):
    
    # 데이터 필터링 및 그룹화
    df_filtered = df[df['month'].isin(target_months)].copy()
    
    # 월별, 작업휴무, 작업유형, 시간분 별 평균 계산
    pf_cycle_full = df_filtered.groupby(['작업휴무', '작업유형', '시간분', 'month']).agg(
        avg_lagging_pf=('지상역률(%)', 'mean'),
        avg_leading_pf=('진상역률(%)', 'mean')
    ).reset_index()
    
    pf_cycle_full['month'] = pf_cycle_full['month'].astype(str)
    
    # 데이터 분리
    df_on = pf_cycle_full[pf_cycle_full['작업휴무'] == '가동'].copy()
    df_off = pf_cycle_full[pf_cycle_full['작업휴무'] == '휴무'].copy()

    # 지상역률 저하 주범인 'Maximum_Load'만 필터링 (가동 지상역률 플롯용)
    df_on_max = df_on[df_on['작업유형'] == 'Maximum_Load']
    
    # 나머지 3개 플롯은 월별 전체 평균을 사용 (패턴이 안정적이므로)
    df_on_avg_leading = df_on.groupby(['시간분', 'month'])[['avg_leading_pf']].mean().reset_index()
    df_off_avg_lagging = df_off.groupby(['시간분', 'month'])[['avg_lagging_pf']].mean().reset_index()
    df_off_avg_leading = df_off.groupby(['시간분', 'month'])[['avg_leading_pf']].mean().reset_index()


    fig, axes = plt.subplots(2, 2, figsize=(18, 12), sharex=True, sharey=True)
    fig.suptitle(f'{title_suffix} 작업휴무 및 작업유형별 15분 단위 평균 역률 패턴', fontsize=20, y=1.02)
    
    # --- 1. Top Left: 지상역률 (가동, Maximum_Load) ---
    sns.lineplot(data=df_on_max, x='시간분', y='avg_lagging_pf', hue='month', 
                 ax=axes[0, 0], palette='viridis', linewidth=2)
    axes[0, 0].axhline(y=LAGGING_CRITERION, color='r', linestyle='--', alpha=0.7)
    axes[0, 0].axvspan(LAGGING_REG_START, LAGGING_REG_END, color='yellow', alpha=0.15)
    axes[0, 0].set_title(f'① 지상역률 (%) - 가동 (Maximum_Load)', fontsize=16)
    axes[0, 0].set_ylabel('평균 지상역률(%)', fontsize=12)
    axes[0, 0].set_xlabel('')
    axes[0, 0].set_ylim(50, 105)
    axes[0, 0].legend(title='월 (Month)', loc='lower right')

    # --- 2. Top Right: 진상역률 (가동, 월별 전체 평균) ---
    sns.lineplot(data=df_on_avg_leading, x='시간분', y='avg_leading_pf', hue='month', 
                 ax=axes[0, 1], palette='viridis', linewidth=2)
    axes[0, 1].axhline(y=LEADING_CRITERION, color='g', linestyle='--', alpha=0.7)
    axes[0, 1].axvspan(22, 24, color='lightgreen', alpha=0.15)
    axes[0, 1].axvspan(0, 9, color='lightgreen', alpha=0.15)
    axes[0, 1].set_title('② 진상역률 (%) - 가동 (월별 전체 평균)', fontsize=16)
    axes[0, 1].set_ylabel('평균 진상역률(%)', fontsize=12)
    axes[0, 1].set_xlabel('')
    axes[0, 1].legend(title='월 (Month)', loc='lower right')

    # --- 3. Bottom Left: 지상역률 (휴무, 월별 전체 평균) ---
    sns.lineplot(data=df_off_avg_lagging, x='시간분', y='avg_lagging_pf', hue='month', 
                 ax=axes[1, 0], palette='viridis', linewidth=2, legend=False)
    axes[1, 0].axhline(y=LAGGING_CRITERION, color='r', linestyle='--', alpha=0.7)
    axes[1, 0].axvspan(LAGGING_REG_START, LAGGING_REG_END, color='yellow', alpha=0.15)
    axes[1, 0].set_title('③ 지상역률 (%) - 휴무 (월별 전체 평균)', fontsize=16)
    axes[1, 0].set_ylabel('평균 지상역률(%)', fontsize=12)
    axes[1, 0].set_xlabel('시간 (Hour, 15분 단위)', fontsize=12)
    axes[1, 0].set_xticks(range(0, 24, 2))

    # --- 4. Bottom Right: 진상역률 (휴무, 월별 전체 평균) ---
    sns.lineplot(data=df_off_avg_leading, x='시간분', y='avg_leading_pf', hue='month', 
                 ax=axes[1, 1], palette='viridis', linewidth=2, legend=False)
    axes[1, 1].axhline(y=LEADING_CRITERION, color='g', linestyle='--', alpha=0.7)
    axes[1, 1].axvspan(22, 24, color='lightgreen', alpha=0.15)
    axes[1, 1].axvspan(0, 9, color='lightgreen', alpha=0.15)
    axes[1, 1].set_title('④ 진상역률 (%) - 휴무 (월별 전체 평균)', fontsize=16)
    axes[1, 1].set_ylabel('평균 진상역률(%)', fontsize=12)
    axes[1, 1].set_xlabel('시간 (Hour, 15분 단위)', fontsize=12)
    axes[1, 1].set_xticks(range(0, 24, 2))

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()





