import yfinance as yf

def get_live_price(symbol):
    try:
        stock = yf.Ticker(symbol + ".NS")  # NSE
        price = stock.info.get("regularMarketPrice")
        return price if price else 0
    except Exception as e:
        print("Live price error:", e)
        return 0
