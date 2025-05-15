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
    "국민의 힘":   "#E61E2B",
    "더불어민주당": "#004EA2",
    "사회대전환":   "#8B4513",
    "개혁신당":     "#FF6B6B",
    BASELINE_PARTY: "#999999",
    NDC_PARTY:      "#000000",
}

# ---------------------------------------------------------------------#
# 1. Load Excel
# ---------------------------------------------------------------------#
EXCEL_PATH = Path(__file__).with_suffix("").parent / "climate_data.xlsx"

@st.cache_data
def load_sheets(path: Path) -> dict[str, pd.DataFrame]:
    """Read every sheet in an Excel file into a dict of DataFrames."""
    if not path.exists():
        st.error(f"엑셀 파일 '{path.name}'이(가) 존재하지 않습니다.")
        st.stop()

    xls = pd.ExcelFile(path)
    return {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names}

sheets = load_sheets(EXCEL_PATH)

def find_sheet(keywords: list[str]) -> pd.DataFrame:
    """Return the first sheet whose name contains any keyword."""
    for name, df in sheets.items():
        if any(k in name for k in keywords):
            return df.copy()
    return pd.DataFrame()

# ---------------------------------------------------------------------#
# 2. Data wrangling
# ---------------------------------------------------------------------#
# 2‑1. Emissions ──────────────────────────────────────────────────────
em_raw = find_sheet(["배출"])
if em_raw.empty:
    st.error("❌ '배출'이라는 단어가 포함된 시트를 찾지 못했습니다.")
    st.stop()

if "정당" not in em_raw.columns:           # wide → long
    emissions_df = em_raw.melt(id_vars="부문", var_name="정당", value_name="값")
else:                                       # already long
    emissions_df = em_raw.rename(columns=str).copy()

sectors = [s for s in emissions_df["부문"].unique() if s != "총배출"]
parties  = emissions_df["정당"].unique().tolist()

# 2‑2. Energy mix ─────────────────────────────────────────────────────
en_raw = find_sheet(["에너지믹스"])
if en_raw.empty:
    energy_df = pd.DataFrame()             # 처리 없이 빈 DF
else:
    energy_df = (en_raw if "시나리오" in en_raw.columns
                 else en_raw.melt(id_vars="에너지원",
                                  var_name="시나리오",
                                  value_name="비중"))

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
# 3. Layout
# ---------------------------------------------------------------------#
st.markdown("<h1 style='text-align:center;'>2025 대선 기후 정책 종합 분석</h1>",
            unsafe_allow_html=True)

TABS = st.tabs(["🌍 배출량/감축", "🔍 부문별", "⚡ 에너지믹스", "🌡 온도경로", "📊 정책"])

# ────────────────────────────────────────────────────────────────────#
# Tab 0 : Total emissions & reduction
# ────────────────────────────────────────────────────────────────────#
with TABS[0]:
    st.subheader("온실가스 총배출량 및 감축 목표")

    total_df = (emissions_df[emissions_df["부문"] == "총배출"]
                .pivot(index="정당", columns="부문", values="값")
                .reset_index()[["정당", "총배출"]])

    base_val = total_df.loc[total_df["정당"] == BASELINE_PARTY, "총배출"].values[0]
    total_df["감축률(%)"] = 100 * (1 - total_df["총배출"] / base_val)

    fig = px.bar(
        total_df.sort_values("감축률(%)", ascending=False),
        x="정당", y="총배출",
        color="정당", text="감축률(%)",
        color_discrete_map=cmap(total_df["정당"].tolist()),
        labels={"총배출": "온실가스 총배출량 (백만톤 CO₂eq)"}, height=500,
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────────────────────────#
# Tab 1 : Sectoral emissions
# ────────────────────────────────────────────────────────────────────#
with TABS[1]:
    st.subheader("부문별 온실가스 배출량")
    sel_parties = st.multiselect("비교할 정당", parties, default=parties[:3])
    sel_sector  = st.selectbox("부문 선택", ["전체"] + sectors)

    if sel_sector == "전체":
        plot_df = emissions_df.query("정당 in @sel_parties & 부문 != '총배출'")
        fig = px.bar(
            plot_df, x="정당", y="값", color="부문",
            barmode="group", height=550,
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"값": "배출량 (백만톤 CO₂eq)"}
        )
    else:
        plot_df = emissions_df.query("정당 in @sel_parties & 부문 == @sel_sector")
        fig = px.bar(
            plot_df, x="정당", y="값", color="정당",
            text="값", height=500,
            color_discrete_map=cmap(sel_parties),
            labels={"값": f"{sel_sector} 배출량 (백만톤 CO₂eq)"}
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')

    st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────────────────────────#
# Tab 2 : Energy mix
# ────────────────────────────────────────────────────────────────────#
with TABS[2]:
    st.subheader("에너지 믹스 분석")

    if energy_df.empty:
        st.info("에너지 믹스 시트를 찾지 못했습니다.")
    else:
        scenarios = energy_df["시나리오"].unique().tolist()
        sel_scenario = st.selectbox("시나리오", scenarios)
        scenario_df  = energy_df.query("시나리오 == @sel_scenario")

        # ―― 원형 그래프(도넛)로 고정 ――
        fig = px.pie(
            scenario_df,
            names="에너지원",
            values="비중",
            title=f"{sel_scenario} 에너지 믹스",
            hole=0.3  # 도넛형
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────────────────────────────#
# Tab 3 : Temperature pathways
# ────────────────────────────────────────────────────────────────────#
with TABS[3]:
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
# Tab 4 : Policies
# ────────────────────────────────────────────────────────────────────#
with TABS[4]:
    st.subheader("정책 비교")

    if policy_df.empty:
        st.info("정책 관련 시트를 찾지 못했습니다.")
    else:
        st.dataframe(policy_df, use_container_width=True)

# ---------------------------------------------------------------------#
# 4. Sidebar & footer
# ---------------------------------------------------------------------#
st.sidebar.header("ℹ️ 정보")
st.sidebar.write(
    "이 대시보드는 Excel 파일 **climate_data.xlsx**의 데이터를 사용합니다. "
    "시트 이름이나 구조가 변하면 코드도 함께 수정해 주세요."
)

st.markdown(
    "<div style='text-align:center; margin-top:3rem; font-size:0.9rem; "
    "color:#666;'>© 2025 기후 정책 분석 대시보드</div>",
    unsafe_allow_html=True,
)