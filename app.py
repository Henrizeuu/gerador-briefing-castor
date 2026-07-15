import streamlit as st
import scraper_apify
import analise_gemini

st.set_page_config(page_title="Gerador de Briefing Castor", page_icon="🦫")

st.title("Gerador de Briefing Automatizado")
st.write("Criação de Estrutura para Páginas Institucionais de Alta Conversão.")

instagram_input = st.text_input("Instagram do Cliente (Ex: https://instagram.com/cliente)")
maps_input = st.text_input("Link do Google Maps da Empresa (Opcional)")

if st.button("Gerar Análise Profissional"):
    if not instagram_input:
        st.warning("⚠️ Por favor, insira pelo menos o link do Instagram.")
    else:
        with st.spinner('🦫 Coletando dados do Instagram e Google Maps (Aguarde 1~2 min)...'):
            # Passo 1: Chama o scraper e pega a pasta gerada
            pasta_do_cliente = scraper_apify.rodar_extracao(instagram_input, maps_input)
            
            if "Erro" in pasta_do_cliente:
                st.error(pasta_do_cliente)
                st.stop()
                
            st.success("Dados extraídos! O cérebro digital está analisando...")
            
        with st.spinner('🧠 Processando Alta Costura Digital e Prova Social...'):
            # Passo 2: Manda a pasta pro Gemini ler
            relatorio_final = analise_gemini.gerar_briefing(pasta_do_cliente)
            
            st.markdown("### 👔 Resultado do Briefing")
            st.write(relatorio_final)