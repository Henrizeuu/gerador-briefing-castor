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
    # 1. EXTRAÇÃO DO INSTAGRAM (USANDO O OFICIAL BLINDADO - 1 REQUISIÇÃO)
    # ---------------------------------------------------------
    try:
        print(f"🦫 Iniciando extração do Instagram (Scraper Oficial) para: {url_insta}")

        # --- FAZ APENAS 1 CHAMADA PARA ECONOMIZAR CRÉDITOS ---
        run_input_perfil = {
            "resultsType": "details",
            "directUrls": [url_insta],
        }
        
        run_perfil = client.actor("apify/instagram-scraper").call(run_input=run_input_perfil)
        
        nome_completo, bio, seguidores, categoria, foto_perfil_url = "", "", 0, "N/A", ""

        for info in client.dataset(run_perfil.default_dataset_id).iterate_items():
            
            # --- SALVA OS DADOS DO PERFIL ---
            nome_completo = info.get('fullName', 'N/A')
            bio = info.get('biography', 'N/A')
            seguidores = info.get('followersCount', 0)
            categoria = info.get('businessCategoryName', 'N/A')
            foto_perfil_url = info.get('profilePicUrlHD') or info.get('profilePicUrl')

            with open(os.path.join(pasta_insta, "dados_perfil.txt"), "w", encoding="utf-8") as f:
                f.write(f"Nome: {nome_completo}\nBio: {bio}\nSeguidores: {seguidores}\nCategoria: {categoria}\n")

            if foto_perfil_url:
                try:
                    req = urllib.request.Request(foto_perfil_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response, open(os.path.join(pasta_insta, "foto_perfil.jpg"), 'wb') as out_file:
                        out_file.write(response.read())
                except Exception as e:
                    print(f"Aviso ao baixar foto de perfil: {e}")

            # --- EXTRAI OS POSTS DA MESMA REQUISIÇÃO (latestPosts) ---
            ultimos_posts = info.get('latestPosts', [])
            
            for post in ultimos_posts:
                shortcode = post.get('shortCode')
                if not shortcode: continue

                pasta_post = os.path.join(pasta_insta, shortcode)
                os.makedirs(pasta_post, exist_ok=True)

                legenda = post.get('caption', '')
                if legenda:
                    with open(os.path.join(pasta_post, "descricao.txt"), "w", encoding="utf-8") as f:
                        f.write(legenda)

                # Lógica de filtragem de imagens do seu script original
                links_para_baixar = []
                if 'childPosts' in post and post['childPosts']:
                    for child in post['childPosts']:
                        if 'videoUrl' not in child or not child['videoUrl']:
                            if 'displayUrl' in child and child['displayUrl']:
                                links_para_baixar.append(child['displayUrl'])
                elif 'videoUrl' not in post or not post['videoUrl']:
                    if 'displayUrl' in post:
                        links_para_baixar.append(post['displayUrl'])

                if links_para_baixar:
                    try:
                        # Baixa apenas a primeira imagem do post
                        req = urllib.request.Request(links_para_baixar[0], headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req) as response, open(os.path.join(pasta_post, "imagem.jpg"), 'wb') as out_file:
                            out_file.write(response.read())
                    except Exception as e:
                        pass
            
            break # Garante que lê só a linha principal e finaliza

    except Exception as e:
        print(f"Aviso na extração do Instagram via Apify Oficial: {e}")

    # ---------------------------------------------------------
    # 2. EXTRAÇÃO DO GOOGLE MAPS (EXATAMENTE COMO VOCÊ MANDOU)
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
