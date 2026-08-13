from datetime import datetime
import os
import subprocess
import cv2
import streamlit as st
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Scanner para SharePoint",
    page_icon="📁",
    layout="centered",
)

# Defina aqui o caminho da pasta sincronizada do seu SharePoint ou OneDrive
# Exemplo (ajuste para o caminho real da sua máquina):
# SAVE_DIR = r"C:\Users\SeuUsuario\Empresa\NomeDoSharePoint - Documentos\Producao\Scans"
# Ou se preferir uma pasta local padrão na sua máquina:
SAVE_DIR = "documentos_escaneados"

if not os.path.exists(SAVE_DIR):
  os.makedirs(SAVE_DIR)

st.title("📁 Scanner com Destino no SharePoint/PC")
st.write(
    "Capture o documento pela webcam para salvá-lo automaticamente na pasta"
    " de destino."
)

# Exibe o caminho atual de salvamento para conferência
st.info(f"📁 Pasta de destino atual: `{os.path.abspath(SAVE_DIR)}`")

# Campo para nomear o arquivo antes de escanear
nome_padrao = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
nome_arquivo = st.text_input("Nome do arquivo a ser salvo:", value=nome_padrao)

col1, col2 = st.columns(2)

with col1:
  btn_capturar = st.button(
      "📸 Capturar e Salvar", type="primary", use_container_width=True
  )

with col2:
  # Botão para abrir a pasta no Windows automaticamente
  btn_abrir_pasta = st.button(
      "📂 Abrir Pasta no Computador", use_container_width=True
  )

# Ação de abrir a pasta
if btn_abrir_pasta:
  try:
    # Comando do Windows para abrir o explorador de arquivos na pasta
    subprocess.Popen(f'explorer "{os.path.abspath(SAVE_DIR)}"')
    st.success("Pasta aberta no Explorador de Arquivos!")
  except Exception as e:
    st.error(f"Erro ao tentar abrir a pasta: {e}")

# Ação de capturar a imagem
if btn_capturar:
  cap = cv2.VideoCapture(0)

  if not cap.isOpened():
    st.error(
        "Erro: Não foi possível acessar a câmera do computador. Verifique se"
        " ela está conectada."
    )
  else:
    ret, frame = cap.read()
    cap.release()

    if ret:
      frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      image = Image.fromarray(frame_rgb)

      nome_final = (
          nome_arquivo.strip() if nome_arquivo.strip() != "" else nome_padrao
      )
      caminho_completo = os.path.join(SAVE_DIR, f"{nome_final}.jpg")

      # Salva a imagem diretamente no diretório especificado
      image.convert("RGB").save(caminho_completo, "JPEG")

      st.success(f"Documento escaneado e salvo com sucesso!")
      st.info(f"Salvo em: `{caminho_completo}`")
      st.image(image, caption=f"Arquivo: {nome_final}.jpg", use_column_width=True)
    else:
      st.error("Falha ao capturar a imagem da câmera.")

# Histórico recente
st.markdown("---")
st.subheader("📂 Arquivos na Pasta de Destino")
if os.path.exists(SAVE_DIR):
  arquivos = os.listdir(SAVE_DIR)
  if arquivos:
    for arq in sorted(arquivos, reverse=True):
      st.text(f"• {arq}")
  else:
    st.info("A pasta está vazia.")
