from enum import Enum, auto

class EmbeddingModelType(Enum):
   
    GEMINI = auto()
    HUGGINGFACE_SBERT = auto()
    

class GenerativeModelType(Enum):
    GEMINI_FLASH = auto()
 
# Escolha o modelo de embedding ativo
ACTIVE_EMBEDDING_MODEL = EmbeddingModelType.GEMINI
ACTIVE_GENERATIVE_MODEL = GenerativeModelType.GEMINI_FLASH


PASTA_CHROMADB = "chromadb_data"
COLLECTION_NAME = "pops_base_conhecimento"

if __name__ == "__main__":
    print("Testando arquivo de configurações (config.py)...")
    print(f"Modelo de Embedding ativo: {ACTIVE_EMBEDDING_MODEL.name}")
    print(f"Modelo Generativo ativo: {ACTIVE_GENERATIVE_MODEL.name}")
    print(f"Pasta do ChromaDB: {PASTA_CHROMADB}")
    print(f"Nome da Coleção: {COLLECTION_NAME}")
