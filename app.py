from datetime import datetime
import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance

# Configuração inicial
SAVE_DIR = "documentos_escaneados"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Scanner Profissional", page_icon="📠")

# --- FORÇAR ALTA RESOLUÇÃO E ESTABILIZAÇÃO VIA JS ---
st.markdown("""
    <script>
    async function setupCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 4096 },
                    height: { ideal: 2160 },
                    facingMode: "environment"
                }
            });
        } catch (err) {
            console.error("Erro ao forçar alta resolução: ", err);
        }
    }
    setupCamera();
    </script>
""", unsafe_allow_html=True)

st.title("📠 Scanner Centralizado & Gestão")
modo_app = st.sidebar.radio("Modo:", ["📷 Documentos", "🖼️ Fotos"])
dispositivo = st.radio("Dispositivo:", ["Webcam do PC", "Celular"])

st.info(f"📁 Pasta destino: {os.path.abspath(SAVE_DIR)}")

# --- FUNÇÕES DE PROCESSAMENTO ---
def aplicar_ajustes(img, brilho, contraste):
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brilho)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contraste)
    return img

def processar_auto_doc(imagem_pil):
    # Aumenta a nitidez antes de processar para melhorar a leitura
    img_cv = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
    cinza = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Filtro de nitidez (Sharpening)
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    img_nitida = cv2.filter2D(cinza, -1, kernel)
    
    adaptativo = cv2.adaptiveThreshold(
        img_nitida, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return Image.fromarray(adaptativo)

# --- CAPTURA ---
# O parâmetro 'quality' ajuda a manter a resolução
img_capturada = st.camera_input("Capturar imagem:", key="cam")

if img_capturada is not None:
    img = Image.open(img_capturada)

    st.sidebar.subheader("🎛️ Ajustes Manuais")
    brilho = st.sidebar.slider("Brilho", 0.5, 2.0, 1.0)
    contraste = st.sidebar.slider("Contraste", 0.5, 2.0, 1.0)

    img_final = aplicar_ajustes(img, brilho, contraste)

    if modo_app == "📷 Documentos":
        if st.checkbox("✅ Aplicar Filtro de Scanner (B&W)"):
            img_final = processar_auto_doc(img_final)

    st.image(img_final, use_container_width=True)

    nome_arq = st.text_input("Nome do arquivo:")
    if st.button("💾 Salvar no Computador", type="primary"):
        nome_final = (nome_arq.strip() if nome_arq.strip() != "" else f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        caminho_final = os.path.join(SAVE_DIR, f"{nome_final}.jpg")
        # Salva com qualidade máxima (quality=100)
        img_final.convert("RGB").save(caminho_final, "JPEG", quality=100)
        st.success(f"Documento salvo em: `{caminho_final}`")

# --- GERENCIAMENTO ---
st.markdown("---")
st.subheader("📂 Documentos Armazenados")
if os.path.exists(SAVE_DIR):
    arquivos = [f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")]
    for arq in sorted(arquivos, reverse=True):
        caminho_completo = os.path.join(SAVE_DIR, arq)
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1: st.text(f"• {arq}")
        with col2:
            with open(caminho_completo, "rb") as file:
                st.download_button("📥 Baixar", file, arq, mime="image/jpeg", key=f"dl_{arq}")
        with col3:
            if st.button("🗑️ Deletar", key=f"del_{arq}"):
                os.remove(caminho_completo)
                st.rerun()
