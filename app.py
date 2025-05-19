import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import numpy as np  # for jitter offsets

# ---------------------------------------------------------------------#
# 0. Page configuration & constants
# ---------------------------------------------------------------------#
st.set_page_config(page_title="2025 대선 기후 정책 종합 분석", layout="wide")

BASELINE_PARTY = "2018년 기준"
NDC_PARTY      = "2030 NDC"

# 정당별 대표색 (필요에 따라 추가)
PARTY_COLORS = {
    "국민의힘":   "#E61E2B",  # 빨강
    "더불어민주당": "#0066FF",  # 파랑
    "개혁신당":     "#FF8800",  # 주황
    "민주노동당":   "#FFD700",  # 노랑
    BASELINE_PARTY: "#999999",
    NDC_PARTY:      "#000000",
}

# ---------------------------------------------------------------------#
# 1. Load Excel
# ---------------------------------------------------------------------#
EXCEL_PATH = Path(__file__).parent / "data" / "climate_data.xlsx"

@st.cache_data
def load_sheets(path: Path) -> dict[str, pd.DataFrame]:
    """Read every sheet in an Excel file into a dict of DataFrames."""
    if not path.exists():
        st.error(f"엑셀 파일 '{path.name}'이(가) 존재하지 않습니다.")
        st.stop()

    xls = pd.ExcelFile(path)
    return {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names}


sheets = load_sheets(EXCEL_PATH)

# --- Debug sidebar: show all sheet names -----------------------------#
with st.sidebar.expander("📄 엑셀 시트 목록", expanded=False):
    st.write(list(sheets.keys()))

def find_sheet(keywords: list[str]) -> pd.DataFrame:
    """
    Return the first sheet whose name contains ANY of the given keywords.
    If nothing matches, raise a descriptive error listing available sheets.
    """
    for name, df in sheets.items():
        if any(k in name for k in keywords):
            return df.copy()

    kw = ", ".join(keywords)
    st.error(
        f"❌ 시트 이름에 [{kw}] 중 하나도 포함되지 않았습니다.\n\n"
        f"현재 엑셀에는 다음 시트가 있습니다:\n{list(sheets.keys())}"
    )
    st.stop()

# ---------------------------------------------------------------------#
# 2. Data wrangling
# ---------------------------------------------------------------------#
# 2‑1. Emissions ──────────────────────────────────────────────────────
EMISSION_KEYWORDS = ["배출", "emission", "총배출"]
em_sheet_name = next(
    (name for name in sheets if any(k in name for k in EMISSION_KEYWORDS)),
    None,
)

if em_sheet_name:
    em_raw = sheets[em_sheet_name]

    # wide → long 변환 여부 판단
    if "정당" not in em_raw.columns:
        emissions_df = em_raw.melt(id_vars="부문", var_name="정당", value_name="값")
    else:
        emissions_df = em_raw.rename(columns=str).copy()
else:
    # 시트가 없으면 빈 DF로 설정하고 이후 탭에서 안내만 표시
    emissions_df = pd.DataFrame()

sectors = [s for s in emissions_df["부문"].unique() if s != "총배출"] if not emissions_df.empty else []
parties  = emissions_df["정당"].unique().tolist() if not emissions_df.empty else []

# Color palette for energy sources (stacked bar)
ENERGY_COLORS = {
    "석탄":    "#000000",  # 검정
    "LNG":     "#808080",  # 회색
    "원자력":  "#0066FF",  # 파랑
    "재생에너지": "#22C55E",  # 초록
    "기타":    "#60A5FA",  # 하늘
    "청정수소/암모니아": "#06B6D4",
    "바이오":  "#A855F7",
    "연료전지": "#10B981",
}

# 2‑2. Energy mix ─────────────────────────────────────────────────────
en_raw = find_sheet(["에너지믹스"])
if en_raw.empty:
    energy_df = pd.DataFrame()             # 처리 없이 빈 DF
else:
    energy_df = (en_raw if "시나리오" in en_raw.columns
                 else en_raw.melt(id_vars="에너지원",
                                  var_name="시나리오",
                                  value_name="비중"))

    # --- Standardize column names ------------------------------------------------
    energy_df = energy_df.rename(columns=lambda c: c.strip().replace("(TWh)", "").replace(" ", ""))

