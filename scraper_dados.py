import os
import urllib.request
from ensta import Guest
from playwright.sync_api import sync_playwright

def rodar_extracao(url_insta, url_maps):
    # Extrai o nome do cliente a partir da URL do Instagram
    nome_cliente = url_insta.strip('/').split('/')[-1]
    if not nome_cliente:
        nome_cliente = "cliente_novo"
        
    pasta_do_cliente = f"./clientes/{nome_cliente}"
    pasta_insta = os.path.join(pasta_do_cliente, "instagram_downloads_apify")
    pasta_maps = os.path.join(pasta_do_cliente, "google_reviews_extraidas")
    
    # Cria a estrutura de pastas esperada pelo analise_gemini.py
    os.makedirs(pasta_insta, exist_ok=True)
    os.makedirs(pasta_maps, exist_ok=True)

    # ---------------------------------------------------------
    # 1. EXTRAÇÃO DO INSTAGRAM (Usando Ensta)
    # ---------------------------------------------------------
    try:
        print(f"🦫 Iniciando extração silenciosa do Instagram via Ensta para: @{nome_cliente}")
        
        # Inicializa o modo Guest (sem login)
        guest = Guest()
        perfil = guest.profile(nome_cliente)
        
        if perfil:
            # Salva a Bio e dados principais
            with open(os.path.join(pasta_insta, "dados_perfil.txt"), "w", encoding="utf-8") as f:
                f.write(f"Nome: {perfil.full_name}\n")
                f.write(f"Bio: {perfil.biography}\n")
                f.write(f"Seguidores: {perfil.follower_count}\n")
                f.write(f"Categoria: {perfil.category_name}\n")
                
            # Salva a foto de perfil em alta resolução
            if perfil.profile_picture_url_hd:
                urllib.request.urlretrieve(perfil.profile_picture_url_hd, os.path.join(pasta_insta, "foto_perfil.jpg"))
            elif perfil.profile_picture_url:
                urllib.request.urlretrieve(perfil.profile_picture_url, os.path.join(pasta_insta, "foto_perfil.jpg"))

            # Observação: O modo Guest do Ensta extrai perfeitamente a Bio e a Foto. 
            # Dependendo das atualizações recentes da API do Instagram, a extração de múltiplos 
            # posts via Guest pode ser limitada. Se o analise_gemini.py precisar das imagens 
            # dos últimos posts para a prova social, e o Ensta não trouxer, podemos 
            # usar o Playwright (logo abaixo) para pegar as fotos também.

    except Exception as e:
        print(f"Aviso na extração do Instagram com Ensta: {e}")

    # ---------------------------------------------------------
    # 2. EXTRAÇÃO DO GOOGLE MAPS (Usando Playwright)
    # ---------------------------------------------------------
    if url_maps:
        try:
            print("🗺️ Iniciando extração de provas sociais do Google Maps...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url_maps)
                
                # Aguarda o carregamento do painel do Maps
                page.wait_for_timeout(4000)
                
                # Extrai todo o texto da página para o Gemini garimpar as provas sociais
                texto_pagina = page.locator("body").inner_text()
                
                with open(os.path.join(pasta_maps, "avaliacoes.txt"), "w", encoding="utf-8") as f:
                    f.write(texto_pagina[:6000]) # Limite generoso para pegar várias avaliações
                    
                browser.close()
        except Exception as e:
            with open(os.path.join(pasta_maps, "avaliacoes.txt"), "w", encoding="utf-8") as f:
                f.write(f"Erro ao extrair Maps: {str(e)}")

    return pasta_do_cliente
