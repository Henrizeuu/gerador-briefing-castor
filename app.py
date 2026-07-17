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
            iframe_pronto = "" # Inicializa a variável do Iframe
            
            if url_maps_tratada and not url_maps_tratada.startswith("http"):
                termo_codificado = urllib.parse.quote(url_maps_tratada)
                url_maps_tratada = f"https://www.google.com/maps/search/?api=1&query={termo_codificado}"
                
                # FABRICA O IFRAME HTML AQUI
                iframe_pronto = f'<iframe src="https://maps.google.com/maps?q={termo_codificado}&t=&z=14&ie=UTF8&iwloc=&output=embed" width="100%" height="400" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'

            # Chama o nosso novo scraper nativo
            pasta_do_cliente = scraper_dados.rodar_extracao(url_insta_tratada, url_maps_tratada)
            
            if not pasta_do_cliente or "Erro" in pasta_do_cliente:
                st.error(pasta_do_cliente if pasta_do_cliente else "Erro desconhecido na extração.")
                st.stop()
                
            st.success("Dados extraídos! O cérebro digital está analisando...")
            
        with st.spinner('🧠 Processando Alta Costura Digital e Prova Social...'):
            # Envia o iframe pronto para o Gemini não precisar alucinar
            relatorio_final = analise_gemini.gerar_briefing(pasta_do_cliente, iframe_pronto)
            
            st.session_state['relatorio_final'] = relatorio_final
            st.session_state['pasta_do_cliente'] = pasta_do_cliente
            st.session_state['url_insta_tratada'] = url_insta_tratada

# --- INÍCIO DA NOVA INTEGRAÇÃO (Fora do primeiro botão) ---

if 'relatorio_final' in st.session_state:
    st.markdown("### 👔 Resultado do Briefing")
    st.write(st.session_state['relatorio_final'])

    st.markdown("---")
    st.markdown("### 🚀 Implantação Automática no GitHub")
    
    # Mudei o texto de exemplo para instruir a digitar só o nome
    dominio_input = st.text_input("Qual será o subdomínio? (ex: bayaradvogados)")
    
    if st.button("Gerar Código Institucional e Subir"):
        with st.spinner("🤖 Gerando código de alta conversão e fazendo deploy..."):
            import gerador_site
            import github_deploy
            import urllib.parse
            
            # --- A MÁGICA ACONTECE AQUI ---
            # Transforma tudo em minúsculo, tira os espaços e cola o seu domínio base
            dominio_completo = f"{dominio_input.strip().lower()}.epiverso.com" if dominio_input else ""
            
            rel_final = st.session_state['relatorio_final']
            pasta_cliente = st.session_state['pasta_do_cliente']
            url_insta = st.session_state['url_insta_tratada']
            
            html_gerado, caminhos_fotos = gerador_site.criar_html_institucional(rel_final, pasta_cliente)
            
            if not html_gerado:
                st.error(caminhos_fotos) 
            else:
                st.success("Código HTML estruturado com sucesso!")
                
                nome_repo = urllib.parse.urlparse(url_insta).path.strip('/').replace('/', '-')
                if not nome_repo: nome_repo = "novo-cliente"
                
                # Agora mandamos a variável "dominio_completo" para o script do GitHub
                resultado_git = github_deploy.subir_para_github(html_gerado, caminhos_fotos, f"cliente-{nome_repo}", dominio_completo)
                st.info(resultado_git)
                
                if "Sucesso" in resultado_git and dominio_completo:
                    st.success(f"🎉 Implantação 100% concluída! A página institucional já está no ar no domínio: http://{dominio_completo}")
                    st.balloons()
