# ============================================================================
# FLASK API SERVER - NOVO FRONTEND HTML/CSS/JS
# ============================================================================
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import urllib.parse

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def serve_index():
    return send_file('index.html')

@app.route('/api/scraper', methods=['POST'])
def api_scraper():
    import scraper_dados
    try:
        data = request.json
        instagram_url = data.get('instagram_url', '')
        maps_url = data.get('maps_url', '')
        
        pasta_cliente = scraper_dados.rodar_extracao(instagram_url, maps_url)
        
        if not pasta_cliente or "Erro" in str(pasta_cliente):
            return jsonify({
                'error': pasta_cliente if pasta_cliente else 'Erro desconhecido na extração.'
            }), 400
        
        return jsonify({
            'pasta_cliente': pasta_cliente,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analise', methods=['POST'])
def api_analise():
    import analise_gemini
    try:
        data = request.json
        pasta_cliente = data.get('pasta_cliente')
        iframe_pronto = data.get('iframe_pronto', '')
        
        relatorio = analise_gemini.gerar_briefing(pasta_cliente, iframe_pronto)
        
        return jsonify({
            'relatorio': relatorio,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deploy', methods=['POST'])
def api_deploy():
    import gerador_site
    import github_deploy
    try:
        data = request.json
        relatorio = data.get('relatorio')
        pasta_cliente = data.get('pasta_cliente')
        instagram_url = data.get('instagram_url')
        dominio = data.get('dominio')
        
        html_gerado, caminhos_fotos = gerador_site.criar_html_institucional(relatorio, pasta_cliente)
        
        if not html_gerado:
            return jsonify({
                'sucesso': False,
                'erro': caminhos_fotos
            }), 400
        
        nome_repo = urllib.parse.urlparse(instagram_url).path.strip('/').replace('/', '-')
        if not nome_repo:
            nome_repo = "novo-cliente"
        
        resultado_git = github_deploy.subir_para_github(
            html_gerado,
            caminhos_fotos,
            f"cliente-{nome_repo}",
            dominio
        )
        
        if "Sucesso" in resultado_git:
            return jsonify({
                'sucesso': True,
                'url': f"http://{dominio}",
                'repo': f"cliente-{nome_repo}"
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': resultado_git
            }), 400
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Servidor rodando em http://localhost:8080")
    print("📄 Acesse o novo frontend clean e profissional!")
    app.run(host='0.0.0.0', port=8080, debug=False)
