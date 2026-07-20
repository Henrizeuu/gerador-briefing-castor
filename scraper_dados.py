import os
import json
import requests
from apify_client import ApifyClient

def baixar_imagem(url, caminho_salvar):
    """Função auxiliar para baixar imagens de forma segura."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            with open(caminho_salvar, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"⚠️ Erro ao baixar imagem {url}: {e}")
    return False

def rodar_extracao(url_insta, url_maps):
    """
    Função principal que orquestra o scraping via Apify e salva os dados.
    """
    print(f"\n--- INÍCIO DA EXECUÇÃO DO SCRAPER ---")
    print(f"Instagram recebido: {url_insta}")
    print(f"Maps recebido: {url_maps}")
    print(f"--- FIM DO INPUT ---\n")

    # Validação básica de token
    APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
    if not APIFY_TOKEN:
        print("❌ Erro crítico: Variável de ambiente APIFY_API_TOKEN não está definida.")
        return "Erro: Token da Apify não configurado."

    client = ApifyClient(APIFY_TOKEN)
    print("✅ Cliente da Apify inicializado com sucesso.")

    # 1. Preparar Estrutura de Pastas
    username = url_insta.split('/')[-2] if '/' in url_insta else url_insta.replace('@', '')
    pasta_base = f"./dados_clientes/{username}"
    pasta_insta = f"{pasta_base}/instagram_downloads_apify"
    pasta_maps = f"{pasta_base}/google_reviews_extraidas"

    os.makedirs(pasta_insta, exist_ok=True)
    os.makedirs(pasta_maps, exist_ok=True)
    print(f"✅ Estrutura de pastas criada: {pasta_base}")

    # ==========================================
    # 2. EXTRAÇÃO DO INSTAGRAM
    # ==========================================
    print("\n--- INICIANDO EXTRAÇÃO DO INSTAGRAM ---")
    texto_completo_insta = "=== DADOS ESTRUTURAIS DO PERFIL ===\n"

    # RUN A: Detalhes do Perfil
    try:
        print("  - Preparando input para detalhes do Instagram...")
        run_input_details = {
            "resultsType": "details",
            "directUrls": [url_insta]
        }
        print("  - Executando Actor de detalhes do Instagram...")
        run_details = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input_details)
        print(f"  - Run de detalhes concluída. Dataset ID: {run_details.default_dataset_id}")

        print("  - Iterando sobre os resultados de detalhes...")
        for item in client.dataset(run_details.default_dataset_id).iterate_items():
            print("  - Processando item de detalhes...")
            texto_completo_insta += f"Nome: {item.get('fullName', 'N/A')}\n"
            texto_completo_insta += f"Username: {item.get('username', 'N/A')}\n"
            texto_completo_insta += f"Bio: {item.get('biography', 'N/A')}\n"
            texto_completo_insta += f"Seguidores: {item.get('followersCount', 0)}\n"
            texto_completo_insta += f"Seguindo: {item.get('followsCount', 0)}\n"
            texto_completo_insta += f"Total de Posts: {item.get('postsCount', 0)}\n"
            texto_completo_insta += f"Link na Bio: {item.get('externalUrl', 'N/A')}\n\n"

            pic_url = item.get('profilePicUrlHD') or item.get('profilePicUrl')
            if pic_url:
                print(f"  - Tentando baixar foto de perfil: {pic_url}")
                baixar_imagem(pic_url, f"{pasta_insta}/foto_perfil.jpg")
            break # Pega só o primeiro item (perfil)
        print("  - Concluído: Extração de detalhes do Instagram.")
    except Exception as e:
        print(f"❌ Erro ao buscar detalhes do Insta: {e}")
        import traceback
        traceback.print_exc()

    # RUN B: Posts e Imagens
    try:
        print("  - Preparando input para posts do Instagram...")
        run_input_posts = {
            "resultsType": "posts",
            "directUrls": [url_insta],
            "resultsLimit": 21
        }
        print("  - Executando Actor de posts do Instagram...")
        run_posts = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input_posts)
        print(f"  - Run de posts concluída. Dataset ID: {run_posts.default_dataset_id}")

        texto_completo_insta += "=== LEGENDAS DOS POSTS RECENTES ===\n"
        img_count = 0
        print("  - Iterando sobre os resultados de posts...")
        for item in client.dataset(run_posts.default_dataset_id).iterate_items():
            print(f"  - Processando post {img_count+1}...")
            if img_count >= 21: break

            caption = item.get('caption', 'Sem legenda').replace('\n', ' ')
            texto_completo_insta += f"- Post {img_count+1}: {caption[:300]}...\n"

            img_urls = []
            if item.get('type') == 'Sidecar' and item.get('carouselImages'):
                img_urls = item['carouselImages']
            elif item.get('images'):
                img_urls = item['images']

            for img_url in img_urls:
                if img_count >= 21: break
                clean_url = img_url.split('?')[0]
                ext = os.path.splitext(clean_url)[1] or '.jpg'
                filename = f"post_{img_count+1}{ext}"

                print(f"  - Tentando baixar imagem do post: {filename}")
                if baixar_imagem(img_url, f"{pasta_insta}/{filename}"):
                    img_count += 1

        print(f"  - Concluído: Extração de posts e imagens. {img_count} imagens baixadas.")
    except Exception as e:
        print(f"❌ Erro ao buscar posts do Insta: {e}")
        import traceback
        traceback.print_exc()

    # Salva o txt do Instagram
    caminho_txt_insta = f"{pasta_insta}/01_dados_insta.txt"
    with open(caminho_txt_insta, 'w', encoding='utf-8') as f:
        f.write(texto_completo_insta)
    print(f"✅ Dados do Instagram salvos em: {caminho_txt_insta}")

    # ==========================================
    # 3. EXTRAÇÃO DO GOOGLE MAPS (Com Diagnóstico Profundo)
    # ==========================================
    print("\n--- INICIANDO EXTRAÇÃO DO GOOGLE MAPS ---")
    print(f"  - Valor bruto de url_maps: '{url_maps}'")
    texto_completo_maps = ""

    # VALIDAÇÃO CRÍTICA: Verifica se a URL do Maps é válida
    if not url_maps or url_maps.strip() == "":
        print("  - ⚠️ URL do Maps vazia ou nula. Pulando extração.")
        texto_completo_maps = "Nenhuma informação do Google Maps fornecida."
    elif not url_maps.startswith(('http://', 'https://')):
        print(f"  - ⚠️ URL do Maps inválida (não começa com http/https): '{url_maps}'. Pulando extração.")
        texto_completo_maps = "URL do Google Maps inválida. Deve começar com 'http://' ou 'https://'."
    else:
        print(f"  - ✅ URL do Maps parece válida: '{url_maps}'. Preparando input para o Actor.")
        run_input_maps = {
            "startUrls": [{"url": url_maps}],
            "language": "pt-BR",
            "maxReviews": 50,
            "reviewsSort": "highestRanking",
            "scrapeReviewsPersonalData": True,
            "scrapeContacts": True,
            "maxImages": 0,
            "scrapeSocialMediaProfiles": {
                "facebooks": False,
                "instagrams": False,
                "youtubes": False,
                "tiktoks": False,
                "twitters": False
            },
        }

        print("  - Executando Actor do Google Maps (compass/crawler-google-places)...")
        try:
            # REMOVIDO: wait_secs e timeout_secs
            run_maps = client.actor("compass/crawler-google-places").call(
                run_input=run_input_maps
            )
            print(f"  - ✅ Run do Maps finalizada com sucesso. Dataset ID: {run_maps.default_dataset_id}")

            print("  - Iterando sobre os resultados do Maps...")
            dados = list(client.dataset(run_maps.default_dataset_id).iterate_items())
            print(f"  - Dados brutos recebidos do dataset: {len(dados)} itens.")

            if not dados:
                print("  - ⚠️ Nenhum item de dados (empresa) retornado pelo Actor do Maps.")
                texto_completo_maps = "Nenhum dado foi extraído do Google Maps. A página pode estar protegida ou o termo de busca pode não retornar resultados."
            else:
                print("  - Processando primeiro item (empresa)...")
                empresa = dados[0] # Assume que o primeiro item é a empresa alvo

                texto_completo_maps += "=== DADOS DO NEGÓCIO (MAPS) ===\n"
                texto_completo_maps += f"Nome: {empresa.get('title', 'N/A')}\n"
                texto_completo_maps += f"Categoria: {empresa.get('categoryName', 'N/A')}\n"
                texto_completo_maps += f"Endereço: {empresa.get('address', 'N/A')}\n"
                texto_completo_maps += f"Telefone: {empresa.get('phone', 'N/A')}\n"
                texto_completo_maps += f"Website: {empresa.get('website', 'N/A')}\n"
                texto_completo_maps += f"Avaliação Geral: {empresa.get('totalScore', 0)} estrelas ({empresa.get('reviewsCount', 0)} avaliações)\n\n"

                texto_completo_maps += "=== AVALIAÇÕES DE CLIENTES (PROVA SOCIAL) ===\n"
                reviews = empresa.get('reviews', [])
                if not reviews:
                    print("  - ⚠️ Nenhuma avaliação textual encontrada no item retornado.")
                    texto_completo_maps += "Nenhuma avaliação textual encontrada no Maps.\n"
                else:
                    print(f"  - Encontradas {len(reviews)} avaliações no item retornado.")
                    for rev in reviews[:20]: # Limita a 20 reviews
                        autor = rev.get('author', 'Anônimo')
                        texto_rev = rev.get('text', 'Sem texto')
                        data_rev = rev.get('publishedAt', '')
                        texto_completo_maps += f"- [{autor}] ({data_rev}): {texto_rev}\n"

        except Exception as e:
            print(f"  - ❌ Erro CRÍTICO ao executar o Actor do Maps: {e}")
            import traceback
            traceback.print_exc()
            texto_completo_maps = f"Erro ao extrair dados do Google Maps: {str(e)}"


    # Salva o txt do Maps
    caminho_txt_maps = f"{pasta_maps}/01_dados_maps.txt"
    with open(caminho_txt_maps, 'w', encoding='utf-8') as f:
        f.write(texto_completo_maps)
    print(f"✅ Dados do Google Maps salvos em: {caminho_txt_maps}")
    print("\n--- FIM DA EXECUÇÃO DO SCRAPER ---")

    return pasta_base
