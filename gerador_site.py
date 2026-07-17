import os
import glob
from google import genai
from google.genai import types

def criar_html_institucional(briefing_texto, pasta_base_cliente):
    CHAVE_API_GEMINI = os.environ.get("GEMINI_TOKEN")
    if not CHAVE_API_GEMINI:
        return None, "Erro: Token do Gemini não configurado."
        
    client = genai.Client(api_key=CHAVE_API_GEMINI)
    
    pasta_instagram = f"{pasta_base_cliente}/instagram_downloads_apify"
    caminhos_imagens = glob.glob(f"{pasta_instagram}/*/*.jpg")
    quantidade_fotos = len(caminhos_imagens[:10])

    prompt_mestre = f"""Atue como um Desenvolvedor Front-end Sênior e Copywriter Especialista em Alta Conversão.
A partir das informações do cliente fornecidas no final deste prompt, escreva o código completo de um Site Institucional Robusto e completo. Esqueça páginas simples; você deve entregar um design estruturado que passe autoridade de mercado (simulando múltiplas seções institucionais ricas) em um único arquivo index.html (com todo o CSS embutido na tag <style>).

REGRAS DE DESENVOLVIMENTO (SIGA RIGOROSAMENTE):
Proibido Economizar Código: Escreva o script de fora a fora. Não abrevie o código, não crie módulos incompletos e não use placeholders como "adicione o resto aqui". Eu preciso da página 100% pronta para ir ao ar.
Design e UX Guiados pelo Nicho: Adapte a identidade visual estritamente ao nicho da empresa.
Se for um nicho fofo/descontraído (ex: pet shop, infantil), use bordas arredondadas (border-radius alto), cores vibrantes, tipografia amigável e tom de voz acolhedor.
Se for um nicho sério/corporativo (ex: advocacia, contabilidade), use formas retas, cantos quadrados, cores sóbrias (azul marinho, dourado, cinza), tipografia serifada ou elegante e tom de voz incisivo.
Se for intermediário (ex: estética, unhas, arquitetura), equilibre elegância com modernidade.
Tecnologia e Animações Modernas: Utilize variáveis CSS no :root para facilitar alterações. Inclua animações fluidas, efeitos de hover avançados, bibliotecas como AOS.js para animações ao rolar a tela, e elementos dinâmicos (como galerias com carrossel infinito).
Estrutura de Conversão: A página deve conter: Header fixo, Hero Section de impacto, Faixa de Benefícios, Sobre a Empresa/Profissional, Serviços/Produtos em formato de cards, Seção de Chamada para Ação (CTA) em destaque, Galeria de Fotos, FAQ (em tag <details>), Mapa (iframe) e Footer completo.
ATENÇÃO AO PORTFÓLIO/GALERIA: Inclua uma seção de Galeria de Fotos/Portfólio APENAS se o nicho for visual. Se for um nicho estritamente corporativo (ex: advocacia, contabilidade), NÃO crie a seção de galeria.
CAMINHOS DAS IMAGENS (MUITO IMPORTANTE): Na parte das fotos, você SEMPRE vai usar a seguinte estrutura de arquivos nas tags <img>: assets/imagem_1.jpg, assets/imagem_2.jpg, assets/imagem_3.jpg... até o limite de fotos disponíveis. NUNCA use .webp.
SEO Técnico e Gatilhos: Inclua Meta Tags otimizadas, botões flutuantes e fixos do WhatsApp pulsantes, e estruturação semântica do HTML (h1, h2, seções claras).
Assinatura Obrigatória da Agência: No Footer, inclua os direitos reservados do cliente e adicione a assinatura exata: Desenvolvido por <a href="https://epiverso.com" target="_blank" style="color: var(--secondary); font-weight: bold; text-decoration: none;">EPIVERSO</a>.

DADOS DO CLIENTE:
{briefing_texto}
quantas fotos no portfólio: {quantidade_fotos}

Baseado nisso, gere o código completo de forma clean. Um site limpo, lindo e muito profissional!
O site deve sempre ser extremamente responsivo para celulares, tablets e computadores. Traga um design moderno, fuja de ícones não utilizados e tire a "cara de IA". Inspire-se em páginas institucionais de alto nível."""

    configuracao = types.GenerateContentConfig(
        temperature=0.6,
        max_output_tokens=8192 
    )

    resposta = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt_mestre,
        config=configuracao
    )

    codigo_limpo = resposta.text.replace("```html", "").replace("```", "").strip()
    return codigo_limpo, caminhos_imagens[:10]
