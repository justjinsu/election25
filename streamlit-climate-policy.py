    # 2018년과 NDC 먼저, 나머지 정당은 감축률 기준 정렬
    total_df = pd.DataFrame(total_emissions)
    base_ndc = total_df[total_df['정당'].isin(['2018년 기준', '2030 NDC'])]
    parties_df = total_df[~total_df['정당'].isin(['2018년 기준', '2030 NDC'])].sort_values('감축률(%)', ascending=False)
    total_df = pd.concat([base_ndc, parties_df])
    
    # 막대 그래프
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
    
    # 2030 NDC 목표 라인 추가
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
    
    # 부문별 배출량 비교
    st.markdown("### 부문별 온실가스 배출량")
    
    # 정당 선택
    selected_emission_parties = st.multiselect(
        "비교할 정당 선택",
        options=['2018년 기준', '2030 NDC'] + emission_parties,
        default=['2018년 기준', '2030 NDC'] + emission_parties[:2] if len(emission_parties) > 2 else ['2018년 기준', '2030 NDC'] + emission_parties
    )
    
    # 부문 선택
    selected_sector = st.selectbox("부문 선택", ["전체"] + sectors)
    
    if selected_sector == "전체":
        # 모든 부문 표시
        for sector in sectors:
            st.markdown(f"#### {sector}")
            
            # 데이터 정리
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
                
                # 막대 그래프
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
        # 선택한 부문만 표시
        st.markdown(f"#### {selected_sector} 부문 상세 분석")
        
        # 데이터 정리
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
            
            # 막대 그래프
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
            
            # 2030 NDC 목표 라인 추가
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
            
            # 워터폴 차트 (기준년도부터 감축 흐름)
            st.markdown("##### 2018년 기준부터 감축 흐름")
            
            # 정당 선택 (최대 3개만)
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
                    
                    # 워터폴 차트 데이터
                    waterfall_data = [
                        {'단계': '2018년 기준', '배출량': base_value, '변화': 0, '타입': 'base'},
                        {'단계': f'{party} 감축', '배출량': -reduction, '변화': -reduction, '타입': 'reduction'},
                        {'단계': f'{party} 목표', '배출량': party_value, '변화': 0, '타입': 'total'}
                    ]
                    
                    waterfall_df = pd.DataFrame(waterfall_data)
                    
                    # 워터폴 차트
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
    
    # 테이블로 모든 데이터 보기
    st.markdown("### 전체 데이터 테이블")
    
    # 데이터 정리
    table_data = []
    
    for sector in sectors + ['총배출']:
        row = {'부문': sector}
        for party in emissions_data.keys():
            if sector in emissions_data[party]:
                value = emissions_data[party][sector]
                row[party] = value
        table_data.append(row)
    
    table_df = pd.DataFrame(table_data)
    
    # 색상 매핑 함수 (감축률에 따른 색상 조정)
    def color_negative_red(val):
        """
        양수면 빨간색, 음수면 초록색으로 색상 변경
        """
        if isinstance(val, (int, float)):
            base_value = table_df.loc[table_df['부문'] == table_df['부문'].iloc[table_df.index.get_loc(val.name)], '2018년 기준'].values[0] \
                if '2018년 기준' in table_df.columns else 0
                
            if base_value > 0:
                # 감축률 계산
                reduction = 100 * (1 - val / base_value)
                
                # 색상 결정 (감축이 많을수록 녹색)
                if reduction <= 0:
                    color = 'red'
                elif reduction < 20:
                    color = 'orange'
                elif reduction < 40:
                    color = '#FFEC19'  # 노랑
                elif reduction < 60:
                    color = 'lightgreen'
                else:
                    color = 'green'
                
                return f'background-color: {color}; color: black;'
        return ''
    
    # 스타일 적용 (2018년 기준과 2030 NDC는 제외)
    style_df = table_df.style.applymap(
        color_negative_red, 
        subset=pd.IndexSlice[:, [col for col in table_df.columns if col not in ['부문', '2018년 기준', '2030 NDC']]]
    )
    
    # 테이블 표시
    st.dataframe(style_df)
    
    # CSV 다운로드 버튼
    csv = table_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="데이터 CSV 다운로드",
        data=csv,
        file_name="climate_policy_emissions.csv",
        mime="text/csv",
    )
    
    # 요약 및 주요 시사점
    st.markdown("### 분석 요약")
    
    # 각 정당의 총 감축률 계산
    summary_data = {}
    base_total = emissions_data.get('2018년 기준', {}).get('총배출', 0)
    
    for party in emissions_data.keys():
        if party != '2018년 기준' and '총배출' in emissions_data[party]:
            party_total = emissions_data[party]['총배출']
            if base_total > 0 and isinstance(party_total, (int, float)):
                reduction = 100 * (1 - party_total / base_total)
                summary_data[party] = {
                    '총배출량': party_total,
                    '감축률': reduction
                }
    
    # 감축률 기준으로 정렬
    sorted_parties = sorted(summary_data.items(), key=lambda x: x[1]['감축률'], reverse=True)
    
    # 요약 텍스트 작성
    st.markdown("#### 정당별 총배출량 감축 목표")
    
    for party, data in sorted_parties:
        party_short = party.split('-')[0] if '-' in party else party
        
        # 색상 설정
        if data['감축률'] < 30:
            badge_color = "red"
        elif data['감축률'] < 50:
            badge_color = "orange"
        else:
            badge_color = "green"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="background-color: {party_colors.get(party, '#999999')}; width: 20px; height: 20px; margin-right: 10px; border-radius: 50%;"></div>
            <div><strong>{party_short}</strong>: 총 <span style="color: {badge_color}; font-weight: bold;">{data['감축률']:.1f}%</span> 감축 목표 ({data['총배출량']:.1f} 백만톤 CO₂eq)</div>
        </div>
        """, unsafe_allow_html=True)

# 탭 3: 에너지 믹스 분석
with tabs[2]:
    st.markdown("<h1 class='title'>2025 대선 기후 정책 종합 분석</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>에너지 믹스 분석</p>", unsafe_allow_html=True)
    
    # 시나리오 선택
    energy_scenarios = list(energy_mix.keys())
    selected_scenario = st.selectbox("시나리오 선택", energy_scenarios)
    
    # 차트 유형 선택
    chart_type = st.radio("차트 유형", ["파이 차트", "바 차트", "테이블"], horizontal=True)
    
    # 선택된 시나리오 데이터
    if selected_scenario in energy_mix:
        scenario_data = energy_mix[selected_scenario]
        
        # 데이터 준비
        energy_df = pd.DataFrame({
            '에너지원': list(scenario_data.keys()),
            '비중(%)': list(scenario_data.values())
        })
        
        # 에너지원 종류별 색상 매핑
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
        
        # 차트 타입에 따라 표시
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
            # 바 차트로 표시
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
            
        else:  # 테이블
            # 정렬 및 포맷팅
            energy_df = energy_df.sort_values('비중(%)', ascending=False)
            energy_df['비중(%)'] = energy_df['비중(%)'].apply(lambda x: f"{x:.1f}%")
            
            # 테이블 표시
            st.markdown(f"#### {selected_scenario} 에너지 믹스")
            st.dataframe(energy_df, use_container_width=True)
    
    # 전체 시나리오 비교
    st.markdown("### 정당별 에너지 믹스 비교")
    
    # 에너지원 선택
    energy_sources = set()
    for scenario in energy_mix.values():
        energy_sources.update(scenario.keys())
    energy_sources = sorted(list(energy_sources))
    
    selected_source = st.selectbox("에너지원 선택", ["전체"] + energy_sources)
    
    if selected_source == "전체":
        # 모든 시나리오, 모든 에너지원 비교
        compare_data = []
        
        for scenario, sources in energy_mix.items():
            for source, value in sources.items():
                compare_data.append({
                    '시나리오': scenario,
                    '에너지원': source,
                    '비중(%)': value
                })
        
        compare_df = pd.DataFrame(compare_data)
        
        # 스택 바 차트로 표시
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
            yaxis=dict(range=[0, 105]),  # 약간 여유 제공
            barmode='stack'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 테이블로 비교
        pivot_df = pd.pivot_table(
            compare_df, 
            values='비중(%)', 
            index='에너지원', 
            columns='시나리오', 
            aggfunc='sum'
        ).reset_index()
        
        # 데이터 정렬
        try:
            pivot_df = pivot_df.sort_values('2023년(현재)', ascending=False)
        except:
            pass
            
        st.dataframe(pivot_df, use_container_width=True)
        
    else:
        # 선택한 에너지원만 비교
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
        
        # 정렬: 현재, NDC, 정당 순서로
        sort_order = ['2023년(현재)', '2030 NDC']
        source_df['sort_key'] = source_df['시나리오'].apply(lambda x: 
                                                       sort_order.index(x) if x in sort_order else len(sort_order))
        source_df = source_df.sort_values('sort_key').drop('sort_key', axis=1)
        
        # 바 차트로 표시
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
        
    # 재생에너지 비중 비교
    st.markdown("### 재생에너지 비중 비교")
    
    # 재생에너지원 정의
    renewable_sources = ['태양광', '풍력', '수력', '바이오', '연료전지', '기타 재생']
    
    # 재생에너지 비중 계산
    renewable_data = []
    
    for scenario, sources in energy_mix.items():
        renewable_total = sum(sources.get(src, 0) for src in renewable_sources)
        renewable_data.append({
            '시나리오': scenario,
            '재생에너지 비중(%)': renewable_total
        })
    
    renewable_df = pd.DataFrame(renewable_data)
    
    # 정렬: 현재, NDC, 정당 순서로
    sort_order = ['2023년(현재)', '2030 NDC']
    renewable_df['sort_key'] = renewable_df['시나리오'].apply(lambda x: 
                                                       sort_order.index(x) if x in sort_order else len(sort_order))
    renewable_df = renewable_df.sort_values('sort_key').drop('sort_key', axis=1)
    
    # 바 차트로 표시
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
    
    # 화석 vs 비화석 비교
    st.markdown("### 화석 연료 vs 청정 에너지 비교")
    
    # 화석연료 정의
    fossil_sources = ['석탄', 'LNG', '석유']
    clean_sources = ['원자력'] + renewable_sources
    
    # 화석/청정 에너지 비중 계산
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
    
    # 정렬: 현재, NDC, 정당 순서로
    sort_order = ['2023년(현재)', '2030 NDC']
    comparison_df['sort_key'] = comparison_df['시나리오'].apply(lambda x: 
                                                       sort_order.index(x) if x in sort_order else len(sort_order))
    comparison_df = comparison_df.sort_values('sort_key').drop('sort_key', axis=1)
    
    # 스택 바 차트로 표시
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
        yaxis=dict(range=[0, 105]),  # 약간 여유 제공
        barmode='stack'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 탭 4: 온도 경로 분석
with tabs[3]:
    st.markdown("<h1 class='title'>2025 대선 기후 정책 종합 분석</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>온도 경로 분석</p>", unsafe_allow_html=True)
    
    # 기준 온도 경로
    reference_paths = ['1.5°C 경로', '2°C 경로', '3°C 경로']
    reference_colors = {
        '1.5°C 경로': '#32CD32',  # 녹색
        '2°C 경로': '#FFA500',    # 주황색
        '3°C 경로': '#FF0000'     # 빨강색
    }
    
    # 정당 경로 (기준 경로 제외)
    party_paths = [p for p in temp_path.keys() if p not in reference_paths]
    
    # 정당 선택
    selected_parties = st.multiselect("정당 선택", party_paths, default=party_paths[:2] if len(party_paths) > 1 else party_paths)
    
    # 온도 경로 차트
    st.markdown("### 온실가스 배출 경로 비교")
    
    # 데이터 준비
    line_data = []
    
    # 기준 경로 데이터
    for path in reference_paths:
        if path in temp_path:
            for year, value in temp_path[path].items():
                line_data.append({
                    '경로': path,
                    '연도': year,
                    '배출량': value,
                    '경로 유형': 'reference',
                    '유형': path
                })
    
    # 정당 경로 데이터
    for path in selected_parties:
        if path in temp_path:
            for year, value in temp_path[path].items():
                line_data.append({
                    '경로': path,
                    '연도': year,
                    '배출량': value,
                    '경로 유형': 'party',
                    '유형': path
                })
    
    # 데이터프레임 생성
    line_df = pd.DataFrame(line_data)
    
    # 선 차트 생성
    fig = px.line(
        line_df,
        x='연도',
        y='배출량',
        color='경로',
        line_dash='경로 유형',
        color_discrete_map={
            **reference_colors,
            **{party: party_colors.get(party, "#999999") for party in selected_parties}
        },
        title="온실가스 배출 경로 비교",
        labels={'배출량': '온실가스 배출량 (백만톤 CO₂eq)'}
    )
    
    # 기준 경로를 두껍게 표시
    for path in reference_paths:
        fig.update_traces(
            line=dict(width=4),
            selector=dict(name=path)
        )
    
    fig.update_layout(
        height=600,
        xaxis_title="연도",
        yaxis_title="온실가스 배출량 (백만톤 CO₂eq)",
        legend_title="경로"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 파리협정 부합 여부 분석
    st.markdown("### 파리협정 부합 여부 분석")
    
    # 부합 여부 분석 데이터
    analysis_data = []
    
    for party in party_paths:
        # 각 기준 경로와의 거리 계산
        distances = {}
        closest_path = None
        min_distance = float('inf')
        
        if party in temp_path:
            party_values = temp_path[party]
            
            for ref_path in reference_paths:
                if ref_path in temp_path:
                    ref_values = temp_path[ref_path]
                    
                    # 공통 연도에 대한 배출량 차이의 제곱합
                    common_years = set(party_values.keys()) & set(ref_values.keys())
                    if common_years:
                        distance = sum((party_values[year] - ref_values[year])**2 for year in common_years)
                        distances[ref_path] = distance
                        
                        if distance < min_distance:
                            min_distance = distance
                            closest_path = ref_path
            
            # 2050년 배출량 (넷제로 여부)
            net_zero_2050 = party_values.get(2050, 0) < 10  # 10 Mt CO₂eq 이하면 넷제로로 간주
            
            # 파리협정 부합 여부 평가
            if closest_path == '1.5°C 경로':
                compliance = "매우 높음"
            elif closest_path == '2°C 경로':
                compliance = "중간"
            else:
                compliance = "낮음"
                
            # 데이터 추가
            analysis_data.append({
                '정당': party,
                '가장 가까운 경로': closest_path,
                '2050 넷제로': "달성" if net_zero_2050 else "미달성",
                '파리협정 부합도': compliance
            })
    
    # 분석 테이블 표시
    if analysis_data:
        analysis_df = pd.DataFrame(analysis_data)
        
        # 컬러 스타일링
        def color_compliance(val):
            if val == "매우 높음":
                return 'background-color: #32CD32; color: white;'
            elif val == "중간":
                return 'background-color: #FFA500; color: white;'
            else:
                return 'background-color: #FF0000; color: white;'
        
        def color_netzero(val):
            if val == "달성":
                return 'background-color: #32CD32; color: white;'
            else:
                return 'background-color: #FF0000; color: white;'
        
        def color_path(val):
            if val == "1.5°C 경로":
                return 'background-color: #32CD32; color: white;'
            elif val == "2°C 경로":
                return 'background-color: #FFA500; color: white;'
            else:
                return 'background-color: #FF0000; color: white;'
        
        # 스타일 적용
        style_analysis = analysis_df.style.\
            applymap(color_compliance, subset=['파리협정 부합도']).\
            applymap(color_netzero, subset=['2050 넷제로']).\
            applymap(color_path, subset=['가장 가까운 경로'])
        
        st.dataframe(style_analysis, use_container_width=True)
        
        # 파리협정 부합도 분석 설명
        st.markdown("""
        **파리협정 부합도 분석 방법**:
        - **가장 가까운 경로**: 각 정당의 배출 경로와 기준 경로(1.5°C, 2°C, 3°C) 간의 제곱 오차 합이 가장 작은 경로
        - **2050 넷제로**: 2050년 배출량이 10 Mt CO₂eq 이하인 경우 넷제로 달성으로 평가
        - **파리협정 부합도**: 
            - 1.5°C 경로에 가장 가까우면 "매우 높음" 
            - 2°C 경로에 가장 가까우면 "중간" 
            - 3°C 경로에 가장 가까우면 "낮음"
        """)
        
    # 시간별 감축률 분석
    st.markdown("### 시간별 감축률 분석")
    
    # 분석 데이터 준비
    reduction_data = []
    
    for path_name, path_data in temp_path.items():
        if path_name in reference_paths + selected_parties:
            # 주요 기준 연도 데이터 확인
            if 2018 in path_data and 2030 in path_data:
                # 2018년 대비 2030년 감축률
                reduction_2030 = 100 * (1 - path_data[2030] / path_data[2018])
                
                reduction_data.append({
                    '경로': path_name,
                    '기간': '2018-2030',
                    '감축률(%)': reduction_2030
                })
            
            if 2030 in path_data and 2050 in path_data:
                # 2030년 대비 2050년 감축률
                reduction_2050 = 100 * (1 - path_data[2050] / path_data[2030])
                
                reduction_data.append({
                    '경로': path_name,
                    '기간': '2030-2050',
                    '감축률(%)': reduction_2050
                })
            
            if 2018 in path_data and 2050 in path_data:
                # 2018년 대비 2050년 감축률
                reduction_total = 100 * (1 - path_data[2050] / path_data[2018])
                
                reduction_data.append({
                    '경로': path_name,
                    '기간': '2018-2050',
                    '감축률(%)': reduction_total
                })
    
    # 감축률 차트
    if reduction_data:
        reduction_df = pd.DataFrame(reduction_data)
        
        # 바 차트
        fig = px.bar(
            reduction_df,
            x='경로',
            y='감축률(%)',
            color='경로',
            facet_col='기간',
            color_discrete_map={
                **reference_colors,
                **{party: party_colors.get(party, "#999999") for party in selected_parties}
            },
            title="기간별 온실가스 감축률 비교",
            text='감축률(%)'
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="",
            yaxis_title="감축률(%)",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 주요 결과 설명
        total_results = reduction_df[reduction_df['기간'] == '2018-2050'].sort_values('감축률(%)', ascending=False)
        
        if not total_results.empty:
            st.markdown("#### 2018년-2050년 총 감축률 순위")
            
            for i, (_, row) in enumerate(total_results.iterrows()):
                path_name = row['경로']
                reduction = row['감축률(%)']
                
                # 기준 경로인지 여부에 따라 다른 형식으로 표시
                if path_name in reference_paths:
                    st.markdown(f"{i+1}. **{path_name}**: {reduction:.1f}% 감축 (기준 경로)")
                else:
                    st.markdown(f"{i+1}. **{path_name}**: {reduction:.1f}% 감축")
    
    # 넷제로 달성 연도 분석
    st.markdown("### 넷제로 달성 연도 분석")
    
    # 분석 데이터 준비
    netzero_data = []
    netzero_threshold = 20  # 20 Mt CO₂eq 이하면 넷제로로 간주
    
    for path_name, path_data in temp_path.items():
        if path_name in reference_paths + selected_parties:
            # 연도별 데이터를 오름차순으로 정렬
            years = sorted(path_data.keys())
            achieved = False
            netzero_year = None
            
            for year in years:
                if path_data[year] <= netzero_threshold:
                    achieved = True
                    netzero_year = year
                    break
            
            netzero_data.append({
                '경로': path_name,
                '넷제로 달성': achieved,
                '달성 연도': netzero_year if achieved else '2050년 이후',
                '2050년 배출량': path_data.get(2050, 'N/A')
            })
    
    # 넷제로 달성 테이블
    if netzero_data:
        netzero_df = pd.DataFrame(netzero_data)
        
        # 컬러 스타일링
        def color_achieved(val):
            if val:
                return 'background-color: #32CD32; color: white;'
            else:
                return 'background-color: #FF0000; color: white;'
        
        def color_year(val):
            if val == '2050년 이후':
                return 'background-color: #FF0000; color: white;'
            elif isinstance(val, (int, float)) and val <= 2050:
                return 'background-color: #32CD32; color: white;'
            else:
                return ''
        
        # 스타일 적용
        style_netzero = netzero_df.style.\
            applymap(color_achieved, subset=['넷제로 달성']).\
            applymap(color_year, subset=['달성 연도'])
        
        st.dataframe(style_netzero, use_container_width=True)
        
        # 넷제로 분석 설명
        st.markdown("""
        **넷제로 분석 방법**:
        - **넷제로 달성**: 연간 온실가스 배출량이 20 Mt CO₂eq 이하로 감소하는 경우 넷제로 달성으로 평가
        - **달성 연도**: 처음으로 넷제로 기준을 달성하는 연도
        - **2050년 배출량**: 2050년 기준 예상 온실가스 배출량
        """)

# 사이드바에 추가 설명
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 앱 사용법")
st.sidebar.markdown("""
1. 엑셀 파일을 업로드하거나 기본 데이터를 사용하세요
2. 탭을 선택하여 다양한 분석 결과를 확인하세요
3. 필터를 조정하여 원하는 정당이나 데이터를 선택하세요
4. 분석 결과를 확인하고 CSV로 다운로드할 수 있습니다
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 데이터 업데이트 방법")
st.sidebar.markdown("""
1. 다음 시트가 포함된 엑셀 파일을 준비하세요:
   - `정성평가_기준`: 정당별 정책 강화 정도
   - `온실가스종합비교`: 부문별 온실가스 배출량
   - `에너지믹스`: 정당별 에너지원 비중
   - `온도경로`: 연도별 배출량 및 온도 경로
2. 엑셀 파일을 업로드하면 자동으로 데이터가 업데이트됩니다
3. 실시간으로 그래프와 분석 결과가 변경됩니다
""")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <small>© 2025 대선 기후 정책 분석 도구 v1.0</small>
</div>
""", unsafe_allow_html=True)import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="2025 대선 기후 정책 분석", layout="wide")

# 정책 데이터
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
    {
        "category": "기후금융",
        "policies": {
            "국민의 힘": {"level": 2, "description": "2027년 5조원"},
            "더불어민주당": {"level": 3, "description": "2027년까지 7조 이상, 탄소세 도입"}
        }
    },
    {
        "category": "녹색금융",
        "policies": {
            "국민의 힘": {"level": 3, "description": "민관합동 녹색투자 펀드 조성, 산업은행 탄소중립 정책금융 확대, 중소·중견기업을 위한 녹색자산유동화증권 이자 비용지원 확대"},
            "사회대전환": {"level": 1, "description": "산업은행을 녹색투자은행으로 전환"}
        }
    },
    {
        "category": "감축목표",
        "policies": {
            "더불어민주당": {"level": 1, "description": "2035년 2018년 대비 52% 감축"}
        }
    },
    {
        "category": "탈석탄",
        "policies": {
            "더불어민주당": {"level": 2, "description": "2040년 탈석탄"}
        }
    },
    {
        "category": "재생에너지",
        "policies": {
            "더불어민주당": {"level": 2, "description": "2030 재생에너지 비중 40%"},
            "사회대전환": {"level": 3, "description": "2030 재생에너지 비중 50%, 2050년 100%"}
        }
    },
    {
        "category": "원자력",
        "policies": {
            "국민의 힘": {"level": 1, "description": "SMR 기술 개발 적극 추진"},
            "사회대전환": {"level": -2, "description": "원전 신규 건설 중단, 핵발전소 수명연장 금지"}
        }
    },
    {
        "category": "산업",
        "policies": {
            "국민의 힘": {"level": 2, "description": "탄소차액계약제도(CCfD) 도입, CCUS 산업 활성화 및 재정지원 확대"},
            "더불어민주당": {"level": 3, "description": "탄소차액계약제도(CCfD) 도입, 산단태양광 설치의무화제도 도입"},
            "사회대전환": {"level": 1, "description": "탄소국경조정제도(CBAM)에 대비한 국가 전략 수립과 대응 체계 구축"}
        }
    },
    {
        "category": "수송",
        "policies": {
            "개혁신당": {"level": 1, "description": "미래차(수소·전기) 산업 지원, 2차전지 산업 육성"}
        }
    },
    {
        "category": "건물",
        "policies": {
            "더불어민주당": {"level": 2, "description": "제로에너지건축물 활성화, 제로에너지건축 및 그린리모델링 시 저리대출 및 보조금 지원 확대"},
            "사회대전환": {"level": 3, "description": "녹색주택 100만호 공급, 건물 에너지 효율 등급제 도입"}
        }
    },
    {
        "category": "플라스틱&폐기물",
        "policies": {
            "국민의 힘": {"level": 1, "description": "플라스틱 경량화·재생원료 사용 확대, 폐자원 순환경제망 구축"},
            "더불어민주당": {"level": 2, "description": "탈플라스틱 컨트롤타워 설치, 플라스틱 폐기물부담금 부과요율 현실화, 수리권 보장 확대"},
            "사회대전환": {"level": 3, "description": "국내 석유화학업계 화석연료 사용 규제 및 생산자책임재활용제도(EPR) 강화"}
        }
    }
]

# 정당 색상
party_colors = {
    "국민의 힘": "#E61E2B",
    "더불어민주당": "#004EA2",
    "사회대전환": "#8B4513",
    "개혁신당": "#FF6B6B"
}

# 레벨 라벨
level_labels = {
    -2: "완화",
    0: "유지",
    1: "강화(약)",
    2: "강화(중)",
    3: "강화(강)"
}

# 페이지 제목
st.title("2025 대선 기후 정책 종합 분석")

# 탭 생성
tab1, tab2, tab3 = st.tabs(["📊 전체 정책 비교", "🔍 정당별 분석", "📈 정책 강도 분포"])

# 탭 1: 전체 정책 비교
with tab1:
    st.header("전체 정책 분야별 정당 입장")
    
    # 정당 선택
    selected_parties = st.multiselect(
        "정당 선택",
        ["국민의 힘", "더불어민주당", "사회대전환", "개혁신당"],
        default=["국민의 힘", "더불어민주당", "사회대전환"]
    )
    
    # 정책별 비교 차트
    for policy in policy_data:
        st.subheader(policy["category"])
        
        # 선택된 정당만 필터링
        relevant_parties = {k: v for k, v in policy["policies"].items() if k in selected_parties}
        
        if relevant_parties:
            # 차트 데이터 준비
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
        
        # 정책 세부사항
        with st.expander(f"{policy['category']} 정책 세부 내용"):
            for party, data in relevant_parties.items():
                st.write(f"**{party}** ({level_labels[data['level']]})")
                st.write(f"- {data['description']}")
                st.write("")

# 탭 2: 정당별 분석
with tab2:
    st.header("정당별 정책 현황")
    
    # 정당 선택
    selected_party = st.selectbox("정당 선택", ["국민의 힘", "더불어민주당", "사회대전환", "개혁신당"])
    
    # 선택된 정당의 모든 정책 수집
    party_policies = []
    for policy in policy_data:
        if selected_party in policy["policies"]:
            party_policies.append({
                "category": policy["category"],
                "level": policy["policies"][selected_party]["level"],
                "description": policy["policies"][selected_party]["description"]
            })
    
    # 정책 분포 차트
    if party_policies:
        df = pd.DataFrame(party_policies)
        
        # 막대 차트
        fig = px.bar(df, x='category', y='level', 
                     title=f"{selected_party} 정책 강도 분포",
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
        
        # 정책 상세 테이블
        st.subheader("정책 상세 내용")
        for i, policy in df.iterrows():
            st.write(f"### {policy['category']}")
            st.write(f"**강도**: {level_labels[policy['level']]}")
            st.write(f"**내용**: {policy['description']}")
            st.write("---")

# 탭 3: 정책 강도 분포
with tab3:
    st.header("전체 정책 강도 분포 분석")
    
    # 전체 데이터 준비
    all_policies = []
    for policy in policy_data:
        for party, data in policy["policies"].items():
            all_policies.append({
                "category": policy["category"],
                "party": party,
                "level": data["level"],
                "description": data["description"]
            })
    
    df_all = pd.DataFrame(all_policies)
    
    # 히트맵
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
    
    # 요약 통계
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("정당별 평균 정책 강도")
        avg_by_party = df_all.groupby('party')['level'].mean().sort_values(ascending=False)
        st.bar_chart(avg_by_party)
    
    with col2:
        st.subheader("정책 분야별 평균 강도")
        avg_by_category = df_all.groupby('category')['level'].mean().sort_values(ascending=False)
        st.bar_chart(avg_by_category)

# 사이드바에 정보 추가
st.sidebar.header("ℹ️ 정보")
st.sidebar.write("""
이 분석은 2025년 대선 후보들의 기후 정책 공약을 
정책 강화 정도에 따라 분석한 결과입니다.

**정책 강도 분류:**
- 완화: 기존 정책보다 덜 강력한 접근
- 유지: 현재 정책 수준 유지
- 강화(약): 기존 정책보다 약간 강화
- 강화(중): 상당한 정책 강화
- 강화(강): 매우 강력한 정책 강화

데이터 출처: 2025 Presidential Election Climate Policy Analysis
""")

# 실행 방법 안내
st.sidebar.header("🚀 배포 방법")
st.sidebar.write("""
1. Streamlit Community Cloud에 무료 배포
2. Heroku, Railway.app 등 플랫폼 활용
3. GitHub Pages + GitHub Actions
4. Vercel, Netlify 등 정적 호스팅
""")

if __name__ == "__main__":
    st.write("앱이 실행 중입니다!")
