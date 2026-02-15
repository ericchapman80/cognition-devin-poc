import sys
from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from trading_agents.config import AppConfig  # noqa: E402
from trading_agents.graph.trading_graph import TradingAgentsGraph  # noqa: E402

st.set_page_config(page_title="AI Trading Agents", page_icon="📈", layout="wide")

SIGNAL_COLORS = {
    "strong_buy": "#00C853",
    "buy": "#4CAF50",
    "hold": "#FFC107",
    "sell": "#FF5722",
    "strong_sell": "#D50000",
    "neutral": "#9E9E9E",
}


def init_session_state():
    defaults = {
        "decision": None,
        "analysis_running": False,
        "step_log": [],
        "price_data": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_sidebar():
    st.sidebar.title("Configuration")

    ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").strip().upper()
    date = st.sidebar.date_input("Analysis Date", value=datetime.now().date())

    st.sidebar.markdown("---")
    st.sidebar.subheader("LLM Settings")
    provider = st.sidebar.selectbox("LLM Provider", ["ollama", "openai"], index=0)
    model = st.sidebar.text_input(
        "Model Name", value="llama3" if provider == "ollama" else "gpt-4o-mini"
    )
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.3, 0.1)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Trading Settings")
    risk = st.sidebar.selectbox(
        "Risk Tolerance", ["conservative", "moderate", "aggressive"], index=1
    )
    debate_rounds = st.sidebar.slider("Debate Rounds", 1, 5, 2)
    period_days = st.sidebar.slider("Analysis Period (days)", 30, 365, 90)

    return {
        "ticker": ticker,
        "date": date.strftime("%Y-%m-%d"),
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "risk": risk,
        "debate_rounds": debate_rounds,
        "period_days": period_days,
    }


def create_candlestick_chart(price_data, ticker, indicators=None):
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f"{ticker} Price", "Volume", "RSI"),
    )

    fig.add_trace(
        go.Candlestick(
            x=price_data.index,
            open=price_data["Open"],
            high=price_data["High"],
            low=price_data["Low"],
            close=price_data["Close"],
            name="Price",
        ),
        row=1,
        col=1,
    )

    if indicators and indicators.get("sma_20") is not None:
        import pandas_ta as ta

        sma20 = ta.sma(price_data["Close"], length=20)
        if sma20 is not None:
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=sma20,
                    name="SMA 20",
                    line=dict(color="orange", width=1),
                ),
                row=1,
                col=1,
            )

    if indicators and indicators.get("sma_50") is not None:
        import pandas_ta as ta

        sma50 = ta.sma(price_data["Close"], length=50)
        if sma50 is not None:
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=sma50,
                    name="SMA 50",
                    line=dict(color="blue", width=1),
                ),
                row=1,
                col=1,
            )

    if indicators and indicators.get("bb_upper") is not None:
        import pandas_ta as ta

        bbands = ta.bbands(price_data["Close"], length=20)
        if bbands is not None and not bbands.empty:
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=bbands.iloc[:, 0],
                    name="BB Upper",
                    line=dict(color="gray", width=1, dash="dot"),
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=bbands.iloc[:, 2],
                    name="BB Lower",
                    line=dict(color="gray", width=1, dash="dot"),
                    fill="tonexty",
                    fillcolor="rgba(128,128,128,0.1)",
                ),
                row=1,
                col=1,
            )

    colors = [
        "#26A69A" if c >= o else "#EF5350"
        for o, c in zip(price_data["Open"], price_data["Close"])
    ]
    fig.add_trace(
        go.Bar(x=price_data.index, y=price_data["Volume"], name="Volume", marker_color=colors),
        row=2,
        col=1,
    )

    if indicators and indicators.get("rsi") is not None:
        import pandas_ta as ta

        rsi = ta.rsi(price_data["Close"], length=14)
        if rsi is not None:
            fig.add_trace(
                go.Scatter(
                    x=price_data.index,
                    y=rsi,
                    name="RSI",
                    line=dict(color="purple", width=1.5),
                ),
                row=3,
                col=1,
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def create_gauge_chart(value, title, min_val=0, max_val=100):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": title},
            gauge={
                "axis": {"range": [min_val, max_val]},
                "bar": {"color": "#1E88E5"},
                "steps": [
                    {"range": [0, 30], "color": "#EF5350"},
                    {"range": [30, 70], "color": "#FFC107"},
                    {"range": [70, 100], "color": "#4CAF50"},
                ],
            },
        )
    )
    fig.update_layout(height=250, template="plotly_dark")
    return fig


