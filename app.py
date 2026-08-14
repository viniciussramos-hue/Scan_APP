from datetime import datetime
import os
import streamlit as st
from PIL import Image

# Configuração inicial
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
  os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Centralizado", page_icon="📠")

st.title("📠 Scanner Centralizado")
st.write("Escolha o método de captura e digitalize seus documentos:")

# Seleção de método
metodo = st.radio(
    "Selecione o dispositivo:", ["Webcam do Computador", "Câmera do Celular"]
)

# Pasta de destino
st.info(f"📁 Pasta destino: {os.path.abspath(SAVE_DIR)}")


# --- FUNÇÃO PARA SALVAR ---
def salvar_imagem(img, nome):
  nome_final = (
      nome.strip()
      if nome.strip() != ""
      else f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
  )
  caminho = os.path.join(SAVE_DIR, f"{nome_final}.jpg")
  img.convert("RGB").save(caminho, "JPEG")
  return caminho


# --- LÓGICA DA WEBCAM DO PC ---
if metodo == "Webcam do Computador":
  st.subheader("Scanner de Mesa (Webcam PC)")
  img_pc = st.camera_input("Capture o documento pela webcam do PC", key="cam_pc")

  if img_pc is not None:
    img = Image.open(img_pc)
    nome_pc = st.text_input("Nome do arquivo (PC):", key="nome_pc")

    if st.button("💾 Salvar Foto do PC", key="btn_salvar_pc"):
      caminho = salvar_imagem(img, nome_pc)
      st.success(f"Documento salvo com sucesso em: `{caminho}`")
      st.balloons()

# --- LÓGICA DO CELULAR ---
else:
  st.subheader("Scanner Móvel (Celular)")
  img_cel = st.camera_input("Tire a foto pelo celular", key="cam_cel")

  if img_cel is not None:
    img = Image.open(img_cel)
    nome_cel = st.text_input("Nome do arquivo (Celular):", key="nome_cel")

    if st.button("💾 Salvar Foto do Celular", key="btn_salvar_cel"):
      caminho = salvar_imagem(img, nome_cel)
      st.success(f"Documento salvo com sucesso em: `{caminho}`")
      st.balloons()

# --- GERENCIAMENTO E EXCLUSÃO DE ARQUIVOS ---
st.markdown("---")
st.subheader("📂 Documentos Armazenados e Gerenciamento")

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
          try:
            os.remove(caminho_completo)
            st.success(f"'{arq}' excluído com sucesso!")
            st.rerun()
          except Exception as e:
            st.error(f"Erro ao deletar: {e}")
  else:
    st.info("Nenhum documento salvo na pasta no momento.")
