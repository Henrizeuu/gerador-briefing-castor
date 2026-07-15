import os
import glob
import PIL.Image
from google import genai
from google.genai import types

def gerar_briefing(pasta_base_cliente):
    CHAVE_API_GEMINI = os.environ.get("GEMINI_TOKEN")
    if not CHAVE_API_GEMINI:
        return "Erro: Token do Gemini não configurado no servidor."
        
    client = genai.Client(api_key=CHAVE_API_GEMINI)

    instrucoes_do_seu_gem = """
    Seu Papel: Você é um Analista de Negócios Sênior e Estrategista de Marketing Digital. Sua especialidade é analisar imagens para extrair informações valiosas de negócios locais.
    
    Gere apenas o questionário preenchido, pronto para copiar e colar no gerador de Landing Pages institucionais:
    Nome e Nicho: [Resposta]
    O Grande Problema: [Resposta]
    A Solução (Serviços): [Resposta]
    Diferencial: [Resposta]
    Autoridade (Sobre): [Resposta]
    FAQ: [Resposta]
    Identidade Visual/Cores: [Resposta]
    Provas Sociais: [Resposta]
    Contato/Endereço: [Cole a resposta aqui]
    iframe do mapa: [Cole a resposta aqui]
    """

    pasta_base_instagram = f"{pasta_base_cliente}/instagram_downloads_apify"
    pasta_base_google = f"{pasta_base_cliente}/google_reviews_extraidas"

    # Busca os textos dinamicamente na pasta do cliente atual
    arquivos_txt_bio = glob.glob(f"{pasta_base_instagram}/*.txt")
    caminho_texto_perfil = arquivos_txt_bio[0] if arquivos_txt_bio else None

    arquivos_txt_reviews = glob.glob(f"{pasta_base_google}/*.txt")
    caminho_texto_reviews = arquivos_txt_reviews[0] if arquivos_txt_reviews else None

    caminhos_todas_imagens = glob.glob(f"{pasta_base_instagram}/*/*.jpg")
    caminhos_todas_imagens.sort()

    if not caminhos_todas_imagens or not caminho_texto_perfil:
        return "❌ Erro: Não foi possível encontrar os dados baixados. Verifique se o perfil existe e é aberto."

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
    
    Abaixo estão as imagens dos últimos posts. Gere seu relatório.
    """

    conteudo_para_enviar = [texto_contexto]

    caminho_foto_perfil = os.path.join(pasta_base_instagram, "foto_perfil.jpg")
    if os.path.exists(caminho_foto_perfil):
        conteudo_para_enviar.append(PIL.Image.open(caminho_foto_perfil))

    for img_path in caminhos_todas_imagens[:21]:
        try:
             shortcode = os.path.basename(os.path.dirname(img_path))
             caminho_desc = os.path.join(pasta_base_instagram, shortcode, "descricao.txt")
             if os.path.exists(caminho_desc):
                 with open(caminho_desc, 'r', encoding='utf-8') as f_desc:
                     conteudo_para_enviar.append(f"Legenda: {f_desc.read()}")
             conteudo_para_enviar.append(PIL.Image.open(img_path))
        except Exception:
             pass

    configuracao = types.GenerateContentConfig(
        system_instruction=instrucoes_do_seu_gem,
        temperature=0.7
    )

    resposta = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=conteudo_para_enviar,
        config=configuracao
    )

    return resposta.text