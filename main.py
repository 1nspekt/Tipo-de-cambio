import requests
import os
import json

# --- CONFIGURACIÓN ---
BANXICO_TOKEN = os.environ.get("BANXICO_TOKEN")
TRMNL_WEBHOOK_URL = os.environ.get("TRMNL_WEBHOOK_URL")
SERIES = "SF43718,SF46410"
URL_BANXICO = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{SERIES}/datos/oportunos"

def get_rates():
    if not BANXICO_TOKEN:
        print("ERROR: Falta el Token de Banxico en los secretos.")
        return None

    # AQUÍ ESTÁ EL TRUCO: Disfrazamos el script de navegador
    headers = {
        "Bmx-Token": BANXICO_TOKEN,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        print(f"Consultando Banxico en: {URL_BANXICO}")
        response = requests.get(URL_BANXICO, headers=headers, timeout=10)
        
        # Si Banxico nos redirige a 'anterior.banxico...', lanzamos error manual
        if "anterior.banxico" in response.url:
             print("Error: Banxico nos redirigió al sitio antiguo.")
        
        response.raise_for_status() 
        data = response.json()
        
    except Exception as e:
        print(f"Error conectando a Banxico: {e}")
        # Intento de depuración: Imprimir qué nos devolvió el servidor si falló
        try:
            print(f"URL final: {response.url}")
        except:
            pass
        return None
    
    rates = {}
    try:
        # Extraemos los datos
        for serie in data['bmx']['series']:
            if 'datos' in serie and len(serie['datos']) > 0:
                amount = float(serie['datos'][0]['dato'])
                formatted = "{:.2f}".format(amount)
                
                if serie['idSerie'] == "SF43718":
                    rates['usd'] = formatted
                elif serie['idSerie'] == "SF46410":
                    rates['eur'] = formatted
            else:
                print(f"Advertencia: La serie {serie['idSerie']} no trajo datos recientes.")
                
    except KeyError as e:
        print(f"Error procesando JSON de Banxico: {e}")
        return None
            
    return rates

def send_to_trmnl(rates):
    if not rates:
        print("No hay datos válidos para enviar a TRMNL.")
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
        print(f"Datos enviados: USD {rates.get('usd')} - EUR {rates.get('eur')}")
    except Exception as e:
         print(f"Error enviando a TRMNL: {e}")

if __name__ == "__main__":
    print("Iniciando script v2 (User-Agent)...")
    tasas = get_rates()
    send_to_trmnl(tasas)
    print("Finalizado.")
