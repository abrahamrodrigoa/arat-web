from fastapi import FastAPI, Header, HTTPException
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = FastAPI()

# 🔐 API KEY
API_KEY = "ius_constitucional_v1_3111979_K#9Lp!"

def check_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="No autorizado")

# 🔗 CONFIG GOOGLE DRIVE
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# ✅ RUTA SEGURA (funciona en Railway)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "dip-python-490901-a9641d72ce14.json")

# ⚠️ VALIDACIÓN PARA EVITAR CRASH
if not os.path.exists(JSON_PATH):
    raise Exception(f"No se encontró el archivo JSON en: {JSON_PATH}")

creds = service_account.Credentials.from_service_account_file(
    JSON_PATH,
    scopes=SCOPES
)

service = build('drive', 'v3', credentials=creds)

# 📁 CARPETA PRINCIPAL
FOLDER_ID = "1TQwJMW-JRI8iq2dakW9-70fLKbGhkCk5"

# 🗂️ MAPEO
CARPETAS = {
    "amparo": "101xGs2qhV7nU2lmrPmmtxOUCwtPWHY6T",
    "libertad": "14km3DYdOVkt6m3uP2lCWAPXotWJZsPNX",
    "reposicion": "1OnT8p9oDVdyDbqBYfUVOEAc9tkujJYBh",
    "cumplimiento": "12yD40NZRGNiJDa5ERikyDAfQSLeR-PhF",
    "inconstitucionalidad": "1KdAeRUNsXdmNGDTe32ux1shomlI8t8Un",
}

# 🧠 DETECTOR
def detectar_tipo(texto: str):
    texto = texto.lower()

    if "amparo" in texto:
        return "amparo"
    elif "libertad" in texto:
        return "libertad"
    elif "cumplimiento" in texto:
        return "cumplimiento"
    elif "inconstitucionalidad" in texto:
        return "inconstitucionalidad"
    elif "reposicion" in texto:
        return "reposicion"
    else:
        return "amparo"

# 🏠 ROOT
@app.get("/")
def root():
    return {"mensaje": "API IUS Constitucional activa"}

# 📁 LISTAR
@app.get("/listar")
def listar(x_api_key: str = Header(None)):
    check_key(x_api_key)

    try:
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents",
            fields="files(id, name)"
        ).execute()

        return results.get('files', [])
    except Exception as e:
        return {"error": str(e)}

# 📂 ARCHIVOS
@app.get("/archivos")
def archivos(tipo: str, x_api_key: str = Header(None)):
    check_key(x_api_key)

    folder_id = CARPETAS.get(tipo)

    if not folder_id:
        return {"error": "tipo no válido"}

    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name)"
        ).execute()

        return results.get('files', [])
    except Exception as e:
        return {"error": str(e)}

# ⚖️ SELECCIONAR
@app.post("/seleccionar")
def seleccionar(data: dict, x_api_key: str = Header(None)):
    check_key(x_api_key)

    query = data.get("texto", "")
    tipo = detectar_tipo(query)
    folder_id = CARPETAS.get(tipo)

    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name)"
        ).execute()

        return {
            "tipo_detectado": tipo,
            "archivos": results.get('files', [])
        }
    except Exception as e:
        return {"error": str(e)}