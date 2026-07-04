"""
OPTIONSx — Opsiyon Analiz Terminali (Streamlit sürümü)
Orijinal Flask + custom JS dashboard'un Streamlit'e dönüştürülmüş hali.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────
# SAYFA AYARLARI
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Idea of Money — Opsiyon Analiz Terminali",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────
# KOYU TEMA / ÖZEL CSS  (orijinal renk paletini koruyoruz)
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root{
  --bg:#080c10;--bg2:#0d1117;--card:#111820;--card2:#161e28;
  --bdr:#1e2d3d;--bdr2:#2a4060;
  --t1:#cdd9e5;--t2:#768b9e;--t3:#3d5266;
  --grn:#39d353;--amb:#e3b341;--red:#f85149;--blu:#58a6ff;--prp:#bc8cff;--cyn:#39c5cf;
}

.stApp{background:var(--bg);}
* {font-family:'IBM Plex Sans',sans-serif;}
h1,h2,h3,.mono{font-family:'IBM Plex Mono',monospace !important;}

/* Streamlit'in üst araç çubuğu (menü/deploy) sabit ve şeffaf geldiği için
   başlığın üzerine biniyordu — arka planını sayfa rengiyle eşitleyip
   altındaki içerik boşluğunu artırıyoruz */
header[data-testid="stHeader"]{
  background:var(--bg);
  height:3.2rem;
}
.block-container{padding-top:4rem;max-width:1500px;}

/* Metric kartları */
div[data-testid="stMetric"]{
  background:var(--card);border:1px solid var(--bdr);border-radius:8px;
  padding:12px 14px;
}
div[data-testid="stMetricLabel"]{
  font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--t3);
  letter-spacing:1px;text-transform:uppercase;
}
div[data-testid="stMetricValue"]{
  font-family:'IBM Plex Mono',monospace;color:var(--t1);
}

/* Sentiment / başlık kutuları */
.optx-card{
  background:var(--card);border:1px solid var(--bdr);border-radius:8px;
  padding:18px;margin-bottom:8px;
}
.optx-title{
  font-family:'IBM Plex Mono',monospace;font-size:36px;font-weight:600;
  color:var(--t1);
}
.optx-title .hl{color:var(--grn);}
.optx-section{
  font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;
  color:var(--t3);letter-spacing:2px;text-transform:uppercase;
  margin:18px 0 8px;border-bottom:1px solid var(--bdr);padding-bottom:6px;
}
.pos{color:var(--grn);} .neg{color:var(--red);}

/* Özel gösterge kartları (RSI durum rozeti, yön işaretli SMA/EMA/Bollinger) */
.ind-card{
  background:var(--card);border:1px solid var(--bdr);border-radius:8px;
  padding:12px 14px;height:100%;
}
.ind-label{
  font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--t3);
  letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;
}
.ind-value{
  font-family:'IBM Plex Mono',monospace;font-size:26px;font-weight:600;
  color:var(--t1);line-height:1.2;
}
.badge{
  display:inline-block;padding:2px 10px;border-radius:12px;
  font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;
  margin-top:6px;letter-spacing:.5px;
}
.badge-red{background:rgba(248,81,73,.15);color:var(--red);}
.badge-gray{background:rgba(118,139,158,.15);color:var(--t2);}
.badge-green{background:rgba(57,211,83,.15);color:var(--grn);}
.arrow-up{color:var(--grn);}
.arrow-down{color:var(--red);}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# BACKEND — orijinal app.py'den taşınan hesap fonksiyonları (değişmedi)
# ──────────────────────────────────────────────────────────────────────────

def safe_float(val):
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return None
        return float(val)
    except Exception:
        return None


def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).iloc[-1]


def calc_technicals(hist):
    close = hist['Close']
    volume = hist['Volume']

    rsi = safe_float(calc_rsi(close, 14))
    sma20 = safe_float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else None
    sma50 = safe_float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
    ema20 = safe_float(close.ewm(span=20).mean().iloc[-1])

    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9).mean()
    macd_val = safe_float(macd_line.iloc[-1])
    signal_val = safe_float(signal_line.iloc[-1])
    macd_hist = safe_float((macd_line - signal_line).iloc[-1])

    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = safe_float((bb_mid + 2 * bb_std).iloc[-1])
    bb_lower = safe_float((bb_mid - 2 * bb_std).iloc[-1])
    bb_mid_val = safe_float(bb_mid.iloc[-1])

    high = hist['High']
    low = hist['Low']
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    atr = safe_float(tr.rolling(14).mean().iloc[-1])

    vol_avg20 = safe_float(volume.rolling(20).mean().iloc[-1])
    vol_ratio = safe_float(volume.iloc[-1] / vol_avg20) if vol_avg20 else None

    momentum = safe_float(((close.iloc[-1] / close.iloc[-10]) - 1) * 100) if len(close) >= 10 else None

    lowest_low = low.rolling(14).min()
    highest_high = high.rolling(14).max()
    stoch_k = safe_float(100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10).iloc[-1])

    return {
        "rsi": round(rsi, 2) if rsi else None,
        "sma20": round(sma20, 2) if sma20 else None,
        "sma50": round(sma50, 2) if sma50 else None,
        "ema20": round(ema20, 2) if ema20 else None,
        "macd": round(macd_val, 4) if macd_val else None,
        "macd_signal": round(signal_val, 4) if signal_val else None,
        "macd_hist": round(macd_hist, 4) if macd_hist else None,
        "bb_upper": round(bb_upper, 2) if bb_upper else None,
        "bb_mid": round(bb_mid_val, 2) if bb_mid_val else None,
        "bb_lower": round(bb_lower, 2) if bb_lower else None,
        "atr": round(atr, 2) if atr else None,
        "vol_ratio": round(vol_ratio, 2) if vol_ratio else None,
        "momentum": round(momentum, 2) if momentum else None,
        "stoch_k": round(stoch_k, 2) if stoch_k else None,
    }


def calculate_max_pain_from_chain(calls, puts, current_price):
    try:
        c = calls[['strike', 'openInterest']].copy()
        p = puts[['strike', 'openInterest']].copy()
        strikes = sorted(set(c['strike'].tolist() + p['strike'].tolist()))
        pain = {}
        for s in strikes:
            cp = sum(max(0, s - r['strike']) * r['openInterest'] for _, r in c.iterrows())
            pp = sum(max(0, r['strike'] - s) * r['openInterest'] for _, r in p.iterrows())
            pain[s] = cp + pp
        if pain:
            return round(float(min(pain, key=pain.get)), 2)
    except Exception:
        pass
    return None


def get_sentiment(put_oi, call_oi):
    if call_oi == 0:
        return "Nötr"
    pcr = put_oi / call_oi
    if pcr > 1.5:
        return "Çok Bearish"
    elif pcr > 1.0:
        return "Bearish"
    elif pcr > 0.7:
        return "Nötr"
    elif pcr > 0.4:
        return "Bullish"
    else:
        return "Çok Bullish"


@st.cache_data(ttl=300, show_spinner=False)
def get_price_history(ticker_symbol, period="1y"):
    t = yf.Ticker(ticker_symbol)
    h = t.history(period=period)
    return h


@st.cache_data(ttl=300, show_spinner=False)
def get_option_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)

    info = ticker.info
    hist = ticker.history(period="1y")

    if hist.empty:
        return {"error": f"'{ticker_symbol}' için veri bulunamadı."}

    current_price = float(hist['Close'].iloc[-1])
    prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
    price_change = current_price - prev_close
    price_change_pct = (price_change / prev_close) * 100

    stock_info = {
        "symbol": ticker_symbol.upper(),
        "name": info.get("longName", ticker_symbol.upper()),
        "current_price": round(current_price, 2),
        "price_change": round(price_change, 2),
        "price_change_pct": round(price_change_pct, 2),
        "volume": info.get("volume", 0),
        "market_cap": info.get("marketCap", 0),
        "pe_ratio": safe_float(info.get("trailingPE")),
        "peg_ratio": safe_float(info.get("pegRatio") or info.get("trailingPegRatio")),
        "week_52_high": safe_float(info.get("fiftyTwoWeekHigh")),
        "week_52_low": safe_float(info.get("fiftyTwoWeekLow")),
        "dividend_yield": safe_float(info.get("dividendYield")),
        "beta": safe_float(info.get("beta")),
        "sector": info.get("sector", "—"),
    }

    technicals = calc_technicals(hist)

    expirations = ticker.options
    if not expirations:
        return {"error": f"'{ticker_symbol}' için opsiyon verisi bulunamadı."}

    all_options = []
    expiration_summary = []

    for exp_date in expirations:
        try:
            opt_chain = ticker.option_chain(exp_date)
            calls = opt_chain.calls.copy()
            puts = opt_chain.puts.copy()

            calls['type'] = 'CALL'
            puts['type'] = 'PUT'
            calls['expiration'] = exp_date
            puts['expiration'] = exp_date

            combined = pd.concat([calls, puts], ignore_index=True)
            combined = combined.fillna(0)

            call_oi = int(calls['openInterest'].sum()) if 'openInterest' in calls.columns else 0
            put_oi = int(puts['openInterest'].sum()) if 'openInterest' in puts.columns else 0
            call_vol = int(calls['volume'].sum()) if 'volume' in calls.columns else 0
            put_vol = int(puts['volume'].sum()) if 'volume' in puts.columns else 0

            exp_dt = datetime.strptime(exp_date, "%Y-%m-%d")
            days_to_exp = (exp_dt - datetime.now()).days
            exp_max_pain = calculate_max_pain_from_chain(calls, puts, current_price)

            expiration_summary.append({
                "date": exp_date,
                "days_to_exp": days_to_exp,
                "call_oi": call_oi,
                "put_oi": put_oi,
                "call_volume": call_vol,
                "put_volume": put_vol,
                "put_call_ratio": round(put_oi / call_oi, 2) if call_oi > 0 else 0,
                "total_oi": call_oi + put_oi,
                "max_pain": exp_max_pain,
            })

            for _, row in combined.iterrows():
                strike = float(row.get('strike', 0))
                if strike > current_price * 1.02:
                    moneyness = "OTM" if row['type'] == 'CALL' else "ITM"
                elif strike < current_price * 0.98:
                    moneyness = "ITM" if row['type'] == 'CALL' else "OTM"
                else:
                    moneyness = "ATM"

                all_options.append({
                    "expiration": exp_date,
                    "days_to_exp": days_to_exp,
                    "type": row['type'],
                    "strike": round(strike, 2),
                    "lastPrice": round(float(row.get('lastPrice', 0)), 2),
                    "bid": round(float(row.get('bid', 0)), 2),
                    "ask": round(float(row.get('ask', 0)), 2),
                    "volume": int(float(row.get('volume', 0))),
                    "openInterest": int(float(row.get('openInterest', 0))),
                    "impliedVolatility": round(float(row.get('impliedVolatility', 0)) * 100, 2),
                    "inTheMoney": bool(row.get('inTheMoney', False)),
                    "moneyness": moneyness,
                })
        except Exception:
            continue

    max_pain = expiration_summary[0]["max_pain"] if expiration_summary else None

    calls_data = [o for o in all_options if o['type'] == 'CALL']
    puts_data = [o for o in all_options if o['type'] == 'PUT']

    total_call_oi = sum(o['openInterest'] for o in calls_data)
    total_put_oi = sum(o['openInterest'] for o in puts_data)
    total_call_vol = sum(o['volume'] for o in calls_data)
    total_put_vol = sum(o['volume'] for o in puts_data)

    summary = {
        "total_expirations": len(expirations),
        "total_options": len(all_options),
        "total_call_oi": total_call_oi,
        "total_put_oi": total_put_oi,
        "total_call_volume": total_call_vol,
        "total_put_volume": total_put_vol,
        "overall_pcr": round(total_put_oi / total_call_oi, 3) if total_call_oi > 0 else 0,
        "max_pain": max_pain,
        "sentiment": get_sentiment(total_put_oi, total_call_oi),
    }

    return {
        "stock": stock_info,
        "technicals": technicals,
        "summary": summary,
        "expirations": list(expirations[:20]),
        "expiration_summary": expiration_summary[:20],
        "options": all_options,
    }


# ──────────────────────────────────────────────────────────────────────────
# YARDIMCI BİÇİMLENDİRME FONKSİYONLARI
# ──────────────────────────────────────────────────────────────────────────

def fnum(n):
    if n is None:
        return "—"
    if abs(n) >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.2f}K"
    return f"{n:,.0f}"


PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='IBM Plex Mono', color='#768b9e', size=11),
    margin=dict(t=10, b=40, l=54, r=10),
    xaxis=dict(gridcolor='#1e2d3d', color='#3d5266'),
    yaxis=dict(gridcolor='#1e2d3d', color='#3d5266'),
    legend=dict(bgcolor='#0d1117', bordercolor='#1e2d3d', borderwidth=1,
                font=dict(size=11, color='#cdd9e5')),
    height=320,
)


# ──────────────────────────────────────────────────────────────────────────
# ARAYÜZ — ÜST BAR / ARAMA
# ──────────────────────────────────────────────────────────────────────────

st.markdown('<div class="optx-title">Idea of <span class="hl">Money</span></div>', unsafe_allow_html=True)
st.caption("Opsiyon Analiz Terminali · yfinance verisiyle çalışır")

col_search, col_btn = st.columns([4, 1])
with col_search:
    ticker_input = st.text_input(
        "Hisse sembolü", value=st.session_state.get("ticker", "AAPL"),
        placeholder="Örn: AAPL, TSLA, NVDA", label_visibility="collapsed"
    ).upper().strip()
with col_btn:
    search_clicked = st.button("ANALİZ ET", use_container_width=True, type="primary")

quick_picks = ["AAPL", "TSLA", "NVDA", "SPY", "QQQ", "AMD", "MSFT"]
qp_cols = st.columns(len(quick_picks))
qp_clicked = None
for i, qp in enumerate(quick_picks):
    if qp_cols[i].button(qp, use_container_width=True):
        qp_clicked = qp

active_ticker = qp_clicked or (ticker_input if search_clicked else st.session_state.get("active_ticker"))
if active_ticker:
    st.session_state["active_ticker"] = active_ticker
    st.session_state["ticker"] = active_ticker

# ──────────────────────────────────────────────────────────────────────────
# VERİ ÇEKME + GÖSTERİM
# ──────────────────────────────────────────────────────────────────────────

if not st.session_state.get("active_ticker"):
    st.info("Yukarıdan bir hisse sembolü girin veya hızlı seçeneklerden birine tıklayın.")
    st.stop()

ticker_symbol = st.session_state["active_ticker"]

with st.spinner(f"{ticker_symbol} için veriler çekiliyor..."):
    try:
        data = get_option_data(ticker_symbol)
    except Exception as e:
        st.error(f"Veri çekilirken hata oluştu: {e}")
        st.stop()

if "error" in data:
    st.error(data["error"])
    st.stop()

stock = data["stock"]
tech = data["technicals"]
summary = data["summary"]
options = data["options"]
exp_summary = data["expiration_summary"]

# ── HİSSE BAŞLIĞI ──
hcol1, hcol2 = st.columns([3, 1])
with hcol1:
    st.markdown(f"### {stock['symbol']} · {stock['name']}")
    st.caption(stock['sector'])
with hcol2:
    change_class = "pos" if stock['price_change'] >= 0 else "neg"
    arrow = "▲" if stock['price_change'] >= 0 else "▼"
    st.markdown(
        f"<div style='text-align:right'>"
        f"<div style='font-family:IBM Plex Mono;font-size:30px;font-weight:600'>${stock['current_price']}</div>"
        f"<div class='{change_class}' style='font-family:IBM Plex Mono'>{arrow} {abs(stock['price_change'])} ({stock['price_change_pct']}%)</div>"
        f"</div>", unsafe_allow_html=True
    )

# ── FİYAT GRAFİĞİ ──
st.markdown('<div class="optx-section">Fiyat Grafiği</div>', unsafe_allow_html=True)

period_options = {"1 Ay": "1mo", "3 Ay": "3mo", "6 Ay": "6mo", "1 Yıl": "1y", "2 Yıl": "2y"}
period_label = st.radio("Aralık", options=list(period_options.keys()), index=3,
                         horizontal=True, key="price_period", label_visibility="collapsed")
selected_period = period_options[period_label]

price_hist = get_price_history(ticker_symbol, selected_period)

if price_hist.empty:
    st.info("Bu hisse için fiyat geçmişi bulunamadı.")
else:
    price_start = float(price_hist['Close'].iloc[0])
    price_end = float(price_hist['Close'].iloc[-1])
    line_color = '#39d353' if price_end >= price_start else '#f85149'
    fill_color = 'rgba(57,211,83,0.10)' if price_end >= price_start else 'rgba(248,81,73,0.10)'

    fig_price = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.75, 0.25], vertical_spacing=0.03,
    )

    fig_price.add_trace(go.Scatter(
        x=price_hist.index, y=price_hist['Close'],
        mode='lines', line=dict(color=line_color, width=2),
        fill='tozeroy', fillcolor=fill_color,
        name="Kapanış", showlegend=False,
        hovertemplate='%{x|%d %b %Y}<br>$%{y:.2f}<extra></extra>',
    ), row=1, col=1)

    vol_colors = ['#39d353' if c >= o else '#f85149'
                  for o, c in zip(price_hist['Open'], price_hist['Close'])]
    fig_price.add_trace(go.Bar(
        x=price_hist.index, y=price_hist['Volume'],
        marker_color=vol_colors, marker_line_width=0,
        name="Hacim", showlegend=False,
    ), row=2, col=1)

    price_min = float(price_hist['Close'].min())
    price_max = float(price_hist['Close'].max())
    price_pad = (price_max - price_min) * 0.08 or price_max * 0.02
    y_range = [price_min - price_pad, price_max + price_pad]

    fig_price.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='IBM Plex Mono', color='#768b9e', size=11),
        margin=dict(t=10, b=30, l=54, r=10),
        height=480,
        xaxis_rangeslider_visible=False,
        xaxis2=dict(gridcolor='#1e2d3d', color='#3d5266'),
        yaxis=dict(gridcolor='#1e2d3d', color='#3d5266', title="Fiyat ($)", range=y_range),
        yaxis2=dict(gridcolor='#1e2d3d', color='#3d5266', title="Hacim"),
    )
    fig_price.update_xaxes(gridcolor='#1e2d3d', color='#3d5266')

    st.plotly_chart(fig_price, use_container_width=True)

# ── TEMEL VERİLER ──
st.markdown('<div class="optx-section">Temel Veriler</div>', unsafe_allow_html=True)
m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
m1.metric("Hacim", fnum(stock['volume']))
m2.metric("Piyasa Değeri", fnum(stock['market_cap']))
m3.metric("F/K Oranı", stock['pe_ratio'] or "—")
m4.metric("PEG Oranı", stock['peg_ratio'] or "—")
m5.metric("52H Yüksek", f"${stock['week_52_high']}" if stock['week_52_high'] else "—")
m6.metric("52H Düşük", f"${stock['week_52_low']}" if stock['week_52_low'] else "—")
m7.metric("Beta", stock['beta'] or "—")

# ── TEKNİK GÖSTERGELER ──
st.markdown('<div class="optx-section">Teknik Göstergeler</div>', unsafe_allow_html=True)

cur_price = stock['current_price']


def rsi_badge(rsi_val):
    if rsi_val is None:
        return '<span class="badge badge-gray">Veri yok</span>'
    if rsi_val >= 70:
        return '<span class="badge badge-red">Aşırı Alım</span>'
    if rsi_val <= 30:
        return '<span class="badge badge-green">Aşırı Satım</span>'
    return '<span class="badge badge-gray">Nötr</span>'


def render_ind_card(col, label, value, badge_html):
    val_txt = value if value is not None else "—"
    col.markdown(
        f'<div class="ind-card"><div class="ind-label">{label}</div>'
        f'<div class="ind-value">{val_txt}</div>{badge_html}</div>',
        unsafe_allow_html=True
    )


t1, t2, t3, t4 = st.columns(4)
render_ind_card(t1, "RSI (14)", tech['rsi'], rsi_badge(tech['rsi']))
t2.metric("SMA 20", f"${tech['sma20']}" if tech['sma20'] else "—",
          delta=round(cur_price - tech['sma20'], 2) if tech['sma20'] else None)
t3.metric("SMA 50", f"${tech['sma50']}" if tech['sma50'] else "—",
          delta=round(cur_price - tech['sma50'], 2) if tech['sma50'] else None)
t4.metric("EMA 20", f"${tech['ema20']}" if tech['ema20'] else "—",
          delta=round(cur_price - tech['ema20'], 2) if tech['ema20'] else None)

b1, b2, b3 = st.columns(3)
b1.metric("Bollinger Üst", f"${tech['bb_upper']}" if tech['bb_upper'] else "—",
          delta=round(cur_price - tech['bb_upper'], 2) if tech['bb_upper'] else None)
b2.metric("Bollinger Orta", f"${tech['bb_mid']}" if tech['bb_mid'] else "—",
          delta=round(cur_price - tech['bb_mid'], 2) if tech['bb_mid'] else None)
b3.metric("Bollinger Alt", f"${tech['bb_lower']}" if tech['bb_lower'] else "—",
          delta=round(cur_price - tech['bb_lower'], 2) if tech['bb_lower'] else None)

# ── SENTIMENT / MAX PAIN ──
st.markdown('<div class="optx-section">Piyasa Hissiyatı</div>', unsafe_allow_html=True)
s1, s2, s3 = st.columns([2, 1, 1])
with s1:
    pcr = summary['overall_pcr']
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pcr,
        title={'text': f"Put/Call Oranı — {summary['sentiment']}", 'font': {'family': 'IBM Plex Mono', 'size': 13, 'color': '#cdd9e5'}},
        gauge={
            'axis': {'range': [0, 2], 'tickcolor': '#3d5266'},
            'bar': {'color': '#58a6ff'},
            'bgcolor': '#111820',
            'steps': [
                {'range': [0, 0.4], 'color': '#0a1f10'},
                {'range': [0.4, 0.7], 'color': '#1a2a10'},
                {'range': [0.7, 1.0], 'color': '#1f1c0a'},
                {'range': [1.0, 1.5], 'color': '#1f130a'},
                {'range': [1.5, 2.0], 'color': '#1f0a0a'},
            ],
        },
        number={'font': {'family': 'IBM Plex Mono', 'color': '#cdd9e5'}}
    ))
    fig_gauge.update_layout(**{**PLOTLY_LAYOUT, 'height': 220})
    st.plotly_chart(fig_gauge, use_container_width=True)
with s2:
    st.metric("Toplam Put OI", fnum(summary['total_put_oi']))
    st.metric("Toplam Call OI", fnum(summary['total_call_oi']))
with s3:
    st.metric("Max Pain", f"${summary['max_pain']}" if summary['max_pain'] else "—")
    st.metric("Toplam Vade Sayısı", summary['total_expirations'])

# ── GRAFİKLER ──
st.markdown('<div class="optx-section">Grafikler</div>', unsafe_allow_html=True)
near_exp = data["expirations"][0]
near = [o for o in options if o["expiration"] == near_exp]
calls_near = sorted([o for o in near if o["type"] == "CALL"], key=lambda x: x["strike"])
puts_near = sorted([o for o in near if o["type"] == "PUT"], key=lambda x: x["strike"])

g1, g2 = st.columns(2)
with g1:
    st.caption("En Yüksek Açık Pozisyon (OI) ve Hacim — Tüm Vadeler")
    all_opts_df = pd.DataFrame(options)

    top_oi = all_opts_df.sort_values("openInterest", ascending=False).head(5)
    top_vol = all_opts_df.sort_values("volume", ascending=False).head(5)

    st.markdown("**🏆 En Yüksek Açık Pozisyon (Top 5)**")
    st.dataframe(
        top_oi[["expiration", "type", "strike", "openInterest", "volume", "impliedVolatility"]].rename(columns={
            "expiration": "Vade", "type": "Tip", "strike": "Strike",
            "openInterest": "Açık Poz.", "volume": "Hacim", "impliedVolatility": "IV %"
        }),
        use_container_width=True, hide_index=True, height=210,
    )

    st.markdown("**🔥 En Yüksek Hacim (Top 5)**")
    st.dataframe(
        top_vol[["expiration", "type", "strike", "volume", "openInterest", "impliedVolatility"]].rename(columns={
            "expiration": "Vade", "type": "Tip", "strike": "Strike",
            "volume": "Hacim", "openInterest": "Açık Poz.", "impliedVolatility": "IV %"
        }),
        use_container_width=True, hide_index=True, height=210,
    )

with g2:
    st.caption(f"Zımni Volatilite (IV) Eğrisi · Vade: {near_exp}")
    cIV = [o for o in calls_near if o["impliedVolatility"] > 0]
    pIV = [o for o in puts_near if o["impliedVolatility"] > 0]
    fig_iv = go.Figure()
    fig_iv.add_scatter(x=[o["strike"] for o in cIV], y=[o["impliedVolatility"] for o in cIV],
                        mode="lines+markers", name="CALL IV%", line=dict(color="#39d353", width=2))
    fig_iv.add_scatter(x=[o["strike"] for o in pIV], y=[o["impliedVolatility"] for o in pIV],
                        mode="lines+markers", name="PUT IV%", line=dict(color="#f85149", width=2))
    fig_iv.update_layout(**{**PLOTLY_LAYOUT, 'yaxis': {**PLOTLY_LAYOUT['yaxis'], 'ticksuffix': '%'}})
    st.plotly_chart(fig_iv, use_container_width=True)

g3, g4 = st.columns(2)
with g3:
    st.caption("Vadelere Göre Açık Pozisyon")
    xlabels = [datetime.strptime(e["date"], "%Y-%m-%d").strftime("%d %b'%y") for e in exp_summary]
    fig_exp = go.Figure()
    fig_exp.add_bar(x=xlabels, y=[e["call_oi"] for e in exp_summary], name="Call OI", marker_color="rgba(57,211,83,.75)")
    fig_exp.add_bar(x=xlabels, y=[e["put_oi"] for e in exp_summary], name="Put OI", marker_color="rgba(248,81,73,.65)")
    fig_exp.update_layout(**{**PLOTLY_LAYOUT, 'barmode': 'group',
                              'xaxis': {**PLOTLY_LAYOUT['xaxis'], 'tickangle': -45}})
    st.plotly_chart(fig_exp, use_container_width=True)

with g4:
    st.caption("Call / Put Hacim Dağılımı")
    fig_pie = go.Figure(go.Pie(
        labels=["Call Hacmi", "Put Hacmi"],
        values=[summary['total_call_volume'], summary['total_put_volume']],
        hole=0.55,
        marker=dict(colors=["#2ea043", "#da3633"], line=dict(color="#080c10", width=3)),
        textposition='none',
        hoverinfo='label+value+percent',
    ))
    fig_pie.update_layout(**{**PLOTLY_LAYOUT, 'height': 320, 'margin': dict(t=16, b=16, l=16, r=16)})
    st.plotly_chart(fig_pie, use_container_width=True)

# ── OPSİYON TABLOSU (Vade bazlı dropdown) ──
st.markdown('<div class="optx-section">Opsiyon Zinciri</div>', unsafe_allow_html=True)
st.caption("Her vadeyi genişleterek o vadenin özetini ve strike bazlı detayını görebilirsin.")

DISPLAY_COLS = ["expiration", "days_to_exp", "type", "strike", "lastPrice", "bid", "ask",
                 "volume", "openInterest", "impliedVolatility", "moneyness"]
DISPLAY_RENAME = {
    "expiration": "Vade", "days_to_exp": "Gün", "type": "Tip", "strike": "Strike",
    "lastPrice": "Son Fiyat", "bid": "Alış", "ask": "Satış", "volume": "Hacim",
    "openInterest": "Açık Poz.", "impliedVolatility": "IV %", "moneyness": "Durum"
}

all_options_df = pd.DataFrame(options)

# ── Tüm vadeleri tek seferde indirme ──
all_cap_col, all_btn_col = st.columns([4, 1])
with all_cap_col:
    st.caption(f"Toplam {len(all_options_df)} kayıt · {len(exp_summary)} vade")
with all_btn_col:
    all_csv_bytes = all_options_df[DISPLAY_COLS].rename(columns=DISPLAY_RENAME).to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇ Tüm Vadeleri İndir",
        data=all_csv_bytes,
        file_name=f"{ticker_symbol}_opsiyonlar_tum-vadeler.csv",
        mime="text/csv",
        use_container_width=True,
        key="dl_all",
    )

for e in exp_summary:
    exp_date = e["date"]
    pcr = e["put_call_ratio"]
    sentiment_label = get_sentiment(e["put_oi"], e["call_oi"])

    max_pain_txt = f"${e['max_pain']}" if e.get("max_pain") else "—"

    pcr_md = f":green[P/C {pcr}]" if pcr < 1 else f":red[P/C {pcr}]"
    if "Bullish" in sentiment_label:
        sent_md = f":green[{sentiment_label}]"
    elif "Bearish" in sentiment_label:
        sent_md = f":red[{sentiment_label}]"
    else:
        sent_md = f":gray[{sentiment_label}]"
    max_pain_md = f':color[Max Pain {max_pain_txt}]{{foreground="#0047AB"}}'

    label = (f"📅  {exp_date}  ·  {e['days_to_exp']} gün  ·  "
             f"{pcr_md}  ·  {sent_md}  ·  {max_pain_md}  ·  Toplam OI {fnum(e['total_oi'])}")

    with st.expander(label, expanded=False):
        # ── Vade özeti ──
        se1, se2, se3, se4, se5, se6, se7 = st.columns(7)
        se1.metric("Call OI", fnum(e["call_oi"]))
        se2.metric("Put OI", fnum(e["put_oi"]))
        se3.metric("Put/Call Oranı", pcr)
        se4.metric("Call Hacim", fnum(e["call_volume"]))
        se5.metric("Put Hacim", fnum(e["put_volume"]))
        se6.metric("Toplam Açık Poz.", fnum(e["total_oi"]))
        se7.metric("Max Pain", f"${e['max_pain']}" if e.get("max_pain") else "—")

        st.markdown("")

        # ── Detay filtreleri (bu vadeye özel) ──
        key_prefix = exp_date.replace("-", "")
        f2, f3 = st.columns([1, 2])
        with f2:
            type_filter = st.radio("Tip", options=["Tümü", "CALL", "PUT"],
                                    horizontal=True, key=f"type_{key_prefix}")
        with f3:
            strike_search = st.text_input("Strike fiyatına göre ara", placeholder="Örn: 150",
                                           key=f"strike_{key_prefix}")

        df_exp = all_options_df[all_options_df["expiration"] == exp_date].copy()
        if type_filter != "Tümü":
            df_exp = df_exp[df_exp["type"] == type_filter]
        if strike_search:
            try:
                val = float(strike_search)
                df_exp = df_exp[df_exp["strike"].astype(str).str.contains(strike_search) | (df_exp["strike"] == val)]
            except ValueError:
                pass

        df_exp_display = df_exp[DISPLAY_COLS].rename(columns=DISPLAY_RENAME)

        cap_col, btn_col = st.columns([4, 1])
        with cap_col:
            st.caption(f"{len(df_exp_display)} kayıt bulundu")
        with btn_col:
            csv_bytes = df_exp_display.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="⬇ Bu Vadeyi İndir",
                data=csv_bytes,
                file_name=f"{ticker_symbol}_opsiyonlar_{exp_date}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"dl_{key_prefix}",
            )

        st.dataframe(
            df_exp_display,
            use_container_width=True,
            height=420,
        )
