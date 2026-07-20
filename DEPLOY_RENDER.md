# Briefing Castor - Deploy no Render.com

Este guia explica como fazer deploy gratuito da aplicação no **Render.com**.

## 🎯 Por que Render.com?

- ✅ **Plano Gratuito Vitalício** (Web Services)
- ✅ Suporte nativo a Python/Flask
- ✅ HTTPS automático
- ✅ Deploy direto do GitHub
- ✅ Sem necessidade de cartão de crédito
- ⚠️ **Atenção**: O serviço entra em "sleep" após 15min de inatividade (acorda em ~30s na próxima requisição)

## 📋 Pré-requisitos

1. Conta no GitHub
2. Conta no Render.com (gratuita)
3. Seu código já está no GitHub

## 🚀 Passo a Passo

### 1. Prepare o Repositório GitHub

Certifique-se de que estes arquivos estão no seu repositório:

```
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── index.html            # Frontend
├── scraper_dados.py      # Scraper
├── analise_gemini.py     # IA Gemini
├── gerador_site.py       # Gerador de sites
├── github_deploy.py      # Deploy GitHub Pages
└── render.yaml           # Configuração do Render (criar este arquivo)
```

### 2. Crie o Arquivo `render.yaml`

Este arquivo já foi criado no repositório. Ele define:
- Ambiente Python 3.12
- Comando de start com gunicorn
- Variáveis de ambiente necessárias
- Health check

### 3. Crie o Web Service no Render

1. Acesse https://dashboard.render.com
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: `briefing-castor` (ou outro nome)
   - **Region**: Escolha a mais próxima (ex: Oregon, Frankfurt)
   - **Branch**: `main` ou `master`
   - **Root Directory**: Deixe em branco (se os arquivos estão na raiz)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Instance Type**: **Free**

### 4. Configure as Variáveis de Ambiente

No painel do Render, vá em **Environment** e adicione:

| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | Sua chave da API Google Gemini |
| `APIFY_API_TOKEN` | Seu token da API Apify |
| `PYTHON_VERSION` | `3.12.0` |

### 5. Deploy

1. Clique em **"Create Web Service"**
2. Aguarde o build (3-5 minutos)
3. Quando estiver verde ("Live"), clique no URL para acessar

## 🔗 URL da Aplicação

Sua aplicação estará disponível em:
```
https://briefing-castor.onrender.com
```
(ou o nome que você escolheu)

## ⚡ Dicas Importantes

### Para evitar sleep (opcional):
- Use um serviço de uptime monitor como [UptimeRobot](https://uptimerobot.com/) (gratuito)
- Configure um ping a cada 14 minutos para manter ativo
- Ou simplesmente aceite o sleep (acorda em ~30s)

### Logs e Debug:
- Acesse **Logs** no painel do Render para ver erros
- Use `print()` no código para debug (aparece nos logs)

### Limites do Plano Free:
- 512 MB RAM
- 750 horas/mês (suficiente para 1 serviço sempre ativo)
- Sleep após 15min de inatividade

## 🆘 Problemas Comuns

### Build falhou:
- Verifique se `requirements.txt` está correto
- Confira se há erros de sintaxe no Python

### Serviço não inicia:
- Verifique as variáveis de ambiente
- Confira os logs para mensagens de erro
- Certifique-se que `app.py` tem `if __name__ == "__main__"` configurado corretamente

### Erro 502 Bad Gateway:
- Aguarde alguns minutos (o serviço pode estar iniciando)
- Verifique os logs

## 🎉 Pronto!

Sua aplicação está rodando gratuitamente na internet!

---

**Próximos passos opcionais:**
- Configure um domínio customizado (gratuito no Render)
- Monitore uso nos dashboards do Render
- Considere upgrade para plano pago ($7/mês) se precisar de mais performance
