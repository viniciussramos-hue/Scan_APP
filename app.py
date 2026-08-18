import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
import os
from datetime import datetime

# Configuração
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner com Corte", page_icon="✂️")
st.title("✂️ Scanner com Ajuste de Bordas")

# 1. Captura
img_file = st.camera_input("Tire a foto do documento:")

if img_file:
    img = Image.open(img_file)
    
    st.subheader("Ajuste as bordas do documento:")
    
    # 2. Interface de Corte Interativa
    # O componente cria a caixa verde que você pode arrastar e redimensionar
    cropped_img = st_cropper(
        img, 
        realtime_update=True, 
        box_color='green', 
        aspect_ratio=None # Permite corte livre
    )
    
    # 3. Salvar
    if st.button("💾 Salvar corte final"):
        nome = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cropped_img.save(os.path.join(SAVE_DIR, nome), quality=100)
        st.success(f"Documento salvo como {nome}!")

# --- GERENCIAMENTO ---
st.markdown("---")
if os.path.exists(SAVE_DIR):
    arquivos = [f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")]
    for arq in sorted(arquivos, reverse=True):
        st.text(f"• {arq}")