def create_signal_distribution_chart(analyst_reports):
    if not analyst_reports:
        return None
    labels = []
    values_list = []
    colors = []
    for report in analyst_reports:
        role_val = report.agent_role
        role = role_val.value if hasattr(role_val, "value") else str(role_val)
        labels.append(role.replace("_", " ").title())
        values_list.append(report.confidence)
        colors.append(SIGNAL_COLORS.get(report.signal, "#9E9E9E"))

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values_list,
            marker_color=colors,
            text=[r.signal.replace("_", " ").upper() for r in analyst_reports],
            textposition="auto",
        )
    )
    fig.update_layout(
        title="Agent Signals & Confidence",
        yaxis_title="Confidence %",
        height=350,
        template="plotly_dark",
    )
    return fig


def render_stock_info(stock_info):
    cols = st.columns(4)
    metrics = [
        ("Current Price", stock_info.get("current_price"), "${:,.2f}"),
        ("Market Cap", stock_info.get("market_cap"), "${:,.0f}"),
        ("P/E Ratio", stock_info.get("pe_ratio"), "{:.2f}"),
        ("Beta", stock_info.get("beta"), "{:.2f}"),
    ]
    for i, (label, val, fmt) in enumerate(metrics):
        with cols[i]:
            if val is not None:
                st.metric(label, fmt.format(val))
            else:
                st.metric(label, "N/A")

    cols2 = st.columns(4)
    metrics2 = [
        ("Revenue Growth", stock_info.get("revenue_growth"), "{:.2%}"),
        ("Profit Margins", stock_info.get("profit_margins"), "{:.2%}"),
        ("Debt/Equity", stock_info.get("debt_to_equity"), "{:.2f}"),
        ("Dividend Yield", stock_info.get("dividend_yield"), "{:.2%}"),
    ]
    for i, (label, val, fmt) in enumerate(metrics2):
        with cols2[i]:
            if val is not None:
                st.metric(label, fmt.format(val))
            else:
                st.metric(label, "N/A")


