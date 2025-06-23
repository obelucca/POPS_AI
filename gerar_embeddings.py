import os
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

print("Tentando carregar variáveis do .env...")
load_dotenv() 
print("Variáveis do .env carregadas.")

API_KEY = os.getenv("GOOGLE_API_KEY") 

if API_KEY:
    print(f"Chave de API (parcial) encontrada: {API_KEY[:5]}...{API_KEY[-5:]}")
else:
    print("Erro: A chave 'GOOGLE_API_KEY' NÃO foi encontrada no ambiente!")
    print(f"Conteúdo do .env esperado: GOOGLE_API_KEY=\"SUA_CHAVE_AQUI\"")
    print("Verifique se o arquivo .env está na mesma pasta do script.")
    exit()

genai.configure(api_key=API_KEY)

PASTA_TEXTOS_EXTRAIDOS = "pops_textos_extraidos"
PASTA_EMBEDDINGS = "pops_chunks_e_embeddings"
PASTA_CHUNKS_E_EMBEDDINGS = "pops_chunks_e_embeddings"

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

def gerar_embedding_para_chunk(chunk_texto):
    try:
        response = genai.embed_content(
            model="models/embedding-001",
            content=chunk_texto,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return response['embedding'] 
    except Exception as e:
        print(f"Erro ao gerar embedding para chunk: {e}")
        return None
    
def processar_textos_e_gerar_embeddings(pasta_origem_txt, pasta_destino_chunks):
    """
    Lê os arquivos .txt, divide em chunks e gera embeddings.
    Salva os chunks e seus embeddings em um formato simples por enquanto.
    """
    if not os.path.exists(pasta_destino_chunks):
        os.makedirs(pasta_destino_chunks)

    todos_os_dados_para_indexar = [] 

    for nome_arquivo_txt in os.listdir(pasta_origem_txt):
        if nome_arquivo_txt.lower().endswith(".txt"):
            caminho_txt_completo = os.path.join(pasta_origem_txt, nome_arquivo_txt)
            print(f"Processando arquivo: {nome_arquivo_txt} para chunking e embedding...")

            texto_completo = carregar_texto_do_arquivo(caminho_txt_completo)
            chunks = dividir_texto_em_chunks(texto_completo)

            for i, chunk in enumerate(chunks):
                print(f"  Gerando embedding para chunk {i+1}/{len(chunks)} de '{nome_arquivo_txt}'...")
                embedding = gerar_embedding_para_chunk(chunk)

                if embedding:
                  
                    todos_os_dados_para_indexar.append({
                        "id": f"{nome_arquivo_txt}_chunk_{i}", 
                        "texto": chunk,
                        "embedding": embedding,
                        "fonte_documento": nome_arquivo_txt
                    })
                else:
                    print(f"  Não foi possível gerar embedding para chunk {i+1} de '{nome_arquivo_txt}'.")


    print(f"\nProcessamento concluído. Total de chunks com embeddings: {len(todos_os_dados_para_indexar)}")
 
    if todos_os_dados_para_indexar:
        print("\nExemplo do primeiro chunk processado com embedding:")
        print(todos_os_dados_para_indexar[0])

    return todos_os_dados_para_indexar

if __name__ == "__main__":
    if not os.path.exists(PASTA_TEXTOS_EXTRAIDOS):
        print(f"Erro: A pasta '{PASTA_TEXTOS_EXTRAIDOS}' não existe. Rode a Etapa 2 primeiro!")
    else:
        print(f"Lendo textos de '{PASTA_TEXTOS_EXTRAIDOS}'...")
        dados_processados = processar_textos_e_gerar_embeddings(PASTA_TEXTOS_EXTRAIDOS, PASTA_CHUNKS_E_EMBEDDINGS)
        print("\nEtapa de Chunking e Geração de Embeddings concluída!")
