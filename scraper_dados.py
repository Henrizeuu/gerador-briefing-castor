import os
import urllib.request
import urllib.parse
from apify_client import ApifyClient

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
    # 1.A. EXTRAÇÃO DO INSTAGRAM LOWCOST (POSTS: $0.30)
    # ---------------------------------------------------------
    try:
        print(f"🦫 Iniciando extração dos Posts (Lowcost) para: @{nome_cliente}")
        run_input_barato = {
            "usernames": [nome_cliente],
            "postsPerProfile": 12,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            }
        }
        
        run_barato = client.actor("sones/instagram-posts-scraper-lowcost").call(run_input=run_input_barato)
        
        for item in client.dataset(run_barato["defaultDatasetId"]).iterate_items():
            shortcode = item.get("code")
            if not shortcode: continue
            
            pasta_post = os.path.join(pasta_insta, shortcode)
            os.makedirs(pasta_post, exist_ok=True)
            
            legenda = ""
            if isinstance(item.get("caption"), dict):
                legenda = item["caption"].get("text", "")
                
            if legenda:
                with open(os.path.join(pasta_post, "descricao.txt"), "w", encoding="utf-8") as f:
                    f.write(legenda)
            
            img_url = ""
            try:
                if item.get("carousel_media"):
                    img_url = item["carousel_media"][0].get("image_versions2", {}).get("candidates", [{}])[0].get("url", "")
                elif item.get("image_versions2"):
                    img_url = item["image_versions2"].get("candidates", [{}])[0].get("url", "")
            except Exception:
                pass
            
            if img_url:
                try:
                    urllib.request.urlretrieve(img_url, os.path.join(pasta_post, "imagem.jpg"))
                except:
                    pass
    except Exception as e:
        print(f"Aviso na extração de Posts do Instagram: {e}")

    # ---------------------------------------------------------
    # 1.B. EXTRAÇÃO DO INSTAGRAM PREMIUM (PERFIL: $0.99)
    # ---------------------------------------------------------
    try:
        print(f"🦫 Iniciando extração do Perfil (Premium) para: @{nome_cliente}")
        
        # Restaurado com os seus parâmetros originais perfeitamente
        run_input_caro = {
            "profiles": [nome_cliente],
            "scrape_profile_data": True,
            "scrape_posts": False,
            "scrape_reels": False,
        }
        
        run_caro = client.actor("hpix/instagram-scraper").call(run_input=run_input_caro)
        
        nome_completo, bio, seguidores, categoria, foto_perfil_url = "", "", 0, "N/A", ""
        
        for item in client.dataset(run_caro["defaultDatasetId"]).iterate_items():
            # Adaptação para pegar os dados independente de como a API formatar
            if item.get("kind") == "profile":
                dados = item.get("data", {})
            else:
                dados = item
                
            if "biography" in dados or "bio" in dados:
                nome_completo = dados.get("full_name", "") or dados.get("fullName", "")
                bio = dados.get("biography", "") or dados.get("bio", "")
                seguidores = dados.get("followers", 0) or dados.get("followersCount", 0) or dados.get("follower_count", 0)
                foto_perfil_url = dados.get("profile_pic_url", "") or dados.get("profilePicUrl", "")
                categoria = dados.get("business_category_name", "N/A") or dados.get("category_name", "N/A") or dados.get("categoryName", "N/A")
                break 
            
        with open(os.path.join(pasta_insta, "dados_perfil.txt"), "w", encoding="utf-8") as f:
            f.write(f"Nome: {nome_completo}\nBio: {bio}\nSeguidores: {seguidores}\nCategoria: {categoria}\n")
            
        if foto_perfil_url:
            try:
                urllib.request.urlretrieve(foto_perfil_url, os.path.join(pasta_insta, "foto_perfil.jpg"))
            except:
                pass

    except Exception as e:
        print(f"Aviso na extração do Perfil do Instagram: {e}")

    # ---------------------------------------------------------
    # 2. EXTRAÇÃO DO GOOGLE MAPS
    # ---------------------------------------------------------
    if url_maps:
        try:
            print("🗺️ Iniciando extração de provas sociais do Google Maps via Apify...")

            run_input_maps = {
                "maxCrawledPlacesPerSearch": 1,
                "maxReviewsPerPlace": 15,
                "reviewsSort": "newest",
                "language": "pt"
            }

            # Lógica inteligente para definir se o input é texto ou Link Direto
            if "query=" in url_maps:
                termo_busca = urllib.parse.unquote(url_maps.split("query=")[1])
                run_input_maps["searchStringsArray"] = [termo_busca]
            elif url_maps.startswith("http"):
                run_input_maps["startUrls"] = [{"url": url_maps}] # Obrigatório para links do maps[cite: 11]
            else:
                run_input_maps["searchStringsArray"] = [url_maps]

            run_maps = client.actor("AabCualFIriz3X6Fs").call(run_input=run_input_maps)

            texto_avaliacoes = ""
            for item in client.dataset(run_maps["defaultDatasetId"]).iterate_items():
                nome_empresa = item.get("title", "Empresa Alvo")
                nota = item.get("totalScore", "Sem nota")
                reviews = item.get("reviews", [])

                texto_avaliacoes += f"Empresa: {nome_empresa} (Nota: {nota})\n\n"

                for rev in reviews:
                    autor = rev.get("author", "Anônimo")
                    texto_review = rev.get("text", "")
                    if texto_review:
                        texto_avaliacoes += f"{autor}: {texto_review}\n---\n"

            with open(os.path.join(pasta_maps, "avaliacoes.txt"), "w", encoding="utf-8") as f:
                f.write(texto_avaliacoes[:6000] if texto_avaliacoes else "Nenhuma avaliação com texto encontrada.")

        except Exception as e:
            with open(os.path.join(pasta_maps, "avaliacoes.txt"), "w", encoding="utf-8") as f:
                f.write(f"Erro ao extrair Maps via Apify: {str(e)}")

    return pasta_do_cliente
