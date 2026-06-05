import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import asyncio

from bot_logic import init_services, query_pops_knowledge_base
load_dotenv()

app = FastAPI(
    title="POPS AI Bot API",
    description="API para interagir com o bot de conhecimento POPs.",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str


@app.get("/")
async def read_root():
    """
    Endpoint simples para o Coolify (e outros serviços) verificarem a saúde da API.
    Retorna um status "ok".
    """
    return {"status": "ok", "message": "API is running and healthy!"}

@app.on_event("startup")
async def startup_event():
    print("Iniciando serviços para API...")
    try:
        init_services()
        print("Serviços de API (ChromaDB, Gemini) iniciados com sucesso.")
    except Exception as e:
        print(f"Erro ao iniciar serviços: {e}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar serviços do bot.")
    
@app.post("/ask")
async def ask_question(request: QueryRequest):
    """
    Endpoint para consultar a base de conhecimento de POPs.
    Recebe uma pergunta e retorna a resposta gerada.
    """
    try:
        answer = await query_pops_knowledge_base(request.question)
        
        return {"answer": answer}
    except Exception as e:
        
        print(f"Erro na requisição /ask: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao processar sua pergunta.")

if __name__ == "__main__":
    
    print("Iniciando servidor Uvicorn para FastAPI (modo local de teste)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
