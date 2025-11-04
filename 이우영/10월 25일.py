import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib import font_manager, rcParams

df = pd.read_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\train_휴무포함.csv")


# ==========================================
# 월별 전력사용량(합계) + 월별 전기요금(평균) 시각화
#  - 최댓값/최솟값 월은 파랑, 나머지는 회색
#  - 평균 전기요금 선은 빨강
#  - seaborn 사용 + 한글 폰트 강제 적용 + grid 제거
# ============================================


# ---------- (A) 한글 폰트 강제 적용 유틸 ----------
def _apply_korean_font():
    # 1) 파일 경로 후보 (있으면 파일 등록)
    CANDIDATE_PATHS = [
        r"C:\Windows\Fonts\malgun.ttf",                       # Windows: 맑은고딕
        r"C:\Windows\Fonts\Malgun.ttf",
        "/System/Library/Fonts/AppleGothic.ttf",              # macOS: AppleGothic
        "/Library/Fonts/AppleSDGothicNeo.ttc",                # macOS: AppleSDGothicNeo
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",    # Linux: 나눔고딕
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Linux: Noto CJK
    ]
    font_path = next((p for p in CANDIDATE_PATHS if os.path.exists(p)), None)
    font_name = None
    if font_path:
        font_manager.fontManager.addfont(font_path)
        font_name = font_manager.FontProperties(fname=font_path).get_name()

    # 2) 파일을 못 찾으면, 시스템에 설치된 폰트 이름에서 탐색
    if not font_name:
        installed = {f.name for f in font_manager.fontManager.ttflist}
        for name in [
            "Malgun Gothic", "AppleGothic", "Apple SD Gothic Neo",
            "NanumGothic", "NanumBarunGothic",
            "Noto Sans CJK KR", "Noto Sans CJK",
        ]:
            if name in installed:
                font_name = name
                break

    # 3) 최종 적용 (없으면 기본 폰트 유지)
    if font_name:
        rcParams["font.family"] = font_name
    rcParams["axes.unicode_minus"] = False

    # 4) seaborn 테마에도 rc로 강제 반영 + grid 끔
    sns.set_theme(
        style="white",
        rc={"font.family": rcParams["font.family"], "axes.unicode_minus": False, "axes.grid": False},
    )
    return font_name

_apply_korean_font()
# -------------------------------------------

# 0) 기본 전처리(안전장치)
assert {"측정일시", "전력사용량(kWh)", "전기요금(원)"}.issubset(df.columns), "필수 컬럼이 없습니다."
if not pd.api.types.is_datetime64_any_dtype(df["측정일시"]):
    df["측정일시"] = pd.to_datetime(df["측정일시"], errors="coerce")

# ym 없으면 생성
if "ym" not in df.columns:
    df["ym"] = df["측정일시"].dt.to_period("M").astype(str)

# 수치형 보장
df["전력사용량(kWh)"] = pd.to_numeric(df["전력사용량(kWh)"], errors="coerce")
df["전기요금(원)"] = pd.to_numeric(df["전기요금(원)"], errors="coerce")

# 1) 월별 집계
# (a) 월별 사용량 '합계'
monthly_usage = df.groupby("ym")["전력사용량(kWh)"].sum(min_count=1).rename("monthly_kwh")

# (b) 월별 '일평균' 전력사용량 (달 길이/결측 보정)
daily_kwh = (df.set_index("측정일시")["전력사용량(kWh)"].resample("D").sum(min_count=1))
monthly_kwh_mean_per_day = daily_kwh.groupby(daily_kwh.index.to_period("M")).mean().rename("monthly_kwh_mean_per_day")

# (c) (참고) 월 평균 전기요금
monthly_cost_mean = df.groupby("ym")["전기요금(원)"].mean().rename("monthly_cost_mean")

out = pd.concat([monthly_usage, monthly_kwh_mean_per_day, monthly_cost_mean], axis=1).sort_index()
plot_df = out.reset_index().rename(columns={"index": "ym"})

# 2) 최대/최소 사용량 월 색상 지정 (파랑), 나머지는 회색
import numpy as np, seaborn as sns
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt

max_val = plot_df["monthly_kwh"].max()
min_val = plot_df["monthly_kwh"].min()
is_max = plot_df["monthly_kwh"].eq(max_val)
is_min = plot_df["monthly_kwh"].eq(min_val)
bar_colors = np.where(is_max | is_min, "#1f77b4", "#bdbdbd")

