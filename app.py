from datetime import datetime
import os
import streamlit as st
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Scanner de Documentos - Local",
    page_icon="📷",
    layout="centered",
)

# Pasta onde os arquivos escaneados serão salvos no computador
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.title("📷 Scanner para Computador")
st.write(
    "Use a câmera do seu celular para fotografar um documento físico e salvá-lo "
    "diretamente no computador."
)

# Opção de escolha: Câmera ou Enviar arquivo existente
opcao = st.radio(
    "Escolha o método:", ["Tirar Foto com a Câmera", "Enviar Arquivo/Imagem"]
)

imagem_capturada = None

if opcao == "Tirar Foto con a Câmera":
    # Aciona a câmera do celular/dispositivo
    imagem_capturada = st.camera_input("Tire a foto do documento")
else:
    # Permite enviar um arquivo já salvo ou PDF/foto da galeria
    imagem_capturada = st.file_uploader(
        "Escolha a imagem do documento", type=["png", "jpg", "jpeg"]
    )

# Se uma imagem foi tirada ou enviada
if imagem_capturada is not None:
  # Exibe a pré-visualização
  image = Image.open(imagem_capturada)
  st.image(image, caption="Pré-visualização do Documento", use_column_width=True)

  # Campo para nomear o arquivo antes de salvar
  nome_padrao = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
  nome_arquivo = st.text_input("Nome do arquivo para salvar:", value=nome_padrao)

  if st.button("💾 Salvar no Computador", type="primary"):
    if nome_arquivo.strip() == "":
      st.warning("Por favor, insira um nome válido para o arquivo.")
    else:
      # Caminho completo do arquivo
      caminho_completo = os.path.id = os.path.join(
          SAVE_DIR, f"{nome_arquivo}.jpg"
      )

      # Salva a imagem convertida em RGB na pasta local
      image.convert("RGB").save(caminho_completo, "JPEG")

      st.success(f"Sucesso! Arquivo salvo em: `{caminho_completo}`")
      st.balloons()

# Exibir histórico recente de arquivos salvos na pasta
st.markdown("---")
st.subheader("📂 Documentos já salvos no PC")
if os.path.exists(SAVE_DIR):
  arquivos = os.listdir(SAVE_DIR)
  if arquivos:
    for arq in sorted(arquivos, reverse=True):
      st.text(f"• {arq}")
  else:
    st.info("Nenhum documento salvo ainda.")
