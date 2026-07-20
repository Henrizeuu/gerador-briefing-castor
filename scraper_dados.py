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
    # Ator: coderx/instagram-profile-scraper-bio-posts
    # ==========================================
    try:
        # O ator exige um array de usernames[cite: 5, 6]
        run_input_insta = {
            "usernames": [username_insta]
        }
        
        # Chama o ator PP60E1JIfagMaQxIP[cite: 6]
        run_insta = client.actor("PP60E1JIfagMaQxIP").call(run_input=run_input_insta)
        
        for item in client.dataset(run_insta["defaultDatasetId"]).iterate_items():
            # Salvar Bio e informações textuais
            caminho_bio = os.path.join(pasta_instagram, "bio_perfil.txt")
            with open(caminho_bio, 'w', encoding='utf-8') as f:
                f.write(f"Nome Completo: {item.get('fullName', '')}\n")
                f.write(f"Username: {item.get('username', '')}\n")
                f.write(f"Bio: {item.get('biography', '')}\n")
                f.write(f"Seguidores: {item.get('followersCount', '')}\n")
                f.write(f"Link na Bio: {item.get('external_url', '')}\n")

            # Baixar Foto de Perfil (Alta Resolução se disponível)
            foto_perfil_url = item.get("hdProfilePicUrl") or item.get("profilePicUrl")
            if foto_perfil_url:
                try:
                    r = requests.get(foto_perfil_url, timeout=10)
                    with open(os.path.join(pasta_instagram, "foto_perfil.jpg"), 'wb') as f:
                        f.write(r.content)
                except Exception as e:
                    print(f"Aviso: Não foi possível baixar a foto de perfil: {e}")

            # Baixar as últimas imagens do feed[cite: 5]
            posts = item.get("latestPosts", [])
            contador_fotos = 1
            for post in posts:
                if contador_fotos > 20: # Limita para não sobrecarregar o Gemini com contexto inútil
                    break
                    
                img_url = post.get("displayUrl")
                if img_url:
                    try:
                        r = requests.get(img_url, timeout=10)
                        # Salva as fotos nomeadas em ordem
                        with open(os.path.join(pasta_instagram, f"foto{contador_fotos}.jpg"), 'wb') as f:
                            f.write(r.content)
                        contador_fotos += 1
                    except Exception as e:
                        continue
                        
    except Exception as e:
        return f"Erro na extração do Instagram: {str(e)}"

    # ==========================================
    # 3. SCRAPER DO GOOGLE MAPS (Reviews e Contatos)
    # Ator: vortex_data/google-maps
    # ==========================================
    if url_maps_tratada:
        try:
            # Prepara a entrada. O Ator aceita URLs diretas através do parâmetro startUrls[cite: 7]
            if url_maps_tratada.startswith("http"):
                run_input_maps = {
                    "startUrls": [{"url": url_maps_tratada}],
                    "maxReviewsPerPlace": 20 # Limite de reviews para análise[cite: 7]
                }
            else:
                # Se o usuário digitou "Empresa, Cidade", criamos uma URL de busca exata para injetar no startUrls[cite: 7]
                termo_codificado = urllib.parse.quote(url_maps_tratada)
                url_busca_maps = f"https://www.google.com/maps/search/?api=1&query={termo_codificado}"
                run_input_maps = {
                    "startUrls": [{"url": url_busca_maps}],
                    "maxReviewsPerPlace": 20
                }

            # Chama o ator AabCualFIriz3X6Fs[cite: 7]
            run_maps = client.actor("AabCualFIriz3X6Fs").call(run_input=run_input_maps)
            
            for item in client.dataset(run_maps["defaultDatasetId"]).iterate_items():
                caminho_maps = os.path.join(pasta_google, "dados_e_reviews.txt")
                with open(caminho_maps, 'w', encoding='utf-8') as f:
                    # Extrai identidade do local e contatos[cite: 7]
                    f.write(f"Título: {item.get('title', '')}\n")
                    f.write(f"Categoria: {item.get('categoryName', '')}\n")
                    f.write(f"Endereço: {item.get('address', '')}\n")
                    f.write(f"Telefone: {item.get('phone', '')}\n")
                    f.write(f"Website: {item.get('website', '')}\n")
                    f.write(f"Nota Total (Score): {item.get('totalScore', '')}\n")
                    f.write(f"Total de Avaliações: {item.get('reviewsCount', '')}\n")
                    
                    # Extrai os textos de reviews[cite: 7]
                    reviews = item.get("reviews", [])
                    f.write("\n=== AVALIAÇÕES (PROVA SOCIAL) ===\n")
                    for rev in reviews:
                        texto_review = rev.get('text', '')
                        if texto_review: # Filtra avaliações vazias (apenas estrelas)
                            f.write(f"\"{texto_review}\" - {rev.get('author', '')}\n")
                
                # Encerra no primeiro resultado válido encontrado
                break
                
        except Exception as e:
            return f"Erro na extração do Google Maps: {str(e)}"

    return pasta_base_cliente
