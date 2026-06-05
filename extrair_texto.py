from PyPDF2 import PdfReader
import fitz
import os 
from PIL import Image
import io

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
    

def extrair_imagens_pdf(caminho_pdf, pasta_destino_imagens):
    
    if not os.path.exists(pasta_destino_imagens):
        os.makedirs(pasta_destino_imagens)

    imagens_salvas = []
    try:
        doc = fitz.open(caminho_pdf)
        nome_base_pdf = os.path.splitext(os.path.basename(caminho_pdf))[0]

        for i, page in enumerate(doc):
            
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                
                image_filename = f"{nome_base_pdf}_page{i+1}_img{img_index+1}.{image_ext}"
                caminho_imagem_completo = os.path.join(pasta_destino_imagens, image_filename)

                try:
                    img_pil = Image.open(io.BytesIO(image_bytes))
                    img_pil.save(caminho_imagem_completo)
                    imagens_salvas.append(caminho_imagem_completo)
                except Exception as e:
                    print(f"Não foi possível salvar imagem {image_filename} (xref={xref}): {e}")
                    
                    continue
        doc.close()
        return imagens_salvas
    except Exception as e:
        print(f"Erro ao extrair imagens do PDF {caminho_pdf}: {e}")
        return []
    
def processar_pasta_pdfs_e_imagens(pasta_origem, pasta_destino_txt, pasta_destino_imagens):
    if not os.path.exists(pasta_destino_txt):
        os.makedirs(pasta_destino_txt)
    if not os.path.exists(pasta_destino_imagens):
        os.makedirs(pasta_destino_imagens)

    for nome_arquivo in os.listdir(pasta_origem):
        if nome_arquivo.lower().endswith(".pdf"):
            caminho_pdf_completo = os.path.join(pasta_origem, nome_arquivo)
            print(f"Processando PDF: {nome_arquivo}...")

            texto_extraido = extrair_texto_pdf(caminho_pdf_completo)
            if texto_extraido:
                nome_txt = nome_arquivo.replace(".pdf", ".txt")
                caminho_txt_completo = os.path.join(pasta_destino_txt, nome_txt)
                with open(caminho_txt_completo, "w", encoding="utf-8") as f:
                    f.write(texto_extraido)
                print(f"Texto salvo em: {caminho_txt_completo}")
            else:
                print(f"Não foi possível extrair texto de: {nome_arquivo}")

        
            imagens_salvas_paths = extrair_imagens_pdf(caminho_pdf_completo, pasta_destino_imagens)
            if imagens_salvas_paths:
                print(f"Imagens salvas para {nome_arquivo}: {len(imagens_salvas_paths)}")
            else:
                print(f"Nenhuma imagem encontrada ou extraída de: {nome_arquivo}")

PASTA_DOS_PDFS = "pops_originais"
PASTA_TEXTOS_EXTRAIDOS = "pops_textos_extraidos"
PASTA_IMAGENS_EXTRAIDAS = "pops_imagens_extraidas"

if __name__ == '__main__':
    if not os.path.exists(PASTA_DOS_PDFS):
        os.makedirs(PASTA_DOS_PDFS)
        print(f"Pasta '{PASTA_DOS_PDFS}' criada. Coloque seus PDFs aqui.")
    else:
        print(f"Pasta '{PASTA_DOS_PDFS}' já existe.")
        processar_pasta_pdfs_e_imagens(PASTA_DOS_PDFS, PASTA_TEXTOS_EXTRAIDOS, PASTA_IMAGENS_EXTRAIDAS) # Chamada atualizada

    print("\nExtração de texto e imagens dos PDFs concluída!")