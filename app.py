import streamlit as st
import urllib.parse
import scraper_dados # Atualizado
import analise_gemini

st.set_page_config(page_title="Gerador de Briefing Castor", page_icon="🦫")

st.title("Gerador de Briefing Automatizado")
st.write("Criação de Estrutura para Páginas Institucionais de Alta Conversão.")

instagram_input = st.text_input("Instagram do Cliente (Ex: @cliente ou Link)")
maps_input = st.text_input("Nome da Empresa e Cidade ou Link do Maps (Ex: Bayar Advogados, Canoas)")

if st.button("Gerar Análise Profissional"):
    if not instagram_input:
        st.warning("⚠️ Por favor, insira pelo menos o Instagram (ex: @cliente).")
    else:
        with st.spinner('🦫 Coletando dados do Instagram e Google Maps (Aguarde 1~2 min)...'):
            
            url_insta_tratada = instagram_input.strip()
            if url_insta_tratada and not url_insta_tratada.startswith("http"):
                if url_insta_tratada.startswith("@"):
                    url_insta_tratada = url_insta_tratada[1:]
                url_insta_tratada = f"https://www.instagram.com/{url_insta_tratada}/"
            
            url_maps_tratada = maps_input.strip() if maps_input else ""
            if url_maps_tratada and not url_maps_tratada.startswith("http"):
                termo_codificado = urllib.parse.quote(url_maps_tratada)
                url_maps_tratada = f"https://www.google.com/maps/search/?api=1&query={termo_codificado}"

            # Chama o nosso novo scraper nativo
            pasta_do_cliente = scraper_dados.rodar_extracao(url_insta_tratada, url_maps_tratada)
            
            if not pasta_do_cliente or "Erro" in pasta_do_cliente:
                st.error(pasta_do_cliente if pasta_do_cliente else "Erro desconhecido na extração.")
                st.stop()
                
            st.success("Dados extraídos! O cérebro digital está analisando...")
            
        with st.spinner('🧠 Processando Alta Costura Digital e Prova Social...'):
            relatorio_final = analise_gemini.gerar_briefing(pasta_do_cliente)
            
            st.session_state['relatorio_final'] = relatorio_final
            st.session_state['pasta_do_cliente'] = pasta_do_cliente
            st.session_state['url_insta_tratada'] = url_insta_tratada

# --- INÍCIO DA NOVA INTEGRAÇÃO (Fora do primeiro botão) ---

# Só exibe essa parte se o briefing já estiver sido gerado e salvo na memória
if 'relatorio_final' in st.session_state:
    st.markdown("### 👔 Resultado do Briefing")
    st.write(st.session_state['relatorio_final'])

    st.markdown("---")
    st.markdown("### 🚀 Implantação Automática no GitHub")
    
    dominio_cliente = st.text_input("Qual será o subdomínio? (ex: cliente.epiverso.com)")
    
    # Botão Etapa 2: Gerar Site e Subir pro GitHub
    if st.button("Gerar Código Institucional e Subir"):
        with st.spinner("🤖 Gerando código de alta conversão e fazendo deploy..."):
            import gerador_site
            import github_deploy
            import urllib.parse
            
            # Recupera as variáveis da memória
            rel_final = st.session_state['relatorio_final']
            pasta_cliente = st.session_state['pasta_do_cliente']
            url_insta = st.session_state['url_insta_tratada']
            
            html_gerado, caminhos_fotos = gerador_site.criar_html_institucional(rel_final, pasta_cliente)
            
            if not html_gerado:
                st.error(caminhos_fotos) # Exibe mensagem de erro se falhar
            else:
                st.success("Código HTML estruturado com sucesso!")
                
                # Limpa o nome do cliente para criar o repo (ex: @joao -> joao)
                nome_repo = urllib.parse.urlparse(url_insta).path.strip('/').replace('/', '-')
                if not nome_repo: nome_repo = "novo-cliente"
                
                resultado_git = github_deploy.subir_para_github(html_gerado, caminhos_fotos, f"cliente-{nome_repo}", dominio_cliente)
                st.info(resultado_git)
                
                if "Sucesso" in resultado_git and dominio_cliente:
                    st.success(f"🎉 Implantação 100% concluída! O site já está no ar no domínio: http://{dominio_cliente}")
                    st.balloons() # Solta balões na tela para comemorar a automação perfeita
