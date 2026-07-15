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
        
        # 1. Tenta criar o repositório. Se ele já existir, selecionamos o existente.
        try:
            repo = usuario.create_repo(nome_cliente_repo, description=f"Site Institucional - {nome_cliente_repo}")
        except Exception:
            repo = usuario.get_repo(nome_cliente_repo)
        
        # Função interna blindada: se o arquivo já existir, ela pega o SHA e atualiza. Se não, cria.
        def salvar_arquivo_no_github(caminho_repo, mensagem, conteudo):
            try:
                # Verifica se o arquivo já existe no repositório
                arquivo_existente = repo.get_contents(caminho_repo, ref="main")
                # Se existir, atualiza enviando o SHA (exatamente o que a documentação pede)
                repo.update_file(arquivo_existente.path, mensagem, conteudo, arquivo_existente.sha, branch="main")
            except Exception:
                # Se não existir, cria do zero
                repo.create_file(caminho_repo, mensagem, conteudo, branch="main")

        # 2. Faz o commit (ou update) do index.html
        salvar_arquivo_no_github("index.html", "Atualizando Index HTML", codigo_html)
        
        # 3. Faz o commit das imagens na pasta /assets com os mesmos nomes que a IA recebeu
        for i, caminho_local in enumerate(lista_imagens):
            caminho_no_github = f"assets/imagem_{i}.jpg"
            with open(caminho_local, 'rb') as f:
                conteudo_imagem = f.read()
            salvar_arquivo_no_github(caminho_no_github, f"Adicionando {caminho_no_github}", conteudo_imagem)

        # 4. Cria (ou atualiza) o arquivo CNAME
        if dominio_customizado:
            salvar_arquivo_no_github("CNAME", "Configurando domínio", dominio_customizado)
            
        return f"Sucesso! Site subiu para [https://github.com/](https://github.com/){usuario.login}/{nome_cliente_repo}"
        
    except Exception as e:
        return f"Erro ao subir pro GitHub: {str(e)}"