# 3) 플롯 (seaborn + twin y-axis)
fig, ax1 = plt.subplots(figsize=(12, 5))

# Bar: 월 사용량(합계)
order = plot_df["ym"].tolist()
sns.barplot(
    data=plot_df, x="ym", y="monthly_kwh",
    order=order, palette=bar_colors,
    edgecolor="black", ax=ax1
)
ax1.set_xlabel("월 (YYYY-MM)")
ax1.set_ylabel("월별 사용량 (kWh)")

# 막대 위 값 표시
for rect, val in zip(ax1.patches, plot_df["monthly_kwh"].values):
    if np.isnan(val):
        continue
    ax1.annotate(
        f"{val:,.0f}",
        xy=(rect.get_x() + rect.get_width()/2, rect.get_height()),
        xytext=(0, 3), textcoords="offset points",
        ha="center", va="bottom", fontsize=9
    )

# 🔴 보조축: 월 '일평균' 전력사용량(빨강 선)
ax2 = ax1.twinx()
sns.lineplot(
    data=plot_df, x="ym", y="monthly_kwh_mean_per_day",
    ax=ax2, color="#d62728", marker="o", linewidth=2.5
)
ax2.set_ylabel("월 '일평균' 전력사용량 (kWh)")
ax2.ticklabel_format(style="plain", axis="y")  # 과학 표기 방지

# 제목/축/범례/스타일
ax1.set_title("월별 전력사용량: 합계(막대) & '일평균'(빨간 선)")
for label in ax1.get_xticklabels():
    label.set_rotation(45)
    label.set_ha("right")

legend_elements = [
    Patch(facecolor="#1f77b4", edgecolor="black", label="최대/최소 사용 월(막대)"),
    Patch(facecolor="#bdbdbd", edgecolor="black", label="기타 월(막대)"),
    Line2D([0], [0], color="#d62728", marker="o", lw=2.5, label="월 '일평균' 사용량(선)"),
]
ax1.legend(handles=legend_elements, loc="upper right", frameon=True)

# grid OFF
ax1.grid(False); ax2.grid(False)

plt.tight_layout()
plt.show()




# 1월~12월 하루하루 전기 사용량 확인하기

# ============================================
# 1월~12월 하루하루 전기 사용량 시각화 (Seaborn)
#  - df: (columns) 측정일시, 전력사용량(kWh)
#  - 출력:
#     (A) 선택 연도 일별 사용량 라인플롯
#     (B) 월별 소형 차트(12개 FacetGrid)
#     (C) [옵션] 달력형 히트맵(월 x 일)
# ============================================

# 0) 기본 전처리
assert {"측정일시", "전력사용량(kWh)"}.issubset(df.columns), "필수 컬럼이 없습니다."
if not pd.api.types.is_datetime64_any_dtype(df["측정일시"]):
    df["측정일시"] = pd.to_datetime(df["측정일시"], errors="coerce")
df = df.dropna(subset=["측정일시"]).copy()
df["전력사용량(kWh)"] = pd.to_numeric(df["전력사용량(kWh)"], errors="coerce")

# 1) 일별 합계(전형적으로 kWh는 합계가 적절)
daily = (
    df.set_index("측정일시")["전력사용량(kWh)"]
      .resample("D").sum(min_count=1)
      .rename("daily_kwh")
      .reset_index()
)
daily["year"]  = daily["측정일시"].dt.year
daily["month"] = daily["측정일시"].dt.month
daily["day"]   = daily["측정일시"].dt.day

# 2) 시각화에 사용할 연도 선택 (데이터가 가장 많은 연도)
year_counts = daily["year"].value_counts(dropna=True)
YEAR = int(year_counts.index[0])  # 가장 데이터가 많은 연도
print(f"[INFO] 시각화 연도 자동선택: {YEAR}")
dy = daily[daily["year"] == YEAR].copy()

# 3A) (전체) 일별 사용량 라인 플롯
plt.figure(figsize=(14, 4.5))
sns.lineplot(data=dy, x="측정일시", y="daily_kwh", linewidth=1.5)
plt.title(f"{YEAR}년 일별 전기 사용량 (kWh)")
plt.xlabel("날짜")
plt.ylabel("일별 사용량 (kWh)")
plt.tight_layout()
plt.show()

