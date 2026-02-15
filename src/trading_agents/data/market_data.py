from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


class MarketDataProvider:
    def get_historical_data(
        self, ticker: str, period_days: int = 90, end_date: str | None = None
    ) -> pd.DataFrame:
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        start = end - timedelta(days=period_days)
        stock = yf.Ticker(ticker)
        df = stock.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
        if df.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        return df

    def get_stock_info(self, ticker: str) -> dict:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", None),
            "forward_pe": info.get("forwardPE", None),
            "dividend_yield": info.get("dividendYield", None),
            "beta": info.get("beta", None),
            "52_week_high": info.get("fiftyTwoWeekHigh", None),
            "52_week_low": info.get("fiftyTwoWeekLow", None),
            "avg_volume": info.get("averageVolume", None),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", None)),
            "revenue_growth": info.get("revenueGrowth", None),
            "profit_margins": info.get("profitMargins", None),
            "debt_to_equity": info.get("debtToEquity", None),
            "return_on_equity": info.get("returnOnEquity", None),
            "free_cash_flow": info.get("freeCashflow", None),
        }

    def get_recent_news(self, ticker: str) -> list[dict]:
        stock = yf.Ticker(ticker)
        news = stock.news or []
        results = []
        for item in news[:10]:
            content = item.get("content", {})
            results.append({
                "title": content.get("title", item.get("title", "No title")),
                "publisher": content.get("provider", {}).get(
                    "displayName", item.get("publisher", "Unknown")
                ),
                "published": content.get("pubDate", ""),
                "summary": content.get("summary", ""),
            })
        return results

    def get_financials(self, ticker: str) -> dict:
        stock = yf.Ticker(ticker)
        result = {}
        income = stock.financials
        if income is not None and not income.empty:
            result["income_statement"] = income.head(4).to_dict()
        balance = stock.balance_sheet
        if balance is not None and not balance.empty:
            result["balance_sheet"] = balance.head(4).to_dict()
        cashflow = stock.cashflow
        if cashflow is not None and not cashflow.empty:
            result["cash_flow"] = cashflow.head(4).to_dict()
        return result
