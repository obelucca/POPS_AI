# POPS AI — Assistente de POPs para Discord & API com RAG & Gemini

![Python](https://img.shields.io/badge/python-3.10-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-enabled-1C3C3C)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

> RAG-powered assistant that answers questions from your company's SOPs. Built with Python, LangChain, ChromaDB and Google Gemini — includes a Discord bot, a REST API via FastAPI, and full Docker support for easy self-hosting.

---

Este repositório contém uma aplicação completa de **RAG (Retrieval-Augmented Generation)** projetada para responder a perguntas sobre os **Procedimentos Operacionais Padrão (POPs)** da sua empresa.

O sistema conta com:
- Pipeline de ingestão de documentos (extração de texto e geração de embeddings)
- Banco vetorial local com **ChromaDB**
- Bot de Discord com comandos interativos (incluindo upload de novos POPs em tempo de execução)
- API **FastAPI** integrada

Tudo orquestrado para rodar em paralelo usando a API do **Google Gemini** (suportando Gemini 2.0 Flash) ou embeddings locais com **SBERT**.

---

## 🚀 Como Funciona o Projeto

O projeto é dividido em três etapas principais, além da interface de consulta:

**1. Extração** (`extrair_texto.py`)
Lê os PDFs colocados na pasta `pops_originais/`, extrai o texto completo e salva em formato `.txt` na pasta `pops_textos_extraidos/`. Também extrai imagens das páginas e salva em `pops_imagens_extraidas/` para uso futuro.

**2. Geração de Embeddings** (`gerar_embeddings.py`)
Lê os textos extraídos, divide em pedaços menores (chunks) usando o `RecursiveCharacterTextSplitter` da LangChain, gera os vetores de embedding usando o modelo configurado (Gemini `models/embedding-001` ou HuggingFace SBERT local) e os armazena no banco de dados vetorial local ChromaDB.

**3. Interface de Consulta (Discord & API)**

- **Bot do Discord** (`bot_discord.py`) — disponibiliza os comandos:
  - `/pop <pergunta>`: consulta a base de dados vetorial e gera a resposta via Gemini.
  - `/addpop <arquivo.txt>`: permite que administradores enviem um novo POP em formato `.txt` diretamente pelo Discord, indexando-o na base vetorial em tempo real.
- **API FastAPI** (`api_bot.py`) — disponibiliza o endpoint `POST /ask` para integrar a base de conhecimento de POPs com outros sistemas internos da empresa.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| Python 3.10 | Linguagem base |
| Discord.py | Integração com a API do Discord e Slash Commands |
| FastAPI & Uvicorn | API REST para expor o serviço de consultas |
| Supervisor | Gerenciamento de processos (Bot + API em paralelo no mesmo container) |
| Google Generative AI SDK | Geração de texto (`gemini-2.0-flash`) e vetorização (`models/embedding-001`) |
| Sentence-Transformers (HuggingFace) | Alternativa local para embeddings (`paraphrase-multilingual-mpnet-base-v2`) |
| ChromaDB | Banco de dados vetorial leve e embarcado |
| PyPDF2 & PyMuPDF (fitz) | Extração de texto e imagens de PDFs |
| LangChain Text Splitters | Divisão inteligente e sobreposta de textos (chunking) |
| Docker & Docker Compose | Empacotamento, orquestração e deploy simplificado |

---

## ⚙️ Configuração dos Modelos (`config.py`)

O arquivo `config.py` centraliza as decisões sobre os modelos que a aplicação utilizará.

**Modelo de Embedding (`ACTIVE_EMBEDDING_MODEL`):**
- `EmbeddingModelType.GEMINI` — usa a API do Google Gemini (`models/embedding-001`). Requer conexão com a internet e API key.
- `EmbeddingModelType.HUGGINGFACE_SBERT` — executa localmente o modelo `paraphrase-multilingual-mpnet-base-v2`. Excelente para evitar custos de API ou limites de requisição.

**Modelo Generativo (`ACTIVE_GENERATIVE_MODEL`):**
- Por padrão configurado como `gemini-2.0-flash`, oferecendo velocidade e respostas precisas.

---

## 📋 Pré-requisitos

Para rodar este projeto, você precisará de:

- Uma **Chave de API do Google Gemini** (gratuita ou paga). Crie a sua no [Google AI Studio](https://aistudio.google.com/).
- Um **Token de Bot do Discord**. Crie sua aplicação no [Discord Developer Portal](https://discord.com/developers/applications).

### Configuração do Bot no Discord Developer Portal

1. No painel da sua aplicação, vá em **Bot**.
2. Ative a opção **Message Content Intent**.
3. Vá em **OAuth2 → URL Generator**.
4. Selecione os escopos: `bot` e `applications.commands`.
5. Selecione as permissões: `Read Messages/View Channels`, `Send Messages`, `Use Slash Commands`.
6. Copie a URL gerada, cole no seu navegador e adicione o bot ao servidor desejado.

---

## ⚙️ Instalação e Configuração Passo a Passo

### Opção 1: Execução Local (Python)

**1. Clonar o repositório**
```bash
git clone https://github.com/obelucca/POPS_AI.git
cd POPS_AI
```

**2. Criar e ativar ambiente virtual**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Instalar dependências**
```bash
pip install -r requirements.txt
```

**4. Configurar variáveis de ambiente**
```bash
cp .env.example .env
```

Abra o arquivo `.env` e insira suas credenciais:
```env
GOOGLE_API_KEY="SUA_CHAVE_API_DO_GEMINI"
DISCORD_BOT_TOKEN="SEU_TOKEN_DO_BOT_DISCORD"
```

**5. Ingestão inicial — processar os PDFs**

Copie todos os seus arquivos PDF de POPs originais para a pasta `pops_originais/` e execute:
```bash
python extrair_texto.py
```

Os textos serão salvos em `pops_textos_extraidos/` e as imagens em `pops_imagens_extraidas/`.

**6. Gerar os embeddings e popular o banco vetorial**
```bash
python gerar_embeddings.py
```

Este script dividirá o texto em chunks e gerará os embeddings conforme definido em `config.py`, populando a pasta `chromadb_data/`.

**7. Iniciar os serviços**

Em terminais separados:
```bash
# Terminal 1 — Bot do Discord
python bot_discord.py

# Terminal 2 — API FastAPI
python api_bot.py
```

---

### Opção 2: Execução via Docker (Recomendado) 🐳

O container Docker utiliza o **Supervisor** para rodar em paralelo a API e o Bot de Discord dentro do mesmo container, de forma leve e auto-gerenciável.

> [!WARNING]
> Antes de subir o container, é necessário executar as **etapas 5 e 6** localmente para gerar o banco vetorial inicial em `chromadb_data/`. Esse diretório é mapeado como volume no `docker-compose` — sem ele, o bot não terá base de conhecimento para consultar.

**Passos:**

1. Configure o arquivo `.env` na raiz do projeto.
2. Coloque seus PDFs na pasta `pops_originais/`.
3. Execute o pipeline de extração e embeddings (etapas 5 e 6 acima).
4. Suba o container:

```bash
docker-compose up --build -d
```

O bot do Discord estará online e a API FastAPI disponível em `http://localhost:8000`.

---

## 🔌 Integração via API FastAPI

### Healthcheck

```http
GET /
```

```json
{
  "status": "ok",
  "message": "API is running and healthy!"
}
```

### Consulta de POP (RAG)

```http
POST /ask
Content-Type: application/json
```

```json
{
  "question": "Como faço para configurar o scanner na impressora Samsung?"
}
```

Resposta:
```json
{
  "answer": "🤖 Olá! Para configurar o scanner, siga este passo a passo:\n1. Ligue a impressora...\n\n[Nota: Retirado de 'POP-ConfiguraçãoScanner.txt']"
}
```

---

## 🗂️ Estrutura de Pastas

```
POPS_AI/
├── chromadb_data/           # Banco de dados vetorial persistido (gerado localmente)
├── pops_originais/          # Coloque seus PDFs de POPs originais aqui
├── pops_textos_extraidos/   # Arquivos .txt resultantes da extração
├── pops_imagens_extraidas/  # Imagens extraídas das páginas dos PDFs
├── temp_files/              # Diretório temporário para uploads (/addpop)
├── .env.example             # Modelo das configurações de ambiente
├── .gitignore               # Regras para evitar commits de dados e chaves
├── Dockerfile               # Configuração da imagem Docker multi-processo (Supervisor)
├── docker-compose.yml       # Orquestração do container, volumes e portas
├── requirements.txt         # Dependências do projeto
├── supervisord.conf         # Configuração do Supervisor para rodar Bot + API
├── config.py                # Configurações globais e seleção de modelos
├── model_factories.py       # Factory pattern para inicializar LLMs/Embeddings
├── bot_logic.py             # Lógica core do RAG (ChromaDB + Prompt + Gemini)
├── api_bot.py               # API FastAPI expondo o endpoint /ask
├── extrair_texto.py         # Ingestão: leitura e extração de PDF
├── gerar_embeddings.py      # Ingestão: chunking, vetorização e persistência no ChromaDB
└── bot_discord.py           # Interface Discord: comandos de barra (/pop, /addpop)
```

---

## 🔒 Publicação Segura no GitHub

> [!IMPORTANT]
> Os arquivos PDF em `pops_originais/`, os textos em `pops_textos_extraidos/` e os dados em `chromadb_data/` podem conter informações confidenciais da sua empresa. **Eles nunca devem ser publicados em um repositório público.**

O `.gitignore` deste projeto já está pré-configurado para ignorar o banco de dados e todo o conteúdo das pastas de dados, mantendo apenas a estrutura via arquivos `.gitkeep`.

**Como publicar de forma limpa:**

Se você já fez commits com PDFs ou dados do ChromaDB no histórico local, a forma mais segura é criar um clone limpo apenas com o código:

1. Crie uma nova pasta fora do diretório atual (ex: `pops_ai_public/`).
2. Copie apenas os arquivos de código e configuração.
3. Crie as pastas de dados com `.gitkeep`.
4. Inicialize o Git e publique:

```bash
git init
git add .
git commit -m "Initial commit: POPS AI structure and API integration"
git remote add origin <URL_DO_SEU_REPOSITORIO>
git branch -M main
git push -u origin main
```

---

## 🗺️ Roadmap

Melhorias planejadas para versões futuras — contribuições são bem-vindas:

- [ ] Suporte a múltiplos idiomas na consulta (detecção automática)
- [ ] Integração com Slack (além do Discord)
- [ ] Histórico de conversas persistido por usuário
- [ ] Interface web simples para upload e consulta de POPs sem necessidade do Discord
- [ ] Suporte a documentos `.docx` além de PDF

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma **issue** com sugestões ou bugs, ou enviar um **pull request** com melhorias.

1. Fork o repositório
2. Crie sua branch: `git checkout -b feature/minha-melhoria`
3. Commit suas mudanças: `git commit -m 'feat: adiciona suporte a docx'`
4. Push para a branch: `git push origin feature/minha-melhoria`
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE) — sinta-se livre para usar, adaptar e distribuir.

---

<p align="center">
  Feito por <a href="https://github.com/obelucca">@obelucca</a>
</p>
