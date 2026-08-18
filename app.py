from datetime import datetime
import os
from PIL import Image
import streamlit as st
from streamlit_cropper import st_cropper

SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
  os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Pro - Alta Resolução", layout="wide")
st.title("📄 Scanner de Documentos (Alta Resolução)")

st.write(
    "💡 **Dica:** Para fotos perfeitas e sem perda de qualidade ao dar zoom,"
    " clique abaixo para tirar a foto com a câmera nativa do seu celular ou"
    " fazer upload de um arquivo."
)

# Componente de upload/captura nativa em alta resolução
img_file = st.file_uploader(
    "Tire uma foto ou selecione o arquivo:", type=["jpg", "jpeg", "png"]
)

if img_file is not None:
  img = Image.open(img_file)

  st.subheader("1. Ajuste as bordas do documento:")
  # Interface de corte interativo mantendo a resolução original da foto
  cropped_img = st_cropper(img, realtime_update=True, box_color="green")

  st.subheader("2. Pré-visualização em Alta Definição:")
  st.image(
      cropped_img,
      caption="Documento em tamanho real (Zoom nítido e perfeito)",
      use_container_width=True,
  )

  nome_padrao = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
  nome = st.text_input("Nome do arquivo:", value=nome_padrao)

  if st.button("💾 Salvar na Pasta do Servidor", type="primary"):
    caminho = os.path.join(SAVE_DIR, f"{nome}.jpg")
    # Salva mantendo 100% de qualidade da foto original
    cropped_img.convert("RGB").save(caminho, quality=100)
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
        # Botão para baixar e escolher o diretório desejado no PC
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
