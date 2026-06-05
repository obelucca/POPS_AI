import os
import google.generativeai as genai
import chromadb
from dotenv import load_dotenv

import config
from model_factories import get_embedding_function, get_generative_model


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client_chroma = None
gemini_model_generation = None
gemini_model_embedding = None
pops_collection = None
embedding_func = None

def init_services():
    global client_chroma, pops_collection, gemini_model_generation, embedding_func
    
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model_generation = get_generative_model()
        print("Serviço de modelo generativo configurado.")
    else:
        print("Erro: GOOGLE_API_KEY não está configurada.")
        
    embedding_func = get_embedding_function()

    try:
        client_chroma = chromadb.PersistentClient(path=config.PASTA_CHROMADB)
        pops_collection = client_chroma.get_or_create_collection(name=config.COLLECTION_NAME)
        print("Base de conhecimento carregada do ChromaDB.")
        print(f"Total de chunks disponíveis: {pops_collection.count()}")
    except Exception as e:
        print(f"Erro ao carregar a base de conhecimento do ChromaDB: {e}")


async def query_pops_knowledge_base(pergunta: str) -> str:
    global gemini_model_generation, embedding_func

    if pops_collection is None or gemini_model_generation is None:
        init_services()

    if pops_collection is None:
        return "Erro interno: A base de conhecimento não foi carregada corretamente."
    if pops_collection.count() == 0:
        return "A base de conhecimento está vazia. Não há informações para consultar."

    try:
        print(f"Gerando embedding para a pergunta: '{pergunta}'")
        
        query_embedding = embedding_func(pergunta, task_type="RETRIEVAL_QUERY")

        print("Buscando chunks relevantes no ChromaDB...")
        results = pops_collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=['documents', 'metadatas']
        )

        relevant_chunks_texts = results['documents'][0]
        relevant_metadatas = results['metadatas'][0]

        if not relevant_chunks_texts:
            return "Desculpe, não encontrei informações relevantes em nossa base de conhecimento para essa pergunta."

        context = "\n\n---\n\n".join(relevant_chunks_texts)
        sources = [f"'{meta['source']}'" for meta in relevant_metadatas if 'source' in meta]
        sources_str = f"\n\nAs informações foram extraídas das seguintes fontes: {', '.join(set(sources))}." if sources else ""

        prompt_with_context = f"""
        Com base EXCLUSIVAMENTE nas seguintes informações de POPs (Procedimentos Operacionais Padrão) fornecidas abaixo:
        --- INFORMAÇÕES DOS POPS ---
        {context}
        --- FIM DAS INFORMAÇÕES DOS POPS ---
        Responda à pergunta do usuário: "{pergunta}"
        Sua resposta deve ser:
        1. Clara e profissional, e você deve ser educado, use emojis.
        2. Direta ao ponto, respondendo estritamente à pergunta.
        3. Se a pergunta implicar um "como fazer", estruture a resposta como um passo a passo (ex: 1., 2., 3.).
        4. NÃO invente, extrapole ou adicione informações que não estão explicitamente no contexto fornecido.
        5. Se as informações fornecidas acima NÃO forem suficientes para responder à pergunta de forma completa, diga educadamente que não encontrou informações suficientes ou que não sabe a resposta com base nos documentos fornecidos.
        6. Cuidado ao informar as senhas, cuidado ao colocar ponto finais ao final de senha para exemplo "senha123" ou "senha123." a senha correta é "senha123" sem o ponto final. Coloque o ponto somente se tiver sido informado no pop.
        7. A cada resposta, adicione no final uma breve nota mencionando qual o titulo do pop no qual a informação foi retirada, caso tenha informações como autor, indique que em caso de dúvidas recorrer ao autor do pop  e informe o nome do autor do pop. 
        {sources_str}
        """

        print("Enviando prompt para o Gemini...")
        response_from_gemini = await gemini_model_generation.generate_content_async(prompt_with_context)

        return response_from_gemini.text

    except Exception as e:
        print(f"Erro inesperado na lógica de consulta: {e}")
        return f"Ocorreu um erro ao tentar buscar a resposta. Por favor, tente novamente mais tarde. Detalhes: {e}"
