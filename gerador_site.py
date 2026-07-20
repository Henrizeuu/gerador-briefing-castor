import os
import glob
import json
from google import genai
from google.genai import types

def criar_html_institucional(briefing_json_texto, pasta_base_cliente):
    """
    Recebe o JSON do briefing e a pasta do cliente, e usa o Gemini para 
    escrever o código HTML completo do site institucional.
    """
    CHAVE_API_GEMINI = os.environ.get("GEMINI_TOKEN")
    if not CHAVE_API_GEMINI:
        return None, "Erro: Token do Gemini não configurado."
        
    client = genai.Client(api_key=CHAVE_API_GEMINI)
    
    # 1. Parsear o JSON do briefing (com fallback de segurança)
    try:
        dados = json.loads(briefing_json_texto)
    except json.JSONDecodeError:
        # Se o Gemini alucinar e não devolver JSON puro, usamos dados padrão para não quebrar o site
        dados = {
            "nome_nicho": "Empresa Cliente",
            "grande_problema": "Soluções especializadas para você.",
            "solucao_servicos": "Nossos serviços",
            "diferencial": "Qualidade e confiança",
            "autoridade_sobre": "Sobre nossa empresa",
            "faq": "Perguntas frequentes",
            "identidade_visual_cores": "#2563EB",
            "provas_sociais": "Clientes satisfeitos",
            "contato_endereco": "Entre em contato",
            "iframe_mapa": ""
        }

    # 2. Mapear Imagens (CORREÇÃO CRÍTICA: Busca na raiz da pasta, não em subpastas)
    pasta_instagram = f"{pasta_base_cliente}/instagram_downloads_apify"
    caminhos_imagens = glob.glob(f"{pasta_instagram}/*.jpg")
    caminhos_imagens.sort()
    
    # Reorganiza para que foto_perfil.jpg seja sempre a primeira (imagem_1)
    foto_perfil_path = f"{pasta_instagram}/foto_perfil.jpg"
    outras_fotos = [img for img in caminhos_imagens if "foto_perfil" not in img]
    
    lista_final_imagens = []
    if os.path.exists(foto_perfil_path):
        lista_final_imagens.append(foto_perfil_path)
    lista_final_imagens.extend(outras_fotos)
    
    # Limita a 10 imagens para o site não ficar pesado no GitHub Pages
    lista_final_imagens = lista_final_imagens[:10]

    # 3. Prompt Mestre para o Gemini (Gerador de Código)
    prompt_mestre = f"""
    Atue como um Desenvolvedor Front-end Sênior e Copywriter Especialista em Alta Conversão.
    Crie um site institucional completo, moderno e responsivo em um único arquivo HTML.
    Use Tailwind CSS via CDN para estilização (rápido, bonito e sem arquivos externos).
    
    DADOS DO CLIENTE (JSON):
    {json.dumps(dados, ensure_ascii=False, indent=2)}
    
    INSTRUÇÕES DE IMAGENS:
    Você tem acesso a {len(lista_final_imagens)} imagens locais que serão hospedadas na pasta 'assets/'.
    No código HTML, referencie-as EXATAMENTE como: 'assets/imagem_1.jpg', 'assets/imagem_2.jpg', 'assets/imagem_3.jpg', etc.
    - Use 'assets/imagem_1.jpg' como a imagem principal (Hero Section ou Sobre).
    - Use as demais em uma seção de Galeria ou Serviços.
    
    ESTRUTURA OBRIGATÓRIA DO SITE:
    1. Header (Logo/Nome e Menu de navegação suave).
    2. Hero Section (Título forte baseado no "Grande Problema", subtítulo com a "Solução", e botão CTA).
    3. Seção Sobre (Baseada em "Autoridade").
    4. Seção Serviços/Soluções (Baseada em "A Solução").
    5. Seção Diferenciais (Por que escolher).
    6. Seção Depoimentos (Baseada em "Provas Sociais").
    7. Seção FAQ.
    8. Seção de Contato e Localização (Incluir o iframe do mapa fornecido no JSON e os dados de contato).
    9. Footer simples.
    
    IDENTIDADE VISUAL:
    Use as cores sugeridas em "identidade_visual_cores". Se não houver HEX, use uma paleta profissional e moderna que combine com o nicho.
    
    FORMATO DE SAÍDA:
    Retorne APENAS o código HTML cru. Não use ```html ... ``` markdown. Apenas o código puro começando com <!DOCTYPE html>.
    """

    configuracao = types.GenerateContentConfig(
        temperature=0.7,
        response_mime_type="text/plain" # Queremos texto puro (HTML)
    )

    try:
        resposta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt_mestre],
            config=configuracao
        )
        html_gerado = resposta.text
        
        # Limpeza de segurança caso o Gemini insira markdown mesmo pedindo para não
        if html_gerado.startswith("```html"):
            html_gerado = html_gerado[7:-3]
        if html_gerado.startswith("```"):
            html_gerado = html_gerado[3:-3]
            
        return html_gerado.strip(), lista_final_imagens
        
    except Exception as e:
        return None, f"Erro na API do Gemini ao gerar o site: {str(e)}"
