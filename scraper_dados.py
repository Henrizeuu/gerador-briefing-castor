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
    # 1. EXTRAÇÃO DO INSTAGRAM (ALL-IN-ONE CHEAP: $0.99)
    # ---------------------------------------------------------
    try:
        print(f"🦫 Iniciando extração completa (Perfil + Posts) para: @{nome_cliente}")
        
        run_input_insta = {
            "profiles": [nome_cliente],
            "scrape_profile_data": True,
            "scrape_posts": True,  # LIGA A EXTRAÇÃO DOS POSTS NA MESMA REQUISIÇÃO
            "scrape_reels": False,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["BUYPROXIES94952"] # Rota Datacenter EUA liberada
            }
        }
        
        run_insta = client.actor("hpix/instagram-scraper").call(run_input=run_input_insta)
        
        nome_completo, bio, seguidores, categoria, foto_perfil_url = "", "", 0, "N/A", ""
        posts_baixados = 0
        
        for item in client.dataset(run_insta.default_dataset_id).iterate_items():
            kind = item.get("kind", "")
            dados = item.get("data", {}) if "data" in item else item
            
            # --- SE FOR OS DADOS DO PERFIL ---
            if kind == "profile" or "biography" in dados or "bio" in dados:
                nome_completo = dados.get("full_name", "") or dados.get("fullName", "")
                bio = dados.get("biography", "") or dados.get("bio", "")
                seguidores = dados.get("followers", 0) or dados.get("followersCount", 0) or dados.get("follower_count", 0)
                foto_perfil_url = dados.get("profile_pic_url", "") or dados.get("profilePicUrl", "")
                categoria = dados.get("business_category_name", "N/A") or dados.get("category_name", "N/A") or dados.get("categoryName", "N/A")
            
            # --- SE FOR UM POST DA TIMELINE ---
            elif kind == "post" or "code" in dados or "shortcode" in dados:
                if posts_baixados >= 12:
                    continue # Trava em 12 posts para manter a máquina leve
                
                shortcode = dados.get("code") or dados.get("shortCode") or dados.get("shortcode")
                if not shortcode: continue
                
                pasta_post = os.path.join(pasta_insta, shortcode)
                os.makedirs(pasta_post, exist_ok=True)
                
                legenda = dados.get("caption", "")
                if isinstance(legenda, dict):
                    legenda = legenda.get("text", "")
                
                if legenda:
                    with open(os.path.join(pasta_post, "descricao.txt"), "w", encoding="utf-8") as f:
                        f.write(legenda)
                
                # Procura a imagem na resposta do Actor
                img_url = dados.get("display_url") or dados.get("displayUrl") or dados.get("thumbnail_url") or dados.get("thumbnail")
                if not img_url and dados.get("image_versions2"):
                    img_url = dados["image_versions2"].get("candidates", [{}])[0].get("url", "")
                elif not img_url and dados.get("carousel_media"):
                    img_url = dados["carousel_media"][0].get("image_versions2", {}).get("candidates", [{}])[0].get("url", "")
                
                if img_url:
                    try:
                        # Blindagem com User-Agent para o download não ser bloqueado
                        req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req) as response, open(os.path.join(pasta_post, "imagem.jpg"), 'wb') as out_file:
                            out_file.write(response.read())
                        posts_baixados += 1
                    except Exception:
                        pass
        
        # Salva o arquivo de Perfil por último
        with open(os.path.join(pasta_insta, "dados_perfil.txt"), "w", encoding="utf-8") as f:
            f.write(f"Nome: {nome_completo}\nBio: {bio}\nSeguidores: {seguidores}\nCategoria: {categoria}\n")
            
        if foto_perfil_url:
            try:
                req = urllib.request.Request(foto_perfil_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(os.path.join(pasta_insta, "foto_perfil.jpg"), 'wb') as out_file:
                    out_file.write(response.read())
            except Exception:
                pass

    except Exception as e:
        print(f"Aviso na extração do Instagram via Apify: {e}")

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

            if "query=" in url_maps:
                texto_puro = urllib.parse.unquote(url_maps.split("query=")[1].split("&")[0])
                if "," in texto_puro:
                    partes = texto_puro.split(",")
                    run_input_maps["searchStringsArray"] = [partes[0].strip()]
                    run_input_maps["locationQueries"] = [partes[1].strip() + ", Brasil"]
                else:
                    run_input_maps["searchStringsArray"] = [texto_puro]
                    run_input_maps["locationQueries"] = ["Brasil"]
            elif url_maps.startswith("http"):
                run_input_maps["startUrls"] = [{"url": url_maps}]
            else:
                if "," in url_maps:
                    partes = url_maps.split(",")
                    run_input_maps["searchStringsArray"] = [partes[0].strip()]
                    run_input_maps["locationQueries"] = [partes[1].strip() + ", Brasil"]
                else:
                    run_input_maps["searchStringsArray"] = [url_maps]
                    run_input_maps["locationQueries"] = ["Brasil"]

            run_maps = client.actor("AabCualFIriz3X6Fs").call(run_input=run_input_maps)

            texto_avaliacoes = ""
            
            for item in client.dataset(run_maps.default_dataset_id).iterate_items():
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
