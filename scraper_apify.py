import os
import urllib.request
from apify_client import ApifyClient

def rodar_extracao(url_instagram, url_maps):
    print(f"=== INICIANDO EXTRAÇÃO DE DADOS ===")
    
    API_TOKEN = os.environ.get("APIFY_TOKEN")
    if not API_TOKEN:
        return None, "Erro: Token do Apify não configurado no servidor."
        
    client = ApifyClient(API_TOKEN)
    LIMITE_DE_POSTS = 80
    LIMITE_DE_AVALIACOES = 8

    # Cria a pasta base dinamicamente com base na URL que o cliente digitou
    nome_do_cliente = url_instagram.strip('/').split('/')[-1]
    pasta_base_cliente = f"cliente_{nome_do_cliente}"
    pasta_destino_insta = os.path.join(pasta_base_cliente, "instagram_downloads_apify")
    os.makedirs(pasta_destino_insta, exist_ok=True)

    # --- PARTE 1: INSTAGRAM ---
    print("\n[1/3] A extrair informações detalhadas e foto do perfil...")
    run_input_perfil = {"resultsType": "details", "directUrls": [url_instagram]}
    run_perfil = client.actor("apify/instagram-scraper").call(run_input=run_input_perfil)
    dados_perfil = list(client.dataset(run_perfil.default_dataset_id).iterate_items())

    if dados_perfil:
        info = dados_perfil[0]
        caminho_txt = os.path.join(pasta_destino_insta, f"info_{info.get('username', 'perfil')}.txt")
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(f"=== DADOS DO PERFIL ===\n")
            f.write(f"Nome: {info.get('fullName', 'N/A')}\n")
            f.write(f"Username: @{info.get('username', 'N/A')}\n")
            f.write(f"Bio: {info.get('biography', 'N/A')}\n")
            f.write(f"Seguidores: {info.get('followersCount', 'N/A')}\n")
        
        url_foto_perfil = info.get('profilePicUrlHD') or info.get('profilePicUrl')
        if url_foto_perfil:
            try:
                req = urllib.request.Request(url_foto_perfil, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(os.path.join(pasta_destino_insta, "foto_perfil.jpg"), 'wb') as out_file:
                    out_file.write(response.read())
            except Exception:
                pass

    print(f"\n[2/3] A raspar os últimos {LIMITE_DE_POSTS} posts...")
    run_input_posts = {"resultsType": "posts", "directUrls": [url_instagram], "resultsLimit": LIMITE_DE_POSTS}
    run_posts = client.actor("apify/instagram-scraper").call(run_input=run_input_posts)
    dados_posts = list(client.dataset(run_posts.default_dataset_id).iterate_items())

    print("\n[3/3] A iniciar o download das imagens e descrições...")
    total_baixado = 0
    LIMITE_IMAGENS = 21

    for post_index, post in enumerate(dados_posts):
        if total_baixado >= LIMITE_IMAGENS: break
        shortcode = post.get('shortCode', f'post_{post_index}')
        legenda = post.get('caption', 'Sem descrição.')
        links_para_baixar = []

        if 'childPosts' in post and post['childPosts']:
             for child in post['childPosts']:
                 if 'videoUrl' not in child or not child['videoUrl']:
                     if 'displayUrl' in child and child['displayUrl']:
                         links_para_baixar.append((child['displayUrl'], '.jpg'))
        elif 'videoUrl' not in post or not post['videoUrl']:
             if 'displayUrl' in post:
                 links_para_baixar.append((post['displayUrl'], '.jpg'))

        if not links_para_baixar: continue

        pasta_do_post = os.path.join(pasta_destino_insta, shortcode)
        os.makedirs(pasta_do_post, exist_ok=True)
        with open(os.path.join(pasta_do_post, "descricao.txt"), 'w', encoding='utf-8') as f_legenda:
            f_legenda.write(legenda)

        for index_midia, (url_midia, extensao) in enumerate(links_para_baixar):
             if total_baixado >= LIMITE_IMAGENS: break
             try:
                 req = urllib.request.Request(url_midia, headers={'User-Agent': 'Mozilla/5.0'})
                 with urllib.request.urlopen(req) as response, open(os.path.join(pasta_do_post, f"midia_{index_midia + 1}{extensao}"), 'wb') as out_file:
                     out_file.write(response.read())
                 total_baixado += 1
             except Exception:
                 pass

    # --- PARTE 2: GOOGLE MAPS ---
    if url_maps and url_maps.startswith("http"):
        print("\n📍 Iniciando a raspagem do Google Maps...")
        run_input_maps = {"startUrls": [{"url": url_maps}], "language": "pt-BR", "maxReviews": LIMITE_DE_AVALIACOES, "scrapeContacts": True}
        run_maps = client.actor("compass/crawler-google-places").call(run_input=run_input_maps)
        dados_maps = list(client.dataset(run_maps.default_dataset_id).iterate_items())

        if dados_maps:
            empresa = dados_maps[0]
            titulo = empresa.get('title', 'Empresa')
            lat, lng = empresa.get('location', {}).get('lat', ''), empresa.get('location', {}).get('lng', '')
            codigo_iframe = f'<iframe width="100%" height="400" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://maps.google.com/maps?q={lat},{lng}&hl=pt-BR&z=15&output=embed"></iframe>' if lat and lng else "Coordenadas não encontradas."
            
            pasta_destino_maps = os.path.join(pasta_base_cliente, "google_reviews_extraidas")
            os.makedirs(pasta_destino_maps, exist_ok=True)
            caminho_arquivo_maps = os.path.join(pasta_destino_maps, f"avaliacoes_e_contatos.txt")
            
            with open(caminho_arquivo_maps, 'w', encoding='utf-8') as f:
                f.write(f"Empresa: {titulo}\nEndereço: {empresa.get('address', '')}\nTelefone: {empresa.get('phone', '')}\n=== IFRAME ===\n{codigo_iframe}\n\n=== AVALIAÇÕES ===\n")
                for rev in empresa.get('reviews', []):
                    texto = rev.get('text', '')
                    if texto: f.write(f"Cliente: {rev.get('name', 'Anônimo')} ({rev.get('stars', 0)} Estrelas)\nDepoimento: {texto}\n---\n")

    # Retorna APENAS o nome da pasta mestre para o Gemini achar tudo depois
    return pasta_base_cliente