import streamlit as st
import urllib.parse
import scraper_apify
import analise_gemini

st.set_page_config(page_title="Gerador de Briefing Castor", page_icon="🦫")

st.title("Gerador de Briefing Automatizado")
st.write("Criação de Estrutura para Páginas Institucionais de Alta Conversão.")

# 1. Ajustamos o texto de instrução para o usuário
instagram_input = st.text_input("Instagram do Cliente (Ex: @cliente ou Link)")
maps_input = st.text_input("Nome da Empresa e Cidade ou Link do Maps (Ex: Bayar Advogados, Canoas)")

if st.button("Gerar Análise Profissional"):
    if not instagram_input:
        st.warning("⚠️ Por favor, insira pelo menos o Instagram (ex: @cliente).")
    else:
        with st.spinner('🦫 Coletando dados do Instagram e Google Maps (Aguarde 1~2 min)...'):
            
            # --- NOVA LÓGICA DE TRATAMENTO DO INSTAGRAM ---
            url_insta_tratada = instagram_input.strip()
            
            # Se não começar com 'http', significa que o usuário digitou só o @ ou o nome
            if url_insta_tratada and not url_insta_tratada.startswith("http"):
                # Se o usuário digitou com '@' no começo, removemos o '@'
                if url_insta_tratada.startswith("@"):
                    url_insta_tratada = url_insta_tratada[1:]
                
                # Montamos a URL completa oficial do Instagram
                url_insta_tratada = f"https://www.instagram.com/{url_insta_tratada}/"
            # ----------------------------------------------
            
            # --- LÓGICA DE TRATAMENTO DO MAPS (Mantida) ---
            url_maps_tratada = maps_input.strip() if maps_input else ""
            
            if url_maps_tratada and not url_maps_tratada.startswith("http"):
                termo_codificado = urllib.parse.quote(url_maps_tratada)
                url_maps_tratada = f"https://www.google.com/maps/search/?api=1&query={termo_codificado}"
            # ----------------------------------------------

            # Passo 1: Chama o scraper passando as DUAS URLs já formatadas
            pasta_do_cliente = scraper_apify.rodar_extracao(url_insta_tratada, url_maps_tratada)
            
            if not pasta_do_cliente or "Erro" in pasta_do_cliente:
                st.error(pasta_do_cliente if pasta_do_cliente else "Erro desconhecido na extração.")
                st.stop()
                
            st.success("Dados extraídos! O cérebro digital está analisando...")
            
        with st.spinner('🧠 Processando Alta Costura Digital e Prova Social...'):
            # Passo 2: Manda a pasta pro Gemini ler
            relatorio_final = analise_gemini.gerar_briefing(pasta_do_cliente)
            
            st.markdown("### 👔 Resultado do Briefing")
            st.write(relatorio_final)
