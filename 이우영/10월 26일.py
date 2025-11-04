import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib import font_manager, rcParams
from matplotlib.ticker import FuncFormatter
import matplotlib as mpl

df = pd.read_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\train_휴무포함.csv")
df.info()
test_df = pd.read_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\test.csv")
test_df.info()

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
    rcParams["axes.unicode_minus"] = False  # 마이너스 깨짐 방지

    # 4) seaborn 테마에도 rc로 강제 반영 + grid 끔
    sns.set_theme(
        style="white",  # grid 없음
        rc={"font.family": rcParams.get("font.family", "sans-serif"),
            "axes.unicode_minus": False,
            "axes.grid": False},
    )
    return font_name

# ✅ 플롯 전에 한 번만 호출
print("Applied font:", _apply_korean_font())



import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams

# ---- 한글 폰트(환경 자동 탐색) ----
def set_korean_font():
    candidates = [
        r"C:\Windows\Fonts\malgun.ttf", r"C:\Windows\Fonts\Malgun.ttf",
        "/System/Library/Fonts/AppleGothic.ttf",
        "/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    name = None
    for p in candidates:
        if os.path.exists(p):
            font_manager.fontManager.addfont(p)
            name = font_manager.FontProperties(fname=p).get_name()
            break
    if not name:
        installed = {f.name for f in font_manager.fontManager.ttflist}
        for n in ["Malgun Gothic","AppleGothic","Apple SD Gothic Neo",
                  "NanumGothic","Noto Sans CJK KR","Noto Sans CJK"]:
            if n in installed: name = n; break
    if name: rcParams["font.family"] = name
    rcParams["axes.unicode_minus"] = False
    sns.set_theme(style="white", rc={"font.family": rcParams.get("font.family","sans-serif"),
                                     "axes.unicode_minus": False, "axes.grid": False})
set_korean_font()

# ---- 데이터 준비 ----
assert {"측정일시","전력사용량(kWh)"}.issubset(df.columns)
if not pd.api.types.is_datetime64_any_dtype(df["측정일시"]):
    df = df.copy()
    df["측정일시"] = pd.to_datetime(df["측정일시"], errors="coerce")

tmp = df.dropna(subset=["측정일시","전력사용량(kWh)"]).copy()
tmp["hour"] = tmp["측정일시"].dt.hour                     # 0~23
tmp["dow"]  = tmp["측정일시"].dt.dayofweek                # 0=월 ... 6=일
dow_names   = {0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"}
tmp["요일"]  = tmp["dow"].map(dow_names)

# 피벗(요일×시간 평균 kWh), 시간 0~23 모두 보이도록 정렬
pivot = tmp.pivot_table(index="요일", columns="hour",
                        values="전력사용량(kWh)", aggfunc="mean")
pivot = pivot.reindex(index=["월","화","수","목","금","토","일"])  # y축 순서 고정
pivot = pivot.reindex(columns=list(range(24)))                  # x축 0~23

# ---- 히트맵 그리기 ----
plt.figure(figsize=(14, 5))
ax = sns.heatmap(pivot, cmap="YlOrRd", linewidths=0.3, linecolor="#eeeeee",
                 cbar_kws={"label":"전력사용량 평균(kWh)"}, annot=False)
ax.set_xlabel("시간(hour)")
ax.set_ylabel("요일")
ax.set_title("요일×시간별 전력사용량 평균 히트맵")
plt.tight_layout()
plt.show()



# 0) 준비: datetime/수치형 보장
assert {"측정일시","전력사용량(kWh)"}.issubset(df.columns), "필수 컬럼이 없습니다."
if not pd.api.types.is_datetime64_any_dtype(df["측정일시"]):
    df = df.copy()
    df["측정일시"] = pd.to_datetime(df["측정일시"], errors="coerce")
df["전력사용량(kWh)"] = pd.to_numeric(df["전력사용량(kWh)"], errors="coerce")

# (선택) 한글 폰트가 이미 설정돼 있다면 생략 가능
rcParams["axes.unicode_minus"] = False

# 1) 월/시간 파생 & 월-시간 평균 피벗
tmp = df.dropna(subset=["측정일시","전력사용량(kWh)"]).copy()
tmp["month"] = tmp["측정일시"].dt.month      # 1~12
tmp["hour"]  = tmp["측정일시"].dt.hour       # 0~23

# pivot: rows=hour(0~23), cols=month(1~12), values=mean kWh
pivot = tmp.pivot_table(index="hour", columns="month",
                        values="전력사용량(kWh)", aggfunc="mean")
pivot = pivot.reindex(index=range(24))  # 0~23 보장

# pivot: index=0..23(hour), columns=month(1..12)
months = sorted([c for c in pivot.columns if pd.notna(c)])

# 12색 고정 매핑
cmap = mpl.cm.get_cmap("tab20", 12)  # 20색 중 12개 샘플
color_map = {m: cmap(i) for i, m in enumerate(months)}

plt.figure(figsize=(12, 6))
for m in months:
    y = pivot[m].values
    plt.plot(range(24), y, marker="o", linewidth=2, color=color_map[m], label=f"{m}월")

plt.xticks(range(24))
plt.xlabel("시간(hour)")
plt.ylabel("전력사용량 평균 (kWh)")
plt.title("월별 시간대 평균 전력사용량")
plt.xticks(range(0, 24, 1))
plt.xlabel("시간(hour)")
plt.ylabel("전력사용량 평균 (kWh)")
plt.title("월별 시간대 평균 전력사용량")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.25), ncol=6, frameon=True)
plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.show()
