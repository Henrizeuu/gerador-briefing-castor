import os
import glob
import json
import PIL.Image
from google import genai
from google.genai import types

def gerar_briefing(pasta_base_cliente, iframe_pronto=""):
    """
    Analisa os dados extraídos (textos e imagens) e gera um Briefing em JSON
    estruturado para o gerador de sites.
    """
    CHAVE_API_GEMINI = os.environ.get("GEMINI_TOKEN")
    if not CHAVE_API_GEMINI:
        return "Erro: Token do Gemini não configurado no servidor."
        
    client = genai.Client(api_key=CHAVE_API_GEMINI)
    
    # Instrução de Sistema (O "Cérebro" do Analista)
    instrucoes_do_seu_gem = """
    Você é um Analista de Negócios Sênior e Estrategista de Marketing Digital especialista em alta conversão.
    Sua tarefa é analisar os dados textuais e visuais de um cliente (Instagram e Google Maps) e extrair informações cruciais para a criação de uma Landing Page.
    
    DIRETRIZES DE ANÁLISE:
    1. Nome e Nicho: Identifique o nome da empresa e o segmento de atuação.
    2. O Grande Problema: Qual dor latente o cliente resolve? (Ex: vazamentos, falta de tempo, insegurança jurídica).
    3. A Solução (Serviços): Liste os principais serviços oferecidos com base nos posts e bio.
    4. Diferencial: O que torna este negócio único? (Ex: atendimento 24h, garantia, experiência).
    5. Autoridade (Sobre): Resuma a história, formação ou tempo de mercado para gerar confiança.
    6. FAQ: Crie 3 a 4 perguntas e respostas frequentes baseadas no nicho e nas avaliações.
    7. Identidade Visual/Cores: Descreva a paleta de cores predominante no feed e o estilo (ex: minimalista, corporativo, vibrante). Sugira códigos HEX se possível.
    8. Provas Sociais: Extraia 2 ou 3 depoimentos curtos e persuasivos das avaliações do Google ou legendas.
    9. Contato/Endereço: Telefone, e-mail e endereço físico (se houver).
    
    FORMATO DE SAÍDA OBRIGATÓRIO:
    Você deve responder APENAS com um objeto JSON válido, sem markdown, sem explicações extras. Use exatamente estas chaves:
    {
      "nome_nicho": "string",
      "grande_problema": "string",
      "solucao_servicos": "string",
      "diferencial": "string",
      "autoridade_sobre": "string",
      "faq": "string (formato: P: ... R: ...)",
      "identidade_visual_cores": "string",
      "provas_sociais": "string",
      "contato_endereco": "string",
      "iframe_mapa": "string (cole o código do iframe fornecido no contexto)"
    }
    """

    # Caminhos das pastas
    pasta_instagram = f"{pasta_base_cliente}/instagram_downloads_apify"
    pasta_google = f"{pasta_base_cliente}/google_reviews_extraidas"

    # 1. Leitura dos Textos
    arquivos_txt_bio = glob.glob(f"{pasta_instagram}/*.txt")
    caminho_texto_perfil = arquivos_txt_bio[0] if arquivos_txt_bio else None
    
    arquivos_txt_reviews = glob.glob(f"{pasta_google}/*.txt")
    caminho_texto_reviews = arquivos_txt_reviews[0] if arquivos_txt_reviews else None

    if not caminho_texto_perfil:
        return "❌ Erro: Não foi possível encontrar os dados baixados do perfil (Bio)."

    with open(caminho_texto_perfil, 'r', encoding='utf-8') as f:
        dados_do_perfil = f.read()

    dados_das_avaliacoes = ""
    if caminho_texto_reviews:
        with open(caminho_texto_reviews, 'r', encoding='utf-8') as f:
            dados_das_avaliacoes = f.read()

    # 2. Montagem do Contexto Textual
    texto_contexto = f"""
    === DADOS ESTRUTURAIS DO PERFIL (INSTAGRAM) ===
    {dados_do_perfil}
    
    === AVALIAÇÕES DO GOOGLE MAPS (PROVA SOCIAL) ===
    {dados_das_avaliacoes if dados_das_avaliacoes else "Nenhuma avaliação fornecida."}
    
    === CÓDIGO DO IFRAME DO MAPA (PARA O SITE) ===
    {iframe_pronto if iframe_pronto else "Nenhum mapa foi fornecido."}
    """

    # 3. Carregamento das Imagens
    conteudo_para_enviar = [texto_contexto]
    
    # Foto de Perfil
    caminho_foto_perfil = os.path.join(pasta_instagram, "foto_perfil.jpg")
    if os.path.exists(caminho_foto_perfil):
        try:
            conteudo_para_enviar.append(PIL.Image.open(caminho_foto_perfil))
        except Exception:
            pass

    # Fotos dos Posts (Limitado a 21 para economizar tokens e contexto)
    caminhos_todas_imagens = glob.glob(f"{pasta_instagram}/*.jpg")
    # Remove a foto de perfil da lista para não duplicar
    caminhos_todas_imagens = [img for img in caminhos_todas_imagens if "foto_perfil" not in img]
    caminhos_todas_imagens.sort()
    
    for img_path in caminhos_todas_imagens[:21]:
        try:
            conteudo_para_enviar.append(PIL.Image.open(img_path))
        except Exception:
            pass

    # 4. Configuração e Chamada da API
    configuracao = types.GenerateContentConfig(
        system_instruction=instrucoes_do_seu_gem,
        temperature=0.2, # Baixa temperatura para focar na extração precisa
        response_mime_type="application/json" # Força a API a devolver apenas JSON
    )

    try:
        resposta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=conteudo_para_enviar,
            config=configuracao
        )
        return resposta.text
    except Exception as e:
        return f"❌ Erro na API do Gemini: {str(e)}"
