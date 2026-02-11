import yfinance as yf
import requests
import os

# --- CONFIGURACIÓN ---
TRMNL_WEBHOOK_URL = os.environ.get("TRMNL_WEBHOOK_URL")

def get_yahoo_rate(ticker):
    try:
        # Descargamos la info del ticker (Par de monedas)
        # 'regularMarketPrice' suele ser el precio más actual
        stock = yf.Ticker(ticker)
        price = stock.fast_info['last_price']
        
        # Formateamos a 2 decimales (ej: 17.23)
        return "{:.2f}".format(price)
    except Exception as e:
        print(f"Error obteniendo {ticker}: {e}")
        return None

def send_to_trmnl(usd, eur):
    if not TRMNL_WEBHOOK_URL:
        print("Error: No hay URL de Webhook.")
        return

    payload = {
        "merge_variables": {
            "usd": usd,
            "eur": eur
        }
    }
    
    try:
        r = requests.post(TRMNL_WEBHOOK_URL, json=payload)
        print(f"Enviado a TRMNL (Status {r.status_code})")
        print(f"Datos -> Dólar: ${usd} | Euro: €{eur}")
    except Exception as e:
         print(f"Error enviando a TRMNL: {e}")

if __name__ == "__main__":
    print("--- Obteniendo datos de Yahoo Finance ---")
    
    # MXN=X es el símbolo oficial para Peso Mexicano en Yahoo
    # Buscamos cuántos pesos cuesta 1 Dólar y 1 Euro
    
    # Dólar (USD a MXN)
    usd_price = get_yahoo_rate("MXN=X")
    
    # Euro (EUR a MXN)
    eur_price = get_yahoo_rate("EURMXN=X")
    
    if usd_price and eur_price:
        send_to_trmnl(usd_price, eur_price)
    else:
        print("Hubo un error con Yahoo Finance, no se enviaron datos.")
