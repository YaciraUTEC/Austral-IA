from fastapi import FastAPI
from austral.routers import asistente
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IMPORTANTE: agregar prefix="/api"
app.include_router(asistente.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("austral.app:app", host="127.0.0.1", port=8000, reload=True)