def render_decision_badge(decision):
    signal = decision.final_signal.replace("_", " ").upper()
    color = SIGNAL_COLORS.get(decision.final_signal, "#9E9E9E")
    st.markdown(
        f"""
        <div style="text-align:center; padding:20px; border-radius:10px;
                    background:linear-gradient(135deg, {color}22, {color}44);
                    border: 2px solid {color};">
            <h1 style="color:{color}; margin:0;">{signal}</h1>
            <h3 style="color:#ccc; margin:5px 0;">Confidence: {decision.confidence:.1f}%</h3>
            <p style="color:#999;">Ticker: {decision.ticker}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    init_session_state()

    st.title("📈 AI Trading Agents")
    st.caption("Multi-Agent LLM Stock Trading Advisor")

    params = render_sidebar()

    run_analysis = st.sidebar.button(
        "🚀 Run Analysis", type="primary", use_container_width=True
    )

    if run_analysis:
        st.session_state.step_log = []
        st.session_state.analysis_running = True

        config = AppConfig.from_env()
        config.llm.provider = params["provider"]
        config.llm.model = params["model"]
        config.llm.temperature = params["temperature"]
        config.trading.risk_tolerance = params["risk"]
        config.trading.max_debate_rounds = params["debate_rounds"]
        config.trading.analysis_period_days = params["period_days"]

        errors = config.validate()
        if errors:
            for err in errors:
                st.error(f"Config error: {err}")
            st.session_state.analysis_running = False
            return

        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            step_count = [0]
            total_steps = 7

            def on_step(step):
                if step.status == "completed":
                    step_count[0] += 1
                    progress_bar.progress(min(step_count[0] / total_steps, 1.0))
                    status_text.info(f"✅ {step.step_name} completed")
                    st.session_state.step_log.append(
                        {"name": step.step_name, "status": "completed"}
                    )
                elif step.status == "error":
                    step_count[0] += 1
                    progress_bar.progress(min(step_count[0] / total_steps, 1.0))
                    status_text.error(f"❌ {step.step_name}: {step.error}")
                    st.session_state.step_log.append(
                        {"name": step.step_name, "status": "error", "error": step.error}
                    )
                else:
                    status_text.info(f"⏳ {step.step_name}...")

            graph = TradingAgentsGraph(config, on_step=on_step)

            try:
                decision = graph.propagate(params["ticker"], params["date"])
                st.session_state.decision = decision
                st.session_state.price_data = decision.price_data
                progress_bar.progress(1.0)
                status_text.success("Analysis complete!")
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.session_state.analysis_running = False
                return

        st.session_state.analysis_running = False

    decision = st.session_state.decision
    if decision is None:
        st.info(
            "Configure your settings in the sidebar and click **Run Analysis** to get started."
        )
        st.markdown("---")
        st.subheader("Quick Start")
        st.markdown(
            """
            1. **Enter a stock ticker** (e.g., AAPL, MSFT, NVDA)
            2. **Choose your LLM provider** (Ollama for local, OpenAI for cloud)
            3. **Set risk tolerance** and analysis parameters
            4. **Click Run Analysis** to get AI-powered trading insights

            **Prerequisites:**
            - Install [Ollama](https://ollama.com) and run `ollama pull llama3`
            - Or set your OpenAI API key in `.env`
            """
        )
        return

    st.markdown("---")
    render_decision_badge(decision)

    st.markdown("---")
    if decision.stock_info:
        st.subheader(
            f"📊 {decision.stock_info.get('name', decision.ticker)} "
            f"({decision.stock_info.get('sector', '')})"
        )
        render_stock_info(decision.stock_info)

    st.markdown("---")
    tab_chart, tab_agents, tab_debate, tab_risk, tab_log = st.tabs(
        ["📈 Chart", "🤖 Agents", "⚔️ Debate", "🛡️ Risk", "📋 Log"]
    )

    with tab_chart:
        price_data = st.session_state.price_data
        if price_data is not None and not price_data.empty:
            chart = create_candlestick_chart(
                price_data, decision.ticker, decision.indicators
            )
            st.plotly_chart(chart, use_container_width=True)

            if decision.indicators:
                st.subheader("Technical Indicators")
                ind = decision.indicators
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if ind.get("rsi") is not None:
                        st.plotly_chart(
                            create_gauge_chart(ind["rsi"], "RSI"), use_container_width=True
                        )
                with col2:
                    if ind.get("current_price") and ind.get("sma_20"):
                        price_v = ind["current_price"]
                        sma_v = ind["sma_20"]
                        pct_from_sma = ((price_v - sma_v) / sma_v) * 100
                        st.metric("Price vs SMA20", f"{pct_from_sma:+.2f}%")
                    if ind.get("macd") is not None:
                        st.metric("MACD", f"{ind['macd']:.4f}")
                with col3:
                    if ind.get("atr") is not None:
                        st.metric("ATR (Volatility)", f"{ind['atr']:.4f}")
                    if ind.get("volume_trend") is not None:
                        st.metric("Volume Trend", f"{ind['volume_trend']:.2f}x avg")
                with col4:
                    if ind.get("price_change_pct") is not None:
                        st.metric("Period Change", f"{ind['price_change_pct']:+.2f}%")
                    if ind.get("bb_upper") is not None and ind.get("bb_lower") is not None:
                        st.metric(
                            "Bollinger Range",
                            f"${ind['bb_lower']:.2f} - ${ind['bb_upper']:.2f}",
                        )

                if decision.signals:
                    st.subheader("Signal Summary")
                    for key, value in decision.signals.items():
                        if key not in ("overall", "confidence"):
                            if "bullish" in value or "bounce" in value:
                                st.success(f"**{key.upper()}**: {value}")
                            elif "bearish" in value or "reversal" in value:
                                st.error(f"**{key.upper()}**: {value}")
                            else:
                                st.info(f"**{key.upper()}**: {value}")

    with tab_agents:
        if decision.analyst_reports:
            chart = create_signal_distribution_chart(decision.analyst_reports)
            if chart:
                st.plotly_chart(chart, use_container_width=True)

            for report in decision.analyst_reports:
                role_val = report.agent_role
                role = role_val.value if hasattr(role_val, "value") else str(role_val)
                with st.expander(
                    f"🤖 {role.replace('_', ' ').title()} — "
                    f"{report.signal.replace('_', ' ').upper()} ({report.confidence:.0f}%)"
                ):
                    st.markdown(report.summary)

        if decision.trader_summary:
            st.subheader("Trader Decision")
            st.markdown(decision.trader_summary)

    with tab_debate:
        if decision.debate_history:
            for i, entry in enumerate(decision.debate_history):
                st.subheader(f"Round {i + 1}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        f"<div style='border-left:4px solid #4CAF50; padding-left:12px;'>"
                        f"<h4 style='color:#4CAF50;'>🐂 Bull Case</h4>"
                        f"{entry.get('bull', 'N/A')}</div>",
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown(
                        f"<div style='border-left:4px solid #EF5350; padding-left:12px;'>"
                        f"<h4 style='color:#EF5350;'>🐻 Bear Case</h4>"
                        f"{entry.get('bear', 'N/A')}</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown("---")
        else:
            st.info("No debate history available. Run an analysis to see the bull/bear debate.")

    with tab_risk:
        if decision.risk_assessment:
            st.subheader("Risk Assessment")
            st.markdown(decision.risk_assessment)
        else:
            st.info("No risk assessment available.")

    with tab_log:
        st.subheader("Analysis Pipeline Log")
        for entry in st.session_state.step_log:
            if entry["status"] == "completed":
                st.success(f"✅ {entry['name']}")
            else:
                st.error(f"❌ {entry['name']}: {entry.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
