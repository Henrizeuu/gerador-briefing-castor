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
# CSS CUSTOMIZADO PARA APARÊNCIA PROFISSIONAL - TEMA PRETO E BRANCO
# ============================================================================
st.markdown("""
<style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e base */
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Background clean */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Container principal */
    .main-container {
        background: #ffffff;
        border-radius: 0;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 1400px;
        border-left: 3px solid #000000;
        padding-left: 2rem;
    }
    
    /* Títulos */
    h1, h2, h3, h4 {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        color: #000000 !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase;
        letter-spacing: -1px;
    }
    
    /* Subtítulo */
    .subtitle {
        color: #666666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Cards de input */
    .input-card {
        background: #f8f9fa;
        border-radius: 0;
        padding: 1.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .input-card:hover {
        border-color: #000000;
        background: #ffffff;
    }
    
    /* Botões customizados */
    .stButton > button {
        background: #000000;
        color: #ffffff;
        border: 2px solid #000000;
        border-radius: 0;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        background: #ffffff;
        color: #000000;
        border-color: #000000;
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 0;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.5rem 0;
        border: 1px solid;
    }
    
    .status-success {
        background: #ffffff;
        color: #000000;
        border-color: #000000;
    }
    
    .status-warning {
        background: #fff8e1;
        color: #000000;
        border-color: #ffc107;
    }
    
    .status-error {
        background: #ffebee;
        color: #000000;
        border-color: #f44336;
    }
    
    /* Seções de resultado */
    .result-section {
        background: #ffffff;
        border-radius: 0;
        padding: 2rem;
        margin-top: 2rem;
        border: 1px solid #e0e0e0;
        border-left: 4px solid #000000;
    }
    
    .result-header {
        border-bottom: 2px solid #000000;
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* JSON display melhorado */
    .json-container {
        background: #000000;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 0;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Divider estilizado */
    .styled-divider {
        height: 2px;
        background: #000000;
        border: none;
        margin: 2rem 0;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 0;
        border: 1px solid #cccccc;
        padding: 0.75rem;
        transition: all 0.3s ease;
        background: #ffffff;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #000000;
        box-shadow: none;
        outline: 2px solid #000000;
        outline-offset: -1px;
    }
    
    /* Remove padding excessivo do Streamlit */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        border-radius: 0;
        border: 1px solid #e0e0e0;
        background: #f8f9fa;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #000000;
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
