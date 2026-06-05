import os
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv
import config

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_embedding_model():
    if config.ACTIVE_EMBEDDING_MODEL == config.EmbeddingModelType.GEMINI:
        print("Usando modelo de embedding: Google Gemini")
        return None 
    elif config.ACTIVE_EMBEDDING_MODEL == config.EmbeddingModelType.HUGGINGFACE_SBERT:
        print("Usando modelo de embedding: Hugging Face SBERT")
        return SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
    
    else:
        raise ValueError("Modelo de embedding ativo não suportado.")

def get_embedding_function():
    if config.ACTIVE_EMBEDDING_MODEL == config.EmbeddingModelType.GEMINI:
        def generate_gemini_embedding(content, task_type):
            response = genai.embed_content(
                model="models/embedding-001",
                content=content,
                task_type=task_type
            )
            return response['embedding']
        return generate_gemini_embedding

    elif config.ACTIVE_EMBEDDING_MODEL == config.EmbeddingModelType.HUGGINGFACE_SBERT:
        model = get_embedding_model()  
        def generate_sbert_embedding(content, task_type=None):
            return model.encode(content, convert_to_tensor=False).tolist()
        return generate_sbert_embedding
    
    else:
        raise ValueError("Modelo de embedding ativo não suportado.")

def get_generative_model():
    
    if config.ACTIVE_GENERATIVE_MODEL == config.GenerativeModelType.GEMINI_FLASH:
        print("Usando modelo generativo: gemini-2.0-flash")
        return genai.GenerativeModel("gemini-2.0-flash")
    
    else:
        raise ValueError("Modelo generativo ativo não suportado.")