# 2‑5. Energy source descriptions (optional sheet) --------------------
# (Load energy source descriptions from sheet if present)
desc_df_raw = find_sheet(["에너지설명", "energy_desc"])
if not desc_df_raw.empty and {"energy_source", "description"}.issubset(desc_df_raw.columns):
    desc_df = desc_df_raw.copy()
else:
    desc_df = pd.DataFrame(columns=["energy_source", "description"])

# Helper to get description for an energy source
def get_energy_desc(source: str) -> str:
    """Return description text from sheet; fallback to hard‑coded default."""
    fallback = {
        "석탄": "발전 단가는 낮지만 탄소·대기오염이 심각합니다.",
        "LNG": "유연성은 좋고 미세먼지 적지만 탄소를 배출합니다.",
        "원자력": "무탄소 베이스로드원이지만 폐기물·안전성 이슈가 있습니다.",
        "재생에너지": "무탄소·분산 가능, 출력 변동성과 부지 제약이 존재합니다.",
        "기타": "수력·바이오·연료전지 등 보조 전원입니다."
    }
    if not desc_df.empty:
        row = desc_df.loc[desc_df["energy_source"] == source]
        if not row.empty:
            return str(row["description"].values[0])
    return fallback.get(source, "")

# ---- If the sheet uses '발전량' instead of '비중', convert to share (%) ----
# (Removed automatic share conversion as per instructions)

# 2‑3. Temperature pathways ───────────────────────────────────────────
tp_raw = find_sheet(["온도경로"])
temp_df = (tp_raw if tp_raw.empty or "경로" in tp_raw.columns
           else tp_raw.melt(id_vars="연도",
                            var_name="경로",
                            value_name="배출량"))

# 2‑4. Policies (optional) ────────────────────────────────────────────
policy_df = find_sheet(["정성평가", "policy"])

def cmap(parties: list[str]) -> dict[str, str]:
    return {p: PARTY_COLORS.get(p, "#808080") for p in parties}

# ---------------------------------------------------------------------#
# Helper for policy scatter chart
# ---------------------------------------------------------------------#
def load_policy_df(sheet_keywords: list[str]) -> pd.DataFrame:
    """
    Return policy DataFrame in long format:
    columns = ['category','party','level','description']
    """
    try:
        df_raw = find_sheet(sheet_keywords)
    except st.runtime.scriptrunner.StopException:  # find_sheet already showed error
        return pd.DataFrame()

    # Expect either already long‑form, or wide JSON‑like sheet
    if set(["category", "party", "level", "description"]).issubset(df_raw.columns):
        return df_raw.copy()

    # Otherwise, try to normalize a nested JSON style
    records = []
    for _, row in df_raw.iterrows():
        cat = row["category"] if "category" in df_raw.columns else row.iloc[0]
        parties_dict = row["parties"] if "parties" in df_raw.columns else None
        if isinstance(parties_dict, dict):
            for p, d in parties_dict.items():
                records.append({
                    "category": cat,
                    "party": p,
                    "level": d.get("level"),
                    "description": d.get("description")
                })
    return pd.DataFrame(records)


def policy_scatter(policy_df: pd.DataFrame, title: str):
    if policy_df.empty:
        st.info("정책 데이터를 찾지 못했습니다.")
        return

    # Keep only levels 1, 2, 3 for this visualization
    policy_df = policy_df.query("level >= 1")

    # 정당 필터 (다중 선택)
    all_parties = sorted(policy_df["party"].unique())
    sel_parties = st.multiselect("비교할 정당", all_parties, default=all_parties,
                                 key=f"filter_{title}", placeholder="정당 선택")
    if sel_parties:
        policy_df = policy_df.query("party in @sel_parties")

    # Jitter duplicates horizontally so all circles are visible
    parties_local = list(policy_df["party"].unique())
    offsets = np.linspace(-0.15, 0.15, len(parties_local))
    offset_map = dict(zip(parties_local, offsets))
    policy_df = policy_df.assign(level_offset=policy_df.apply(
        lambda r: r["level"] + offset_map[r["party"]], axis=1))

    policy_df["symbol"] = policy_df["level"].apply(
        lambda v: 'x' if pd.isna(v) else 'circle'
    )

    fig = px.scatter(
        policy_df,
        x="level_offset",
        y="category",
        color="party",
        symbol="symbol",
        symbol_map={'circle':'circle','x':'x'},
        hover_data=["description"],
        color_discrete_map=PARTY_COLORS,
        height=700,
    )
    fig.update_traces(marker_size=16)
    # Make 'X' markers bigger & grey
    fig.update_traces(selector=dict(symbol='x'),
                      marker_size=18,
                      marker_color="#BBBBBB")
    fig.update_xaxes(
        range=[0.5, 3.5],
        tickvals=[1, 2, 3],
        ticktext=["공약없음", "정책명시", "정책강화"]
    )
    fig.update_layout(title=title, yaxis_title="", xaxis_title="정책 강도")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------#
