import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------------------------#
# 0. Page configuration & constants
# ---------------------------------------------------------------------#
st.set_page_config(page_title="2025 대선 기후 정책 종합 분석", layout="wide")

BASELINE_PARTY = "2018년 기준"
NDC_PARTY      = "2030 NDC"

# 정당별 대표색 (필요에 따라 추가)
PARTY_COLORS = {
    "국민의 힘":   "#E61E2B",  # 빨강
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
    "석탄":   "#4B5563",
    "LNG":    "#60A5FA",
    "원자력": "#F59E0B",
    "태양광": "#FBBF24",
    "풍력":   "#34D399",
    "수력":   "#3B82F6",
    "바이오": "#A855F7",
    "연료전지": "#10B981",
    "기타":   "#9CA3AF",
    "청정수소/암모니아": "#06B6D4",
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

    # 정당 필터
    all_parties = sorted(policy_df["party"].unique())
    party_filter = st.radio("정당 선택", ["전체"] + all_parties,
                            horizontal=True, key=f"filter_{title}")
    if party_filter != "전체":
        policy_df = policy_df.query("party == @party_filter")

    fig = px.scatter(
        policy_df,
        x="level",
        y="category",
        color="party",
        hover_data=["description"],
        color_discrete_map=PARTY_COLORS,
        height=700,
    )
    fig.update_traces(marker_size=16)
    fig.update_xaxes(range=[-2, 3],
                     tickvals=[-2, -1, 0, 1, 2, 3],
                     ticktext=["완화", "-1", "유지", "강화(약)", "강화(중)", "강화(강)"])
    fig.update_layout(title=title, yaxis_title="", xaxis_title="정책 강도")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------#
# 3. Layout
# ---------------------------------------------------------------------#
st.markdown("<h1 style='text-align:center;'>2025 대선 기후 정책 종합 분석</h1>",
            unsafe_allow_html=True)

# Top‑level tabs
TABS = st.tabs([
    "⚡ 에너지믹스",
    "🌡 온도경로",
    "📊 정책-대선",
    "📊 정책-지난총선",
    "📊 정책-지난대선"
])

# ────────────────────────────────────────────────────────────────────#
# Tab 0 : Energy mix (stacked bars 2018 ‑ 2035 ‑ selected)
# ────────────────────────────────────────────────────────────────────#
with TABS[0]:
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
                barmode="stack",
                height=450
            )
            if value_col == "비중":
                fig.update_yaxes(range=[0, 100])
            fig.update_xaxes(title="")
            fig.update_yaxes(title=y_label)
            fig.update_layout(showlegend=False, title=scn)
            col.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        stacked_mix(base_scn,   c1)
        stacked_mix(target_scn, c2)
        stacked_mix(sel_scn,    c3)

# ────────────────────────────────────────────────────────────────────#
# Tab 1 : Temperature pathways
# ────────────────────────────────────────────────────────────────────#
with TABS[1]:
    st.subheader("온도 경로 분석")

    if temp_df.empty:
        st.info("온도경로 시트를 찾지 못했습니다.")
    else:
        paths_all = temp_df["경로"].unique()
        ref_paths = [p for p in paths_all if "°C" in p]
        party_paths = [p for p in paths_all if p not in ref_paths]

        sel_paths = st.multiselect("정당 경로 선택", party_paths,
                                   default=party_paths[:2] if party_paths else [])
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
# Tab 2 : Policy – current election
# ────────────────────────────────────────────────────────────────────#
with TABS[2]:
    st.subheader("정책 비교 – 2025 대선")
    df_policy_current = load_policy_df(["policy", "정책"])
    policy_scatter(df_policy_current, "2025 대선 정책 강도 분포")

# ────────────────────────────────────────────────────────────────────#
# Tab 3 : Policy – previous general election
# ────────────────────────────────────────────────────────────────────#
with TABS[3]:
    st.subheader("정책 비교 – 지난 총선")
    df_policy_gen = load_policy_df(["총선", "policy_gen"])
    policy_scatter(df_policy_gen, "지난 총선 정책 강도 분포")

# ────────────────────────────────────────────────────────────────────#
# Tab 4 : Policy – previous presidential election
# ────────────────────────────────────────────────────────────────────#
with TABS[4]:
    st.subheader("정책 비교 – 지난 대선")
    df_policy_prev = load_policy_df(["대선", "policy_prev"])
    policy_scatter(df_policy_prev, "지난 대선 정책 강도 분포")

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
    unsafe_allow_html=True,
)