# 3B) (월별) 소형 차트 12개: 각 월의 일별 사용량 + 월평균(빨간 점선)
#    - x: day(1~31), y: daily_kwh, col: month
#    - 월별 평균선: 각 축에 수평선(axhline)으로 표시

# 3B) (월별) 소형 차트 12개: 각 월의 일별 사용량 + 월평균(빨간 점선) + 범례에 월 평균값 표시
# --------------------------------------------
# 월별 일일 전력 사용량 소형 차트 (11개) + 사각형 테두리 + 월 평균(빨간 점선) + 범례
# --------------------------------------------
# ====== 추가: 한글 폰트 설정 ======
# =========================================
# 0) 한글 폰트(플롯 전에 1번만 설정)
# =========================================
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from matplotlib.patches import Rectangle
from math import ceil

def set_korean_font_matplotlib():
    candidates = [
        r"C:\Windows\Fonts\malgun.ttf",                        # Windows
        r"C:\Windows\Fonts\Malgun.ttf",
        "/System/Library/Fonts/AppleGothic.ttf",               # macOS
        "/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",     # Linux
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    font_name = None
    for p in candidates:
        if os.path.exists(p):
            try:
                font_manager.fontManager.addfont(p)
                font_name = font_manager.FontProperties(fname=p).get_name()
                break
            except Exception:
                pass
    if not font_name:
        installed = {f.name for f in font_manager.fontManager.ttflist}
        for name in ["Malgun Gothic","AppleGothic","Apple SD Gothic Neo",
                     "NanumGothic","NanumBarunGothic","Noto Sans CJK KR","Noto Sans CJK"]:
            if name in installed:
                font_name = name
                break
    if font_name:
        rcParams["font.family"] = font_name
    rcParams["axes.unicode_minus"] = False
    return font_name

print("Applied font:", set_korean_font_matplotlib())

# =========================================
# 월별 일일 전기 사용량: matplotlib-only 전체 코드
# =========================================
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
from math import ceil
from matplotlib.lines import Line2D

# -------------------------------------------------
# 0) 한글 폰트 적용 (환경에 맞는 폰트 자동 탐색)
# -------------------------------------------------
def set_korean_font_matplotlib():
    candidates = [
        r"C:\Windows\Fonts\malgun.ttf",                        # Windows
        r"C:\Windows\Fonts\Malgun.ttf",
        "/System/Library/Fonts/AppleGothic.ttf",               # macOS
        "/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",     # Linux
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    font_name = None
    for p in candidates:
        if os.path.exists(p):
            try:
                font_manager.fontManager.addfont(p)
                font_name = font_manager.FontProperties(fname=p).get_name()
                break
            except Exception:
                pass
    if not font_name:
        installed = {f.name for f in font_manager.fontManager.ttflist}
        for name in ["Malgun Gothic","AppleGothic","Apple SD Gothic Neo",
                     "NanumGothic","NanumBarunGothic","Noto Sans CJK KR","Noto Sans CJK"]:
            if name in installed:
                font_name = name
                break
    if font_name:
        rcParams["font.family"] = font_name
    rcParams["axes.unicode_minus"] = False
    return font_name

print("Applied font:", set_korean_font_matplotlib())

# -------------------------------------------------
# 1) 데이터 준비 예시 (dy가 이미 있다고 가정)
#    dy: ['month','day','daily_kwh'] (+ 선택: 'year')
# -------------------------------------------------
# 안전 캐스팅
dy = dy.copy()
dy["month"] = pd.to_numeric(dy["month"], errors="coerce").astype("Int64")
dy["day"]   = pd.to_numeric(dy["day"], errors="coerce").astype("Int64")
dy["daily_kwh"] = pd.to_numeric(dy["daily_kwh"], errors="coerce")

# 월별 평균 (표도 필요하면 monthly_summary로 사용)
month_means = dy.groupby("month", dropna=True)["daily_kwh"].mean().round(1)
monthly_summary = (
    dy.groupby("month", dropna=True)["daily_kwh"]
      .agg(daily_kwh_mean="mean", days_observed="count", daily_kwh_sum="sum")
      .round({"daily_kwh_mean": 1})
      .sort_index()
)
print(monthly_summary)

# 몇 개 월을 그릴지 (None이면 전부, 숫자면 앞에서 N개월)
N_MONTHS = None  # 예: 11로 제한하려면 11
months_available = sorted(dy["month"].dropna().unique().tolist())
months_to_plot = months_available if N_MONTHS is None else months_available[:N_MONTHS]
dy11 = dy[dy["month"].isin(months_to_plot)].copy()

# 연도(있으면 제목에 사용)
YEAR = int(dy11["year"].iloc[0]) if "year" in dy11.columns and len(dy11["year"].dropna()) else None

# -------------------------------------------------
# 2) 서브플롯 생성 (개별 y축 스케일 사용)
# -------------------------------------------------
n = len(months_to_plot)
cols = 4
rows = ceil(n / cols)

fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*3),
                         sharex=False, sharey=False, squeeze=False)
