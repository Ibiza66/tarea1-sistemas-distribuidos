"""
Cache - Tarea 1 Sistemas Distribuidos.

El servicio simula un cache para almacenar resultados de consultas


"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Any

app = FastAPI()


class ConsultaRequest(BaseModel):
    tipo_consulta: str
    parametros: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/consulta")
def recibir_consulta(consulta: ConsultaRequest):

    print("Consulta recibida:")
    print(consulta.model_dump())

    return {
        "mensaje": "Consulta recibida correctamente",
        "consulta": consulta.model_dump()
    }