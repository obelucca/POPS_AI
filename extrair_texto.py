from PyPDF2 import PdfReader
import os 

def extrair_texto_pdf(caminho_pdf):
    try:
        reader = PdfReader(caminho_pdf)
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() + "\n"
        return texto_completo
    except Exception as e:
        print(f"Erro ao extrair texto do PDF {caminho_pdf}: {e}")
        return None
    
def processar_pasta_pdfs(pasta_origem, pasta_destino_txt):
    if not os.path.exists(pasta_destino_txt):
        os.makedirs(pasta_destino_txt) # Cria a pasta de destino se ela não existir

    for nome_arquivo in os.listdir(pasta_origem):
        if nome_arquivo.lower().endswith(".pdf"):
            caminho_pdf_completo = os.path.join(pasta_origem, nome_arquivo)
            print(f"Extraindo texto de: {nome_arquivo}...")
            texto_extraido = extrair_texto_pdf(caminho_pdf_completo)

            if texto_extraido:
                # Cria o nome do arquivo .txt com o mesmo nome do PDF, mas com extensão .txt
                nome_txt = nome_arquivo.replace(".pdf", ".txt")
                caminho_txt_completo = os.path.join(pasta_destino_txt, nome_txt)
                with open(caminho_txt_completo, "w", encoding="utf-8") as f:
                    f.write(texto_extraido)
                print(f"Texto salvo em: {caminho_txt_completo}")
            else:
                print(f"Não foi possível extrair texto de: {nome_arquivo}")

PASTA_DOS_PDFS = "pops_originais" 
PASTA_TEXTOS_EXTRAIDOS = "pops_textos_extraidos"

if not os.path.exists(PASTA_DOS_PDFS):
    os.makedirs(PASTA_DOS_PDFS)
    print(f"Pasta '{PASTA_DOS_PDFS}' criada. Coloque seus PDFs aqui.")
else:
    print(f"Pasta '{PASTA_DOS_PDFS}' já existe.")
    processar_pasta_pdfs(PASTA_DOS_PDFS, PASTA_TEXTOS_EXTRAIDOS)

print("\nExtração de texto dos PDFs concluída!")