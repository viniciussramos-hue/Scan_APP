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

st.set_page_config(page_title="Scanner Estilo CamScanner", page_icon="📠")

st.title("📠 Scanner Inteligente (Estilo CamScanner)")
st.write(
    "Capture o documento. O sistema fará o recorte e ajuste automático das"
    " bordas."
)

# Seleção de método
metodo = st.radio(
    "Selecione o dispositivo:", ["Webcam do Computador", "Câmera do Celular"]
)

# Pasta de destino
st.info(f"📁 Pasta destino: {os.path.abspath(SAVE_DIR)}")


# --- FUNÇÃO DE PROCESSAMENTO (ESTILO CAMSCANNER) ---
def ajustar_documento(imagem_pil):
  # Converte imagem PIL para formato OpenCV (BGR)
  img_cv = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)

  # Reduz a imagem para processamento mais rápido
  altura_original, largura_original = img_cv.shape[:2]
  ratio = altura_original / 500.0
  img_resized = cv2.resize(
      img_cv, (int(largura_original / ratio), int(500))
  )

  # Pré-processamento: escala de cinza, desfoque e detecção de bordas
  cinza = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
  desfoque = cv2.GaussianBlur(cinza, (5, 5), 0)
  bordas = cv2.Canny(desfoque, 75, 200)

  # Encontra os contornos
  contornos, _ = cv2.findContours(
      bordas.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
  )
  contornos = sorted(contornos, key=cv2.contourArea, reverse=True)[:5]

  canto_documento = None

  # Procura por um contorno de 4 cantos (o papel)
  for c in contornos:
    perimetro = cv2.arcLength(c, True)
    aproximacao = cv2.approxPolyDP(c, 0.02 * perimetro, True)

    if len(aproximacao) == 4:
      canto_documento = aproximacao
      break

  # Se encontrou as bordas do papel, faz a correção de perspectiva (Warp)
  if canto_documento is not None:
    pts = canto_documento.reshape(4, 2) * ratio

    # Ordena os pontos: superior esquerdo, superior direito, inferior direito, inferior esquerdo
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[argmax_s := np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    (tl, tr, br, bl) = rect

    # Calcula a largura do novo documento ajustado
    larguraA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    larguraB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    largura_maxima = max(int(larguraA), int(larguraB))

    # Calcula a altura do novo documento ajustado
    alturaA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    alturaB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    altura_maxima = max(int(alturaA), int(alturaB))

    # Destino dos pontos para a visão de cima (retangular perfeito)
    dst = np.array(
        [
            [0, 0],
            [largura_maxima - 1, 0],
            [largura_maxima - 1, altura_maxima - 1],
            [0, altura_maxima - 1],
        ],
        dtype="float32",
    )

    # Matriz de transformação e aplicação
    M = cv2.getPerspectiveTransform(rect, dst)
    comprimido = cv2.warpPerspective(
        img_cv, M, (largura_maxima, altura_maxima)
    )

    # Converte de volta para RGB (PIL)
    img_final = Image.fromarray(cv2.cvtColor(comprimido, cv2.COLOR_BGR2RGB))
    return img_final, True  # Retorna a imagem ajustada e True indicando sucesso no corte

  else:
    # Se não achar as bordas exatas automaticamente, retorna a imagem original tratada em preto e branco/contraste
    # aplicando um efeito visual de scanner (realce de texto)
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
def salvar_imagem(img, nome):
  nome_final = (
      nome.strip()
      if nome.strip() != ""
      else f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
  )
  caminho = os.path.join(SAVE_DIR, f"{nome_final}.jpg")
  img.convert("RGB").save(caminho, "JPEG")
  return caminho


# --- CAPTURA (WEBCAM PC OU CELULAR) ---
img_capturada = None

if metodo == "Webcam do Computador":
  st.subheader("Scanner de Mesa (Webcam PC)")
  img_capturada = st.camera_input(
      "Capture o documento pela webcam do PC", key="cam_pc"
  )
else:
  st.subheader("Scanner Móvel (Celular)")
  img_capturada = st.camera_input("Tire a foto pelo celular", key="cam_cel")

if img_capturada is not None:
  imagem_original = Image.open(img_capturada)

  # Processa o ajuste automático estilo CamScanner
  with st.spinner(
      "Processando e ajustando as bordas do documento automaticamente..."
  ):
    imagem_ajustada, encontrou_bordas = ajustar_documento(imagem_original)

  st.image(
      imagem_ajustada,
      caption=(
          "Documento Ajustado e Tratado"
          if encontrou_bordas
          else "Tratamento de Contraste Aplicado"
      ),
      use_column_width=True,
  )

  nome_arquivo = st.text_input("Nome do arquivo:", value="")

  if st.button("💾 Salvar Documento Ajustado", type="primary"):
    caminho = salvar_imagem(imagem_ajustada, nome_arquivo)
    st.success(f"Documento escaneado e salvo com sucesso em: `{caminho}`")
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
