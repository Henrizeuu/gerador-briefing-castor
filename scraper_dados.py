import os
import json
import requests
import urllib.parse
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
    print(f"🦫 INICIANDO EXTRAÇÃO: Instagram={url_insta} | Maps={url_maps}")
    
    APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
    if not APIFY_TOKEN:
        return "Erro: Variável de ambiente APIFY_API_TOKEN não configurada."

    client = ApifyClient(APIFY_TOKEN)

    # 1. Preparar Estrutura de Pastas
    username = url_insta.split('/')[-2] if '/' in url_insta else url_insta.replace('@', '')
    pasta_base = f"./dados_clientes/{username}"
    pasta_insta = f"{pasta_base}/instagram_downloads_apify"
    pasta_maps = f"{pasta_base}/google_reviews_extraidas"
    
    os.makedirs(pasta_insta, exist_ok=True)
    os.makedirs(pasta_maps, exist_ok=True)

    # ==========================================
    # 2. EXTRAÇÃO DO INSTAGRAM
    # ==========================================
    print("📸 [1/2] Extraindo dados do Instagram...")
    texto_completo_insta = "=== DADOS ESTRUTURAIS DO PERFIL ===\n"
    
    # RUN A: Detalhes do Perfil
    try:
        run_input_details = {
            "resultsType": "details",
            "directUrls": [url_insta]
        }
        run_details = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input_details, wait_secs=120)
        
        for item in client.dataset(run_details["defaultDatasetId"]).iterate_items():
            texto_completo_insta += f"Nome: {item.get('fullName', 'N/A')}\n"
            texto_completo_insta += f"Username: {item.get('username', 'N/A')}\n"
            texto_completo_insta += f"Bio: {item.get('biography', 'N/A')}\n"
            texto_completo_insta += f"Seguidores: {item.get('followersCount', 0)}\n"
            texto_completo_insta += f"Seguindo: {item.get('followsCount', 0)}\n"
            texto_completo_insta += f"Total de Posts: {item.get('postsCount', 0)}\n"
            texto_completo_insta += f"Link na Bio: {item.get('externalUrl', 'N/A')}\n\n"
            
            pic_url = item.get('profilePicUrlHD') or item.get('profilePicUrl')
            if pic_url:
                baixar_imagem(pic_url, f"{pasta_insta}/foto_perfil.jpg")
            break
    except Exception as e:
        print(f"❌ Erro ao buscar detalhes do Insta: {e}")

    # RUN B: Posts e Imagens
    try:
        run_input_posts = {
            "resultsType": "posts",
            "directUrls": [url_insta],
            "resultsLimit": 21 
        }
        run_posts = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input_posts, wait_secs=120)
        
        texto_completo_insta += "=== LEGENDAS DOS POSTS RECENTES ===\n"
        img_count = 0
        
        for item in client.dataset(run_posts["defaultDatasetId"]).iterate_items():
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
                
                if baixar_imagem(img_url, f"{pasta_insta}/{filename}"):
                    img_count += 1
                    
    except Exception as e:
        print(f"❌ Erro ao buscar posts do Insta: {e}")

    with open(f"{pasta_insta}/01_dados_insta.txt", 'w', encoding='utf-8') as f:
        f.write(texto_completo_insta)
    print("✅ Instagram concluído!")

    # ==========================================
    # 3. EXTRAÇÃO DO GOOGLE MAPS (CORRIGIDO)
    # ==========================================
    print("🗺️ [2/2] Extraindo dados do Google Maps...")
    texto_completo_maps = ""
    
    if not url_maps or url_maps.strip() == "":
        print("⚠️ URL do Maps não fornecida, criando arquivo vazio...")
        texto_completo_maps = "Nenhuma informação do Google Maps fornecida."
    else:
        # Usando o Google Maps Scraper da VortexData (AabCualFIriz3X6Fs)
        run_input_maps = {}
        
        try:
            if url_maps.startswith("http"):
                # URL direta do Google Maps
                run_input_maps = {
                    "startUrls": [{"url": url_maps}],
                    "maxReviewsPerPlace": 50,
                    "extractContactsFromWebsite": False,
                    "maxCrawledPlacesPerSearch": 1
                }
            else:
                # Texto de busca (ex: "Bayar Advogados, Canoas")
                partes = url_maps.split(',')
                search_term = partes[0].strip()
                location = partes[1].strip() if len(partes) > 1 else "Brazil"
                
                run_input_maps = {
                    "searchStringsArray": [search_term],
                    "locationQueries": [location],
                    "maxCrawledPlacesPerSearch": 1,
                    "maxReviewsPerPlace": 50,
                    "extractContactsFromWebsite": False,
                    "skipClosedPlaces": False
                }
            
            print(f"🚀 Iniciando scraper do Maps com input: {json.dumps(run_input_maps, indent=2)}")
            
            # Executa o actor e espera (timeout maior)
            run_maps = client.actor("AabCualFIriz3X6Fs").call(
                run_input=run_input_maps, 
                wait_secs=300,  # 5 minutos de timeout
                memory_bytes=4096 * 1024 * 1024  # 4GB de memória
            )
            
            print(f"✅ Run do Maps finalizada. Dataset ID: {run_maps['defaultDatasetId']}")
            
            # Busca os resultados
            items_encontrados = 0
            for item in client.dataset(run_maps["defaultDatasetId"]).iterate_items():
                # Ignora linhas de diagnóstico
                if item.get("isDiagnostic") or item.get("recordType") == "run-diagnostic":
                    print(f"️ Ignorando item de diagnóstico: {item.get('diagnosticHints', 'N/A')}")
                    continue
                
                items_encontrados += 1
                texto_completo_maps += "=== DADOS DO NEGÓCIO (MAPS) ===\n"
                texto_completo_maps += f"Nome: {item.get('title', 'N/A')}\n"
                texto_completo_maps += f"Categoria: {item.get('categoryName', 'N/A')}\n"
                texto_completo_maps += f"Endereço: {item.get('address', 'N/A')}\n"
                texto_completo_maps += f"Telefone: {item.get('phone', 'N/A')}\n"
                texto_completo_maps += f"Website: {item.get('website', 'N/A')}\n"
                texto_completo_maps += f"Avaliação Geral: {item.get('totalScore', 0)} estrelas ({item.get('reviewsCount', 0)} avaliações)\n\n"

                texto_completo_maps += "=== AVALIAÇÕES DE CLIENTES (PROVA SOCIAL) ===\n"
                reviews = item.get('reviews', [])
                if not reviews:
                    texto_completo_maps += "Nenhuma avaliação textual encontrada no Maps.\n"
                
                for rev in reviews[:20]:  # Limita a 20 reviews para não estourar o contexto
                    autor = rev.get('author', 'Anônimo')
                    texto_rev = rev.get('text', 'Sem texto')
                    data_rev = rev.get('publishedAt', '')
                    texto_completo_maps += f"- [{autor}] ({data_rev}): {texto_rev}\n"
                
                # Como limitamos para 1 lugar, podemos dar break aqui
                break 
            
            if items_encontrados == 0:
                print("⚠️ Nenhum item válido encontrado no dataset do Maps.")
                texto_completo_maps = "Nenhum dado foi extraído do Google Maps. Verifique se o termo de busca está correto."
                
        except Exception as e:
            print(f"❌ Erro ao buscar dados do Maps: {e}")
            import traceback
            traceback.print_exc()
            texto_completo_maps = f"Erro ao extrair dados do Google Maps: {str(e)}"

    with open(f"{pasta_maps}/01_dados_maps.txt", 'w', encoding='utf-8') as f:
        f.write(texto_completo_maps)
    print("✅ Maps concluído!")

    print("🎉 EXTRAÇÃO TOTAL FINALIZADA!")
    return pasta_base
