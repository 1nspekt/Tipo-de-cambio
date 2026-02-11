import requests
import os
import json

# --- CONFIGURACIÓN ---
# GitHub leerá esto de los secretos
BANXICO_TOKEN = os.environ.get("BANXICO_TOKEN")
TRMNL_WEBHOOK_URL = os.environ.get("TRMNL_WEBHOOK_URL")
SERIES = "SF43718,SF46410"
URL_BANXICO = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{SERIES}/datos/oportunos"

def get_rates():
    # Verificamos que existan las credenciales
    if not BANXICO_TOKEN:
        print("ERROR CRÍTICO: No se encontró el BANXICO_TOKEN en los secretos.")
        return None
    if not TRMNL_WEBHOOK_URL:
        print("ERROR CRÍTICO: No se encontró la TRMNL_WEBHOOK_URL en los secretos.")
        return None

    headers = {"Bmx-Token": BANXICO_TOKEN}
    try:
        response = requests.get(URL_BANXICO, headers=headers)
        response.raise_for_status() # Lanza error si la web falla
        data = response.json()
    except Exception as e:
        print(f"Error conectando a Banxico: {e}")
        return None
    
    rates = {}
    try:
        # Procesamos la respuesta de Banxico
        for serie in data['bmx']['series']:
            amount = float(serie['datos'][0]['dato'])
            formatted = "{:.2f}".format(amount)
            
            if serie['idSerie'] == "SF43718":
                rates['usd'] = formatted
            elif serie['idSerie'] == "SF46410":
                rates['eur'] = formatted
    except KeyError:
        print("Error: La respuesta de Banxico no tiene el formato esperado. Revisa tu Token.")
        print(f"Respuesta recibida: {data}")
        return None
            
    return rates

def send_to_trmnl(rates):
    if not rates:
        print("No hay datos para enviar.")
        return

    payload = {
        "merge_variables": {
            "usd": rates.get('usd', '0.00'),
            "eur": rates.get('eur', '0.00')
        }
    }
    
    try:
        r = requests.post(TRMNL_WEBHOOK_URL, json=payload)
        print(f"Enviado a TRMNL. Estado: {r.status_code}")
        print(f"Datos: USD {rates.get('usd')} - EUR {rates.get('eur')}")
    except Exception as e:
         print(f"Error enviando a TRMNL: {e}")

if __name__ == "__main__":
    print("Iniciando script...")
    tasas = get_rates()
    send_to_trmnl(tasas)
    print("Finalizado.")
