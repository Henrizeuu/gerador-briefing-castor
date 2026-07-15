import streamlit as st
import urllib.parse # <-- IMPORTANTE ADICIONAR ISSO AQUI
import scraper_apify
import analise_gemini

st.set_page_config(page_title="Gerador de Briefing Castor", page_icon="🦫")

st.title("Gerador de Briefing Automatizado")
st.write("Criação de Estrutura para Páginas Institucionais de Alta Conversão.")

instagram_input = st.text_input("Instagram do Cliente (Ex: https://instagram.com/cliente)")

# Mudamos a instrução para o usuário entender que pode digitar só o nome
maps_input = st.text_input("Nome da Empresa e Cidade ou Link do Maps (Ex: Bayar Advogados, Canoas)")

if st.button("Gerar Análise Profissional"):
    if not instagram_input:
        st.warning("⚠️ Por favor, insira pelo menos o link do Instagram.")
    else:
        with st.spinner('🦫 Coletando dados do Instagram e Google Maps (Aguarde 1~2 min)...'):
            
            # --- NOVA LÓGICA DE TRATAMENTO DO MAPS ---
            url_maps_tratada = maps_input
            
            # Se o usuário digitou algo, mas não é um link (não começa com http)
            if maps_input and not maps_input.startswith("http"):
                # Codifica o texto (troca espaços por %20, etc)
                termo_codificado = urllib.parse.quote(maps_input)
                # Cria a URL oficial de busca do Google Maps
                url_maps_tratada = f"https://www.google.com/maps/search/?api=1&query={termo_codificado}"
            # -----------------------------------------

            # Passo 1: Chama o scraper passando a URL tratada
            pasta_do_cliente = scraper_apify.rodar_extracao(instagram_input, url_maps_tratada)
            
            if not pasta_do_cliente or "Erro" in pasta_do_cliente:
                st.error(pasta_do_cliente if pasta_do_cliente else "Erro desconhecido na extração.")
                st.stop()
                
            st.success("Dados extraídos! O cérebro digital está analisando...")
            
        with st.spinner('🧠 Processando Alta Costura Digital e Prova Social...'):
            # Passo 2: Manda a pasta pro Gemini ler
            relatorio_final = analise_gemini.gerar_briefing(pasta_do_cliente)
            
            st.markdown("### 👔 Resultado do Briefing")
            st.write(relatorio_final)
