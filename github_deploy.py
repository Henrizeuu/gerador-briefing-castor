import os
from github import Github
from github import Auth

def subir_para_github(codigo_html, lista_imagens, nome_cliente_repo, dominio_customizado):
    # Você precisará gerar um Personal Access Token (PAT) no GitHub e colocar no .env
    TOKEN_GITHUB = os.environ.get("GITHUB_TOKEN")
    if not TOKEN_GITHUB:
        return "Erro: Token do GitHub não configurado."

    auth = Auth.Token(TOKEN_GITHUB)
    g = Github(auth=auth)

    try:
        usuario = g.get_user()
        
        # 1. Cria o repositório do cliente (privado ou público, aqui está como público para o Pages funcionar free)
        repo = usuario.create_repo(nome_cliente_repo, description=f"Site Institucional - {nome_cliente_repo}")
        
        # 2. Faz o commit do index.html
        repo.create_file("index.html", "Commit inicial: Index HTML", codigo_html, branch="main")
        
        # 3. Faz o commit das imagens na pasta /assets
        for caminho_local in lista_imagens:
            nome_arquivo = os.path.basename(caminho_local)
            caminho_no_github = f"assets/{nome_arquivo}"
            
            with open(caminho_local, 'rb') as f:
                conteudo_imagem = f.read()
                
            repo.create_file(caminho_no_github, f"Adicionando {nome_arquivo}", conteudo_imagem, branch="main")

        # 4. Cria o arquivo CNAME para o GitHub Pages reconhecer o domínio (epiverso.exemplocliente.com)
        if dominio_customizado:
            repo.create_file("CNAME", "Configurando domínio", dominio_customizado, branch="main")
            
        return f"Sucesso! Site subiu para [https://github.com/Henrizeuu/](https://github.com/Henrizeuu/){nome_cliente_repo}"
        
    except Exception as e:
        return f"Erro ao subir pro GitHub: {str(e)}"