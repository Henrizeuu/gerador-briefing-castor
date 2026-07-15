import os
import urllib.request
import instaloader
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
    # 1. EXTRAÇÃO DO INSTAGRAM (Usando Instaloader)
    # ---------------------------------------------------------
    try:
        L = instaloader.Instaloader(download_videos=False, save_metadata=False)
        profile = instaloader.Profile.from_username(L.context, nome_cliente)
        
        # Salva a Bio no diretório raiz do insta
        with open(os.path.join(pasta_insta, "dados_perfil.txt"), "w", encoding="utf-8") as f:
            f.write(f"Nome: {profile.full_name}\nBio: {profile.biography}\nSeguidores: {profile.followers}")
            
        # Salva a foto de perfil
        if profile.profile_pic_url:
            urllib.request.urlretrieve(profile.profile_pic_url, os.path.join(pasta_insta, "foto_perfil.jpg"))
            
        # Baixa as imagens e descrições dos últimos 10 posts
        for i, post in enumerate(profile.get_posts()):
            if i >= 10: break
            pasta_post = os.path.join(pasta_insta, post.shortcode)
            os.makedirs(pasta_post, exist_ok=True)
            
            urllib.request.urlretrieve(post.url, os.path.join(pasta_post, "imagem.jpg"))
            
            with open(os.path.join(pasta_post, "descricao.txt"), "w", encoding="utf-8") as f:
                f.write(post.caption if post.caption else "Sem legenda.")
                
    except Exception as e:
        print(f"Aviso na extração do Instagram: {e}")

    # ---------------------------------------------------------
    # 2. EXTRAÇÃO DO GOOGLE MAPS (Usando Playwright)
    # ---------------------------------------------------------
    if url_maps:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url_maps)
                # Aguarda o carregamento do painel do Maps
                page.wait_for_timeout(4000)
                
                # Extrai todo o texto da página para o Gemini garimpar as provas sociais
                texto_pagina = page.locator("body").inner_text()
                
                with open(os.path.join(pasta_maps, "avaliacoes.txt"), "w", encoding="utf-8") as f:
                    f.write(texto_pagina[:5000]) # Limita para não estourar o contexto
                    
                browser.close()
        except Exception as e:
            with open(os.path.join(pasta_maps, "avaliacoes.txt"), "w", encoding="utf-8") as f:
                f.write(f"Erro ao extrair Maps: {str(e)}")

    return pasta_do_cliente