# 3. Layout
# ---------------------------------------------------------------------#
st.markdown("<h1 style='text-align:center;'>2025 대선 기후 정책 종합 분석</h1>",
            unsafe_allow_html=True)

# Top‑level tabs
TABS = st.tabs([
    "⚡ 에너지믹스 후보 비교",          # index 0
    "⚡ 에너지믹스 (기준·목표·선택)",  # index 1
    "🌡 온도경로",                    # 2
    "📊 정책-대선",                  # 3
    "📊 정책-지난총선",              # 4
    "ℹ️ 설명"                        # 5
])

# ────────────────────────────────────────────────────────────────────#
# Tab 0 : Energy mix – all candidates side‑by‑side
# ────────────────────────────────────────────────────────────────────#
with TABS[0]:
    st.subheader("에너지 믹스 – 후보/정당 간 비교")

    # Recompute scenario list locally
    scenarios = energy_df["시나리오"].unique().tolist() if not energy_df.empty else []
    base_scn   = "정부(실적)-2018"
    target_scn = "정부(계획)-2040"

    if energy_df.empty:
        st.info("에너지 믹스 시트를 찾지 못했습니다.")
    else:
        # 후보 시나리오 = everything except base & target
        candidate_scn = [s for s in scenarios if s not in [base_scn, target_scn]]
        if not candidate_scn:
            st.warning("후보 시나리오가 없습니다.")
        else:
            # determine which numeric column to use
            if "비중" in energy_df.columns:
                value_col = "비중"
            else:
                numeric_cols = energy_df.select_dtypes("number").columns
                value_col = next(col for col in numeric_cols if col not in ["에너지원"])
            fig_all = px.bar(
                energy_df.query("시나리오 in @candidate_scn"),
                y="시나리오",
                x=value_col,
                color="에너지원",
                orientation="h",
                color_discrete_map=ENERGY_COLORS,
                category_orders={
                    "에너지원": ["석탄","LNG","원자력","재생에너지","기타"],
                    "시나리오": candidate_scn  # keep order as in data
                },
                barmode="stack",
                height=500
            )
            if value_col == "비중":
                fig_all.update_xaxes(range=[0, 100], title="비중 (%)")
            else:
                fig_all.update_xaxes(title=value_col)
            fig_all.update_layout(legend_title="에너지원")
            st.plotly_chart(fig_all, use_container_width=True)


# ────────────────────────────────────────────────────────────────────#
# Tab 1 : Energy mix (기준·목표·선택)
# ────────────────────────────────────────────────────────────────────#
with TABS[1]:
    st.subheader("에너지 믹스 – 2018 vs 2035 vs 선택 시나리오")

    if energy_df.empty:
        st.info("에너지 믹스 시트를 찾지 못했습니다.")
    else:
        scenarios = energy_df["시나리오"].unique().tolist()
        base_scn   = "정부(실적)-2018"
        target_scn = "정부(계획)-2040"
        if base_scn not in scenarios or target_scn not in scenarios:
            st.error("에너지 믹스 시트에 기준·목표 시나리오 이름이 없습니다. "
                     "현재 시나리오 목록: " + ", ".join(scenarios))
            st.stop()

        selectable = [s for s in scenarios if s not in [base_scn, target_scn]]

        if not selectable:
            st.error("선택할 추가 시나리오가 없습니다. 시트에 정당/시나리오를 더 추가해 주세요.")
            st.stop()

        sel_scn = st.selectbox("정당/시나리오 선택", selectable)

        def stacked_mix(scn, col):
            df_plot = energy_df.query("시나리오 == @scn")

            if "비중" in df_plot.columns:
                value_col = "비중"
                y_label   = "비중 (%)"
            else:
                # pick the first numeric column that is not '에너지원' or '시나리오'
                numeric_cols = df_plot.select_dtypes("number").columns
                value_col = next(col for col in numeric_cols if col not in ["에너지원"])
                y_label   = value_col

            # create a single‑column label so the scenario shows as one bar
            df_plot = df_plot.assign(scn_label=scn)

            fig = px.bar(
                df_plot,
                x="scn_label",           # one bar per scenario
                y=value_col,
                color="에너지원",
                color_discrete_map=ENERGY_COLORS,
                category_orders={"에너지원": ["석탄","LNG","원자력","재생에너지","기타"]},
                barmode="stack",
                height=450
            )
            if value_col == "비중":
                fig.update_yaxes(range=[0, 100])
            fig.update_xaxes(title="")
            fig.update_yaxes(title=y_label)
            fig.update_layout(showlegend=True, legend_title="에너지원", title=scn)
            col.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        stacked_mix(base_scn,   c1)
        stacked_mix(target_scn, c2)
        stacked_mix(sel_scn,    c3)

