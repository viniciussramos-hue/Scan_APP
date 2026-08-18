from datetime import datetime
import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import streamlit as st
from streamlit_cropper import st_cropper

SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
  os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Pro - Alta Resolução", layout="wide")
st.title("📄 Scanner de Documentos (Câmera com Alta Resolução)")

# Tenta abrir a câmera traseira do celular por padrão com foco em alta definição
try:
  img_file = st.camera_input(
      "Tire a foto do documento:", key="cam", facing_mode="environment"
  )
except TypeError:
  img_file = st.camera_input("Tire a foto do documento:", key="cam")

if img_file is not None:
  # Carrega a imagem original em alta qualidade
  img = Image.open(img_file)

  # --- PROCESSAMENTO DE NITIDEZ PARA EVITAR BORRÃO NO ZOOM ---
  # Converte para OpenCV para aplicar melhoria de foco e nitidez
  img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

  # Filtro de nitidez (Sharpening Kernel) para destacar os textos ao dar zoom
  kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
  img_nitida = cv2.filter2D(img_cv, -1, kernel)
  img_processada = Image.fromarray(cv2.cvtColor(img_nitida, cv2.COLOR_BGR2RGB))

  st.subheader("1. Ajuste as bordas do documento (Estilo CamScanner):")
  # Interface de corte interativo mantendo a resolução da foto tratada
  cropped_img = st_cropper(
      img_processada, realtime_update=True, box_color="green"
  )

  st.subheader("2. Pré-visualização em Alta Definição:")
  st.image(
      cropped_img,
      caption=(
          "Documento com foco aprimorado (Pronto para dar zoom sem perder"
          " qualidade)"
      ),
      use_container_width=True,
  )

  nome_padrao = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
  nome = st.text_input("Nome do arquivo:", value=nome_padrao)

  if st.button("💾 Salvar na Pasta do Servidor", type="primary"):
    caminho = os.path.join(SAVE_DIR, f"{nome}.jpg")
    # Salva com qualidade máxima (quality=100)
    cropped_img.convert("RGB").save(caminho, "JPEG", quality=100)
    st.success(f"Salvo com sucesso em alta definição: {caminho}")

# --- GERENCIAMENTO E DOWNLOAD PARA O PC ---
st.markdown("---")
st.subheader("📂 Documentos Armazenados")

if os.path.exists(SAVE_DIR):
  arquivos = [f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")]

  if arquivos:
    st.write(f"Total de {len(arquivos)} documento(s) na pasta:")

    for arq in sorted(arquivos, reverse=True):
      caminho_completo = os.path.join(SAVE_DIR, arq)
      col1, col2, col3 = st.columns([3, 1, 1])

      with col1:
        st.text(f"• {arq}")

      with col2:
        with open(caminho_completo, "rb") as file:
          st.download_button(
              label="📥 Baixar",
              data=file,
              file_name=arq,
              mime="image/jpeg",
              key=f"dl_{arq}",
          )

      with col3:
        if st.button("🗑️ Deletar", key=f"del_{arq}"):
          os.remove(caminho_completo)
          st.success(f"'{arq}' excluído!")
          st.rerun()
  else:
    st.info("Nenhum documento salvo no momento.")
