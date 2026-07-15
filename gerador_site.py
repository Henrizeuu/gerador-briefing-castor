import os
import glob
from google import genai
from google.genai import types

def criar_html_institucional(briefing_texto, pasta_base_cliente):
    CHAVE_API_GEMINI = os.environ.get("GEMINI_TOKEN")
    if not CHAVE_API_GEMINI:
        return None, "Erro: Token do Gemini não configurado."
        
    client = genai.Client(api_key=CHAVE_API_GEMINI)
    
    # Busca apenas os nomes dos arquivos das imagens raspadas
    pasta_instagram = f"{pasta_base_cliente}/instagram_downloads_apify"
    caminhos_imagens = glob.glob(f"{pasta_instagram}/*/*.jpg")
    
    # Cria uma lista de caminhos relativos para a IA usar (ex: ./assets/midia_1.jpg)
    nomes_imagens_para_ia = []
    for i, caminho in enumerate(caminhos_imagens[:10]): # Limite de 10 imagens no site
        nome_arquivo = os.path.basename(caminho)
        nomes_imagens_para_ia.append(f"./assets/{nome_arquivo}")

    instrucoes_desenvolvedor = """
    Seu Papel: Você é um Desenvolvedor Front-end Master especializado em sites institucionais robustos e páginas de alta conversão. Você NUNCA cria e-commerces ou lojas virtuais.
    
    Sua Tarefa: Transformar o briefing recebido em um arquivo 'index.html' completo, moderno e responsivo, contendo CSS embarcado (<style>) e JavaScript se necessário.
    
    Diretrizes Rigorosas:
    1. Estrutura Robusta: O site deve ter as seções: Header (com navegação), Hero (o grande problema e diferencial), Sobre Nós (autoridade), Serviços (a solução), Depoimentos (provas sociais), FAQ e Footer.
    2. Imagens: Use EXATAMENTE os caminhos de imagens fornecidos. Não crie imagens genéricas. Distribua essas imagens de forma inteligente nas seções do site.
    3. Design: Profissional, utilizando as cores do briefing. Use tendências modernas (sombras suaves, tipografia limpa, botões com hover).
    4. Saída: Retorne EXCLUSIVAMENTE o código HTML completo. Sem marcações de bloco de código (```html), sem explicações, apenas o código cru que pode ser salvo diretamente em um arquivo.
    """

    prompt = f"""
    === BRIEFING DO CLIENTE ===
    {briefing_texto}
    
    === IMAGENS DISPONÍVEIS ===
    Use estas imagens nas tags <img> do site (elas estarão na pasta assets):
    {nomes_imagens_para_ia}
    
    Crie o código HTML/CSS/JS em um único arquivo agora.
    """

    configuracao = types.GenerateContentConfig(
        system_instruction=instrucoes_desenvolvedor,
        temperature=0.4 # Temperatura menor para focar em código estruturado
    )

    resposta = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=configuracao
    )

    # Limpa possíveis blocos de código caso a IA teime em colocar
    codigo_limpo = resposta.text.replace("```html", "").replace("```", "").strip()
    return codigo_limpo, caminhos_imagens[:10]