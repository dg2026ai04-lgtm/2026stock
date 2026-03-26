import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="한-미 주식 비교 분석기", layout="wide")

st.title("📈 한-미 주요 주식 수익률 비교 대시보드")
st.markdown("한국과 미국의 주요 주식들의 누적 수익률을 한눈에 비교해 보세요.")

# 1. 사전 정의된 종목 딕셔너리 (한국 주식은 .KS 또는 .KQ가 필요합니다)
TICKERS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "NAVER": "035420.KS",
    "애플 (AAPL)": "AAPL",
    "테슬라 (TSLA)": "TSLA",
    "엔비디아 (NVDA)": "NVDA",
    "마이크로소프트 (MSFT)": "MSFT",
    "S&P 500 ETF (SPY)": "SPY"
}

# 2. 사이드바 설정
st.sidebar.header("⚙️ 분석 설정")
selected_names = st.sidebar.multiselect(
    "비교할 종목을 선택하세요",
    options=list(TICKERS.keys()),
    default=["삼성전자", "애플 (AAPL)", "엔비디아 (NVDA)"]
)

period = st.sidebar.selectbox(
    "조회 기간", 
    options=["1mo", "3mo", "6mo", "1y", "3y", "5y", "max"], 
    index=3,
    format_func=lambda x: {"1mo":"1개월", "3mo":"3개월", "6mo":"6개월", "1y":"1년", "3y":"3년", "5y":"5년", "max":"전체"}[x]
)

# 3. 데이터 로드 및 처리
@st.cache_data
def load_data(tickers, period):
    # yfinance를 통해 종가(Close) 데이터 다운로드
    data = yf.download(tickers, period=period)['Close']
    
    # 단일 종목일 경우 Series로 반환되므로 DataFrame으로 변환
    if isinstance(data, pd.Series):
        data = data.to_frame()
        data.columns = tickers
        
    return data

if not selected_names:
    st.warning("👈 왼쪽 사이드바에서 비교할 종목을 하나 이상 선택해 주세요.")
else:
    # 선택된 한글 이름에 매칭되는 티커 심볼 리스트 생성
    selected_tickers = [TICKERS[name] for name in selected_names]
    
    with st.spinner('데이터를 불러오는 중입니다...'):
        df = load_data(selected_tickers, period)
        
        # 결측치 처리 (휴장일이 다르므로 이전 데이터로 채움)
        df = df.fillna(method='ffill').dropna()

        # 컬럼명을 다시 보기 편한 한글 이름으로 변경
        reverse_tickers = {v: k for k, v in TICKERS.items()}
        df.columns = [reverse_tickers.get(col, col) for col in df.columns]

        # 4. 누적 수익률 계산 (첫 날의 가격을 기준으로 몇 % 상승/하락했는지)
        df_returns = (df / df.iloc[0] - 1) * 100

        # 5. 차트 그리기 (Plotly)
        st.subheader("📊 기간 내 누적 수익률 (%)")
        fig = px.line(
            df_returns, 
            x=df_returns.index, 
            y=df_returns.columns,
            labels={'value': '누적 수익률 (%)', 'Date': '날짜', 'variable': '종목'}
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # 6. 상세 데이터 요약
        st.subheader("📋 최근 종가 데이터")
        st.dataframe(df.tail(5).style.format("{:,.2f}"))
