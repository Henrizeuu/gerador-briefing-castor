# Guia de Deploy no Hugging Face Spaces

## 🚀 Deploy Rápido em 5 Minutos

### Opção 1: Via Interface Web (Recomendado)

1. **Acesse o Hugging Face**
   - Vá para https://huggingface.co/spaces
   - Faça login na sua conta (crie uma grátis se necessário)

2. **Crie um Novo Space**
   - Clique em "Create new Space"
   - Preencha as informações:
     - **Space name**: `briefing-castor` (ou outro nome)
     - **License**: MIT
     - **SDK**: Docker
     - **Visibility**: Public
   - Clique em "Create Space"

3. **Adicione os Arquivos**
   
   No seu novo Space, clique em "Files" → "Add file" → "Upload files" e faça upload de:
   - `Dockerfile`
   - `requirements.txt`
   - `app.py`
   - `index.html`
   - `scraper_dados.py`
   - `gerador_site.py`
   - `analise_gemini.py`
   - `github_deploy.py`
   - `README.md`

4. **Configure as Variáveis de Ambiente**
   - Vá em "Settings" → "Variables and secrets"
   - Adicione:
     - `GEMINI_API_KEY`: Sua chave da API Google Gemini
     - `APIFY_API_TOKEN`: Seu token da Apify
   
   Para obter as chaves:
   - Gemini: https://aistudio.google.com/app/apikey
   - Apify: https://console.apify.com/account#/integrations

5. **Aguarde o Deploy**
   - O Hugging Face vai automaticamente buildar e deployar
   - Tempo estimado: 3-5 minutos
   - Acompanhe o status na aba "Logs"

6. **Acesse sua Aplicação**
   - URL: `https://huggingface.co/spaces/SEU-USUARIO/briefing-castor`

### Opção 2: Via Git (Avançado)

```bash
# Clone seu Space
git clone https://huggingface.co/spaces/SEU-USUARIO/briefing-castor
cd briefing-castor

# Copie os arquivos do projeto
cp /caminho/do/projeto/* .

# Commit e push
git add .
git commit -m "Initial commit"
git push
```

## 🔧 Troubleshooting

### Build Falhou
- Verifique os logs na aba "Logs" do Space
- Confirme que todos os arquivos foram uploadados
- Teste localmente com `docker build -t briefing-castor .`

### Aplicação não inicia
- Verifique se as variáveis de ambiente estão configuradas
- Confira os logs de runtime na aba "Logs"
- Teste as APIs separadamente

### Erro de Permissão
- Certifique-se de que o Space está como Public
- Verifique se as chaves de API são válidas

## 💡 Dicas

- O plano gratuito oferece CPU básico (suficiente para esta aplicação)
- Para mais performance, considere upgrade para GPU
- Mantenha as chaves de API em segredo (nunca commit no git)
- Use a aba "Logs" para debug em tempo real

## 📊 Recursos do Plano Gratuito

- **CPU**: 2 vCPU
- **RAM**: 16GB
- **Storage**: 8GB
- **Uptime**: Sempre ativo (não entra em sleep)
- **HTTPS**: Incluído automaticamente

## 🎉 Pronto!

Sua aplicação está rodando gratuitamente no Hugging Face Spaces!
Compartilhe o link com seus clientes e equipe.
