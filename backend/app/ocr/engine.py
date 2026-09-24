import cv2
import pytesseract
import pdf2image
import numpy as np

def preprocessar_imagem(imagem):
    """Aplica filtros para melhorar a leitura do OCR."""
    # Converte para escala de cinza
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    # Aplica threshold para deixar o texto preto no fundo branco
    _, binario = cv2.threshold(cinza, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # Remove ruídos
    denoised = cv2.medianBlur(binario, 3)
    return denoised

def extrair_texto_ocr(caminho_pdf: str) -> str:
    """Converte PDF para imagem e aplica OCR."""
    texto_final = ""
    try:
        # Converte PDF para imagens (DPI alto para melhorar OCR)
        paginas = pdf2image.convert_from_path(caminho_pdf, dpi=300)
        
        for pagina in paginas:
            # Converte PIL para OpenCV
            imagem_cv = np.array(pagina)
            imagem_cv = cv2.cvtColor(imagem_cv, cv2.COLOR_RGB2BGR)
            
            # Pré-processa a imagem
            imagem_tratada = preprocessar_imagem(imagem_cv)
            
            # Aplica OCR
            texto = pytesseract.image_to_string(imagem_tratada, lang='por')
            texto_final += texto + "\n\n"
            
    except Exception as e:
        print(f"Erro no OCR: {e}")
        return ""
    return texto_final.strip()