#
# Tab 2 : Temperature pathways
# ────────────────────────────────────────────────────────────────────#
with TABS[2]:
    st.subheader("온도 경로 분석")

    if temp_df.empty:
        st.info("온도경로 시트를 찾지 못했습니다.")
    else:
        paths_all = temp_df["경로"].unique()
        ref_paths = [p for p in paths_all if "°C" in p]
        party_paths = [p for p in paths_all if p not in ref_paths]

        sel_paths = st.multiselect("정당 경로 선택", party_paths,
                                   default=party_paths)  # 모든 경로 기본 선택
        plot_df = temp_df.query("경로 in @ref_paths or 경로 in @sel_paths")

        line_dash = plot_df["경로"].apply(
            lambda x: "dash" if x in ref_paths else "solid")

        fig = px.line(
            plot_df, x="연도", y="배출량", color="경로",
            line_dash=line_dash,
            color_discrete_map={**cmap(sel_paths),
                                **{p: "#444444" for p in ref_paths}},
            labels={"배출량": "배출량 (백만톤 CO₂eq)"}, height=600
        )
        st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────────────────────────#
# Tab 3 : Policy – current election
# ────────────────────────────────────────────────────────────────────#
with TABS[3]:
    st.subheader("정책 비교 – 2025 대선")
    df_policy_current = load_policy_df(["policy", "정책"])
    policy_scatter(df_policy_current, "2025 대선 정책 강도 분포")

# ────────────────────────────────────────────────────────────────────#
# Tab 4 : Policy – previous general election
# ────────────────────────────────────────────────────────────────────#
with TABS[4]:
    st.subheader("정책 비교 – 지난 총선")
    df_policy_gen = load_policy_df(["총선", "policy_gen"])
    policy_scatter(df_policy_gen, "지난 총선 정책 강도 분포")

