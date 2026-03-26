# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Comparison", layout="wide")

st.title("📊 한국 vs 미국 주식 수익률 비교")

# 기본 종목 리스트
korea_stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "네이버": "035420.KS",
    "카카오": "035720.KS"
}

us_stocks = {
    "애플": "AAPL",
    "마이크로소프트": "MSFT",
    "테슬라": "TSLA",
    "엔비디아": "NVDA"
}

st.sidebar.header("📌 설정")

selected_korea = st.sidebar.multiselect(
    "한국 주식 선택",
    list(korea_stocks.keys()),
    default=["삼성전자"]
)

selected_us = st.sidebar.multiselect(
    "미국 주식 선택",
    list(us_stocks.keys()),
    default=["애플"]
)

period = st.sidebar.selectbox(
    "기간 선택",
    ["1mo", "3mo", "6mo", "1y", "3y", "5y"],
    index=3
)

# 티커 변환
selected_tickers = [korea_stocks[s] for s in selected_korea] + \
                   [us_stocks[s] for s in selected_us]

if not selected_tickers:
    st.warning("주식을 선택해주세요!")
    st.stop()

@st.cache_data
def load_data(tickers, period):
    data = yf.download(tickers, period=period)["Adj Close"]
    return data

# 데이터 로드
try:
    data = load_data(selected_tickers, period)
except Exception as e:
    st.error("데이터를 불러오는 중 오류 발생")
    st.stop()

# 수익률 계산
returns = (data / data.iloc[0] - 1) * 100

st.subheader("📈 수익률 비교 (%)")

fig, ax = plt.subplots()
returns.plot(ax=ax)
ax.set_ylabel("수익률 (%)")
ax.grid(True)

st.pyplot(fig)

# 개별 통계
st.subheader("📊 요약")
summary = pd.DataFrame({
    "최종 수익률 (%)": returns.iloc[-1],
    "최고가": data.max(),
    "최저가": data.min()
})

st.dataframe(summary)

st.caption("데이터 출처: Yahoo Finance (yfinance)")

# requirements.txt 내용
# 아래 내용을 requirements.txt 파일로 저장하세요
requirements_txt = """
streamlit
yfinance
pandas
matplotlib
"""

st.download_button(
    label="📥 requirements.txt 다운로드",
    data=requirements_txt,
    file_name="requirements.txt",
    mime="text/plain"
)
