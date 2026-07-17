import os
from github import Github
from github import Auth

def subir_para_github(codigo_html, lista_imagens, nome_cliente_repo, dominio_customizado):
    TOKEN_GITHUB = os.environ.get("GITHUB_TOKEN")
    if not TOKEN_GITHUB:
        return "Erro: Token do GitHub não configurado."

    auth = Auth.Token(TOKEN_GITHUB)
    g = Github(auth=auth)

    try:
        usuario = g.get_user()
        
        try:
            repo = usuario.create_repo(nome_cliente_repo, description=f"Site Institucional - {nome_cliente_repo}")
        except Exception:
            repo = usuario.get_repo(nome_cliente_repo)
        
        def salvar_arquivo_no_github(caminho_repo, mensagem, conteudo):
            try:
                arquivo_existente = repo.get_contents(caminho_repo, ref="main")
                repo.update_file(arquivo_existente.path, mensagem, conteudo, arquivo_existente.sha, branch="main")
            except Exception:
                repo.create_file(caminho_repo, mensagem, conteudo, branch="main")

        salvar_arquivo_no_github("index.html", "Atualizando Index HTML", codigo_html)
        
        # Ajuste crucial: Começar a contar do 1 e forçar o formato .jpg para alinhar com o HTML gerado
        for i, caminho_local in enumerate(lista_imagens):
            caminho_no_github = f"assets/imagem_{i+1}.jpg"
            with open(caminho_local, 'rb') as f:
                conteudo_imagem = f.read()
            salvar_arquivo_no_github(caminho_no_github, f"Adicionando {caminho_no_github}", conteudo_imagem)

        if dominio_customizado:
            salvar_arquivo_no_github("CNAME", "Configurando domínio", dominio_customizado)
            
        return f"Sucesso! Site subiu para https://github.com/{usuario.login}/{nome_cliente_repo}"
        
    except Exception as e:
        return f"Erro ao subir pro GitHub: {str(e)}"
