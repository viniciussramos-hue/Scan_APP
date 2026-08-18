import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
import os
from datetime import datetime

SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Pro", layout="wide")
st.title("📄 Scanner de Documentos")

# 1. Captura
img_file = st.camera_input("Tire a foto do documento:")

if img_file:
    img = Image.open(img_file)
    
    st.subheader("1. Ajuste as bordas:")
    # Interface de corte
    cropped_img = st_cropper(img, realtime_update=True, box_color='green')
    
    # 2. Pré-visualização (Renderização)
    st.subheader("2. Pré-visualização do resultado:")
    st.image(cropped_img, caption="Como ficará salvo", use_container_width=True)
    
    # 3. Salvar
    nome_padrao = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    nome = st.text_input("Nome do arquivo:", value=nome_padrao)
    
    if st.button("💾 Salvar no Computador", type="primary"):
        caminho = os.path.join(SAVE_DIR, f"{nome}.jpg")
        cropped_img.convert("RGB").save(caminho, quality=100)
        st.success(f"Arquivo salvo com sucesso em: {caminho}")
        st.balloons() # Feedback de sucesso

# --- GERENCIAMENTO ---
st.markdown("---")
st.subheader("📂 Documentos Armazenados")
if os.path.exists(SAVE_DIR):
    arquivos = [f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")]
    for arq in sorted(arquivos, reverse=True):
        col1, col2 = st.columns([4, 1])
        col1.text(f"• {arq}")
        if col2.button("🗑️ Deletar", key=f"del_{arq}"):
            os.remove(os.path.join(SAVE_DIR, arq))
            st.rerun()
