from datetime import datetime
import os
from PIL import Image
import streamlit as st
from streamlit_cropper import st_cropper

SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
  os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Pro", layout="wide")
st.title("📄 Scanner de Documentos com Ajuste de Bordas")

# 1. Captura pela câmera
img_file = st.camera_input("Tire a foto do documento:")

if img_file:
  img = Image.open(img_file)

  st.subheader("1. Ajuste as bordas do documento:")
  # Interface de corte interativo (estilo CamScanner)
  cropped_img = st_cropper(img, realtime_update=True, box_color="green")

  # 2. Pré-visualização do resultado cortado
  st.subheader("2. Pré-visualização do resultado:")
  st.image(
      cropped_img, caption="Como o documento ficará salvo", use_container_width=True
  )

  # 3. Nomeação e Salvamento na pasta interna do projeto
  nome_padrao = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
  nome = st.text_input("Nome do arquivo:", value=nome_padrao)

  if st.button("💾 Salvar na Pasta do Servidor", type="primary"):
    caminho = os.path.join(SAVE_DIR, f"{nome}.jpg")
    cropped_img.convert("RGB").save(caminho, quality=100)
    st.success(f"Arquivo salvo com sucesso em: {caminho}")

# --- GERENCIAMENTO E DOWNLOAD PARA O PC ---
st.markdown("---")
st.subheader("📂 Documentos Armazenados")

if os.path.exists(SAVE_DIR):
  arquivos = [f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")]

  if arquivos:
    st.write(f"Total de {len(arquivos)} documento(s) na pasta:")

    for arq in sorted(arquivos, reverse=True):
      caminho_completo = os.path.join(SAVE_DIR, arq)

      # Criamos colunas para alinhar o nome, o botão de baixar e o de deletar
      col1, col2, col3 = st.columns([3, 1, 1])

      with col1:
        st.text(f"• {arq}")

      with col2:
        # Botão de download nativo: abre a janela do seu SO para escolher onde salvar no PC
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
