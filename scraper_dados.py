import os
import urllib.request
from apify_client import ApifyClient
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
    # 1. EXTRAÇÃO DO INSTAGRAM (Híbrida: $0.30 + $0.99)
    # ---------------------------------------------------------
    try:
        print(f"🦫 Iniciando extração híbrida e otimizada do Instagram para: @{nome_cliente}")
        client = ApifyClient("<YOUR_API_TOKEN>")
        
        # --- PASSO A: O scraper barato ($0.30) faz o trabalho braçal ---
        print("Executando scraper low-cost para dados base e mídia...")
        run_input_barato = {
            "usernames": [nome_cliente],
            "postsPerProfile": 1, # Puxa só 1 post para extrair o bloco 'user' (nome e foto)
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            }
        }
        run_barato = client.actor("sones/instagram-posts-scraper-lowcost").call(run_input=run_input_barato)
        
        dados_baratos = {}
        for item in client.dataset(run_barato.default_dataset_id).iterate_items():
            if "user" in item:
                dados_baratos = item["user"]
                break
                
        nome_completo = dados_baratos.get("full_name", "")
        foto_perfil_url = dados_baratos.get("profile_pic_url", "")
        
        # --- PASSO B: O scraper premium ($0.99) pega só o que o barato não consegue ---
        print("Executando scraper premium apenas para Bio e métricas...")
        run_input_caro = {
            "profiles": [nome_cliente],
            "scrape_profile_data": True,
            "scrape_posts": False,
            "scrape_reels": False,
        }
        run_caro = client.actor("hpix/instagram-scraper").call(run_input=run_input_caro)
        
        dados_caros = {}
        for item in client.dataset(run_caro.default_dataset_id).iterate_items():
            if item.get("profile"):
                dados_caros = item["profile"]
                break
                
        bio = dados_caros.get("biography", "")
        seguidores = dados_caros.get("followers", 0)
        categoria = dados_caros.get("business_category_name", "N/A")

        # Salva todos os dados combinados no arquivo
        with open(os.path.join(pasta_insta, "dados_perfil.txt"), "w", encoding="utf-8") as f:
            f.write(f"Nome: {nome_completo}\n")
            f.write(f"Bio: {bio}\n")
            f.write(f"Seguidores: {seguidores}\n")
            f.write(f"Categoria: {categoria}\n")
            
        # Baixa a foto de perfil usando o link do scraper mais barato
        if foto_perfil_url:
            urllib.request.urlretrieve(foto_perfil_url, os.path.join(pasta_insta, "foto_perfil.jpg"))

    except Exception as e:
        print(f"Aviso na extração do Instagram com Apify: {e}")

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
