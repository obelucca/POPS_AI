import os
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import chromadb
import config
from model_factories import get_embedding_function

print("Tentando carregar variáveis do .env...")
load_dotenv() 
print("Variáveis do .env carregadas.")

API_KEY = os.getenv("GOOGLE_API_KEY") 

if API_KEY:
    print(f"Chave de API (parcial) encontrada: {API_KEY[:5]}...{API_KEY[-5:]}")
    genai.configure(api_key=API_KEY)
else:
    print("Erro: A chave 'GOOGLE_API_KEY' NÃO foi encontrada no ambiente!")
    print(f"Conteúdo do .env esperado: GOOGLE_API_KEY=\"SUA_CHAVE_AQUI\"")
    print("Verifique se o arquivo .env está na mesma pasta do script.")
    exit()

PASTA_TEXTOS_EXTRAIDOS = "pops_textos_extraidos"
PASTA_CHROMADB = config.PASTA_CHROMADB

def carregar_texto_do_arquivo(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        return f.read()
    
def dividir_texto_em_chunks(texto_completo):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False, 
    )
    chunks = text_splitter.split_text(texto_completo)
    return chunks

def gerar_embedding_para_chunk(chunk_texto, embedding_func):
    try:
        embedding = embedding_func(chunk_texto, task_type="RETRIEVAL_DOCUMENT")
        return embedding
    except Exception as e:
        print(f"Erro ao gerar embedding para chunk: {e}")
        return None
    
def processar_textos_e_salvar_no_chroma(pasta_origem_txt, pasta_chromadb):
    client = chromadb.PersistentClient(path=pasta_chromadb)
    collection = client.get_or_create_collection(name=config.COLLECTION_NAME)
    print(f"Coleção '{config.COLLECTION_NAME}' ChromaDB pronta.")

    documents = []
    embeddings_list = []
    metadatas = []
    ids = []
    
    embedding_func = get_embedding_function()

    for nome_arquivo_txt in os.listdir(pasta_origem_txt):
        if nome_arquivo_txt.lower().endswith(".txt"):
            caminho_txt_completo = os.path.join(pasta_origem_txt, nome_arquivo_txt)
            print(f"Processando arquivo: {nome_arquivo_txt} para chunking e embedding...")

            texto_completo = carregar_texto_do_arquivo(caminho_txt_completo)
            chunks = dividir_texto_em_chunks(texto_completo)

            for i, chunk in enumerate(chunks):
                print(f"  Gerando embedding para chunk {i+1}/{len(chunks)} de '{nome_arquivo_txt}'...")
                
                embedding = gerar_embedding_para_chunk(chunk, embedding_func)

                if embedding is not None:
                    documents.append(chunk) 
                    embeddings_list.append(embedding) 
                    metadatas.append({"source": nome_arquivo_txt, "chunk_index": i}) 
                    ids.append(f"{nome_arquivo_txt}_{i}") 
                else:
                    print(f"  Não foi possível gerar embedding para chunk {i+1} de '{nome_arquivo_txt}'. Será ignorado.")

    if documents:
        print(f"\nAdicionando {len(documents)} chunks ao ChromaDB...")
        collection.add(
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadatas,
            ids=ids
        )
        print("Chunks adicionados ao ChromaDB com sucesso!")
        print(f"Total de chunks na coleção: {collection.count()}")
    else:
        print("Nenhum chunk com embedding válido para adicionar ao ChromaDB.")

    return collection 

if __name__ == "__main__":
    if not os.path.exists(PASTA_TEXTOS_EXTRAIDOS):
        print(f"Erro: A pasta '{PASTA_TEXTOS_EXTRAIDOS}' não existe. Rode a Etapa 2 primeiro!")
    else:
        print(f"Lendo textos de '{PASTA_TEXTOS_EXTRAIDOS}' e salvando no ChromaDB...")
        
        pops_collection = processar_textos_e_salvar_no_chroma(PASTA_TEXTOS_EXTRAIDOS, PASTA_CHROMADB)
        print("\nEtapa de Armazenamento de Embeddings no Banco de Dados Vetorial concluída!")
