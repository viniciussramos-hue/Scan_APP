from datetime import datetime
import os
import streamlit as st
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Scanner Móvel para PC", page_icon="📱", layout="centered"
)

# Pasta onde os arquivos escaneados serão salvos no computador
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
  os.makedirs(SAVE_DIR)

st.title("📱 Scanner Móvel p/ Computador")
st.write(
    "Use a câmera do celular para escanear o documento. Ele será salvo"
    " automaticamente no computador."
)

# Campo para capturar a foto (funciona perfeitamente pelo celular)
img_file = st.camera_input("Tire a foto do documento")

if img_file is not None:
  # Abre e processa a imagem
  img = Image.open(img_file)

  # Nome padrão com data e hora
  nome_padrao = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
  nome_arquivo = st.text_input("Nome do arquivo:", value=nome_padrao)

  if st.button("💾 Salvar no Computador", type="primary"):
    nome_final = (
        nome_arquivo.strip() if nome_arquivo.strip() != "" else nome_padrao
    )
    caminho_final = os.path.join(SAVE_DIR, f"{nome_final}.jpg")

    # Salva na pasta do PC
    img.convert("RGB").save(caminho_final, "JPEG")
    st.success(f"Documento salvo com sucesso em: `{caminho_final}`")
    st.balloons()

# Área de gerenciamento de arquivos salvos
st.markdown("---")
st.subheader("📂 Documentos Armazenados")

if os.path.exists(SAVE_DIR):
  arquivos = [f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")]
  if arquivos:
    st.write(f"Total de {len(arquivos)} documento(s) salvo(s):")
    for arq in sorted(arquivos, reverse=True):
      caminho_completo = os.path.join(SAVE_DIR, arq)
      with open(caminho_completo, "rb") as file:
        st.download_button(
            label=f"📥 Baixar {arq}",
            data=file,
            file_name=arq,
            mime="image/jpeg",
        )
  else:
    st.info("Nenhum documento salvo ainda.")
