import os
import glob
import PIL.Image
from google import genai
from google.genai import types

def gerar_briefing(pasta_base_cliente, iframe_pronto=""):
    CHAVE_API_GEMINI = os.environ.get("GEMINI_TOKEN")
    if not CHAVE_API_GEMINI:
        return "Erro: Token do Gemini não configurado no servidor."
        
    client = genai.Client(api_key=CHAVE_API_GEMINI)

    instrucoes_do_seu_gem = """
    Você é um Analista de Negócios Sênior e Copywriter de Alta Conversão.
    Analise os dados do cliente e crie os textos persuasivos para um site institucional.
    
    REGRA DE OURO: Retorne ÚNICA E EXCLUSIVAMENTE um objeto JSON válido, sem NENHUMA formatação markdown (sem ```json), sem texto antes e sem texto depois. O sistema quebrará se você retornar qualquer coisa que não seja o JSON puro.
    
    Estrutura exata do JSON que você deve retornar:
    {
      "nome_empresa": "[Extraia o nome]",
      "nicho": "[Qual é a área de atuação]",
      "hero_headline": "[Uma frase de impacto curta e forte para o topo do site baseada no grande problema do cliente]",
      "hero_subheadline": "[Um parágrafo curto explicando como a empresa resolve esse problema]",
      "diferencial": "[O maior diferencial em 5 palavras]",
      "sobre_autoridade": "[Um parágrafo resumindo a autoridade e experiência]",
      "servico_1": "[Nome de um serviço principal]",
      "servico_2": "[Nome do segundo serviço principal]",
      "servico_3": "[Nome do terceiro serviço principal]",
      "faq_1_p": "[Pergunta frequente 1]",
      "faq_1_r": "[Resposta 1]",
      "faq_2_p": "[Pergunta frequente 2]",
      "faq_2_r": "[Resposta 2]",
      "faq_3_p": "[Pergunta frequente 3]",
      "faq_3_r": "[Resposta 3]",
      "depoimento_1_nome": "[Nome de um cliente do Google Maps]",
      "depoimento_1_texto": "[Resumo do elogio 1]",
      "depoimento_2_nome": "[Nome de outro cliente]",
      "depoimento_2_texto": "[Resumo do elogio 2]",
      "iframe_mapa": "[Cole o CÓDIGO DO IFRAME DO MAPA fornecido abaixo EXATAMENTE como recebeu]"
    }
    """

    pasta_base_instagram = f"{pasta_base_cliente}/instagram_downloads_apify"
    pasta_base_google = f"{pasta_base_cliente}/google_reviews_extraidas"

    arquivos_txt_bio = glob.glob(f"{pasta_base_instagram}/*.txt")
    caminho_texto_perfil = arquivos_txt_bio[0] if arquivos_txt_bio else None
    arquivos_txt_reviews = glob.glob(f"{pasta_base_google}/*.txt")
    caminho_texto_reviews = arquivos_txt_reviews[0] if arquivos_txt_reviews else None
    caminhos_todas_imagens = glob.glob(f"{pasta_base_instagram}/*.jpg")
    caminhos_todas_imagens.sort()

    if not caminho_texto_perfil:
        return "❌ Erro: Não foi possível encontrar os dados baixados do perfil (Bio)."

    with open(caminho_texto_perfil, 'r', encoding='utf-8') as f:
        dados_do_perfil = f.read()

    dados_das_avaliacoes = ""
    if caminho_texto_reviews:
        with open(caminho_texto_reviews, 'r', encoding='utf-8') as f:
            dados_das_avaliacoes = f.read()

    texto_contexto = f"""
    === DADOS ESTRUTURAIS DO PERFIL ===
    {dados_do_perfil}
    === AVALIAÇÕES DO GOOGLE MAPS ===
    {dados_das_avaliacoes if dados_das_avaliacoes else "Nenhuma avaliação fornecida."}
    === CÓDIGO DO IFRAME DO MAPA ===
    {iframe_pronto if iframe_pronto else "Nenhum mapa foi fornecido."}
    """

    conteudo_para_enviar = [texto_contexto]
    caminho_foto_perfil = os.path.join(pasta_base_instagram, "foto_perfil.jpg")
    if os.path.exists(caminho_foto_perfil):
        conteudo_para_enviar.append(PIL.Image.open(caminho_foto_perfil))

    for img_path in caminhos_todas_imagens[:21]:
        try:
             conteudo_para_enviar.append(PIL.Image.open(img_path))
        except Exception:
             pass

    configuracao = types.GenerateContentConfig(
        system_instruction=instrucoes_do_seu_gem,
        temperature=0.2, # Super baixo para focar apenas em extrair e formatar JSON
        response_mime_type="application/json" # Força a API a devolver apenas JSON
    )

    resposta = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=conteudo_para_enviar,
        config=configuracao
    )

    return resposta.text
