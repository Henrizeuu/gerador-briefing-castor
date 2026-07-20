import streamlit as st
import urllib.parse
import scraper_dados
import analise_gemini

# Configuração da Página
st.set_page_config(page_title="Gerador de Briefing Castor", page_icon="🦫", layout="wide")

st.title("🦫 Gerador de Briefing Automatizado")
st.write("Criação de Estrutura para Páginas Institucionais de Alta Conversão.")

# --- CAMPOS DE ENTRADA ---
col1, col2 = st.columns(2)
with col1:
    instagram_input = st.text_input("Instagram do Cliente", placeholder="Ex: @cliente ou Link completo")
with col2:
    maps_input = st.text_input("Google Maps (Opcional)", placeholder="Ex: Bayar Advogados, Canoas ou Link do Maps")

# --- BOTÃO 1: GERAÇÃO DE ANÁLISE ---
if st.button("🚀 Gerar Análise Profissional", type="primary", use_container_width=True):
    if not instagram_input:
        st.warning("⚠️ Por favor, insira pelo menos o Instagram do cliente.")
    else:
        with st.spinner('🦫 Coletando dados do Instagram e Google Maps (Aguarde 1~2 min)...'):
            # 1. Tratamento da URL do Instagram
            url_insta_tratada = instagram_input.strip()
            if url_insta_tratada and not url_insta_tratada.startswith("http"):
                if url_insta_tratada.startswith("@"):
                    url_insta_tratada = url_insta_tratada[1:]
                url_insta_tratada = f"https://www.instagram.com/{url_insta_tratada}/"
            
            # 2. Tratamento do Google Maps e Geração do Iframe
            url_maps_tratada = maps_input.strip() if maps_input else ""
            iframe_pronto = "" 
            
            if url_maps_tratada and not url_maps_tratada.startswith("http"):
                termo_codificado = urllib.parse.quote(url_maps_tratada)
                iframe_pronto = f'<iframe src="https://maps.google.com/maps?q={termo_codificado}&t=&z=14&ie=UTF8&iwloc=&output=embed" width="100%" height="400" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'

            # 3. CHAMADA DO SCRAPER (CORREÇÃO CRÍTICA: Chamado apenas 1 vez!)
            pasta_do_cliente = scraper_dados.rodar_extracao(url_insta_tratada, url_maps_tratada)
            
            if not pasta_do_cliente or "Erro" in str(pasta_do_cliente):
                st.error(pasta_do_cliente if pasta_do_cliente else "Erro desconhecido na extração.")
                st.stop()
            
            st.success("✅ Dados extraídos com sucesso! O cérebro digital está analisando...")

        # 4. Análise do Gemini
        with st.spinner(' Processando Alta Costura Digital e Prova Social...'):
            relatorio_final = analise_gemini.gerar_briefing(pasta_do_cliente, iframe_pronto)
            
            # Salva tudo na sessão para o próximo passo
            st.session_state['relatorio_final'] = relatorio_final
            st.session_state['pasta_do_cliente'] = pasta_do_cliente
            st.session_state['url_insta_tratada'] = url_insta_tratada
            st.session_state['iframe_pronto'] = iframe_pronto

# --- SEÇÃO 2: VISUALIZAÇÃO E DEPLOY (Só aparece se a análise já foi feita) ---
if 'relatorio_final' in st.session_state:
    st.markdown("---")
    st.markdown("### 👔 Resultado do Briefing")
    
    # Tenta formatar como JSON se o Gemini retornou JSON, senão mostra texto puro
    try:
        import json
        dados_briefing = json.loads(st.session_state['relatorio_final'])
        st.json(dados_briefing)
    except:
        st.write(st.session_state['relatorio_final'])
        
    st.markdown("---")
    st.markdown("### 🌐 Implantação Automática no GitHub")
    
    col_dominio, col_btn = st.columns([3, 1])
    with col_dominio:
        dominio_input = st.text_input("Qual será o subdomínio?", placeholder="Ex: bayaradvogados", value=st.session_state.get('dominio_input', ''))
        st.session_state['dominio_input'] = dominio_input # Mantém o valor na tela
        
    with col_btn:
        st.write("") # Espaçador
        if st.button("📤 Gerar Site e Subir", type="secondary"):
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
                        
                        st.info(resultado_git)
                        
                        if "Sucesso" in resultado_git and dominio_completo:
                            st.success(f" Implantação 100% concluída! Página no ar: http://{dominio_completo}")
                            st.balloons()
