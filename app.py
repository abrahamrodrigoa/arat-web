from fastapi import FastAPI, Header, HTTPException
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = FastAPI()

API_KEY = "ius_constitucional_v1_3111979_K#9Lp!"

def check_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="No autorizado")

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "dip-python-490901-a9641d72ce14.json")

service = None

try:
    if os.path.exists(JSON_PATH):
        creds = service_account.Credentials.from_service_account_file(
            JSON_PATH,
            scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=creds)
    else:
        print("⚠️ JSON no encontrado")
except Exception as e:
    print("⚠️ Error Google Drive:", e)

FOLDER_ID = "1TQwJMW-JRI8iq2dakW9-70fLKbGhkCk5"

CARPETAS = {
    "amparo": "101xGs2qhV7nU2lmrPmmtxOUCwtPWHY6T",
    "libertad": "14km3DYdOVkt6m3uP2lCWAPXotWJZsPNX",
    "reposicion": "1OnT8p9oDVdyDbqBYfUVOEAc9tkujJYBh",
    "cumplimiento": "12yD40NZRGNiJDa5ERikyDAfQSLeR-PhF",
    "inconstitucionalidad": "1KdAeRUNsXdmNGDTe32ux1shomlI8t8Un",
}

# 🧠 INTELIGENCIA DE INTERPRETACIÓN
SINONIMOS = {
    "amparo": ["amparo", "acción de amparo", "protección constitucional"],
    "libertad": ["libertad", "acción de libertad", "habeas corpus"],
    "reposicion": ["reposición", "reposicion", "recurso de reposición"],
    "cumplimiento": ["cumplimiento", "acción de cumplimiento"],
    "inconstitucionalidad": ["inconstitucionalidad", "acción de inconstitucionalidad"]
}

def detectar_tipo(texto: str):
    texto = texto.lower()

    for tipo, palabras in SINONIMOS.items():
        for palabra in palabras:
            if palabra in texto:
                return tipo

    return "amparo"  # default

@app.get("/")
def root():
    return {"mensaje": "API IUS Constitucional activa"}

@app.get("/listar")
def listar(x_api_key: str = Header(None)):
    check_key(x_api_key)

    if not service:
        return {"error": "Drive no configurado"}

    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents",
        fields="files(id, name)"
    ).execute()

    return results.get('files', [])

@app.get("/archivos")
def archivos(tipo: str, x_api_key: str = Header(None)):
    check_key(x_api_key)

    if not service:
        return {"error": "Drive no configurado"}

    tipo_detectado = detectar_tipo(tipo)

    folder_id = CARPETAS.get(tipo_detectado)

    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()

    return {
        "tipo_detectado": tipo_detectado,
        "archivos": results.get('files', [])
    }

@app.post("/seleccionar")
def seleccionar(data: dict, x_api_key: str = Header(None)):
    check_key(x_api_key)

    if not service:
        return {"error": "Drive no configurado"}

    texto = data.get("texto", "")

    tipo = detectar_tipo(texto)
    folder_id = CARPETAS.get(tipo)

    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()

    return {
        "tipo_detectado": tipo,
        "archivos": results.get('files', [])
    }