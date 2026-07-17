import os
import glob
import re
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
A partir das informações do cliente fornecidas no final deste prompt, escreva o código completo de um Site Institucional Robusto e completo em um único arquivo index.html (com todo o CSS embutido na tag <style>).

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

DADOS DO CLIENTE:
{briefing_texto}
quantas fotos no portfólio: {quantidade_fotos}"""

    configuracao = types.GenerateContentConfig(
        temperature=0.4, # Temperatura reduzida para focar em código e evitar respostas criativas longas
        max_output_tokens=8192 
    )

    try:
        resposta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_mestre,
            config=configuracao
        )
        
        texto_bruto = resposta.text
        
        # --- FILTRO BLINDADO 2.0 (Expressões Regulares) ---
        # Varre a resposta e recorta o HTML, eliminando qualquer conversa que a IA tenha escrito antes
        match = re.search(r'(<!DOCTYPE html>|<html)', texto_bruto, re.IGNORECASE)
        if match:
            codigo_limpo = texto_bruto[match.start():]
        else:
            codigo_limpo = texto_bruto
            
        # Limpa as crases de formatação do Markdown que possam sobrar
        codigo_limpo = codigo_limpo.replace("```html", "").replace("```", "").strip()
        
        # Trava de segurança final: Se a IA não fechou o arquivo, nós garantimos que não vai quebrar o layout
        if not codigo_limpo.endswith("</html>"):
            codigo_limpo += "\n</body>\n</html>"
            
        return codigo_limpo, caminhos_imagens[:10]
        
    except Exception as e:
        return None, f"Erro na API do Gemini ao gerar o código: {str(e)}"
