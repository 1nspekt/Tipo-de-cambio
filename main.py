import requests
import os
import json

# --- CONFIGURACIÓN ---
# Usamos una API abierta que NO bloquea GitHub
TRMNL_WEBHOOK_URL = os.environ.get("TRMNL_WEBHOOK_URL")

def get_rate(base_currency):
    # Consulta la API open.er-api.com (No requiere Token)
    url = f"https://open.er-api.com/v6/latest/{base_currency}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Obtenemos el valor en Pesos Mexicanos (MXN)
        mxn_rate = data['rates']['MXN']
        return "{:.2f}".format(mxn_rate)
    except Exception as e:
        print(f"Error obteniendo {base_currency}: {e}")
        return "0.00"

def send_to_trmnl(usd_val, eur_val):
    if not TRMNL_WEBHOOK_URL:
        print("Error: No se encontró la URL del Webhook en los secretos.")
        return

    payload = {
        "merge_variables": {
            "usd": usd_val,
            "eur": eur_val
        }
    }
    
    try:
        print(f"Enviando datos... USD: {usd_val} | EUR: {eur_val}")
        r = requests.post(TRMNL_WEBHOOK_URL, json=payload)
        print(f"Respuesta de TRMNL: {r.status_code}")
    except Exception as e:
         print(f"Error enviando a TRMNL: {e}")

if __name__ == "__main__":
    print("--- Iniciando Actualización de Divisas ---")
    
    # 1. Obtener Dólar
    print("Consultando Dólar...")
    usd_price = get_rate("USD")
    
    # 2. Obtener Euro
    print("Consultando Euro...")
    eur_price = get_rate("EUR")
    
    # 3. Enviar a tu pantalla
    if usd_price != "0.00" and eur_price != "0.00":
        send_to_trmnl(usd_price, eur_price)
    else:
        print("Hubo un error obteniendo los datos, no se envió nada.")
        
    print("--- Finalizado ---")
