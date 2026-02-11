import requests
from bs4 import BeautifulSoup
import os
import re

# --- CONFIGURACIÓN ---
TRMNL_WEBHOOK_URL = os.environ.get("TRMNL_WEBHOOK_URL")
# Usamos la portada principal, donde aparecen los recuadros de resumen
URL_BANXICO_HOME = "https://www.banxico.org.mx/"

def get_banxico_html_rates():
    try:
        # Usamos un "disfraz" de navegador muy común para evitar bloqueos
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Referer": "https://www.google.com/"
        }
        
        print(f"Intentando acceder a: {URL_BANXICO_HOME}")
        session = requests.Session()
        response = session.get(URL_BANXICO_HOME, headers=headers, timeout=20)
        
        # Si nos redirigen al sitio "anterior" (bloqueo), lanzamos error
        if "anterior.banxico" in response.url:
            print("BLOQUEO DETECTADO: Banxico nos redirigió al sitio antiguo por seguridad.")
            return None
            
        response.raise_for_status()
        
        # --- ANÁLISIS DEL HTML ---
        soup = BeautifulSoup(response.content, 'html.parser')
        rates = {}

        # Banxico suele poner los datos en una lista o estructura llamada 'bmx-indicadores' o similar.
        # Buscamos por el texto visible que usa la página
        
        # 1. BUSCAR DÓLAR FIX
        # Buscamos el texto "FIX" y tratamos de encontrar el número cercano
        # El HTML de Banxico es complejo, buscamos patrones de texto
        todo_el_texto = soup.get_text()
        
        # Usamos Expresiones Regulares para encontrar el patrón del precio
        # Busca "FIX" seguido de cualquier cosa y luego un número decimal
        # Ejemplo en web: "FIX ... 17.2315"
        match_usd = re.search(r"FIX.*?(\d{2}\.\d{4})", todo_el_texto, re.DOTALL)
        if match_usd:
            rates['usd'] = match_usd.group(1)
            print(f"¡Encontrado Dólar FIX!: {rates['usd']}")
        else:
            # Intento secundario: buscar por estructura de bloque
            print("No se encontró patrón 'FIX', buscando alternativo...")
            
        # 2. BUSCAR EURO
        # Busca "Euro" seguido de un número
        match_eur = re.search(r"Euro.*?(\d{2}\.\d{4})", todo_el_texto, re.DOTALL)
        if match_eur:
            rates['eur'] = match_eur.group(1)
            print(f"¡Encontrado Euro!: {rates['eur']}")
            
        return rates

    except Exception as e:
        print(f"Error leyendo Banxico Web: {e}")
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
        print(f"Datos enviados -> Dólar: ${usd} | Euro: €{eur}")
    except Exception as e:
         print(f"Error enviando a TRMNL: {e}")

if __name__ == "__main__":
    print("--- Iniciando Scraper Banxico Directo ---")
    data = get_banxico_html_rates()
    
    if data and 'usd' in data:
        # Si encontramos el dólar, enviamos (el euro es opcional si falla)
        usd_val = data.get('usd', '0.00')
        eur_val = data.get('eur', '0.00') # Si no encuentra euro, manda 0.00
        send_to_trmnl(usd_val, eur_val)
    else:
        print("FALLO: No se pudieron extraer los datos directamente de Banxico.")
        print("Causa probable: Banxico cambió su diseño o bloqueó la IP de GitHub.")
