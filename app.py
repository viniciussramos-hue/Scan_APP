import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
import cv2
import numpy as np
import os
from datetime import datetime

SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Pro", layout="wide")
st.title("📄 Scanner com Detecção e Ajuste")

# 1. Função de Detecção Automática (CamScanner Style)
def detectar_e_cortar(img_pil):
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Pega o maior contorno
    contornos = sorted(contours, key=cv2.contourArea, reverse=True)
    if contornos:
        peri = cv2.arcLength(contornos[0], True)
        approx = cv2.approxPolyDP(contornos[0], 0.02 * peri, True)
        if len(approx) == 4:
            # Se detectou 4 pontos, corta automaticamente
            x, y, w, h = cv2.boundingRect(approx)
            return img_pil.crop((x, y, x + w, y + h))
    return img_pil # Retorna original se não detectar

# 2. Captura
img_file = st.camera_input("Tire a foto:", key="cam")

if img_file:
    img = Image.open(img_file)
    
    # Tenta detectar automaticamente
    img_detectada = detectar_e_cortar(img)
    
    st.subheader("Ajuste Final (Arraste se precisar)")
    # Interface interativa para ajuste fino
    img_final = st_cropper(img_detectada, realtime_update=True, box_color='blue')
    
    # 3. Salvar
    nome_padrao = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    nome = st.text_input("Nome do arquivo:", value=nome_padrao)
    
    if st.button("💾 Salvar no Computador"):
        caminho = os.path.join(SAVE_DIR, f"{nome}.jpg")
        img_final.convert("RGB").save(caminho, quality=100)
        st.success(f"Salvo em: {caminho}")

# --- GERENCIAMENTO ---
st.markdown("---")
if os.path.exists(SAVE_DIR):
    arquivos = [f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")]
    for arq in sorted(arquivos, reverse=True):
        col1, col2 = st.columns([4, 1])
        col1.text(f"• {arq}")
        if col2.button("🗑️ Deletar", key=f"del_{arq}"):
            os.remove(os.path.join(SAVE_DIR, arq))
            st.rerun()