# ────────────────────────────────────────────────────────────────────#
# Tab 5 : Explanation
# ────────────────────────────────────────────────────────────────────#
with TABS[5]:
    st.subheader("대시보드 설명서")
    
    st.markdown("""
**본 대시보드 시각화 의도**  
> *정확한 수치 예측보다는 ‘기후 투표’ 관점에서 **각 정당이 상상하는 전원(에너지원) 구성과 온실가스 배출경로를 직관적으로 보여주기** 위한 자료입니다. 5월 23일 토론회 이후 추가 데이터 반영 예정입니다.*

---

### 주요 가정 (총 발전량·연도)
| 구분 | 총 발전량 (TWh) | 출처·메모 |
|------|----------------|-----------|
| 2018년 정부 실적 | 540 | 한국에너지공단·한전 통계 기반 |
| 2038년 정부 계획 | 703.5 | 제11차 전력수급기본계획(실무안) |
| 2040·2035년 예측 | 700 | 모든 시나리오 동일, 연 1 % 증가 가정 |

---

### 에너지원 개념·장단점
""" , unsafe_allow_html=True)


    st.markdown("""
| 에너지원 | 장점 | 단점 |
|----------|------|------|
| **석탄** | 발전 단가가 낮고 기 설치 설비 활용 가능 | 탄소·미세먼지 배출이 가장 심각 |
| **LNG** | 출력 조절이 용이해 신재생 변동성 보완 | 여전히 화석연료·메탄 누출 우려 |
| **원자력** | 무탄소·베이스로드 역할, 단가 안정 | 안전성·폐기물·건설 기간/비용 |
| **재생에너지** | 무탄소·분산형, 연료비 없음 | 간헐성·부지 한계·계통 보강 비용 |
| **기타**<br>(수력·바이오 등) | 보조전원·저탄소 대안 | 자원 제약, 환경·원료 지속가능성 |
""", unsafe_allow_html=True)

    # --------------------------- NEW SECTIONS ---------------------------
    st.markdown("""
---

## 온실경로 설명
1. **2018년 기준 배출량** – 모든 시나리오는 2018년 총배출 727.6 MtCO₂eq에서 출발  
2. **2030년 NDC 목표** – 2018년 대비 **40 % 감축**(436.6 MtCO₂eq) 달성을 공통 가정  
3. **후보별 2040년 에너지 믹스** – 각 후보 공약 기반 발전원별 발전량(TWh) 구성  
4. **국가 공식 배출계수 적용** – 환경부 고시 계수 사용 (석탄 0.8230, LNG 0.3625 kgCO₂/kWh)  
5. **비전력 부문 가정** – 전력 외 부문은 2030 NDC 달성 이후 **변화 없이 유지** *(권영국 후보 제외)*  
6. **권영국 후보 특별 경로** – 2035년 70 % 감축 → 2050 탄소중립(선형 감소)  
7. **온도 경로 비교** – IPCC AR6 1.5 °C / 2 °C / 3 °C 경로를 한국 비례 적용  
8. **2050년 전망** – 권영국 후보 0 MtCO₂eq, 타 후보 281.1 MtCO₂eq (전력만 탄소중립)

---

## 후보별 핵심 가정
### 1. 민주당‑이재명 _(2040 목표, 700 TWh)_
* **에너지 믹스** – 석탄 0 %, LNG 10 %(70 TWh), 원자력 35.2 %(248.3 TWh), 재생 54.5 %(381.7 TWh)
* **핵심 공약** – 2040 석탄 전면 폐쇄·재생에너지 주력·서해안 20 GW 해상풍력 등
* **2040 배출량** 306.5 MtCO₂eq *(전력 25.4 Mt)*
* **2050 전망** 281.1 MtCO₂eq *(2018 대비 61.4 % 감축)*

### 2. 국민의힘‑김문수 _(2040 목표, 700 TWh)_
* **에너지 믹스** – 석탄 10.1 %(70.9), LNG 15 %(105), 원자력 60 %(420), 재생 13.9 %(97.1)
* **핵심 공약** – 원전 60 %(대형6+SMR1), LNG 15 %
* **2040 배출량** 321.1 MtCO₂eq *(전력 41.0 Mt)*
* **2050 전망** 281.1 MtCO₂eq *(61.4 % 감축)*

### 3. 개혁신당‑이준석 _(2040 목표, 700 TWh)_
* **에너지 믹스** – 석탄 10.1 %, LNG 10.6 %, 원자력 35.2 %, 재생 29.2 %, 청정수소/암모니아 6.2 %
* **핵심 기조** – 11차 전기본 준용, 원전 확대 공감
* **2040 배출량** 394.8 MtCO₂eq *(전력 110.7 Mt)*
* **2050 전망** 281.1 MtCO₂eq *(61.4 % 감축)*

### 4. 민주노동당‑권영국 _(2035 목표, 700 TWh)_
* **에너지 믹스** – 석탄 0 %, LNG 10 %, 원자력 0 %, 재생 60 %, 기타(ESS·분산·수소) 30 %
* **핵심 공약** – 2035 탈석탄·2040 탈핵·재생 60 %·70 % 감축
* **2035 배출량** 218.3 MtCO₂eq *(70 % 감축)*
* **2050 전망** 0 MtCO₂eq *(완전 탄소중립)*
""")

# ---------------------------------------------------------------------#
# 4. Sidebar & footer
# ---------------------------------------------------------------------#
st.sidebar.header("ℹ️ 정보")
st.sidebar.write(
    "이 대시보드는 **data/climate_data.xlsx**의 데이터를 사용합니다. "
    "경로 또는 파일 이름이 바뀌면 코드의 `EXCEL_PATH`도 함께 수정해 주세요."
)

st.markdown(
    "<div style='text-align:center; margin-top:3rem; font-size:0.9rem; "
    "color:#666;'>© 2025 기후 정책 분석 대시보드</div>",
    unsafe_allow_html=True
)
