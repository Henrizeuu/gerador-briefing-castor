# 🚀 Briefing Castor - Pronto para Deploy Gratuito

Seu projeto está **100% configurado** para deploy gratuito no **Render.com**!

## 📁 Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `render.yaml` | Configuração automática para Render.com |
| `DEPLOY_RENDER.md` | Guia completo passo-a-passo |
| `README.md` | Atualizado com informações de deploy |
| `app.py` | Backend Flask (configurado para produção) |
| `requirements.txt` | Dependências com gunicorn |
| `index.html` | Frontend profissional preto e branco |

## 🎯 Resumo da Configuração

### O que foi feito:
✅ Arquivo `render.yaml` criado com configuração completa  
✅ Backend Flask configurado com Gunicorn para produção  
✅ Frontend HTML/CSS moderno e responsivo  
✅ Scraper Google Maps funcionando corretamente  
✅ Integração com IA Gemini configurada  
✅ Guia de deploy detalhado  

### Configurações do Render:
- **Tipo**: Web Service (Python)
- **Plano**: Free (512MB RAM)
- **Build**: `pip install -r requirements.txt`
- **Start**: `gunicorn app:app --bind 0.0.0.0:$PORT`
- **Região**: Oregon (mais próxima do Brasil)
- **Auto Deploy**: Ativado

## 🔑 Variáveis de Ambiente Necessárias

No painel do Render, configure:

```
GEMINI_API_KEY=sua_chave_aqui
APIFY_API_TOKEN=seu_token_aqui
PYTHON_VERSION=3.12.0
```

## ⚡ Deploy em 5 Minutos

1. **Suba para o GitHub** (se ainda não estiver):
   ```bash
   git add .
   git commit -m "Preparando para deploy no Render"
   git push origin main
   ```

2. **Acesse Render.com**: https://dashboard.render.com

3. **Crie novo Web Service**:
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub
   - Selecione o branch `main`

4. **Configure**:
   - Nome: `briefing-castor`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Instance Type: **Free**

5. **Adicione as variáveis de ambiente** (GEMINI_API_KEY, APIFY_API_TOKEN)

6. **Clique em "Create Web Service"** e aguarde 3-5 minutos

## 🌐 Sua Aplicação Estará Em

```
https://briefing-castor.onrender.com
```

## ⚠️ Importante: Sleep Mode

O plano free do Render entra em sleep após 15min de inatividade:
- **Primeiro acesso**: ~30 segundos para "acordar"
- **Solução opcional**: Use [UptimeRobot](https://uptimerobot.com/) para pingar a cada 14min

## 🆘 Precisa de Ajuda?

Consulte o arquivo `DEPLOY_RENDER.md` para:
- Passo a passo detalhado com prints
- Solução de problemas comuns
- Dicas de otimização
- Como adicionar domínio customizado

## ✨ Alternativas Gratuitas

Se preferir outras plataformas:
- **Fly.io**: 3 VMs grátis (256MB cada)
- **Railway.app**: $5 crédito/mês
- **Hugging Face Spaces**: SDK Docker (pago agora)

---

**🎉 Tudo pronto! Só fazer o deploy!**
