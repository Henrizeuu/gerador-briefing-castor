import os
import urllib.parse
import requests
from apify_client import ApifyClient

def rodar_extracao(url_insta_tratada, url_maps_tratada):
    """
    Executa a extração de dados do Instagram e Google Maps via Apify.
    Cria as pastas estruturadas e faz o download de bio, reviews e imagens.
    """
    CHAVE_API_APIFY = os.environ.get("APIFY_TOKEN")
    if not CHAVE_API_APIFY:
        return "Erro: Token da Apify (APIFY_TOKEN) não configurado."
        
    client = ApifyClient(CHAVE_API_APIFY)
    
    # 1. Estruturação de Pastas
    # Extrai o username limpo da URL do Instagram para nomear a pasta do cliente
    username_insta = url_insta_tratada.strip('/').split('/')[-1]
    pasta_base_cliente = f"cliente_{username_insta}"
    
    pasta_instagram = f"{pasta_base_cliente}/instagram_downloads_apify"
    pasta_google = f"{pasta_base_cliente}/google_reviews_extraidas"
    
    os.makedirs(pasta_instagram, exist_ok=True)
    os.makedirs(pasta_google, exist_ok=True)

    # ==========================================
    # 2. SCRAPER DO INSTAGRAM (Bio e Posts)
    # Ator: apify/instagram-scraper (shu8hvrXbJbY3Eb9W)
    # ==========================================
    try:
        # --- ETAPA A: Resgatar Detalhes do Perfil (Bio) ---
        run_input_bio = {
            "resultsType": "details",
            "directUrls": [url_insta_tratada]
        }
        
        run_bio = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input_bio)
        
        for item in client.dataset(run_bio["defaultDatasetId"]).iterate_items():
            # Salvar Bio e informações textuais
            caminho_bio = os.path.join(pasta_instagram, "bio_perfil.txt")
            with open(caminho_bio, 'w', encoding='utf-8') as f:
                f.write(f"Nome Completo: {item.get('fullName', '')}\n")
                f.write(f"Username: {item.get('username', '')}\n")
                f.write(f"Bio: {item.get('biography', '')}\n")
                f.write(f"Seguidores: {item.get('followersCount', '')}\n")
                f.write(f"Link na Bio: {item.get('externalUrl', '')}\n")

            # Baixar Foto de Perfil
            foto_perfil_url = item.get("profilePicUrlHD") or item.get("profilePicUrl")
            if foto_perfil_url:
                try:
                    r = requests.get(foto_perfil_url, timeout=10)
                    with open(os.path.join(pasta_instagram, "foto_perfil.jpg"), 'wb') as f:
                        f.write(r.content)
                except Exception as e:
                    print(f"Aviso: Não foi possível baixar a foto de perfil: {e}")
            
            # Encerra no primeiro resultado (o perfil alvo)
            break

        # --- ETAPA B: Resgatar os Posts para a Galeria ---
        run_input_posts = {
            "resultsType": "posts",
            "directUrls": [url_insta_tratada],
            "resultsLimit": 20
        }
        
        run_posts = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input_posts)
        
        contador_fotos = 1
        for post in client.dataset(run_posts["defaultDatasetId"]).iterate_items():
            if contador_fotos > 20: # Trava de segurança extra
                break
            
            # O novo scraper pode colocar a imagem principal em diferentes chaves dependendo do tipo de post
            img_url = post.get("displayUrl")
            if not img_url and post.get("images"):
                img_url = post["images"][0]
            if not img_url and post.get("carouselImages"):
                img_url = post["carouselImages"][0]
                
            if img_url:
                try:
                    r = requests.get(img_url, timeout=10)
                    with open(os.path.join(pasta_instagram, f"foto{contador_fotos}.jpg"), 'wb') as f:
                        f.write(r.content)
                    contador_fotos += 1
                except Exception:
                    continue
                    
    except Exception as e:
        return f"Erro na extração do Instagram: {str(e)}"

    # ==========================================
    # 3. SCRAPER DO GOOGLE MAPS (Reviews e Contatos)
    # Ator: vortex_data/google-maps
    # ==========================================
    if url_maps_tratada:
        try:
            if url_maps_tratada.startswith("http"):
                run_input_maps = {
                    "startUrls": [{"url": url_maps_tratada}],
                    "maxReviewsPerPlace": 20 
                }
            else:
                termo_codificado = urllib.parse.quote(url_maps_tratada)
                url_busca_maps = f"https://www.google.com/maps/search/?api=1&query={termo_codificado}"
                run_input_maps = {
                    "startUrls": [{"url": url_busca_maps}],
                    "maxReviewsPerPlace": 20
                }

            run_maps = client.actor("AabCualFIriz3X6Fs").call(run_input=run_input_maps)
            
            for item in client.dataset(run_maps["defaultDatasetId"]).iterate_items():
                caminho_maps = os.path.join(pasta_google, "dados_e_reviews.txt")
                with open(caminho_maps, 'w', encoding='utf-8') as f:
                    f.write(f"Título: {item.get('title', '')}\n")
                    f.write(f"Categoria: {item.get('categoryName', '')}\n")
                    f.write(f"Endereço: {item.get('address', '')}\n")
                    f.write(f"Telefone: {item.get('phone', '')}\n")
                    f.write(f"Website: {item.get('website', '')}\n")
                    f.write(f"Nota Total (Score): {item.get('totalScore', '')}\n")
                    f.write(f"Total de Avaliações: {item.get('reviewsCount', '')}\n")
                    
                    reviews = item.get("reviews", [])
                    f.write("\n=== AVALIAÇÕES (PROVA SOCIAL) ===\n")
                    for rev in reviews:
                        texto_review = rev.get('text', '')
                        if texto_review: 
                            f.write(f"\"{texto_review}\" - {rev.get('author', '')}\n")
                break
                
        except Exception as e:
            return f"Erro na extração do Google Maps: {str(e)}"

    return pasta_base_cliente
