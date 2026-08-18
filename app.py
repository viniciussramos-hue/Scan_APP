from datetime import datetime
import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance

SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Pro", page_icon="📄")
st.title("📄 Scanner de Documentos")

# --- FUNÇÃO DE PROCESSAMENTO (MAIS SEGURA) ---
def processar_documento(imagem_pil, sensibilidade, usar_filtro):
    img_cv = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
    
    # 1. Ajuste de Brilho/Contraste Automático para evitar branco total
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    img_cv = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    if not usar_filtro:
        return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

    # 2. Filtro B&W apenas se solicitado
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    # Sensibilidade dinâmica baseada no slider
    block_size = int(sensibilidade) * 2 + 1
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, block_size, 10)
    
    return Image.fromarray(thresh)

# --- FLUXO DE CAPTURA ---
img_file = st.camera_input("Tire a foto do documento:", key="cam")

if img_file:
    img = Image.open(img_file)
    
    st.subheader("Ajustes de Renderização")
    usar_filtro = st.checkbox("Aplicar Filtro Preto e Branco (Scanner)", value=True)
    sensibilidade = st.slider("Sensibilidade do Filtro (se ficar branco, diminua)", 1, 20, 10)
    
    if st.button("✨ Processar Documento"):
        with st.spinner("Ajustando iluminação..."):
            st.session_state['img_final'] = processar_documento(img, sensibilidade, usar_filtro)
    
    if 'img_final' in st.session_state:
        st.image(st.session_state['img_final'], use_container_width=True)
        
        nome_arq = st.text_input("Nome do arquivo:")
        if st.button("💾 Salvar no Computador"):
            nome = nome_arq if nome_arq else f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state['img_final'].convert("RGB").save(os.path.join(SAVE_DIR, f"{nome}.jpg"), "JPEG", quality=95)
            st.success("Documento salvo!")
            del st.session_state['img_final']
