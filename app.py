from datetime import datetime
import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance

# Configuração
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Pro", page_icon="📄")
st.title("📄 Scanner de Documentos Pro")

# --- FUNÇÕES DE PROCESSAMENTO ---
def processar_documento(imagem_pil):
    # Converte PIL -> OpenCV
    img_cv = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
    
    # 1. Transformação de Perspectiva (Endireitar documento)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200)
    
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos = sorted(contours, key=cv2.contourArea, reverse=True)
    
    final_img = img_cv # Fallback
    for c in contornos:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            # Encontrou o documento: aplica perspectiva
            pts = approx.reshape(4, 2)
            # Ordena os pontos (tl, tr, br, bl)
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            
            (tl, tr, br, bl) = rect
            width = max(int(np.linalg.norm(br-bl)), int(np.linalg.norm(tr-tl)))
            height = max(int(np.linalg.norm(tr-br)), int(np.linalg.norm(tl-bl)))
            
            dst = np.array([[0,0], [width-1,0], [width-1, height-1], [0, height-1]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            final_img = cv2.warpPerspective(img_cv, M, (width, height))
            break

    # 2. Realce de Texto (Black & White)
    gray_final = cv2.cvtColor(final_img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray_final, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    return Image.fromarray(thresh)

# --- FLUXO DE CAPTURA ---
img_file = st.camera_input("Tire a foto do documento:", key="cam")

if img_file:
    img = Image.open(img_file)
    
    # Criamos um container para a imagem processada
    st.subheader("Visualização e Ajustes")
    
    # Botão para renderizar (força o processamento)
    if st.button("✨ Renderizar Documento / Ajustar Bordas"):
        with st.spinner("Processando..."):
            img_processada = processar_documento(img)
            st.session_state['img_final'] = img_processada
    
    # Exibe a imagem se já tiver sido renderizada
    if 'img_final' in st.session_state:
        st.image(st.session_state['img_final'], caption="Resultado Final", use_container_width=True)
        
        nome_arq = st.text_input("Nome do arquivo:")
        if st.button("💾 Salvar no Computador"):
            nome = nome_arq if nome_arq else f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state['img_final'].convert("RGB").save(os.path.join(SAVE_DIR, f"{nome}.jpg"), "JPEG", quality=100)
            st.success("Documento salvo!")
            del st.session_state['img_final'] # Limpa para a próxima