axes = axes.flatten()

# 스타일
line_color = "#1f77b4"  # 일별 사용량
mean_color = "#d62728"  # 월 평균선
yfmt = FuncFormatter(lambda y, _: f"{y:,.0f}")  # 천단위 콤마

# -------------------------------------------------
# 3) 월별 패널 그리기
# -------------------------------------------------
for i, m in enumerate(months_to_plot):
    ax = axes[i]
    dsub = dy11.loc[dy11["month"] == m].sort_values("day")
    y = dsub["daily_kwh"].to_numpy(dtype=float)

    # (A) 일별 사용량 라인
    ax.plot(dsub["day"], y, linewidth=1.5, color=line_color)

    # (B) 월 평균선
    avg_val = month_means.loc[m] if m in month_means.index else np.nan
    if pd.notna(avg_val):
        ax.axhline(avg_val, linestyle="--", color=mean_color, linewidth=1.8)

    # (C) 패널별 y축 범위 자동 설정 (여백 8%)
    if np.isfinite(np.nanmin(y)) and np.isfinite(np.nanmax(y)):
        ymin, ymax = float(np.nanmin(y)), float(np.nanmax(y))
        pad = 0.08 * (ymax - ymin) if ymax > ymin else 1.0
        ax.set_ylim(ymin - pad, ymax + pad)
    else:
        ax.set_ylim(0, 1)

    # x축 1~31 고정
    ax.set_xlim(1, 31)

    # 테두리 사각형
    rect = Rectangle((0, 0), 1, 1, fill=False, transform=ax.transAxes,
                     clip_on=False, linewidth=1.2, edgecolor="#555555")
    ax.add_patch(rect)

    # 타이틀
    ax.set_title(f"{m}월", fontsize=11)

    # 축 라벨 (하단행/좌측열만 표시)
    r, c = divmod(i, cols)
    if r == rows - 1:
        ax.set_xlabel("일(day)")
    else:
        ax.set_xticklabels([])
    if c == 0:
        ax.set_ylabel("사용량(kWh)")
    else:
        ax.set_yticklabels([])

    ax.yaxis.set_major_formatter(yfmt)

    # (D) 평균값 라벨(우상단, 빨간 박스)
    if pd.notna(avg_val):
        ax.text(
            0.98, 0.90, f"평균 {avg_val:,.1f}",
            transform=ax.transAxes, ha="right", va="center",
            fontsize=9, color=mean_color,
            bbox=dict(facecolor="white", edgecolor=mean_color,
                      linewidth=0.8, boxstyle="round,pad=0.2")
        )

# 남는 빈 축 숨기기
for j in range(i + 1, rows * cols):
    axes[j].axis("off")

# -------------------------------------------------
# 4) 제목/범례/레이아웃
# -------------------------------------------------
title_txt = f"{YEAR}년 월별 일일 전기 사용량" if YEAR else "월별 일일 전기 사용량"
fig.suptitle(title_txt + f" (선택 {n}개월)", y=0.98, fontsize=13)

legend_handles = [
    Line2D([0], [0], color=line_color, lw=2, label="일별 사용량"),
    Line2D([0], [0], color=mean_color, lw=2, linestyle="--", label="월 평균"),
]
fig.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, 1.03),
           ncol=2, frameon=True, fontsize=10)

plt.tight_layout(rect=[0, 0, 1, 0.95])  # 제목/범례 공간 확보
plt.show()
