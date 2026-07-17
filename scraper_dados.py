import os
import urllib.request
from apify_client import ApifyClient
from playwright.sync_api import sync_playwright

def rodar_extracao(url_insta, url_maps):
    nome_cliente = url_insta.strip('/').split('/')[-1]
    if not nome_cliente:
        nome_cliente = "cliente_novo"
        
    pasta_do_cliente = f"./clientes/{nome_cliente}"
    pasta_insta = os.path.join(pasta_do_cliente, "instagram_downloads_apify")
    pasta_maps = os.path.join(pasta_do_cliente, "google_reviews_extraidas")
    
    os.makedirs(pasta_insta, exist_ok=True)
    os.makedirs(pasta_maps, exist_ok=True)

    CHAVE_APIFY = os.environ.get("APIFY_TOKEN")
    client = ApifyClient(CHAVE_APIFY)

    # ---------------------------------------------------------
    # 1. EXTRAÇÃO DO INSTAGRAM (Híbrida: $0.30 + $0.99)
    # ---------------------------------------------------------
    try:
        print(f"🦫 Iniciando extração do Instagram para: @{nome_cliente}")
        
        # --- PASSO A: Scraper Low-cost para os Posts ---
        run_input_barato = {
            "usernames": [nome_cliente],
            "postsPerProfile": 12, 
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            }
        }
        run_barato = client.actor("sones/instagram-posts-scraper-lowcost").call(run_input=run_input_barato)
        
        nome_completo, foto_perfil_url = "", ""
        
        for item in client.dataset(run_barato.default_dataset_id).iterate_items():
            if "user" in item and not nome_completo:
                nome_completo = item["user"].get("full_name", "")
                foto_perfil_url = item["user"].get("profile_pic_url", "")
            
            if "code" in item:
                shortcode = item["code"]
                pasta_post = os.path.join(pasta_insta, shortcode)
                os.makedirs(pasta_post, exist_ok=True)
                
                legenda = item.get("caption", {}).get("text", "") if item.get("caption") else ""
                if legenda:
                    with open(os.path.join(pasta_post, "descricao.txt"), "w", encoding="utf-8") as f:
                        f.write(legenda)
                
                # --- A CORREÇÃO ESTÁ AQUI: Lendo a coluna image_url do seu print ---
                img_url = item.get("image_url")
                
                # Fallbacks caso seja um carrossel ou vídeo sem imagem na raiz
                if not img_url:
                    try:
                        if item.get("carousel_media") and len(item["carousel_media"]) > 0:
                            img_url = item["carousel_media"][0].get("image_url") or item["carousel_media"][0].get("image_versions2", {}).get("candidates", [{}])[0].get("url", "")
                        elif item.get("image_versions2") and item["image_versions2"].get("candidates"):
                            img_url = item["image_versions2"]["candidates"][0].get("url", "")
                    except:
                        pass
                
                # Salva a imagem na pasta
                if img_url:
                    try:
                        urllib.request.urlretrieve(img_url, os.path.join(pasta_post, "imagem.jpg"))
                    except:
                        pass
        
        # --- PASSO B: Scraper Premium para o Perfil (Bio, Seguidores, etc) ---
        run_input_caro = {
            "profiles": [nome_cliente],
            "scrape_profile_data": True,
            "scrape_posts": False,
            "scrape_reels": False,
        }
        run_caro = client.actor("hpix/instagram-scraper").call(run_input=run_input_caro)
        
        dados_caros = {}
        for item in client.dataset(run_caro.default_dataset_id).iterate_items():
            if item.get("kind") == "profile":
                dados_caros = item.get("data", {})
                break
            elif "biography" in item:
                dados_caros = item
                break

        bio = dados_caros.get("biography", "") or dados_caros.get("bio", "")
        seguidores = dados_caros.get("followers", 0) or dados_caros.get("followersCount", 0) or dados_caros.get("follower_count", 0)
        categoria = dados_caros.get("business_category_name", "N/A") or dados_caros.get("category_name", "N/A")

        with open(os.path.join(pasta_insta, "dados_perfil.txt"), "w", encoding="utf-8") as f:
            f.write(f"Nome: {nome_completo}\nBio: {bio}\nSeguidores: {seguidores}\nCategoria: {categoria}\n")
            
        if foto_perfil_url:
            try:
                urllib.request.urlretrieve(foto_perfil_url, os.path.join(pasta_insta, "foto_perfil.jpg"))
            except:
                pass

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

