import pandas as pd, numpy as np
import seaborn as sns, matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\train_휴무포함.csv")
df.info()

assert {"측정일시","전력사용량(kWh)","휴무여부"}.issubset(df.columns), "필수 컬럼 누락"
if not pd.api.types.is_datetime64_any_dtype(df["측정일시"]):
    df = df.copy()
    df["측정일시"] = pd.to_datetime(df["측정일시"], errors="coerce")
df["전력사용량(kWh)"] = pd.to_numeric(df["전력사용량(kWh)"], errors="coerce")

# 휴무/가동 표준화 (예: 'Y'/'N', '휴무'/'가동' 등 혼재 대비)
def normalize_holiday(x):
    x = str(x).strip().lower()
    if x in ["y","yes","휴무","true","1"]:
        return "휴무"
    return "가동"
tmp = df.dropna(subset=["측정일시","전력사용량(kWh)","휴무여부"]).copy()
tmp["휴무상태"] = tmp["휴무여부"].map(normalize_holiday)
tmp["hour"] = tmp["측정일시"].dt.hour
tmp["date"] = tmp["측정일시"].dt.date
sns.set_theme(style="whitegrid")

plt.figure(figsize=(10,5))
sns.histplot(data=tmp, x="전력사용량(kWh)", hue="휴무상태",
             bins=40, stat="density", common_norm=False, kde=True, alpha=0.35)
plt.title("전력사용량 분포 (구간 단위)")
plt.xlabel("전력사용량 (kWh)"); plt.ylabel("밀도")
plt.tight_layout(); plt.show()

# 일별 합계
daily = (tmp.groupby(["date","휴무상태"])["전력사용량(kWh)"]
           .sum().reset_index(name="일합계_kWh"))

fig, ax = plt.subplots(1,2, figsize=(12,5))
sns.violinplot(data=daily, x="휴무상태", y="일합계_kWh", inner="quartile", ax=ax[0])
ax[0].set_title("일합계 분포(바이올린)"); ax[0].set_xlabel(""); ax[0].set_ylabel("일합계 (kWh)")

# ECDF(누적분포)로 전체 형태 비교
for k, g in daily.groupby("휴무상태"):
    x = np.sort(g["일합계_kWh"].values)
    y = np.arange(1, len(x)+1)/len(x)
    ax[1].plot(x, y, label=k)
ax[1].set_title("일합계 ECDF"); ax[1].set_xlabel("일합계 (kWh)"); ax[1].set_ylabel("누적비율")
ax[1].legend()
plt.tight_layout(); plt.show()


# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager, rcParams

# -----------------------------
# 0) 한글 폰트 설정 (OS 자동 탐색)
# -----------------------------
def set_korean_font():
    candidates = [
        r"C:\Windows\Fonts\malgun.ttf", r"C:\Windows\Fonts\Malgun.ttf",  # Windows
        "/System/Library/Fonts/AppleGothic.ttf",                         # macOS
        "/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",               # Linux
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

    # seaborn 테마에도 반영 + grid off
    sns.set_theme(style="whitegrid",
                  rc={"font.family": rcParams.get("font.family", "sans-serif"),
                      "axes.unicode_minus": False,
                      "axes.grid": False})
    return font_name

print("Applied font:", set_korean_font())

# -----------------------------
# 1) 데이터 준비/타입 보정
# -----------------------------
assert {"측정일시","전력사용량(kWh)","휴무여부"}.issubset(df.columns), "필수 컬럼 누락"

df = df.copy()
if not pd.api.types.is_datetime64_any_dtype(df["측정일시"]):
    df["측정일시"] = pd.to_datetime(df["측정일시"], errors="coerce")

df["전력사용량(kWh)"] = pd.to_numeric(df["전력사용량(kWh)"], errors="coerce")

# 휴/가동 표준화
def normalize_holiday(x: object) -> str:
    s = str(x).strip()
    if s in {"휴", "가동"}:
        return s
    sl = s.lower()
    if sl in {"y","yes","true","1","휴무","휴일"}:
        return "휴"
    return "가동"

df["휴무상태"] = df["휴무여부"].map(normalize_holiday)

# -----------------------------
# 2) 월별 '일합계' 평균 계산
# -----------------------------
df["date"]  = df["측정일시"].dt.date
df["month"] = df["측정일시"].dt.month

daily = (df
         .groupby(["date","month","휴무상태"], as_index=False)["전력사용량(kWh)"]
         .sum()
         .rename(columns={"전력사용량(kWh)":"일합계_kWh"}))

monthly_mean = (daily
                .groupby(["month","휴무상태"], as_index=False)["일합계_kWh"]
                .mean()
                .rename(columns={"일합계_kWh":"월평균_일합계_kWh"}))

# 월×휴/가동 모든 조합 유지(1~12월)
all_months = pd.Index(range(1,13), name="month")
cats = pd.CategoricalDtype(["휴","가동"], ordered=True)
monthly_mean["휴무상태"] = monthly_mean["휴무상태"].astype(cats)
monthly_mean = (monthly_mean
                .set_index(["month","휴무상태"])
                .reindex(pd.MultiIndex.from_product([all_months, cats.categories],
                                                    names=["month","휴무상태"]))
                .reset_index())

# (선택) NaN을 0으로 채우려면 아래 주석 해제
# monthly_mean["월평균_일합계_kWh"] = monthly_mean["월평균_일합계_kWh"].fillna(0)

# -----------------------------
# 3) 시각화 (그룹 막대)
# -----------------------------
fmt = FuncFormatter(lambda y, _: f"{y:,.0f}")
palette = {"휴":"#ff7f0e", "가동":"#1f77b4"}  # 휴=주황, 가동=파랑

plt.figure(figsize=(12, 5))
ax = sns.barplot(
    data=monthly_mean,
    x="month", y="월평균_일합계_kWh",
    hue="휴무상태", hue_order=["휴","가동"],
    palette=palette, edgecolor="black"
)

ax.set_xlabel("월")
ax.set_ylabel("전력사용량 월평균(일합계 기준, kWh)")
ax.yaxis.set_major_formatter(fmt)
ax.set_xticklabels([f"{m}월" for m in range(1,13)])

# 막대 위 값 라벨
for p in ax.patches:
    h = p.get_height()
    if np.isfinite(h):
        ax.annotate(f"{h:,.0f}",
                    (p.get_x() + p.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9)

ax.legend(title="", loc="upper right")
ax.set_title("월별 휴/가동 전력사용량 평균 (일합계 기준)")

plt.tight_layout()
plt.show()
