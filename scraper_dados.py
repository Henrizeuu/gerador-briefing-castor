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
    # 1. EXTRAÇÃO DO INSTAGRAM (ALL-IN-ONE: PERFIL + POSTS)
    # ---------------------------------------------------------
    try:
        print(f"🦫 Iniciando extração completa do Instagram para: @{nome_cliente}")
        
        run_input_insta = {
            "usernames": [nome_cliente]
        }
        
        # A CORREÇÃO ESTÁ AQUI: passei a variável run_input_insta correta!
        run_insta = client.actor("PP60E1JIfagMaQxIP").call(run_input=run_input_insta)
        
        nome_completo, bio, seguidores, categoria, foto_perfil_url = "", "", 0, "N/A", ""
        
        for item in client.dataset(run_insta.default_dataset_id).iterate_items():
            
            # --- SALVANDO DADOS DO PERFIL ---
            nome_completo = item.get("fullName", "")
            bio = item.get("biography", "")
            seguidores = item.get("followersCount", 0)
            categoria = item.get("businessCategoryName", "N/A")
            foto_perfil_url = item.get("hdProfilePicUrl") or item.get("profilePicUrl", "")
            
            # --- SALVANDO MÍDIAS E LEGENDAS DOS POSTS ---
            latest_posts = item.get("latestPosts", [])
            for post in latest_posts:
                shortcode = post.get("shortCode")
                if not shortcode: continue
                
                pasta_post = os.path.join(pasta_insta, shortcode)
                os.makedirs(pasta_post, exist_ok=True)
                
                legenda = post.get("caption", "")
                if legenda:
                    with open(os.path.join(pasta_post, "descricao.txt"), "w", encoding="utf-8") as f:
                        f.write(legenda)
                
                img_url = post.get("displayUrl", "")
                if img_url:
                    try:
                        urllib.request.urlretrieve(img_url, os.path.join(pasta_post, "imagem.jpg"))
                    except:
                        pass
            
            break 
            
        with open(os.path.join(pasta_insta, "dados_perfil.txt"), "w", encoding="utf-8") as f:
            f.write(f"Nome: {nome_completo}\nBio: {bio}\nSeguidores: {seguidores}\nCategoria: {categoria}\n")
            
        if foto_perfil_url:
            try:
                urllib.request.urlretrieve(foto_perfil_url, os.path.join(pasta_insta, "foto_perfil.jpg"))
            except:
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

            if url_maps.startswith("http"):
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
