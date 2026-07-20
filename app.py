import os
import json
import time
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuração da API do Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Configuração da API da Apify
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
APIFY_BASE_URL = "https://api.apify.com/v2"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/scraper', methods=['POST'])
def scraper():
    try:
        data = request.json
        search_term = data.get('searchTerm', '')
        location = data.get('location', '')
        
        if not search_term or not location:
            return jsonify({'error': 'Termo de busca e localização são obrigatórios'}), 400

        # Input para o Google Maps Scraper da Apify
        run_input = {
            "startUrls": [],
            "searchStringsArray": [search_term],
            "locationQuery": location,
            "language": "pt-BR",
            "maxReviews": 50,
            "reviewsSort": "mostRelevant",
            "scrapeReviewsPersonalData": True,
            "includeReviewsText": True,
            "includeOwnerResponse": True,
            "scrapePlaceDetailPage": True,
            "scrapeContacts": True,
            "maxImages": 0,
            "scrapeSocialMediaProfiles": {
                "facebooks": False,
                "instagrams": False,
                "youtubes": False,
                "tiktoks": False,
                "twitters": False
            },
            "searchMatching": "all",
            "placeMinimumStars": "",
            "website": "allPlaces",
            "skipClosedPlaces": False,
            "scrapeTableReservationProvider": False,
            "scrapeOrderOnline": False,
            "includeWebResults": False,
            "scrapeDirectories": False,
            "maxQuestions": 0,
            "maximumLeadsEnrichmentRecords": 0,
            "verifyLeadsEnrichmentEmails": False,
            "reviewsFilterString": "",
            "reviewsOrigin": "all",
            "scrapeImageAuthors": False,
            "enableCompetitorAnalysis": False,
            "maxCompetitorsToAnalyze": 30,
            "allPlacesNoSearchAction": ""
        }

        # Iniciar a execução na Apify
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {APIFY_API_TOKEN}"
        }
        
        # Usar o actor de Google Maps Scraper
        actor_id = "apify/google-maps-scraper"
        response = requests.post(
            f"{APIFY_BASE_URL}/acts/{actor_id}/runs",
            headers=headers,
            json=run_input
        )
        
        if response.status_code != 201:
            return jsonify({'error': f'Erro ao iniciar scraper: {response.text}'}), 500
        
        run_data = response.json()
        run_id = run_data['data']['id']
        
        # Aguardar a conclusão da execução
        while True:
            time.sleep(5)
            run_status = requests.get(
                f"{APIFY_BASE_URL}/actor-runs/{run_id}",
                headers=headers
            )
            run_status_data = run_status.json()['data']
            
            if run_status_data['status'] == 'SUCCEEDED':
                break
            elif run_status_data['status'] in ['FAILED', 'ABORTED']:
                error_msg = run_status_data.get('errorMessage', 'Execução falhou')
                return jsonify({'error': error_msg}), 500
        
        # Buscar os resultados
        dataset_id = run_status_data['defaultDatasetId']
        items_response = requests.get(
            f"{APIFY_BASE_URL}/datasets/{dataset_id}/items",
            headers=headers
        )
        
        if items_response.status_code != 200:
            return jsonify({'error': 'Erro ao buscar resultados'}), 500
        
        results = items_response.json()
        
        # Processar os dados para extrair reviews
        processed_data = []
        for place in results:
            place_info = {
                'title': place.get('title', ''),
                'address': place.get('address', ''),
                'rating': place.get('googleRating', 0),
                'total_reviews': place.get('totalReviews', 0),
                'phone': place.get('phone', ''),
                'website': place.get('website', ''),
                'reviews': []
            }
            
            # Extrair reviews de várias fontes possíveis
            reviews_list = (
                place.get('reviews') or 
                place.get('reviewsData') or 
                place.get('googleReviews') or 
                place.get('reviewList') or 
                place.get('placeReviews') or 
                place.get('reviewsItems') or 
                []
            )
            
            # Se não encontrou nas chaves padrão, procurar em todo o objeto
            if not reviews_list:
                for key, value in place.items():
                    if isinstance(value, list) and len(value) > 0:
                        if any(isinstance(item, dict) and ('text' in item or 'reviewText' in item or 'snippet' in item) for item in value):
                            reviews_list = value
                            break
            
            for review in reviews_list[:50]:  # Limitar a 50 reviews
                review_info = {
                    'author': review.get('authorName') or review.get('author') or review.get('reviewerName') or '',
                    'rating': review.get('rating') or review.get('stars') or 0,
                    'text': review.get('text') or review.get('reviewText') or review.get('snippet') or review.get('reviewBody') or '',
                    'time': review.get('time') or review.get('timestamp') or review.get('publishedAt') or '',
                    'owner_response': review.get('ownerAnswer') or review.get('ownerResponse') or review.get('response') or ''
                }
                place_info['reviews'].append(review_info)
            
            processed_data.append(place_info)
        
        return jsonify({'success': True, 'data': processed_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analise', methods=['POST'])
def analise():
    try:
        if not GEMINI_API_KEY:
            return jsonify({'error': 'Chave da API Gemini não configurada'}), 500
        
        data = request.json
        scraped_data = data.get('data', [])
        
        if not scraped_data:
            return jsonify({'error': 'Nenhum dado para analisar'}), 400
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Com base nos seguintes dados de avaliações de clientes do Google Maps, gere um briefing profissional e detalhado em português do Brasil.
        Inclua:
        1. Resumo geral da reputação da empresa
        2. Pontos fortes mais mencionados
        3. Pontos fracos e oportunidades de melhoria
        4. Análise de sentimentos predominantes
        5. Sugestões de ações estratégicas
        6. Principais palavras-chave mencionadas
        
        Dados das avaliações:
        {json.dumps(scraped_data, ensure_ascii=False, indent=2)}
        
        Formate a resposta em Markdown com títulos, subtítulos e listas para facilitar a leitura.
        """
        
        response = model.generate_content(prompt)
        
        return jsonify({'success': True, 'briefing': response.text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
