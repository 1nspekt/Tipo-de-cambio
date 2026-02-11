import yfinance as yf
import requests
import os
from datetime import datetime
import pytz

TRMNL_WEBHOOK_URL = os.environ.get("TRMNL_WEBHOOK_URL")

def get_yahoo_rate(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.fast_info['last_price']
        return "{:.2f}".format(price)
    except Exception as e:
        print(f"Error obteniendo {ticker}: {e}")
        return None

def get_current_time():
    tz = pytz.timezone('America/Mexico_City')
    return datetime.now(tz).strftime("%d %b, %I:%M %p")

def send_to_trmnl(usd, eur, date_str):
    if not TRMNL_WEBHOOK_URL: return

    # Creamos las frases con el toque humano que pediste
    frase_usd = f"El tipo de cambio es de {usd} Pesos Mexicanos (MXN) por cada Dólar estadounidense (USD)."
    frase_eur = f"Y de {eur} Pesos por cada Euro."

    payload = {
        "merge_variables": {
            "texto_usd": frase_usd,
            "texto_eur": frase_eur,
            "updated_at": date_str
        }
    }
    
    requests.post(TRMNL_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    usd_val = get_yahoo_rate("MXN=X")
    eur_val = get_yahoo_rate("EURMXN=X")
    if usd_val and eur_val:
        send_to_trmnl(usd_val, eur_val, get_current_time())
