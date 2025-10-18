# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="호텔 수요 예측",
    page_icon="🏨",
    layout="wide"
)

# 제목
st.title("🏨 호텔 객실 수요 예측 시스템")
st.markdown("---")

# 데이터 로드
@st.cache_data
def load_data():
    daily = pd.read_csv('data/daily_bookings.csv')
    forecast = pd.read_csv('data/forecast_results.csv')
    daily['date'] = pd.to_datetime(daily['date'])
    forecast['date'] = pd.to_datetime(forecast['date'])
    return daily, forecast

# 사이드바 (모든 탭에서 공통)
st.sidebar.header("📊 프로젝트 정보")
st.sidebar.markdown("""
**개발 배경:**  
호시노야 도쿄 인턴십 경험을 바탕으로  
SK AX의 재고 관리 솔루션을 구현

**기술 스택:**  
- Python
- Prophet (시계열 예측)
- Streamlit (대시보드)
- Plotly (시각화)

**데이터:**  
- 2015~2017년 호텔 예약 데이터
- 약 119,000건의 실제 예약 기록
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**개발자:** 박아진")
st.sidebar.markdown("**날짜:** 2025년 10월")

# 푸터 함수 (모든 탭에서 공통)
def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>🏨 Hotel Demand Forecasting System | Powered by Prophet & Streamlit</p>
        <p>본 프로젝트는 SK AX의 수요 예측 솔루션을 모방한 교육용 프로젝트입니다.</p>
    </div>
    """, unsafe_allow_html=True)

try:
    daily, forecast = load_data()
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📈 예측 요약", "📋 상세 데이터", "💡 인사이트"])
    
    # ========== 탭 1: 예측 요약 ==========
    with tab1:
        # 주요 지표
        st.subheader("📈 향후 30일 예측 요약")
        col1, col2, col3, col4 = st.columns(4)
        
        avg_pred = forecast['prediction'].mean()
        max_pred = forecast['prediction'].max()
        min_pred = forecast['prediction'].min()
        total_pred = forecast['prediction'].sum()
        
        with col1:
            st.metric("평균 예상 예약", f"{avg_pred:.0f}건")
        
        with col2:
            st.metric("최대 예상 예약", f"{max_pred:.0f}건")
        
        with col3:
            st.metric("최소 예상 예약", f"{min_pred:.0f}건")
        
        with col4:
            st.metric("30일 총 예약", f"{total_pred:,}건")
        
        st.markdown("---")
        
        # 예측 그래프
        st.subheader("📊 예약 수요 예측 (향후 30일)")
        
        fig = go.Figure()
        
        # 과거 데이터 (최근 60일만)
        recent_daily = daily.tail(60)
        fig.add_trace(go.Scatter(
            x=recent_daily['date'],
            y=recent_daily['bookings'],
            mode='lines',
            name='과거 실적',
            line=dict(color='gray', width=2),
            opacity=0.6
        ))
        
        # 예측값
        fig.add_trace(go.Scatter(
            x=forecast['date'],
            y=forecast['prediction'],
            mode='lines+markers',
            name='예측값',
            line=dict(color='#FF4B4B', width=3),
            marker=dict(size=6)
        ))
        
        # 신뢰구간 상한
        fig.add_trace(go.Scatter(
            x=forecast['date'],
            y=forecast['upper_bound'],
            mode='lines',
            name='상한 (95%)',
            line=dict(color='lightcoral', width=1, dash='dash'),
            showlegend=True
        ))
        
        # 신뢰구간 하한
        fig.add_trace(go.Scatter(
            x=forecast['date'],
            y=forecast['lower_bound'],
            mode='lines',
            name='하한 (95%)',
            line=dict(color='lightcoral', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(255,182,193,0.2)',
            showlegend=True
        ))
        
        fig.update_layout(
            xaxis_title="날짜",
            yaxis_title="예약 건수",
            hovermode='x unified',
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        show_footer()
    
    # ========== 탭 2: 상세 데이터 ==========
    with tab2:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📋 예측 데이터 상세")
            st.dataframe(
                forecast[['date', 'prediction', 'lower_bound', 'upper_bound']],
                use_container_width=True,
                height=600
            )
        
        with col_right:
            st.subheader("📊 일별 예측 분포")
            
            # 막대 그래프
            fig_bar = px.bar(
                forecast,
                x='date',
                y='prediction',
                labels={'date': '날짜', 'prediction': '예측 건수'},
                color='prediction',
                color_continuous_scale='Reds'
            )
            fig_bar.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        show_footer()
    
    # ========== 탭 3: 인사이트 ==========
    with tab3:
        st.subheader("💡 주요 인사이트")
        
        # 최대/최소 예약일
        max_idx = forecast['prediction'].idxmax()
        min_idx = forecast['prediction'].idxmin()
        max_date = forecast.loc[max_idx, 'date'].strftime('%Y년 %m월 %d일')
        min_date = forecast.loc[min_idx, 'date'].strftime('%Y년 %m월 %d일')
        
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.info(f"""
            **📈 최대 수요 예상일**  
            {max_date}  
            예상 예약: {max_pred:.0f}건
            """)
        
        with insight_col2:
            st.warning(f"""
            **📉 최소 수요 예상일**  
            {min_date}  
            예상 예약: {min_pred:.0f}건
            """)
        
        # 주간 평균
        st.markdown("---")
        st.subheader("📅 주간별 평균 예측")
        
        forecast_copy = forecast.copy()
        forecast_copy['week'] = ((forecast_copy.index) // 7) + 1
        weekly_avg = forecast_copy.groupby('week')['prediction'].mean().reset_index()
        weekly_avg['week_label'] = weekly_avg['week'].apply(lambda x: f"{x}주차")
        
        fig_weekly = px.bar(
            weekly_avg,
            x='week_label',
            y='prediction',
            labels={'week_label': '주차', 'prediction': '평균 예약 건수'},
            color='prediction',
            color_continuous_scale='Teal'
        )
        fig_weekly.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_weekly, use_container_width=True)
        
        show_footer()

except FileNotFoundError:
    st.error("❌ 데이터 파일을 찾을 수 없습니다. data 폴더에 파일이 있는지 확인해주세요.")
except Exception as e:
    st.error(f"❌ 오류 발생: {str(e)}")