import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="2025 대선 기후 정책 종합 분석", layout="wide")

# Apply custom styling
st.markdown("""
<style>
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
    }
    .subtitle {
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Placeholder data - Replace with actual data when available
# Party colors
party_colors = {
    "국민의 힘": "#E61E2B",
    "더불어민주당": "#004EA2",
    "사회대전환": "#8B4513",
    "개혁신당": "#FF6B6B",
    "2018년 기준": "#999999",
    "2030 NDC": "#000000"
}

# Placeholder for emissions data
emissions_data = {
    "2018년 기준": {
        "총배출": 727.6,
        "에너지": 632.4,
        "산업공정": 57.0,
        "농업": 21.0,
        "폐기물": 17.2
    },
    "2030 NDC": {
        "총배출": 436.6,
        "에너지": 334.1,
        "산업공정": 42.0,
        "농업": 19.4,
        "폐기물": 11.0
    },
    "국민의 힘": {
        "총배출": 500.0,
        "에너지": 400.0,
        "산업공정": 45.0,
        "농업": 20.0,
        "폐기물": 15.0
    },
    "더불어민주당": {
        "총배출": 450.0,
        "에너지": 350.0,
        "산업공정": 40.0,
        "농업": 19.0,
        "폐기물": 11.0
    }
}

# Energy mix data
energy_mix = {
    "2023년(현재)": {
        "석탄": 35.0,
        "LNG": 30.0,
        "원자력": 25.0,
        "태양광": 5.0,
        "풍력": 3.0,
        "수력": 2.0
    },
    "2030 NDC": {
        "석탄": 15.0,
        "LNG": 25.0,
        "원자력": 30.0,
        "태양광": 15.0,
        "풍력": 10.0,
        "수력": 5.0
    },
    "국민의 힘": {
        "석탄": 10.0,
        "LNG": 20.0,
        "원자력": 40.0,
        "태양광": 15.0,
        "풍력": 10.0,
        "수력": 5.0
    },
    "더불어민주당": {
        "석탄": 5.0,
        "LNG": 15.0,
        "원자력": 25.0,
        "태양광": 30.0,
        "풍력": 20.0,
        "수력": 5.0
    }
}

# Temperature pathway data
temp_path = {
    "1.5°C 경로": {
        2020: 55.0,
        2025: 45.0,
        2030: 30.0,
        2040: 15.0,
        2050: 0.0
    },
    "2°C 경로": {
        2020: 55.0,
        2025: 47.0,
        2030: 35.0,
        2040: 20.0,
        2050: 5.0
    },
    "3°C 경로": {
        2020: 55.0,
        2025: 50.0,
        2030: 45.0,
        2040: 35.0,
        2050: 25.0
    },
    "국민의 힘": {
        2020: 55.0,
        2025: 48.0,
        2030: 40.0,
        2040: 25.0,
        2050: 10.0
    },
    "더불어민주당": {
        2020: 55.0,
        2025: 46.0,
        2030: 32.0,
        2040: 18.0,
        2050: 5.0
    }
}

# Policy data
policy_data = [
    {
        "category": "거버넌스",
        "policies": {
            "국민의 힘": {"level": 3, "description": "탄소중립녹색성장 위원회 기능 강화, 기후위기특별위원회 상설화, 석탄화력발전소 폐지지역 지원 특별법 제정 및 탄소중립기본법 개정"}
        }
    },
    {
        "category": "배출권거래제",
        "policies": {
            "국민의 힘": {"level": 3, "description": "배출권거래제 유상할당 확대"}
        }
    },
    # More policy data would go here
]

# Derive parties list and sectors from data
emission_parties = [party for party in emissions_data.keys() if party not in ["2018년 기준", "2030 NDC"]]
sectors = ["에너지", "산업공정", "농업", "폐기물"]  # Define sectors that appear in the emissions data

# Calculate total emissions for each party
total_emissions = []
for party, data in emissions_data.items():
    if "총배출" in data:
        reduction_rate = 0
        if party != "2018년 기준" and "총배출" in emissions_data["2018년 기준"]:
            base_value = emissions_data["2018년 기준"]["총배출"]
            if base_value > 0:
                reduction_rate = 100 * (1 - data["총배출"] / base_value)
                
        total_emissions.append({
            "정당": party,
            "총배출량": data["총배출"],
            "감축률(%)": reduction_rate
        })

# Main title
st.markdown("<h1 class='title'>2025 대선 기후 정책 종합 분석</h1>", unsafe_allow_html=True)

# Create tabs
tabs = st.tabs(["🌍 배출량 및 감축 목표", "🔍 부문별 배출량", "⚡ 에너지 믹스 분석", "🌡 온도 경로 분석", "📊 정책 비교"])

# Tab 1: Emissions and Reduction Targets
with tabs[0]:
    st.markdown("<p class='subtitle'>온실가스 배출량 및 감축 목표</p>", unsafe_allow_html=True)
    
    # Sort data: 2018 and NDC first, then parties by reduction rate
    total_df = pd.DataFrame(total_emissions)
    base_ndc = total_df[total_df['정당'].isin(['2018년 기준', '2030 NDC'])]
    parties_df = total_df[~total_df['정당'].isin(['2018년 기준', '2030 NDC'])].sort_values('감축률(%)', ascending=False)
    total_df = pd.concat([base_ndc, parties_df])
    
    # Bar chart for total emissions
    fig = px.bar(
        total_df,
        x='정당',
        y='총배출량',
        color='정당',
        color_discrete_map={party: party_colors.get(party, "#999999") for party in total_df['정당']},
        text='감축률(%)',
        height=500,
        labels={'총배출량': '온실가스 총배출량 (백만톤 CO₂eq)'}
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    
    fig.update_layout(
        title='정당별 온실가스 총배출량 목표',
        xaxis_title='',
        yaxis_title='백만톤 CO₂eq',
    )
    
    # Add 2030 NDC target line
    if '2030 NDC' in emissions_data:
        ndc_value = emissions_data['2030 NDC'].get('총배출', 0)
        if ndc_value > 0:
            fig.add_shape(
                type="line",
                x0=-0.5,
                y0=ndc_value,
                x1=len(total_df) - 0.5,
                y1=ndc_value,
                line=dict(color="red", width=2, dash="dash"),
            )
            fig.add_annotation(
                x=len(total_df) - 1,
                y=ndc_value,
                text="2030 NDC 목표",
                showarrow=False,
                yshift=10,
                font=dict(size=12, color="red")
            )
    
    st.plotly_chart(fig, use_container_width=True)

# Tab 2: Sectoral Emissions
with tabs[1]:
    st.markdown("<p class='subtitle'>부문별 온실가스 배출량</p>", unsafe_allow_html=True)
    
    # Party selection
    selected_emission_parties = st.multiselect(
        "비교할 정당 선택",
        options=['2018년 기준', '2030 NDC'] + emission_parties,
        default=['2018년 기준', '2030 NDC'] + emission_parties[:2] if len(emission_parties) > 2 else ['2018년 기준', '2030 NDC'] + emission_parties
    )
    
    # Sector selection
    selected_sector = st.selectbox("부문 선택", ["전체"] + sectors)
    
    if selected_sector == "전체":
        # Show all sectors
        for sector in sectors:
            st.markdown(f"#### {sector}")
            
            # Data preparation
            sector_data = []
            base_value = emissions_data.get('2018년 기준', {}).get(sector, 0)
            
            for party in selected_emission_parties:
                if party in emissions_data and sector in emissions_data[party]:
                    value = emissions_data[party][sector]
                    reduction = 0
                    if base_value > 0 and isinstance(value, (int, float)):
                        reduction = 100 * (1 - value / base_value)
                        
                    sector_data.append({
                        '정당': party,
                        '배출량': value if isinstance(value, (int, float)) else 0,
                        '감축률(%)': reduction
                    })
            
            if sector_data:
                sector_df = pd.DataFrame(sector_data)
                
                # Bar chart
                fig = px.bar(
                    sector_df,
                    x='정당',
                    y='배출량',
                    color='정당',
                    color_discrete_map={party: party_colors.get(party, "#999999") for party in sector_df['정당']},
                    text='감축률(%)',
                    height=400,
                    labels={'배출량': f'{sector} 배출량 (백만톤 CO₂eq)'}
                )
                
                fig.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside'
                )
                
                fig.update_layout(
                    xaxis_title='',
                    yaxis_title='백만톤 CO₂eq',
                )
                
                st.plotly_chart(fig, use_container_width=True)
    else:
        # Show only selected sector
        st.markdown(f"#### {selected_sector} 부문 상세 분석")
        
        # Data preparation
        sector_data = []
        base_value = emissions_data.get('2018년 기준', {}).get(selected_sector, 0)
        
        for party in selected_emission_parties:
            if party in emissions_data and selected_sector in emissions_data[party]:
                value = emissions_data[party][selected_sector]
                reduction = 0
                if base_value > 0 and isinstance(value, (int, float)):
                    reduction = 100 * (1 - value / base_value)
                    
                sector_data.append({
                    '정당': party,
                    '배출량': value if isinstance(value, (int, float)) else 0,
                    '감축률(%)': reduction
                })
        
        if sector_data:
            sector_df = pd.DataFrame(sector_data)
            
            # Bar chart
            fig = px.bar(
                sector_df,
                x='정당',
                y='배출량',
                color='정당',
                color_discrete_map={party: party_colors.get(party, "#999999") for party in sector_df['정당']},
                text='감축률(%)',
                height=500,
                labels={'배출량': f'{selected_sector} 배출량 (백만톤 CO₂eq)'}
            )
            
            fig.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
            
            fig.update_layout(
                title=f'{selected_sector} 부문 정당별 배출량 목표',
                xaxis_title='',
                yaxis_title='백만톤 CO₂eq',
            )
            
            # Add 2030 NDC target line
            if '2030 NDC' in emissions_data and selected_sector in emissions_data['2030 NDC']:
                ndc_value = emissions_data['2030 NDC'][selected_sector]
                if isinstance(ndc_value, (int, float)) and ndc_value > 0:
                    fig.add_shape(
                        type="line",
                        x0=-0.5,
                        y0=ndc_value,
                        x1=len(sector_df) - 0.5,
                        y1=ndc_value,
                        line=dict(color="red", width=2, dash="dash"),
                    )
                    fig.add_annotation(
                        x=len(sector_df) - 1,
                        y=ndc_value,
                        text=f"2030 NDC {selected_sector} 목표",
                        showarrow=False,
                        yshift=10,
                        font=dict(size=12, color="red")
                    )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Waterfall chart (reduction flow from base year)
            st.markdown("##### 2018년 기준부터 감축 흐름")
            
            # Select parties (max 3)
            display_parties = sector_df['정당'].tolist()
            if '2018년 기준' in display_parties:
                display_parties.remove('2018년 기준')
            
            if len(display_parties) > 3:
                display_parties = display_parties[:3]
            
            for party in display_parties:
                if party == '2018년 기준':
                    continue
                    
                party_value = sector_df[sector_df['정당'] == party]['배출량'].values[0]
                base_value = sector_df[sector_df['정당'] == '2018년 기준']['배출량'].values[0] if '2018년 기준' in sector_df['정당'].tolist() else 0
                
                if base_value > 0 and isinstance(party_value, (int, float)):
                    reduction = base_value - party_value
                    
                    # Waterfall chart data
                    waterfall_data = [
                        {'단계': '2018년 기준', '배출량': base_value, '변화': 0, '타입': 'base'},
                        {'단계': f'{party} 감축', '배출량': -reduction, '변화': -reduction, '타입': 'reduction'},
                        {'단계': f'{party} 목표', '배출량': party_value, '변화': 0, '타입': 'total'}
                    ]
                    
                    waterfall_df = pd.DataFrame(waterfall_data)
                    
                    # Waterfall chart
                    fig = go.Figure(go.Waterfall(
                        name="20",
                        orientation="v",
                        measure=["absolute", "relative", "total"],
                        x=waterfall_df['단계'],
                        textposition="outside",
                        text=waterfall_df['배출량'].apply(lambda x: f"{abs(x):.1f}"),
                        y=waterfall_df['배출량'],
                        connector={"line": {"color": "rgb(63, 63, 63)"}},
                        decreasing={"marker": {"color": "#36D399"}},
                        increasing={"marker": {"color": "#F87272"}},
                        totals={"marker": {"color": party_colors.get(party, "#999999")}}
                    ))
                    
                    fig.update_layout(
                        title=f"{party}의 {selected_sector} 부문 감축 목표 (2018년 대비)",
                        height=400,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown("### 전체 데이터 테이블")
    
    # Data preparation
    table_data = []
    
    for sector in sectors + ['총배출']:
        row = {'부문': sector}
        for party in emissions_data.keys():
            if sector in emissions_data[party]:
                value = emissions_data[party][sector]
                row[party] = value
        table_data.append(row)
    
    table_df = pd.DataFrame(table_data)
    
    # Color mapping function based on reduction rate
    def color_negative_red(val):
        """
        Color positive values red, negative values green
        """
        if isinstance(val, (int, float)):
            try:
                base_value = table_df.loc[table_df['부문'] == table_df['부문'].iloc[table_df.index.get_loc(val.name)], '2018년 기준'].values[0] \
                    if '2018년 기준' in table_df.columns else 0
                    
                if base_value > 0:
                    # Calculate reduction rate
                    reduction = 100 * (1 - val / base_value)
                    
                    # Determine color (more reduction = more green)
                    if reduction <= 0:
                        color = 'red'
                    elif reduction < 20:
                        color = 'orange'
                    elif reduction < 40:
                        color = '#FFEC19'  # yellow
                    elif reduction < 60:
                        color = 'lightgreen'
                    else:
                        color = 'green'
                    
                    return f'background-color: {color}; color: black;'
            except (IndexError, ValueError):
                pass
        return ''
    
    # Apply style (exclude 2018 baseline and 2030 NDC)
    style_df = table_df.style.applymap(
        color_negative_red, 
        subset=pd.IndexSlice[:, [col for col in table_df.columns if col not in ['부문', '2018년 기준', '2030 NDC']]]
    )
    
    # Display table
    st.dataframe(style_df)
    
    # CSV download button
    csv = table_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="데이터 CSV 다운로드",
        data=csv,
        file_name="climate_policy_emissions.csv",
        mime="text/csv",
    )

# Tab 3: Energy Mix Analysis
with tabs[2]:
    st.markdown("<p class='subtitle'>에너지 믹스 분석</p>", unsafe_allow_html=True)
    
    # Scenario selection
    energy_scenarios = list(energy_mix.keys())
    selected_scenario = st.selectbox("시나리오 선택", energy_scenarios)
    
    # Chart type selection
    chart_type = st.radio("차트 유형", ["파이 차트", "바 차트", "테이블"], horizontal=True)
    
    # Selected scenario data
    if selected_scenario in energy_mix:
        scenario_data = energy_mix[selected_scenario]
        
        # Data preparation
        energy_df = pd.DataFrame({
            '에너지원': list(scenario_data.keys()),
            '비중(%)': list(scenario_data.values())
        })
        
        # Energy source color mapping
        energy_colors = {
            '석탄': '#1e1e1e',
            'LNG': '#4682B4',
            '원자력': '#FF6347',
            '태양광': '#FFD700',
            '풍력': '#32CD32',
            '수력': '#00BFFF',
            '바이오': '#8B4513',
            '연료전지': '#9370DB',
            '기타 재생': '#66CDAA',
            '기타': '#808080'
        }
        
        # Display based on chart type
        if chart_type == "파이 차트":
            fig = px.pie(
                energy_df, 
                values='비중(%)', 
                names='에너지원',
                title=f"{selected_scenario} 에너지 믹스",
                color='에너지원',
                color_discrete_map={src: energy_colors.get(src, '#999999') for src in energy_df['에너지원']},
                hover_data=['비중(%)'],
                labels={'비중(%)': '비중'}
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )
            
            fig.update_layout(
                height=500,
                margin=dict(l=20, r=20, t=50, b=20),
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "바 차트":
            # Bar chart
            fig = px.bar(
                energy_df, 
                x='에너지원', 
                y='비중(%)',
                title=f"{selected_scenario} 에너지 믹스",
                color='에너지원',
                color_discrete_map={src: energy_colors.get(src, '#999999') for src in energy_df['에너지원']},
                text='비중(%)'
            )
            
            fig.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
            
            fig.update_layout(
                height=500,
                xaxis_title="",
                yaxis_title="비중(%)",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:  # Table
            # Sort and format
            energy_df = energy_df.sort_values('비중(%)', ascending=False)
            energy_df['비중(%)'] = energy_df['비중(%)'].apply(lambda x: f"{x:.1f}%")
            
            # Display table
            st.markdown(f"#### {selected_scenario} 에너지 믹스")
            st.dataframe(energy_df, use_container_width=True)
    
    # Compare all scenarios
    st.markdown("### 정당별 에너지 믹스 비교")
    
    # Energy source selection
    energy_sources = set()
    for scenario in energy_mix.values():
        energy_sources.update(scenario.keys())
    energy_sources = sorted(list(energy_sources))
    
    selected_source = st.selectbox("에너지원 선택", ["전체"] + energy_sources)
    
    if selected_source == "전체":
        # Compare all scenarios and all energy sources
        compare_data = []
        
        for scenario, sources in energy_mix.items():
            for source, value in sources.items():
                compare_data.append({
                    '시나리오': scenario,
                    '에너지원': source,
                    '비중(%)': value
                })
        
        compare_df = pd.DataFrame(compare_data)
        
        # Stacked bar chart
        fig = px.bar(
            compare_df,
            x='시나리오',
            y='비중(%)',
            color='에너지원',
            color_discrete_map={src: energy_colors.get(src, '#999999') for src in energy_sources},
            title="시나리오별 에너지 믹스 비교",
            text='비중(%)'
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='inside'
        )
        
        fig.update_layout(
            height=600,
            xaxis_title="",
            yaxis_title="비중(%)",
            yaxis=dict(range=[0, 105]),  # Add some margin
            barmode='stack'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison table
        pivot_df = pd.pivot_table(
            compare_df, 
            values='비중(%)', 
            index='에너지원', 
            columns='시나리오', 
            aggfunc='sum'
        ).reset_index()
        
        # Sort data
        try:
            pivot_df = pivot_df.sort_values('2023년(현재)', ascending=False)
        except:
            pass
            
        st.dataframe(pivot_df, use_container_width=True)
        
    else:
        # Compare only selected energy source
        source_data = []
        
        for scenario, sources in energy_mix.items():
            if selected_source in sources:
                source_data.append({
                    '시나리오': scenario,
                    '비중(%)': sources[selected_source]
                })
            else:
                source_data.append({
                    '시나리오': scenario,
                    '비중(%)': 0
                })
        
        source_df = pd.DataFrame(source_data)
        
        # Sort: current, NDC, parties
        sort_order = ['2023년(현재)', '2030 NDC']
        source_df['sort_key'] = source_df['시나리오'].apply(lambda x: 
                                                        sort_order.index(x) if x in sort_order else len(sort_order))
        source_df = source_df.sort_values('sort_key').drop('sort_key', axis=1)
        
        # Bar chart
        fig = px.bar(
            source_df,
            x='시나리오',
            y='비중(%)',
            title=f"{selected_source} 비중 비교",
            color='시나리오',
            text='비중(%)'
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="",
            yaxis_title=f"{selected_source} 비중(%)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    # Renewable energy comparison
    st.markdown("### 재생에너지 비중 비교")
    
    # Define renewable energy sources
    renewable_sources = ['태양광', '풍력', '수력', '바이오', '연료전지', '기타 재생']
    
    # Calculate renewable energy percentage
    renewable_data = []
    
    for scenario, sources in energy_mix.items():
        renewable_total = sum(sources.get(src, 0) for src in renewable_sources)
        renewable_data.append({
            '시나리오': scenario,
            '재생에너지 비중(%)': renewable_total
        })
    
    renewable_df = pd.DataFrame(renewable_data)
    
    # Sort: current, NDC, parties
    sort_order = ['2023년(현재)', '2030 NDC']
    renewable_df['sort_key'] = renewable_df['시나리오'].apply(lambda x: 
                                                        sort_order.index(x) if x in sort_order else len(sort_order))
    renewable_df = renewable_df.sort_values('sort_key').drop('sort_key', axis=1)
    
    # Bar chart
    fig = px.bar(
        renewable_df,
        x='시나리오',
        y='재생에너지 비중(%)',
        title="재생에너지 총 비중 비교",
        color='시나리오',
        text='재생에너지 비중(%)'
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="",
        yaxis_title="재생에너지 비중(%)",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Fossil vs. clean energy comparison
    st.markdown("### 화석 연료 vs 청정 에너지 비교")
    
    # Define fossil fuels
    fossil_sources = ['석탄', 'LNG', '석유']
    clean_sources = ['원자력'] + renewable_sources
    
    # Calculate fossil/clean energy percentages
    comparison_data = []
    
    for scenario, sources in energy_mix.items():
        fossil_total = sum(sources.get(src, 0) for src in fossil_sources)
        clean_total = sum(sources.get(src, 0) for src in clean_sources)
        
        comparison_data.append({
            '시나리오': scenario,
            '에너지 유형': '화석 연료',
            '비중(%)': fossil_total
        })
        
        comparison_data.append({
            '시나리오': scenario,
            '에너지 유형': '청정 에너지',
            '비중(%)': clean_total
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Sort: current, NDC, parties
    sort_order = ['2023년(현재)', '2030 NDC']
    comparison_df['sort_key'] = comparison_df['시나리오'].apply(lambda x: 
                                                        sort_order.index(x) if x in sort_order else len(sort_order))
    comparison_df = comparison_df.sort_values('sort_key').drop('sort_key', axis=1)
    
    # Stacked bar chart
    fig = px.bar(
        comparison_df,
        x='시나리오',
        y='비중(%)',
        color='에너지 유형',
        color_discrete_map={
            '화석 연료': '#1e1e1e',
            '청정 에너지': '#32CD32'
        },
        title="화석 연료 vs 청정 에너지 비중 비교",
        text='비중(%)'
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='inside'
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="",
        yaxis_title="비중(%)",
        yaxis=dict(range=[0, 105]),  # Add some margin
        barmode='stack'
    )
    
    st.plotly_chart(fig, use_container_width=True) 

# Tab 4: Temperature Pathway Analysis
with tabs[3]:
    st.markdown("<p class='subtitle'>온도 경로 분석</p>", unsafe_allow_html=True)
    
    # Reference temperature pathways
    reference_paths = ['1.5°C 경로', '2°C 경로', '3°C 경로']
    reference_colors = {
        '1.5°C 경로': '#32CD32',  # green
        '2°C 경로': '#FFA500',    # orange
        '3°C 경로': '#FF0000'     # red
    }
    
    # Party pathways (excluding reference pathways)
    party_paths = [p for p in temp_path.keys() if p not in reference_paths]
    
    # Party selection
    selected_parties = st.multiselect("정당 선택", party_paths, default=party_paths[:2] if len(party_paths) > 1 else party_paths)
    
    # Temperature pathway chart
    st.markdown("### 온실가스 배출 경로 비교")
    
    # Data preparation
    line_data = []
    
    # Reference pathway data
    for path in reference_paths:
        if path in temp_path:
            for year, value in temp_path[path].items():
                line_data.append({
                    '경로': path,
                    '연도': year,
                    '배출량': value,
                    '경로 유형': 'reference'
                })
    
    # Party pathway data
    for path in selected_parties:
        if path in temp_path:
            for year, value in temp_path[path].items():
                line_data.append({
                    '경로': path,
                    '연도': year,
                    '배출량': value,
                    '경로 유형': 'party'
                })
    
    if line_data:
        line_df = pd.DataFrame(line_data)
        
        # Line chart
        fig = px.line(
            line_df,
            x='연도',
            y='배출량',
            color='경로',
            title="온실가스 배출 경로 비교",
            labels={'배출량': '온실가스 배출량 (백만톤 CO₂eq)'},
            color_discrete_map={
                **reference_colors,
                **{party: party_colors.get(party, "#999999") for party in selected_parties}
            },
            line_dash='경로 유형',
            line_dash_map={'reference': 'dash', 'party': 'solid'}
        )
        
        fig.update_layout(
            height=600,
            xaxis_title="연도",
            yaxis_title="배출량 (백만톤 CO₂eq)",
            xaxis=dict(
                tickmode='array',
                tickvals=[2020, 2025, 2030, 2040, 2050]
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create comparison tables
        st.markdown("### 주요 연도별 배출량 비교")
        
        pivot_df = pd.pivot_table(
            line_df,
            values='배출량',
            index='경로',
            columns='연도',
            aggfunc='first'
        ).reset_index()
        
        # Custom sort order
        reference_order = {path: i for i, path in enumerate(reference_paths)}
        pivot_df['sort_key'] = pivot_df['경로'].apply(lambda x: reference_order.get(x, 999))
        pivot_df = pivot_df.sort_values('sort_key').drop('sort_key', axis=1)
        
        st.dataframe(pivot_df, use_container_width=True)
        
        # Calculate implied temperature
        st.markdown("### 2050년 기준 예상 온도 경로")
        
        # Very simplified temperature assessment
        target_year = 2050
        temp_assessment = []
        
        for path in selected_parties:
            if path in temp_path and target_year in temp_path[path]:
                party_value = temp_path[path][target_year]
                
                # Simple mapping based on 2050 emissions values
                # These thresholds should be adjusted based on actual science
                if party_value <= temp_path['1.5°C 경로'].get(target_year, 0) * 1.2:
                    implied_temp = "1.5°C 경로에 근접"
                    color = "#32CD32"  # green
                elif party_value <= temp_path['2°C 경로'].get(target_year, 0) * 1.2:
                    implied_temp = "2°C 경로에 근접"
                    color = "#FFA500"  # orange
                else:
                    implied_temp = "3°C 이상 경로"
                    color = "#FF0000"  # red
                
                temp_assessment.append({
                    "정당": path,
                    "2050년 배출량": party_value,
                    "예상 온도 경로": implied_temp,
                    "color": color
                })
        
        if temp_assessment:
            assessment_df = pd.DataFrame(temp_assessment)
            
            for idx, row in assessment_df.iterrows():
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; border-radius: 5px; background-color: rgba(0,0,0,0.05);">
                    <div style="width: 20px; height: 20px; background-color: {row['color']}; margin-right: 10px; border-radius: 50%;"></div>
                    <div style="flex: 1;">
                        <strong>{row['정당']}</strong>: 2050년 배출량 {row['2050년 배출량']} 백만톤 - {row['예상 온도 경로']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Compare with global reduction requirements
        st.markdown("### 글로벌 감축 요구사항 비교")
        st.write("""
        IPCC에 따르면, 지구 온도 상승을 1.5°C 이내로 제한하기 위해서는 2050년까지 넷제로(net-zero) 배출을 달성해야 합니다.
        2°C 이내 제한을 위해서는 2070년까지 넷제로를 달성해야 합니다.
        """)
        
        # NDC compliance check
        st.markdown("### 현행 NDC와의 정합성")
        
        if '2030 NDC' in emissions_data and '총배출' in emissions_data['2030 NDC']:
            ndc_target = emissions_data['2030 NDC']['총배출']
            
            st.write(f"한국의 2030 NDC 목표는 {ndc_target} 백만톤 CO₂eq입니다.")
            
            ndc_compliance = []
            
            for path in selected_parties:
                if path in temp_path and 2030 in temp_path[path]:
                    party_2030 = temp_path[path][2030]
                    difference = party_2030 - ndc_target
                    difference_percent = (difference / ndc_target) * 100 if ndc_target > 0 else 0
                    
                    if difference <= 0:
                        assessment = "NDC 목표 달성"
                        color = "green"
                    elif difference_percent <= 10:
                        assessment = "NDC 목표에 근접"
                        color = "orange"
                    else:
                        assessment = "NDC 목표와 상당한 차이"
                        color = "red"
                    
                    ndc_compliance.append({
                        "정당": path,
                        "2030년 배출량": party_2030,
                        "NDC 차이": difference,
                        "차이(%)": difference_percent,
                        "평가": assessment,
                        "color": color
                    })
            
            if ndc_compliance:
                compliance_df = pd.DataFrame(ndc_compliance)
                
                for idx, row in compliance_df.iterrows():
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 10px; border-radius: 5px; background-color: rgba(0,0,0,0.05);">
                        <div style="width: 20px; height: 20px; background-color: {row['color']}; margin-right: 10px; border-radius: 50%;"></div>
                        <div style="flex: 1;">
                            <strong>{row['정당']}</strong>: 2030년 배출량 {row['2030년 배출량']} 백만톤 - 
                            NDC 대비 {row['차이']:.1f} 백만톤 ({row['차이(%)']:.1f}%) 차이 - {row['평가']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True) 

# Tab 5: Policy Comparison
with tabs[4]:
    st.markdown("<p class='subtitle'>정책 비교</p>", unsafe_allow_html=True)
    
    # Level labels
    level_labels = {
        -2: "완화",
        -1: "소폭 완화",
        0: "유지",
        1: "강화(약)",
        2: "강화(중)",
        3: "강화(강)"
    }
    
    # Party selection
    selected_policy_parties = st.multiselect(
        "정당 선택",
        ["국민의 힘", "더불어민주당", "사회대전환", "개혁신당"],
        default=["국민의 힘", "더불어민주당", "사회대전환"] if "사회대전환" in [p.get("policies", {}).keys() for p in policy_data] else ["국민의 힘", "더불어민주당"]
    )
    
    # Policy-by-policy comparison
    for policy in policy_data:
        st.subheader(policy["category"])
        
        # Filter selected parties
        relevant_parties = {k: v for k, v in policy["policies"].items() if k in selected_policy_parties}
        
        if relevant_parties:
            # Chart data preparation
            fig = go.Figure()
            
            for party, data in relevant_parties.items():
                fig.add_trace(go.Scatter(
                    x=[data["level"]],
                    y=[0],
                    mode='markers+text',
                    name=party,
                    marker=dict(
                        size=20,
                        color=party_colors.get(party, "#999999")
                    ),
                    text=[party],
                    textposition="top center",
                    hoverinfo='text',
                    hovertext=f"{party}: {data['description']}"
                ))
            
            fig.update_layout(
                showlegend=False,
                xaxis=dict(
                    range=[-2.5, 3.5],
                    ticktext=list(level_labels.values()),
                    tickvals=list(level_labels.keys()),
                    title="정책 강도"
                ),
                yaxis=dict(
                    range=[-0.5, 0.5],
                    showticklabels=False,
                    showgrid=False
                ),
                height=200,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Policy details
        with st.expander(f"{policy['category']} 정책 세부 내용"):
            for party, data in relevant_parties.items():
                st.write(f"**{party}** ({level_labels[data['level']]})")
                st.write(f"- {data['description']}")
                st.write("")
    
    # Party-by-party analysis
    st.header("정당별 정책 현황")
    
    # Party selection
    selected_detail_party = st.selectbox("정당 선택", selected_policy_parties)
    
    # Collect all policies for selected party
    party_policies = []
    for policy in policy_data:
        if selected_detail_party in policy["policies"]:
            party_policies.append({
                "category": policy["category"],
                "level": policy["policies"][selected_detail_party]["level"],
                "description": policy["policies"][selected_detail_party]["description"]
            })
    
    # Policy distribution chart
    if party_policies:
        df = pd.DataFrame(party_policies)
        
        # Bar chart
        fig = px.bar(df, x='category', y='level', 
                    title=f"{selected_detail_party} 정책 강도 분포",
                    color='level',
                    color_continuous_scale='RdYlGn',
                    hover_data=['description'])
        
        fig.update_layout(
            yaxis=dict(
                ticktext=list(level_labels.values()),
                tickvals=list(level_labels.keys()),
                title="정책 강도"
            ),
            xaxis_title="정책 분야",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Policy details table
        st.subheader("정책 상세 내용")
        for i, policy in df.iterrows():
            st.markdown(f"#### {policy['category']}")
            st.markdown(f"**강도**: {level_labels[policy['level']]}")
            st.markdown(f"**내용**: {policy['description']}")
            st.markdown("---")
    
    # Overall policy intensity distribution
    st.header("전체 정책 강도 분포 분석")
    
    # Prepare all data
    all_policies = []
    for policy in policy_data:
        for party, data in policy["policies"].items():
            if party in selected_policy_parties:
                all_policies.append({
                    "category": policy["category"],
                    "party": party,
                    "level": data["level"],
                    "description": data["description"]
                })
    
    df_all = pd.DataFrame(all_policies)
    
    if not df_all.empty:
        # Heatmap
        try:
            pivot_df = df_all.pivot_table(index='party', columns='category', values='level', fill_value=None)
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns,
                y=pivot_df.index,
                colorscale='RdYlGn',
                text=[[level_labels.get(cell, "") for cell in row] for row in pivot_df.values],
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(
                    title="정책 강도",
                    ticktext=list(level_labels.values()),
                    tickvals=list(level_labels.keys())
                )
            ))
            
            fig.update_layout(
                title="정당별 정책 분야별 강도",
                xaxis_title="정책 분야",
                yaxis_title="정당",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("정당별 평균 정책 강도")
                avg_by_party = df_all.groupby('party')['level'].mean().sort_values(ascending=False)
                
                # Bar chart for party average
                fig = px.bar(
                    x=avg_by_party.index,
                    y=avg_by_party.values,
                    labels={'x': '정당', 'y': '평균 정책 강도'},
                    color=avg_by_party.index,
                    color_discrete_map=party_colors
                )
                
                fig.update_layout(
                    showlegend=False,
                    xaxis_title="정당",
                    yaxis_title="평균 정책 강도"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("정책 분야별 평균 강도")
                avg_by_category = df_all.groupby('category')['level'].mean().sort_values(ascending=False)
                
                # Bar chart for category average
                fig = px.bar(
                    x=avg_by_category.index,
                    y=avg_by_category.values,
                    labels={'x': '정책 분야', 'y': '평균 정책 강도'}
                )
                
                fig.update_layout(
                    xaxis_title="정책 분야",
                    yaxis_title="평균 정책 강도"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"차트를 그리는 데 오류가 발생했습니다: {e}")
            st.write("충분한 데이터가 없을 수 있습니다.")

# Add sidebar information
st.sidebar.header("ℹ️ 정보")
st.sidebar.write("""
이 대시보드는 2025년 대선 후보들의 기후 정책 공약을 분석한 결과입니다.

**데이터 소스:**
- 온실가스 배출량: 온실가스종합정보센터
- 정당 정책: 각 정당 공약집
""")

# Add footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; background-color: #f0f0f0; border-radius: 5px;">
<p>© 2024 기후 정책 분석 대시보드</p>
</div>
""", unsafe_allow_html=True)

# Main function for local execution
if __name__ == "__main__":
    st.write("앱이 실행 중입니다!") 