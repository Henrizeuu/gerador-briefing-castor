import os
import glob
import json
import shutil
from github import Github

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


def subir_para_github(html_content, image_paths, repo_name, custom_domain):
    """
    Cria um repositório no GitHub com o HTML e imagens do site,
    e configura o GitHub Pages com domínio personalizado.
    """
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    GITHUB_USER = os.environ.get("GITHUB_USER")
    
    if not GITHUB_TOKEN or not GITHUB_USER:
        return "❌ Erro: Tokens do GitHub não configurados nas variáveis de ambiente."
    
    try:
        # Autenticação
        g = Github(GITHUB_TOKEN)
        user = g.get_user()
        
        # Criar repositório público
        print(f"Criando repositório: {repo_name}")
        repo = user.create_repo(
            name=repo_name,
            description="Site gerado automaticamente - EpiVerso",
            public=True,
            auto_init=True
        )
        
        # Criar estrutura de arquivos
        print("Upload do index.html...")
        repo.create_file(
            path="index.html",
            message="Deploy inicial: HTML do site",
            content=html_content.encode('utf-8')
        )
        
        # Upload das imagens
        if image_paths:
            print(f"Upload de {len(image_paths)} imagens...")
            os.makedirs("./temp_assets", exist_ok=True)
            
            for idx, img_path in enumerate(image_paths, 1):
                if os.path.exists(img_path):
                    # Copia imagem para pasta temporária com nome padronizado
                    temp_name = f"imagem_{idx}.jpg"
                    temp_path = f"./temp_assets/{temp_name}"
                    shutil.copy2(img_path, temp_path)
                    
                    # Lê e faz upload
                    with open(temp_path, "rb") as f:
                        content = f.read()
                    
                    repo.create_file(
                        path=f"assets/{temp_name}",
                        message=f"Upload da imagem {idx}",
                        content=content
                    )
            
            # Limpa pasta temporária
            shutil.rmtree("./temp_assets")
        
        # Configurar GitHub Pages
        print("Configurando GitHub Pages...")
        pages_info = repo.create_pages(source={"branch": "main"})
        
        # Aguarda propagação do DNS (em produção isso é assíncrono)
        deploy_url = f"https://{GITHUB_USER}.github.io/{repo_name}/"
        
        mensagem_sucesso = (
            f"✅ Sucesso! Repositório '{repo_name}' criado e configurado.\n\n"
            f"🌐 URL do GitHub Pages: {deploy_url}\n"
            f"🔗 Domínio personalizado configurado: {custom_domain}\n\n"
            f"⏳ Aguarde alguns minutos para a propagação do DNS."
        )
        
        # Cria arquivo CNAME para domínio customizado
        if custom_domain:
            repo.create_file(
                path="CNAME",
                message=f"Configura domínio personalizado: {custom_domain}",
                content=custom_domain.replace("https://", "").replace("http://", "").strip()
            )
        
        return mensagem_sucesso
        
    except Exception as e:
        error_msg = f"❌ Erro no deploy: {str(e)}"
        print(error_msg)
        return error_msg
