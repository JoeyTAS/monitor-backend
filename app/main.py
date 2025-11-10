from fastapi import FastAPI
from .api.endpoints import auth, sites # Importamos los routers

app = FastAPI(title="Website Monitor API")

# Incluimos los routers en la app principal
# Es buena práctica ponerles un prefijo y etiquetas
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(sites.router, prefix="/api/v1/sites", tags=["Sites"])
# cors
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las fuentes (en producción, especificar dominios)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "API del Monitor"}