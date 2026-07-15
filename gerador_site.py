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
    Atue como um Desenvolvedor Front-end Sênior e Copywriter Especialista em Landing Pages de Alta Conversão.
A partir das informações do cliente fornecidas no final deste prompt, escreva o código completo de uma Landing Page em um único arquivo index.html (com todo o CSS embutido na tag <style>).
REGRAS DE DESENVOLVIMENTO (SIGA RIGOROSAMENTE):
Proibido Economizar Código: Escreva o script de fora a fora. Não abrevie o código, não crie módulos incompletos e não use placeholders como "adicione o resto aqui". Eu preciso da página 100% pronta para ir ao ar.
Design e UX Guiados pelo Nicho: Adapte a identidade visual estritamente ao nicho da empresa.
Se for um nicho fofo/descontraído (ex: pet shop, infantil), use bordas arredondadas (border-radius alto), cores vibrantes, tipografia amigável e tom de voz acolhedor.
Se for um nicho sério/corporativo (ex: advocacia, contabilidade), use formas retas, cantos quadrados, cores sóbrias (azul marinho, dourado, cinza), tipografia serifada ou elegante e tom de voz incisivo.
Se for intermediário (ex: estética, unhas, arquitetura), equilibre elegância com modernidade.
Tecnologia e Animações Modernas: Utilize variáveis CSS no :root para facilitar alterações. Inclua animações fluidas, efeitos de hover avançados, bibliotecas como AOS.js para animações ao rolar a tela, e elementos dinâmicos (como galerias com carrossel infinito).
Estrutura de Conversão: A página deve conter: Header fixo, Hero Section de impacto, Faixa de Benefícios, Sobre a Empresa/Profissional, Serviços/Produtos em formato de cards, Seção de Chamada para Ação (CTA) em destaque, Galeria de Fotos, FAQ (em tag <details>), Mapa (iframe) e Footer completo.
ATENÇÃO AO PORTFÓLIO/GALERIA: Inclua uma seção de Galeria de Fotos/Portfólio APENAS se o nicho for visual (ex: pet shop, estética, arquitetura, reformas). Se for um nicho estritamente corporativo ou consultivo (ex: advocacia, contabilidade, seguros), NÃO crie a seção de galeria.
SEO Técnico e Gatilhos: Inclua Meta Tags otimizadas, botões flutuantes e fixos do WhatsApp pulsantes, e estruturação semântica do HTML (h1, h2, seções claras).
Assinatura Obrigatória da Agência: No Footer, inclua os direitos reservados do cliente e adicione a assinatura exata: Desenvolvido por <a href="https://epiverso.com" target="_blank" style="color: var(--secondary); font-weight: bold; text-decoration: none;">EPIVERSO</a>. O link deve sempre abrir em uma nova aba e usar a cor secundária ou de destaque do tema para chamar a atenção.
DADOS DO CLIENTE:
Nome e Nicho: [Cole a resposta aqui]
O Grande Problema: [Cole a resposta aqui]
A Solução (Serviços): [Cole a resposta aqui]
Diferencial: [Cole a resposta aqui]
Autoridade (Sobre): [Cole a resposta aqui]
Perguntas Frequentes FAQ: [Cole a resposta aqui]
Identidade Visual/Cores: [Cole a resposta aqui]
Contato/Endereço: [Cole a resposta aqui]
Provas Sociais: [Cole a resposta aqui]
iframe do mapa: [Cole a resposta aqui]
quantas fotos no portfólio: [Cole a resposta aqui]
Baseado nisso, gere o código completo de forma clean um site limpo e lindo e muito profissional!
na parte das fotos você sempre vai colocar foto1.webp, foto2.webp...  que é como vou subir nessa ordem, sempre
o site deve sempre ser extremamente responsivo, para celulares, tabletes e computadores
traga sempre um design moderno fuja do que esta acostumado icones que não usa, tire essa cara de ia se inpire em sites que são lindos e modernos sem fugir do que ja foi proposto antes
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
