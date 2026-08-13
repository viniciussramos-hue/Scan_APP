import streamlit as st
import os
import cv2
from datetime import datetime
from PIL import Image

# Configuração inicial
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Centralizado", page_icon="📠")

st.title("📠 Scanner Centralizado")
st.write("Escolha o método de captura abaixo:")

# Seleção de método
metodo = st.radio("Selecione a câmera:", ["Webcam do Computador", "Câmera do Celular"])

# Pasta de destino
st.info(f"📁 Pasta destino: {os.path.abspath(SAVE_DIR)}")

# --- FUNÇÃO PARA SALVAR ---
def salvar_imagem(img, nome):
    nome_final = nome.strip() if nome.strip() != "" else f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    caminho = os.path.join(SAVE_DIR, f"{nome_final}.jpg")
    img.convert("RGB").save(caminho, "JPEG")
    return caminho

# --- LÓGICA DO CELULAR ---
if metodo == "Câmera do Celular":
    st.subheader("Scanner Móvel")
    img_file = st.camera_input("Tire a foto pelo celular")
    if img_file:
        nome = st.text_input("Nome do arquivo (Celular):")
        if st.button("💾 Salvar Foto do Celular"):
            caminho = salvar_imagem(Image.open(img_file), nome)
            st.success(f"Salvo em: {caminho}")

# --- LÓGICA DA WEBCAM DO PC ---
else:
    st.subheader("Scanner de Mesa (Webcam PC)")
    nome_pc = st.text_input("Nome do arquivo (PC):")
    if st.button("📸 Capturar da Webcam do PC"):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            caminho = salvar_imagem(img, nome_pc)
            st.image(img, caption="Captura Realizada", use_column_width=True)
            st.success(f"Salvo em: {caminho}")
        else:
            st.error("Não foi possível acessar a webcam do PC.")

# --- GERENCIAMENTO ---
st.markdown("---")
st.subheader("📂 Documentos Armazenados")
arquivos = [f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")]
for arq in sorted(arquivos, reverse=True):
    with open(os.path.join(SAVE_DIR, arq), "rb") as file:
        st.download_button(label=f"📥 Baixar {arq}", data=file, file_name=arq, mime="image/jpeg")
