from datetime import datetime
import os
import cv2
import streamlit as st
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Scanner de Documentos - Webcam PC",
    page_icon="📠",
    layout="centered",
)

# Pasta onde os arquivos escaneados serão salvos no computador
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
  os.makedirs(SAVE_DIR)

st.title("📠 Scanner com Câmera do PC")
st.write(
    "Posicione o documento embaixo da webcam do computador e clique no botão"
    " abaixo para digitalizar."
)

# Campo para nomear o arquivo antes de escanear
nome_padrao = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
nome_arquivo = st.text_input("Nome do arquivo a ser salvo:", value=nome_padrao)

# Botão para capturar a imagem da webcam do PC
if st.button("📸 Capturar e Escanear", type="primary"):
  # Abre a webcam do computador (0 geralmente é a webcam padrão)
  cap = cv2.VideoCapture(0)

  if not cap.isOpened():
    st.error(
        "Erro: Não foi possível acessar a câmera do computador. Verifique se"
        " ela está conectada."
    )
  else:
    # Lê um frame da câmera
    ret, frame = cap.read()
    # Libera a câmera imediatamente após a captura
    cap.release()

    if ret:
      # Converte a imagem de BGR (OpenCV) para RGB (Pillow/Streamlit)
      frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      image = Image.fromarray(frame_rgb)

      # Define o caminho para salvar
      if nome_arquivo.strip() == "":
        nome_final = nome_padrao
      else:
        nome_final = nome_arquivo.strip()

      caminho_completo = os.path.join(SAVE_DIR, f"{nome_final}.jpg")

      # Salva o arquivo na pasta do computador
      image.save(caminho_completo, "JPEG")

      st.success(f"Documento escaneado e salvo com sucesso!")
      st.info(f"Salvo em: `{caminho_completo}`")

      # Mostra a imagem capturada na tela
      st.image(
          image, caption=f"Documento: {nome_final}.jpg", use_column_width=True
      )
    else:
      st.error("Falha ao capturar a imagem da câmera.")

# Exibir histórico recente de arquivos salvos na pasta
st.markdown("---")
st.subheader("📂 Documentos Escaneados no PC")
if os.path.exists(SAVE_DIR):
  arquivos = os.listdir(SAVE_DIR)
  if arquivos:
    for arq in sorted(arquivos, reverse=True):
      st.text(f"• {arq}")
  else:
    st.info("Nenhum documento escaneado ainda.")
