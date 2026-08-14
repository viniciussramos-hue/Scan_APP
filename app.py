from datetime import datetime
import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image

# Configuração inicial
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
  os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Centralizado", page_icon="📠")

st.title("📠 Scanner Centralizado & Gestão de Arquivos")
st.write(
    "Escolha o modo de operação desejado entre documentos digitalizados ou"
    " fotos normais:"
)

# Menu principal de navegação/modos
modo_app = st.sidebar.radio(
    "Escolha o Modo:",
    ["📷 Scanner de Documentos (Com Ajuste)", "🖼️ Fotos Normais / Galeria"],
)

# Dispositivo de captura
dispositivo = st.radio(
    "Dispositivo de origem:", ["Webcam do Computador", "Câmera do Celular"]
)

st.info(f"📁 Pasta destino no computador: {os.path.abspath(SAVE_DIR)}")


# --- FUNÇÃO DE PROCESSAMENTO (ESTILO CAMSCANNER PARA DOCUMENTOS) ---
def processar_como_documento(imagem_pil):
  img_cv = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)

  altura_original, largura_original = img_cv.shape[:2]
  ratio = altura_original / 500.0
  img_resized = cv2.resize(
      img_cv, (int(largura_original / ratio), int(500))
  )

  cinza = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
  desfoque = cv2.GaussianBlur(cinza, (5, 5), 0)
  bordas = cv2.Canny(desfoque, 75, 200)

  contornos, _ = cv2.findContours(
      bordas.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
  )
  contornos = sorted(contornos, key=cv2.contourArea, reverse=True)[:5]

  canto_documento = None
  for c in contornos:
    perimetro = cv2.arcLength(c, True)
    aproximacao = cv2.approxPolyDP(c, 0.02 * perimetro, True)
    if len(aproximacao) == 4:
      canto_documento = aproximacao
      break

  if canto_documento is not None:
    pts = canto_documento.reshape(4, 2) * ratio
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    (tl, tr, br, bl) = rect
    larguraA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    larguraB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    largura_maxima = max(int(larguraA), int(larguraB))

    alturaA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    alturaB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    altura_maxima = max(int(alturaA), int(alturaB))

    dst = np.array(
        [
            [0, 0],
            [largura_maxima - 1, 0],
            [largura_maxima - 1, altura_maxima - 1],
            [0, altura_maxima - 1],
        ],
        dtype="float32",
    )

    M = cv2.getPerspectiveTransform(rect, dst)
    comprimido = cv2.warpPerspective(
        img_cv, M, (largura_maxima, altura_maxima)
    )
    img_final = Image.fromarray(cv2.cvtColor(comprimido, cv2.COLOR_BGR2RGB))
    return img_final, True
  else:
    # Filtro de alto contraste tipo preto e branco para documentos caso não ache os cantos
    cinza_full = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    adaptativo = cv2.adaptiveThreshold(
        cinza_full,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        10,
    )
    img_final = Image.fromarray(adaptativo)
    return img_final, False


# --- FUNÇÃO PARA SALVAR ---
def salvar_imagem(img, nome, prefixo="doc"):
  nome_final = (
      nome.strip()
      if nome.strip() != ""
      else f"{prefixo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
  )
  caminho = os.path.join(SAVE_DIR, f"{nome_final}.jpg")
  img.convert("RGB").save(caminho, "JPEG")
  return caminho


st.markdown("---")

# ==========================================
# MODO 1: SCANNER DE DOCUMENTOS (COM AJUSTE)
# ==========================================
if modo_app == "📷 Scanner de Documentos (Com Ajuste)":
  st.subheader("📄 Módulo de Escaneamento de Documentos")
  st.write(
      "Este modo aplica o tratamento de bordas e ajuste de perspectiva para"
      " documentos físicos."
  )

  img_capturada = None
  if dispositivo == "Webcam do Computador":
    img_capturada = st.camera_input("Capturar documento via PC", key="doc_pc")
  else:
    img_capturada = st.camera_input(
        "Capturar documento via Celular", key="doc_cel"
    )

  if img_capturada is not None:
    imagem_original = Image.open(img_capturada)

    with st.spinner("Processando e ajustando o documento..."):
      imagem_processada, ajustado = processar_como_documento(imagem_original)

    st.image(
        imagem_processada,
        caption=(
            "Documento Ajustado com Sucesso"
            if ajustado
            else "Tratamento de Contraste Aplicado"
        ),
        use_column_width=True,
    )
    nome_doc = st.text_input("Nome do documento:", value="")

    if st.button("💾 Salvar Documento Ajustado", type="primary"):
      caminho = salvar_imagem(imagem_processada, nome_doc, prefixo="doc_scan")
      st.success(f"Salvo em: `{caminho}`")
      st.balloons()

# ==========================================
# MODO 2: FOTOS NORMAIS / GALERIA
# ==========================================
else:
  st.subheader("🖼️ Módulo de Fotos Normais")
  st.write(
      "Este modo salva a imagem exatamente como foi tirada, sem alterações"
      " geométricas."
  )

  img_foto = None
  if dispositivo == "Webcam do Computador":
    img_foto = st.camera_input("Tirar foto normal via PC", key="foto_pc")
  else:
    img_foto = st.camera_input("Tirar foto normal via Celular", key="foto_cel")

  if img_foto is not None:
    imagem_normal = Image.open(img_foto)
    st.image(
        imagem_normal, caption="Pré-visualização da Foto", use_column_width=True
    )
    nome_foto = st.text_input("Nome da foto:", value="")

    if st.button("💾 Salvar Foto Normal", type="primary"):
      caminho = salvar_imagem(imagem_normal, nome_foto, prefixo="foto")
      st.success(f"Foto salva em: `{caminho}`")
      st.balloons()

# ==========================================
# GERENCIAMENTO GERAL DOS ARQUIVOS SALVOS
# ==========================================
st.markdown("---")
st.subheader("📂 Gerenciamento de Arquivos no Computador")

if os.path.exists(SAVE_DIR):
  arquivos = [
      f
      for f in os.listdir(SAVE_DIR)
      if f.endswith((".jpg", ".jpeg", ".png"))
  ]

  if arquivos:
    st.write(f"Total de {len(arquivos)} arquivo(s) armazenado(s):")

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
    st.info("A pasta de destino está vazia.")
