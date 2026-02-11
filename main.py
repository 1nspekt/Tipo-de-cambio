{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import requests\
import json\
from datetime import datetime\
\
# CONFIGURACI\'d3N\
BANXICO_TOKEN = "fedf38ebb107e2291b915cb606e57a940f2dd8a37e76165e9c4b660881a6aab9"\
TRMNL_WEBHOOK_URL = "https://trmnl.com/api/custom_plugins/64136d9c-0ce2-495f-b3fb-1544201df5a5"\
\
# IDs de series (USD FIX y Euro)\
SERIES = "SF43718,SF46410"\
URL_BANXICO = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/\{SERIES\}/datos/oportunos"\
\
def get_rates():\
    headers = \{"Bmx-Token": BANXICO_TOKEN\}\
    response = requests.get(URL_BANXICO, headers=headers)\
    data = response.json()\
    \
    rates = \{\}\
    \
    for serie in data['bmx']['series']:\
        amount = float(serie['datos'][0]['dato'])\
        # Formato a 2 decimales\
        formatted = "\{:.2f\}".format(amount)\
        \
        if serie['idSerie'] == "SF43718":\
            rates['usd'] = formatted\
        elif serie['idSerie'] == "SF46410":\
            rates['eur'] = formatted\
            \
    return rates\
\
def send_to_trmnl(rates):\
    payload = \{\
        "merge_variables": \{\
            "usd": rates['usd'],\
            "eur": rates['eur']\
        \}\
    \}\
    requests.post(TRMNL_WEBHOOK_URL, json=payload)\
    print("Datos enviados a TRMNL exitosamente.")\
\
if __name__ == "__main__":\
    rates = get_rates()\
    send_to_trmnl(rates)}
import requests
import os
import json

# --- CONFIGURACIÓN SEGURA ---
# Ahora le decimos al código: "Busca estas variables en el entorno de ejecución"
BANXICO_TOKEN = os.environ.get("BANXICO_TOKEN")
TRMNL_WEBHOOK_URL = os.environ.get("TRMNL_WEBHOOK_URL")

# IDs de series (USD FIX y Euro)
SERIES = "SF43718,SF46410"
URL_BANXICO = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{SERIES}/datos/oportunos"

def get_rates():
    if not BANXICO_TOKEN:
        print("Error: No se encontró el Token de Banxico")
        return None

    headers = {"Bmx-Token": BANXICO_TOKEN}
    response = requests.get(URL_BANXICO, headers=headers)
    
    if response.status_code != 200:
        print(f"Error conectando a Banxico: {response.status_code}")
        return None

    data = response.json()
    rates = {}
    
    for serie in data['bmx']['series']:
        amount = float(serie['datos'][0]['dato'])
        formatted = "{:.2f}".format(amount)
        
        if serie['idSerie'] == "SF43718":
            rates['usd'] = formatted
        elif serie['idSerie'] == "SF46410":
            rates['eur'] = formatted
            
    return rates

def send_to_trmnl(rates):
    if not rates:
        return

    payload = {
        "merge_variables": {
            "usd": rates.get('usd', '0.00'),
            "eur": rates.get('eur', '0.00')
        }
    }
    # Enviamos la petición POST al Webhook
    requests.post(TRMNL_WEBHOOK_URL, json=payload)
    print(f"Datos enviados: USD {rates.get('usd')} - EUR {rates.get('eur')}")

if __name__ == "__main__":
    rates = get_rates()
    send_to_trmnl(rates)
