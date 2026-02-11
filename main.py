import yfinance as yf
import requests
import os
from datetime import datetime
import pytz

# --- CONFIGURACIÓN ---
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
    # Obtenemos la hora de México
    tz = pytz.timezone('America/Mexico_City')
    now = datetime.now(tz)
    # Formato: 10 Feb 02:30 PM
    return now.strftime("%d %b %I:%M %p")

def send_to_trmnl(usd, eur, date_str):
    if not TRMNL_WEBHOOK_URL:
        print("Error: No hay URL de Webhook.")
        return

    payload = {
        "merge_variables": {
            "usd": usd,
            "eur": eur,
            "updated_at": date_str
        }
    }
    
    try:
        r = requests.post(TRMNL_WEBHOOK_URL, json=payload)
        print(f"Enviado a TRMNL. Datos: USD {usd} | EUR {eur} | Fecha {date_str}")
    except Exception as e:
         print(f"Error enviando a TRMNL: {e}")

if __name__ == "__main__":
    print("--- Obteniendo datos Financieros ---")
    
    usd_price = get_yahoo_rate("MXN=X")
    eur_price = get_yahoo_rate("EURMXN=X")
    current_time = get_current_time()
    
    if usd_price and eur_price:
        send_to_trmnl(usd_price, eur_price, current_time)
    else:
        print("Error en la obtención de datos.")
