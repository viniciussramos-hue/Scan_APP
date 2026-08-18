from datetime import datetime
import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance

# Configuração inicial
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Profissional", page_icon="📠")

# --- FUNÇÕES DE PROCESSAMENTO AVANÇADO ---
def ajustar_perspectiva(imagem_pil):
    """Detecta bordas e corrige a perspectiva do documento."""
    img_cv = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
    
    # Redimensionamento para detecção de bordas mais rápida
    ratio = img_cv.shape[0] / 500.0
    img_res = cv2.resize(img_cv, (int(img_cv.shape[1] / ratio), 500))
    
    # Detecção de bordas (Canny)
    gray = cv2.cvtColor(img_res, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4: # Se encontrou um retângulo
            pts = approx.reshape(4, 2) * ratio
            
            # Ordenar pontos para o Warp
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            
            # Perspectiva plana
            (tl, tr, br, bl) = rect
            widthA = np.sqrt(((br[0] - bl[0])**2) + ((br[1] - bl[1])**2))
            widthB = np.sqrt(((tr[0] - tl[0])**2) + ((tr[1] - tl[1])**2))
            maxW = max(int(widthA), int(widthB))
            heightA = np.sqrt(((tr[0] - br[0])**2) + ((tr[1] - br[1])**2))
            heightB = np.sqrt(((tl[0] - bl[0])**2) + ((tl[1] - bl[1])**2))
            maxH = max(int(heightA), int(heightB))
            
            dst = np.array([[0,0], [maxW-1,0], [maxW-1, maxH-1], [0, maxH-1]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(img_cv, M, (maxW, maxH))
            return Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
            
    return imagem_pil # Retorna original se não achar bordas

def aplicar_realce_texto(img):
    """Aplica foco e contraste para leitura profissional."""
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0) # Aumenta o foco/nitidez
    img = ImageEnhance.Contrast(img).enhance(1.2)
    return img

# --- INTERFACE ---
st.title("📠 Scanner Profissional")
img_capturada = st.camera_input("Capturar documento:", key="cam")

if img_capturada:
    img = Image.open(img_capturada)
    
    # Processamento Automático
    with st.spinner("Ajustando perspectiva e foco..."):
        img_ajustada = ajustar_perspectiva(img)
        img_final = aplicar_realce_texto(img_ajustada)
    
    st.image(img_final, caption="Documento Renderizado", use_container_width=True)
    
    if st.button("💾 Salvar Documento Ajustado"):
        nome_final = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        img_final.convert("RGB").save(os.path.join(SAVE_DIR, nome_final), "JPEG", quality=100)
        st.success(f"Documento salvo como {nome_final}")
