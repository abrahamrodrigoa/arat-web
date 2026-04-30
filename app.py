from fastapi import FastAPI, Header, HTTPException
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = FastAPI()

# 🔐 TU API KEY (la misma que pondrás en GPT)
API_KEY = "ius_constitucional_v1_3111979_K#9Lp!"

def check_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="No autorizado")

# 🔗 CONFIG GOOGLE DRIVE
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

creds = service_account.Credentials.from_service_account_file(
    r'D:\Agentes IA\02 Juridic-IA\dip-python-490901-a9641d72ce14.json',
    scopes=SCOPES
)

service = build('drive', 'v3', credentials=creds)

# 📁 ID de tu carpeta principal
FOLDER_ID = "1TQwJMW-JRI8iq2dakW9-70fLKbGhkCk5"

# 🗂️ MAPEO DE CARPETAS (según lo que listaste)
CARPETAS = {
    "amparo": "101xGs2qhV7nU2lmrPmmtxOUCwtPWHY6T",
    "libertad": "14km3DYdOVkt6m3uP2lCWAPXotWJZsPNX",
    "reposicion": "1OnT8p9oDVdyDbqBYfUVOEAc9tkujJYBh",
    "cumplimiento": "12yD40NZRGNiJDa5ERikyDAfQSLeR-PhF",
    "inconstitucionalidad": "1KdAeRUNsXdmNGDTe32ux1shomlI8t8Un",
}

# 🧠 Detectar tipo automáticamente
def detectar_tipo(texto):
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

# 📁 Listar todo (raíz)
@app.get("/listar")
def listar(x_api_key: str = Header(None)):
    check_key(x_api_key)

    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents",
        fields="files(id, name)"
    ).execute()

    return results.get('files', [])

# 📂 Listar archivos dentro de una carpeta por tipo
@app.get("/archivos")
def archivos(tipo: str, x_api_key: str = Header(None)):
    check_key(x_api_key)

    folder_id = CARPETAS.get(tipo)

    if not folder_id:
        return {"error": "tipo no válido"}

    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()

    return results.get('files', [])

# ⚖️ Selección automática según texto del usuario
@app.post("/seleccionar")
def seleccionar(data: dict, x_api_key: str = Header(None)):
    check_key(x_api_key)

    query = data.get("texto", "")

    tipo = detectar_tipo(query)
    folder_id = CARPETAS.get(tipo)

    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()

    return {
        "tipo_detectado": tipo,
        "archivos": results.get('files', [])
    }