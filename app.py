import streamlit as st
import urllib.parse
import json
import scraper_dados
import analise_gemini

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Gerador de Briefing Castor",
    page_icon="🦫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS CUSTOMIZADO PARA APARÊNCIA PROFISSIONAL
# ============================================================================
st.markdown("""
<style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e base */
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Container principal com glassmorphism */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin: 2rem auto;
        max-width: 1400px;
    }
    
    /* Títulos */
    h1, h2, h3, h4 {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }
    
    /* Subtítulo */
    .subtitle {
        color: #4a5568;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Cards de input */
    .input-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .input-card:hover {
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Botões customizados */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    .status-success {
        background: #c6f6d5;
        color: #22543d;
    }
    
    .status-warning {
        background: #feebc8;
        color: #744210;
    }
    
    .status-error {
        background: #fed7d7;
        color: #742a2a;
    }
    
    /* Seções de resultado */
    .result-section {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .result-header {
        border-bottom: 3px solid #667eea;
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* JSON display melhorado */
    .json-container {
        background: #1a202c;
        color: #48bb78;
        padding: 1.5rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Divider estilizado */
    .styled-divider {
        height: 3px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 2px;
        margin: 2rem 0;
    }
    
    /* Loading spinner customizado */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Remove padding excessivo do Streamlit */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER COM LOGO E TÍTULO
# ============================================================================
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.markdown("<div style='font-size: 3rem;'>🦫</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1>Gerador de Briefing Automatizado</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Criação de Estrutura para Páginas Institucionais de Alta Conversão com IA</p>", unsafe_allow_html=True)

# Container principal
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ============================================================================
# SEÇÃO 1: ENTRADA DE DADOS
# ============================================================================
st.markdown("### 📋 Dados do Cliente")
st.markdown("<p style='color: #718096; margin-bottom: 1.5rem;'>Preencha as informações abaixo para iniciar a análise automatizada.</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    instagram_input = st.text_input(
        "📸 Instagram do Cliente",
        placeholder="@cliente ou https://instagram.com/cliente",
        help="Digite o @ do Instagram ou a URL completa do perfil"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    maps_input = st.text_input(
        "📍 Google Maps (Opcional)",
        placeholder="Ex: Bayar Advogados, Canoas ou Link do Maps",
        help="Nome do negócio no Google Maps ou URL completa"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# BOTÃO DE GERAÇÃO DE ANÁLISE
# ============================================================================
st.markdown("")
generate_col = st.columns([2, 1, 2])
with generate_col[1]:
    generate_button = st.button(
        "🚀 Gerar Análise Profissional",
        type="primary",
        use_container_width=True
    )

# ============================================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================================
if generate_button:
    if not instagram_input:
        st.markdown('<div class="status-badge status-warning">⚠️ Por favor, insira pelo menos o Instagram do cliente.</div>', unsafe_allow_html=True)
    else:
        # Criar container de loading
        loading_container = st.container()
        with loading_container:
            # Barra de progresso animada
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Tratamento de URLs
            status_text.text("⏳ Processando URLs...")
            progress_bar.progress(10)
            
            url_insta_tratada = instagram_input.strip()
            if url_insta_tratada and not url_insta_tratada.startswith("http"):
                if url_insta_tratada.startswith("@"):
                    url_insta_tratada = url_insta_tratada[1:]
                url_insta_tratada = f"https://www.instagram.com/{url_insta_tratada}/"
            
            progress_bar.progress(20)
            
            # Step 2: Google Maps Iframe
            status_text.text("🗺️ Gerando mapa de localização...")
            url_maps_tratada = maps_input.strip() if maps_input else ""
            iframe_pronto = "" 
            
            if url_maps_tratada and not url_maps_tratada.startswith("http"):
                termo_codificado = urllib.parse.quote(url_maps_tratada)
                iframe_pronto = f'<iframe src="https://maps.google.com/maps?q={termo_codificado}&t=&z=14&ie=UTF8&iwloc=&output=embed" width="100%" height="400" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'
            
            progress_bar.progress(30)
            
            # Step 3: Scraper
            status_text.text("🦫 Coletando dados do Instagram e Google Maps...")
            progress_bar.progress(40)
            
            pasta_do_cliente = scraper_dados.rodar_extracao(url_insta_tratada, url_maps_tratada)
            
            progress_bar.progress(60)
            
            if not pasta_do_cliente or "Erro" in str(pasta_do_cliente):
                st.error(f"❌ {pasta_do_cliente if pasta_do_cliente else 'Erro desconhecido na extração.'}")
                st.stop()
            
            status_text.text("✅ Dados extraídos com sucesso!")
            st.success("✅ Dados coletados! Iniciando análise com IA...")
            progress_bar.progress(70)
        
        # Step 4: Análise Gemini
        with st.spinner('🧠 Processando estratégia digital e prova social...'):
            relatorio_final = analise_gemini.gerar_briefing(pasta_do_cliente, iframe_pronto)
            progress_bar.progress(90)
            
            # Salvar na sessão
            st.session_state['relatorio_final'] = relatorio_final
            st.session_state['pasta_do_cliente'] = pasta_do_cliente
            st.session_state['url_insta_tratada'] = url_insta_tratada
            st.session_state['iframe_pronto'] = iframe_pronto
            
            progress_bar.progress(100)
            status_text.text("✨ Análise concluída!")

# ============================================================================
# SEÇÃO 2: RESULTADOS E DEPLOY
# ============================================================================
if 'relatorio_final' in st.session_state:
    st.markdown('</div>', unsafe_allow_html=True)  # Fecha container principal
    
    # Divider
    st.markdown('<hr class="styled-divider"/>', unsafe_allow_html=True)
    
    # Novo container para resultados
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown('<div class="result-header">', unsafe_allow_html=True)
    st.markdown("### 👔 Resultado do Briefing")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tentar formatar como JSON
    try:
        dados_briefing = json.loads(st.session_state['relatorio_final'])
        
        # Exibir em formato de cards
        cols = st.columns(2)
        items = list(dados_briefing.items())
        
        for idx, (key, value) in enumerate(items):
            col_idx = idx % 2
            with cols[col_idx]:
                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                st.info(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False))
        
        # Expander para ver JSON completo
        with st.expander("📄 Ver JSON Completo"):
            st.code(json.dumps(dados_briefing, indent=2, ensure_ascii=False), language="json")
            
    except Exception as e:
        st.write(st.session_state['relatorio_final'])
        st.warning(f"⚠️ Não foi possível formatar como JSON: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================================
    # SEÇÃO 3: DEPLOY NO GITHUB
    # ============================================================================
    st.markdown('<div class="result-section" style="margin-top: 2rem;">', unsafe_allow_html=True)
    st.markdown('<div class="result-header">', unsafe_allow_html=True)
    st.markdown("### 🌐 Implantação Automática no GitHub")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_dominio, col_btn = st.columns([3, 1])
    with col_dominio:
        dominio_input = st.text_input(
            "Qual será o subdomínio?",
            placeholder="bayaradvogados",
            value=st.session_state.get('dominio_input', ''),
            help="Este será o prefixo do seu domínio (ex: bayaradvogados.epiverso.com)"
        )
        st.session_state['dominio_input'] = dominio_input
        
    with col_btn:
        st.write("")  # Espaçador
        deploy_button = st.button("📤 Gerar Site e Subir", type="secondary")
    
    if deploy_button:
        if not dominio_input:
            st.error("⚠️ Digite o nome do subdomínio antes de subir.")
        else:
            with st.spinner("🤖 Gerando código de alta conversão e fazendo deploy..."):
                import gerador_site
                import github_deploy
                
                rel_final = st.session_state['relatorio_final']
                pasta_cliente = st.session_state['pasta_do_cliente']
                url_insta = st.session_state['url_insta_tratada']
                
                # Gera o HTML
                html_gerado, caminhos_fotos = gerador_site.criar_html_institucional(rel_final, pasta_cliente)
                
                if not html_gerado:
                    st.error(f"❌ Erro ao gerar o site: {caminhos_fotos}") 
                else:
                    st.success("✅ Código HTML estruturado com sucesso!")
                    
                    # Preview do HTML
                    with st.expander("👁️ Preview do Código HTML"):
                        st.code(html_gerado[:2000] + "...", language="html")
                    
                    # Define o nome do repositório
                    nome_repo = urllib.parse.urlparse(url_insta).path.strip('/').replace('/', '-')
                    if not nome_repo: 
                        nome_repo = "novo-cliente"
                        
                    # Monta o domínio completo
                    dominio_completo = f"{dominio_input.strip().lower()}.epiverso.com"
                    
                    # Sobe para o GitHub
                    resultado_git = github_deploy.subir_para_github(
                        html_gerado, 
                        caminhos_fotos, 
                        f"cliente-{nome_repo}", 
                        dominio_completo
                    )
                    
                    # Exibir resultado
                    if "Sucesso" in resultado_git:
                        st.success(f"🎉 Implantação 100% concluída!")
                        st.balloons()
                        st.markdown(f"""
                        ### ✅ Site no ar!
                        - **URL:** http://{dominio_completo}
                        - **Repositório:** github.com/{st.session_state.get('github_user', 'usuario')}/cliente-{nome_repo}
                        """)
                    else:
                        st.error(resultado_git)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Fecha container de resultados

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #718096; padding: 2rem;'>"
    "<p>Desenvolvido com 💜 por EpiVerso | Powered by AI & Apify</p>"
    "</div>",
    unsafe_allow_html=True
)
