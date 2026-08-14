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

st.title("📠 Scanner Centralizado & Gestão")
modo_app = st.sidebar.radio("Modo:", ["📷 Documentos", "🖼️ Fotos"])
dispositivo = st.radio("Dispositivo:", ["Webcam do PC", "Celular"])

# --- FUNÇÕES DE PROCESSAMENTO ---
def aplicar_ajustes(img, brilho, contraste):
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brilho)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contraste)
    return img

def processar_auto_doc(imagem_pil):
    img_cv = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
    # ... (mesma lógica de detecção de bordas anterior)
    cinza = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    adaptativo = cv2.adaptiveThreshold(cinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 10)
    return Image.fromarray(adaptativo)

# --- LÓGICA DE CAPTURA ---
img_capturada = st.camera_input("Capturar:", key="cam")

if img_capturada is not None:
    img = Image.open(img_capturada)
    
    st.sidebar.subheader("🎛️ Ajustes Manuais")
    brilho = st.sidebar.slider("Brilho", 0.5, 2.0, 1.0)
    contraste = st.sidebar.slider("Contraste", 0.5, 2.0, 1.0)
    
    # Aplica ajustes manuais
    img_final = aplicar_ajustes(img, brilho, contraste)
    
    # Opção para tratamento automático estilo scanner
    if modo_app == "📷 Documentos":
        if st.checkbox("✅ Aplicar Filtro de Scanner (B&W)"):
            img_final = processar_auto_doc(img_final)
            
    st.image(img_final, use_container_width=True)
    
    nome_arq = st.text_input("Nome do arquivo:")
    if st.button("💾 Salvar"):
        nome_final = nome_arq if nome_arq else f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        img_final.convert("RGB").save(os.path.join(SAVE_DIR, f"{nome_final}.jpg"), "JPEG")
        st.success("Salvo!")

# --- GERENCIAMENTO ---
st.markdown("---")
if os.path.exists(SAVE_DIR):
    arquivos = [f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")]
    for arq in sorted(arquivos, reverse=True):
        caminho = os.path.join(SAVE_DIR, arq)
        col1, col2, col3 = st.columns([3,1,1])
        with col1: st.text(arq)
        with col2:
            with open(caminho, "rb") as f:
                st.download_button("📥", f, arq, key=f"dl_{arq}")
        with col3:
            if st.button("🗑️", key=f"del_{arq}"):
                os.remove(caminho)
                st.rerun()
