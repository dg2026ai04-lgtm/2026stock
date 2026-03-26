import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 비교 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-card: #111827;
    --bg-card2: #1a2235;
    --accent-green: #00ff88;
    --accent-red: #ff4466;
    --accent-blue: #3b82f6;
    --accent-yellow: #f59e0b;
    --text-primary: #f0f4ff;
    --text-secondary: #8892a4;
    --border: #1e2d40;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

.stApp {
    background: var(--bg-primary);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Header */
.dashboard-header {
    font-family: 'Space Mono', monospace;
    text-align: center;
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.dashboard-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #00ff88 0%, #3b82f6 50%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.dashboard-header p {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin-top: 0.5rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 2px;
}

/* Metric Cards */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.75rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover {
    border-color: #2d3f55;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 12px 0 0 12px;
}
.metric-card.green::before { background: var(--accent-green); }
.metric-card.red::before   { background: var(--accent-red); }
.metric-card.blue::before  { background: var(--accent-blue); }

.metric-name {
    font-size: 0.78rem;
    color: var(--text-secondary);
    letter-spacing: 1px;
    font-family: 'Space Mono', monospace;
    text-transform: uppercase;
}
.metric-ticker {
    font-size: 0.7rem;
    color: #4a5568;
    font-family: 'Space Mono', monospace;
}
.metric-price {
    font-size: 1.5rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    margin: 0.3rem 0;
    color: var(--text-primary);
}
.metric-return {
    font-size: 1rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
}
.metric-return.positive { color: var(--accent-green); }
.metric-return.negative { color: var(--accent-red); }

/* Section Headers */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 3px;
    color: var(--text-secondary);
    text-transform: uppercase;
    margin: 1.5rem 0 1rem;
    border-left: 2px solid var(--accent-blue);
    padding-left: 0.75rem;
}

/* Flag badges */
.flag-badge {
    display: inline-block;
    font-size: 0.85rem;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.3);
    color: #93c5fd;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1px;
}

/* Plotly chart containers */
.element-container iframe { border-radius: 12px; }

/* Selectbox & Multiselect styling */
[data-testid="stMultiSelect"] > div > div {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px;
}

div[data-baseweb="select"] > div {
    background: var(--bg-card2) !important;
    border-color: var(--border) !important;
}

/* Radio buttons */
[data-testid="stRadio"] > div { gap: 0.5rem; }

/* Divider */
hr { border-color: var(--border); margin: 1.5rem 0; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: #1e2d40; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Data Definitions ──────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "현대차": "005380.KS",
    "기아": "000270.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "셀트리온": "068270.KS",
    "POSCO홀딩스": "005490.KS",
    "KB금융": "105560.KS",
    "신한지주": "055550.KS",
    "LG화학": "051910.KS",
    "삼성바이오로직스": "207940.KS",
    "현대모비스": "012330.KS",
    "두산에너빌리티": "034020.KS",
}

US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet (Google)": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-B",
    "JPMorgan Chase": "JPM",
    "Eli Lilly": "LLY",
    "Broadcom": "AVGO",
    "Visa": "V",
    "UnitedHealth": "UNH",
    "ExxonMobil": "XOM",
    "Johnson & Johnson": "JNJ",
}

INDICES = {
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
}

PERIOD_MAP = {
    "1주": "5d",
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
    "2년": "2y",
    "5년": "5y",
}

# ── Helper Functions ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(tickers: list, period: str) -> dict:
    data = {}
    for t in tickers:
        try:
            tk = yf.Ticker(t)
            hist = tk.history(period=period, auto_adjust=True)
            if not hist.empty:
                data[t] = hist
        except Exception:
            pass
    return data

@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(ticker: str) -> dict:
    try:
        return yf.Ticker(ticker).info
    except Exception:
        return {}

def calc_return(series: pd.Series) -> float:
    if len(series) < 2:
        return 0.0
    return (series.iloc[-1] / series.iloc[0] - 1) * 100

def format_price(price, ticker):
    if ".KS" in ticker or ".KQ" in ticker:
        return f"₩{price:,.0f}"
    return f"${price:,.2f}"

def color_class(val):
    return "positive" if val >= 0 else "negative"

