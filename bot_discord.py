import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import asyncio
import aiohttp
import bot_logic  

from bot_logic import init_services, query_pops_knowledge_base

from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not DISCORD_BOT_TOKEN:
    raise ValueError("O token do bot Discord 'DISCORD_BOT_TOKEN' não foi encontrado no arquivo .env.")

bot_logic.init_services()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

TEMP_FILES_DIR = "temp_files"
os.makedirs(TEMP_FILES_DIR, exist_ok=True)


def dividir_texto_em_chunks(texto_completo):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_text(texto_completo)


def processar_e_adicionar_pop(caminho_arquivo, nome_arquivo, embedding_func, pops_collection):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        texto_completo = f.read()

    chunks = dividir_texto_em_chunks(texto_completo)

    documents = []
    embeddings_list = []
    metadatas = []
    ids = []

    for i, chunk in enumerate(chunks):
        try:
            embedding = embedding_func(chunk, task_type="RETRIEVAL_DOCUMENT")
        except Exception as e:
            print(f"Erro ao gerar embedding para chunk {i} do arquivo {nome_arquivo}: {e}")
            continue
        
        documents.append(chunk)
        embeddings_list.append(embedding)
        metadatas.append({"source": nome_arquivo, "chunk_index": i})
        ids.append(f"{nome_arquivo}_{i}")

    if not documents:
        raise ValueError("Nenhum embedding válido foi gerado para os chunks.")

    try:
        pops_collection.add(
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Arquivo '{nome_arquivo}' indexado com sucesso. {len(documents)} chunks adicionados.")
    except Exception as e:
        raise RuntimeError(f"Erro ao adicionar dados na coleção do ChromaDB: {e}")


@bot.event
async def on_ready():
    print(f'Bot logado como {bot.user}')
    print(f"✅ Bot conectado como {bot.user}, e pronto para receber comandos!")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 {len(synced)} comandos sincronizados")
    except Exception as e:
        print(f"Erro ao sincronizar comandos de barra: {e}")


@bot.tree.command(name="addpop", description="Adicionar um arquivo de POP (.txt) ao sistema")
@app_commands.describe(arquivo="O arquivo .txt do POP")
async def addpop(interaction: discord.Interaction, arquivo: discord.Attachment):
    if not arquivo.filename.lower().endswith(".txt"):
        await interaction.response.send_message("❌ Apenas arquivos .txt são aceitos.", ephemeral=True)
        return

    await interaction.response.send_message("📥 Recebendo arquivo e salvando...", ephemeral=True)

    file_path = os.path.join(TEMP_FILES_DIR, arquivo.filename)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(arquivo.url) as resp:
                if resp.status == 200:
                    with open(file_path, "wb") as f:
                        f.write(await resp.read())
                else:
                    await interaction.followup.send("❌ Falha ao baixar o arquivo.", ephemeral=True)
                    return

        await interaction.followup.send(f"📄 Arquivo `{arquivo.filename}` salvo com sucesso, iniciando processamento...", ephemeral=True)

        # Obtém embedding_func e pops_collection atualizados do bot_logic
        embedding_func = bot_logic.embedding_func
        pops_collection = bot_logic.pops_collection

        if embedding_func is None or pops_collection is None:
            await interaction.followup.send("❌ Os serviços de embedding ou base de conhecimento não estão inicializados.", ephemeral=True)
            return

        # Processa o arquivo para chunking, embedding e inserção no ChromaDB em thread separada
        try:
            await asyncio.to_thread(processar_e_adicionar_pop, file_path, arquivo.filename, embedding_func, pops_collection)
            await interaction.followup.send(f"✅ POP `{arquivo.filename}` adicionado ao banco com sucesso!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro ao processar o POP: {e}", ephemeral=True)

    finally:
        # Apaga o arquivo salvo para não acumular lixo
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Erro ao remover arquivo temporário {file_path}: {e}")


@bot.tree.command(name="pop", description="Consulta a base de conhecimento de POPs.")
@app_commands.describe(pergunta="Sua pergunta sobre os POPs.")
async def pop_command(interaction: discord.Interaction, pergunta: str):
    await interaction.response.send_message(
        f"Olá {interaction.user.mention}! Consultando a base de conhecimento sobre '{pergunta}'... Por favor, aguarde.",
        ephemeral=True
    )
    
    resposta = await query_pops_knowledge_base(pergunta)

    await interaction.followup.send(f"**Resposta:**\n{resposta}", ephemeral=True)


def split_message_by_chunks(text, max_chars=1900):
    messages = []
    current_message = ""
    lines = text.splitlines(True)
    for line in lines:
        if len(current_message) + len(line) <= max_chars:
            current_message += line
        else:
            messages.append(current_message)
            current_message = line
    if current_message:
        messages.append(current_message)

    final_messages = []
    for msg in messages:
        while len(msg) > max_chars:
            split_point = msg.rfind(' ', 0, max_chars)
            if split_point == -1:
                split_point = max_chars
            final_messages.append(msg[:split_point])
            msg = msg[split_point:].strip()
        if msg:
            final_messages.append(msg)
    return final_messages


if __name__ == '__main__':
    print("Iniciando bot Discord...")

    try:
        init_services()
    except Exception as e:
        print(f"Falha na inicialização dos serviços: {e}")
        exit(1)

    bot.run(DISCORD_BOT_TOKEN)
