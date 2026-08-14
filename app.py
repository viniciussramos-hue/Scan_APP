from datetime import datetime
import os
import cv2
import streamlit as st
from PIL import Image

# Configuração inicial
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
  os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Centralizado", page_icon="📠")

st.title("📠 Scanner Centralizado")
st.write("Escolha o método de captura abaixo:")

# Seleção de método
metodo = st.radio(
    "Selecione a câmera:", ["Webcam do Computador", "Câmera do Celular"]
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


# --- LÓGICA DO CELULAR ---
if metodo == "Câmera do Celular":
  st.subheader("Scanner Móvel")
  img_file = st.camera_input("Tire a foto pelo celular")

  if img_file:
    nome = st.text_input("Nome do arquivo (Celular):")
    if st.button("💾 Salvar Foto do Celular", key="btn_celular"):
      caminho = salvar_imagem(Image.open(img_file), nome)
      st.success(f"Salvo em: {caminho}")

# --- LÓGICA DA WEBCAM DO PC ---
else:
  st.subheader("Scanner de Mesa (Webcam PC)")
  nome_pc = st.text_input("Nome do arquivo (PC):")

  if st.button("📸 Capturar da Webcam do PC", key="btn_pc"):
    # Força a abertura usando o driver padrão do Windows (DirectShow)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
      st.error(
          "❌ Erro de Permissão ou Câmera Ocupada: O Windows bloqueou o acesso"
          " ou a câmera está em uso por outro app."
      )
    else:
      ret, frame = cap.read()
      cap.release()

      if ret and frame is not None:
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        caminho = salvar_imagem(img, nome_pc)
        st.image(img, caption="Captura Realizada", use_column_width=True)
        st.success(f"Salvo com sucesso em: {caminho}")
      else:
        st.error(
            "A câmera conectou, mas não conseguiu capturar o quadro de"
            " imagem."
        )

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