def arrow(val):
    return "▲" if val >= 0 else "▼"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">⚙ 설정</div>', unsafe_allow_html=True)

    period_label = st.selectbox(
        "기간 선택",
        list(PERIOD_MAP.keys()),
        index=3,
    )
    period = PERIOD_MAP[period_label]

    st.markdown('<div class="section-title">🇰🇷 한국 주식</div>', unsafe_allow_html=True)
    kr_selected_names = st.multiselect(
        "종목 선택 (복수 가능)",
        list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "NAVER", "현대차"],
        key="kr",
    )
    kr_selected = {n: KR_STOCKS[n] for n in kr_selected_names}

    st.markdown('<div class="section-title">🇺🇸 미국 주식</div>', unsafe_allow_html=True)
    us_selected_names = st.multiselect(
        "종목 선택 (복수 가능)",
        list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Microsoft", "Tesla"],
        key="us",
    )
    us_selected = {n: US_STOCKS[n] for n in us_selected_names}

    st.markdown('<div class="section-title">📊 지수</div>', unsafe_allow_html=True)
    show_indices = st.multiselect(
        "지수 선택",
        list(INDICES.keys()),
        default=["KOSPI", "S&P 500", "NASDAQ"],
    )

    st.markdown("---")
    chart_type = st.radio(
        "차트 스타일",
        ["라인", "캔들스틱", "영역"],
        horizontal=True,
    )

    st.markdown("---")
    st.markdown('<p style="color:#4a5568;font-size:0.7rem;font-family:Space Mono,monospace;text-align:center">데이터: Yahoo Finance<br>자동 갱신: 5분</p>', unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
  <h1>GLOBAL STOCK DASHBOARD</h1>
  <p>KOREA × USA · REAL-TIME COMPARISON</p>
</div>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
all_tickers = list(kr_selected.values()) + list(us_selected.values()) + [INDICES[i] for i in show_indices]

if not all_tickers:
    st.warning("사이드바에서 종목을 하나 이상 선택해 주세요.")
    st.stop()

with st.spinner("📡 데이터 수집 중..."):
    raw = fetch_data(all_tickers, period)

# ── Index Summary Bar ─────────────────────────────────────────────────────────
if show_indices:
    st.markdown('<div class="section-title">📈 주요 지수</div>', unsafe_allow_html=True)
    idx_cols = st.columns(len(show_indices))
    for col, idx_name in zip(idx_cols, show_indices):
        ticker = INDICES[idx_name]
        if ticker in raw:
            close = raw[ticker]["Close"]
            ret = calc_return(close)
            last = close.iloc[-1]
            cc = "green" if ret >= 0 else "red"
            with col:
                st.markdown(f"""
                <div class="metric-card {cc}">
                  <div class="metric-name">{idx_name}</div>
                  <div class="metric-price">{last:,.2f}</div>
                  <div class="metric-return {color_class(ret)}">{arrow(ret)} {ret:+.2f}%</div>
                  <div class="metric-ticker">{period_label} 수익률</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# ── Returns Bar Chart ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 수익률 한눈에 비교</div>', unsafe_allow_html=True)

returns_data = []
for name, ticker in {**kr_selected, **us_selected}.items():
    if ticker in raw:
        close = raw[ticker]["Close"]
        ret = calc_return(close)
        market = "🇰🇷 한국" if ".KS" in ticker or ".KQ" in ticker else "🇺🇸 미국"
        returns_data.append({"종목": name, "수익률(%)": ret, "시장": market, "ticker": ticker})

if returns_data:
    df_ret = pd.DataFrame(returns_data).sort_values("수익률(%)", ascending=True)

    colors = [
        "#00ff88" if v >= 0 else "#ff4466"
        for v in df_ret["수익률(%)"]
    ]

    fig_bar = go.Figure(go.Bar(
        x=df_ret["수익률(%)"],
        y=df_ret["종목"],
        orientation="h",
        marker=dict(
            color=colors,
            opacity=0.85,
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        text=[f"{v:+.2f}%" for v in df_ret["수익률(%)"]],
        textposition="outside",
        textfont=dict(family="Space Mono", size=11, color="#c0ccd8"),
        hovertemplate="<b>%{y}</b><br>수익률: %{x:.2f}%<extra></extra>",
    ))

    fig_bar.add_vline(x=0, line_color="#2d3f55", line_width=1.5)

    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Noto Sans KR", color="#8892a4"),
        xaxis=dict(
            gridcolor="#1e2d40", zeroline=False,
            ticksuffix="%", tickfont=dict(family="Space Mono", size=10),
        ),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11)),
        margin=dict(l=10, r=60, t=20, b=20),
        height=max(300, len(returns_data) * 38),
        hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2d40", font_color="#f0f4ff"),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ── Normalized Price Chart ────────────────────────────────────────────────────
st.markdown('<div class="section-title">📉 정규화 수익률 추이 (기준: 100)</div>', unsafe_allow_html=True)

fig_line = go.Figure()

KR_PALETTE = ["#00ff88", "#00d4aa", "#22d3ee", "#34d399", "#6ee7b7", "#a7f3d0"]
US_PALETTE = ["#3b82f6", "#818cf8", "#a78bfa", "#f59e0b", "#f97316", "#fb7185"]

kr_i = us_i = 0
for name, ticker in kr_selected.items():
    if ticker in raw:
        close = raw[ticker]["Close"].dropna()
        normalized = (close / close.iloc[0]) * 100
        color = KR_PALETTE[kr_i % len(KR_PALETTE)]
        kr_i += 1

        if chart_type == "영역":
            fig_line.add_trace(go.Scatter(
                x=normalized.index, y=normalized.values,
                name=f"🇰🇷 {name}", line=dict(color=color, width=1.5),
                fill="tozeroy", fillcolor=color.replace("#", "rgba(") + "10)" if color.startswith("#") else color,
                mode="lines",
                hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.1f}}<extra></extra>",
            ))
        else:
            fig_line.add_trace(go.Scatter(
                x=normalized.index, y=normalized.values,
                name=f"🇰🇷 {name}", line=dict(color=color, width=2),
                mode="lines",
                hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.1f}}<extra></extra>",
            ))

for name, ticker in us_selected.items():
    if ticker in raw:
        close = raw[ticker]["Close"].dropna()
        normalized = (close / close.iloc[0]) * 100
        color = US_PALETTE[us_i % len(US_PALETTE)]
        us_i += 1
        fig_line.add_trace(go.Scatter(
            x=normalized.index, y=normalized.values,
            name=f"🇺🇸 {name}", line=dict(color=color, width=2, dash="dot"),
            mode="lines",
            hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.1f}}<extra></extra>",
        ))

fig_line.add_hline(y=100, line_color="#2d3f55", line_width=1, line_dash="dash")
fig_line.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0d1520",
    font=dict(family="Noto Sans KR", color="#8892a4"),
    xaxis=dict(gridcolor="#1a2535", showgrid=True, zeroline=False, tickfont=dict(family="Space Mono", size=10)),
    yaxis=dict(gridcolor="#1a2535", showgrid=True, zeroline=False, ticksuffix="", tickfont=dict(family="Space Mono", size=10)),
    legend=dict(
        orientation="v", x=1.01, y=1,
        bgcolor="rgba(17,24,39,0.8)", bordercolor="#1e2d40", borderwidth=1,
        font=dict(size=11),
    ),
    height=460,
    margin=dict(l=10, r=160, t=20, b=30),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2d40", font_color="#f0f4ff"),
)
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# ── Individual Candlestick / Area Charts ──────────────────────────────────────
st.markdown('<div class="section-title">🕯 개별 종목 차트</div>', unsafe_allow_html=True)

all_stocks = {**{"🇰🇷 " + k: v for k, v in kr_selected.items()},
              **{"🇺🇸 " + k: v for k, v in us_selected.items()}}

if all_stocks:
    tabs = st.tabs(list(all_stocks.keys()))
    for tab, (display_name, ticker) in zip(tabs, all_stocks.items()):
        with tab:
            if ticker not in raw:
                st.error(f"데이터를 불러올 수 없습니다: {ticker}")
                continue
            df = raw[ticker]
            close = df["Close"].dropna()
            ret = calc_return(close)
            last_price = close.iloc[-1]
            is_korean = ".KS" in ticker or ".KQ" in ticker

            # Stats row
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("현재가", format_price(last_price, ticker))
            c2.metric("기간 수익률", f"{ret:+.2f}%", delta=f"{ret:.2f}%")
            if len(close) > 0:
                c3.metric("최고가", format_price(close.max(), ticker))
                c4.metric("최저가", format_price(close.min(), ticker))

            # Chart
            if chart_type == "캔들스틱" and all(c in df.columns for c in ["Open", "High", "Low", "Close"]):
                fig_ind = go.Figure(go.Candlestick(
                    x=df.index,
                    open=df["Open"], high=df["High"],
                    low=df["Low"], close=df["Close"],
                    increasing_line_color="#00ff88",
                    decreasing_line_color="#ff4466",
                    name=display_name,
                ))
            else:
                fill_color = "rgba(0,255,136,0.08)" if ret >= 0 else "rgba(255,68,102,0.08)"
                line_color = "#00ff88" if ret >= 0 else "#ff4466"
                fig_ind = go.Figure(go.Scatter(
                    x=close.index, y=close.values,
                    fill="tozeroy", fillcolor=fill_color,
                    line=dict(color=line_color, width=2),
                    mode="lines",
                    name=display_name,
                ))

            # Volume subplot
            if "Volume" in df.columns and df["Volume"].sum() > 0:
                fig_ind = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                        row_heights=[0.75, 0.25], vertical_spacing=0.04)
                if chart_type == "캔들스틱" and all(c in df.columns for c in ["Open", "High", "Low", "Close"]):
                    fig_ind.add_trace(go.Candlestick(
                        x=df.index, open=df["Open"], high=df["High"],
                        low=df["Low"], close=df["Close"],
                        increasing_line_color="#00ff88", decreasing_line_color="#ff4466",
                        name=display_name,
                    ), row=1, col=1)
                else:
                    fill_color = "rgba(0,255,136,0.08)" if ret >= 0 else "rgba(255,68,102,0.08)"
                    line_color = "#00ff88" if ret >= 0 else "#ff4466"
                    fig_ind.add_trace(go.Scatter(
                        x=close.index, y=close.values,
                        fill="tozeroy", fillcolor=fill_color,
                        line=dict(color=line_color, width=2),
                        name=display_name,
                    ), row=1, col=1)

                vol_colors = ["#00ff88" if c >= o else "#ff4466"
                              for c, o in zip(df["Close"], df["Open"])]
                fig_ind.add_trace(go.Bar(
                    x=df.index, y=df["Volume"],
                    marker_color=vol_colors, opacity=0.5, name="거래량",
                ), row=2, col=1)

                fig_ind.update_yaxes(title_text="거래량", row=2, col=1,
                                     tickfont=dict(family="Space Mono", size=9))

            fig_ind.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#0d1520",
                font=dict(family="Noto Sans KR", color="#8892a4"),
                xaxis_rangeslider_visible=False,
                height=480,
                margin=dict(l=10, r=10, t=15, b=20),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                hovermode="x unified",
                hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2d40", font_color="#f0f4ff"),
            )
            fig_ind.update_xaxes(gridcolor="#1a2535", tickfont=dict(family="Space Mono", size=10))
            fig_ind.update_yaxes(gridcolor="#1a2535", tickfont=dict(family="Space Mono", size=10))
            st.plotly_chart(fig_ind, use_container_width=True)

st.markdown("---")

# ── Correlation Heatmap ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔗 종목 간 상관관계</div>', unsafe_allow_html=True)

close_df = pd.DataFrame()
for name, ticker in {**kr_selected, **us_selected}.items():
    if ticker in raw:
        s = raw[ticker]["Close"].dropna()
        close_df[name] = s

if len(close_df.columns) >= 2:
    close_df = close_df.dropna()
    corr = close_df.pct_change().dropna().corr()

    fig_heat = go.Figure(go.Heatmap(
        z=corr.values,
        x=list(corr.columns),
        y=list(corr.index),
        colorscale=[
            [0.0, "#ff4466"],
            [0.5, "#111827"],
            [1.0, "#00ff88"],
        ],
        zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}",
        textfont=dict(family="Space Mono", size=11),
        hovertemplate="<b>%{x}</b> × <b>%{y}</b><br>상관계수: %{z:.3f}<extra></extra>",
    ))
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Noto Sans KR", color="#8892a4"),
        height=400,
        margin=dict(l=10, r=10, t=15, b=10),
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10)),
    )
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("상관관계 분석을 위해 2개 이상의 종목을 선택해 주세요.")

st.markdown("---")

# ── Data Table ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 수익률 요약 테이블</div>', unsafe_allow_html=True)

if returns_data:
    df_table = pd.DataFrame(returns_data)
    df_table["현재가"] = df_table.apply(
        lambda r: format_price(raw[r["ticker"]]["Close"].iloc[-1], r["ticker"])
        if r["ticker"] in raw else "N/A", axis=1
    )
    df_table["최고가"] = df_table.apply(
        lambda r: format_price(raw[r["ticker"]]["Close"].max(), r["ticker"])
        if r["ticker"] in raw else "N/A", axis=1
    )
    df_table["최저가"] = df_table.apply(
        lambda r: format_price(raw[r["ticker"]]["Close"].min(), r["ticker"])
        if r["ticker"] in raw else "N/A", axis=1
    )
    df_table["수익률"] = df_table["수익률(%)"].apply(lambda x: f"{x:+.2f}%")
    df_table = df_table[["시장", "종목", "현재가", "수익률", "최고가", "최저가"]].sort_values("수익률(%)" if "수익률(%)" in df_table.columns else "종목", ascending=False)

    st.dataframe(
        df_table.drop(columns=["수익률(%)"] if "수익률(%)" in df_table.columns else []),
        use_container_width=True,
        hide_index=True,
        height=min(400, (len(df_table) + 1) * 40),
    )

st.markdown("""
<div style="text-align:center;color:#2d3f55;font-family:Space Mono,monospace;font-size:0.7rem;padding:2rem 0 1rem">
  GLOBAL STOCK DASHBOARD · POWERED BY YAHOO FINANCE + STREAMLIT<br>
  ⚠ 본 대시보드는 정보 제공 목적으로만 사용되며 투자 권유가 아닙니다
</div>
""", unsafe_allow_html=True)
