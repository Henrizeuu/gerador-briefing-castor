# Gerador de Briefing com IA

Aplicação web para extrair avaliações do Google Maps e gerar briefings profissionais usando IA.

## Funcionalidades

- 🕵️ Extração de avaliações do Google Maps via Apify
- 🤖 Análise de sentimentos e geração de briefing com Google Gemini
- 🎨 Interface moderna e responsiva em preto e branco
- 📱 Totalmente compatível com dispositivos móveis

## Deploy no Hugging Face Spaces

### Passo 1: Criar um novo Space
1. Acesse https://huggingface.co/spaces
2. Clique em "Create new Space"
3. Escolha um nome (ex: `seu-usuario/gerador-briefing`)
4. Selecione **Docker** como SDK
5. Escolha o plano **Free** (CPU básico)
6. Clique em "Create Space"

### Passo 2: Configurar o Space
No seu novo Space, crie os seguintes arquivos:

#### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

#### requirements.txt
```
flask
flask-cors
requests
google-generativeai
pydantic
gunicorn
```

#### app.py
(Copie o conteúdo do app.py deste repositório)

#### index.html
(Copie o conteúdo do index.html deste repositório)

### Passo 3: Configurar Variáveis de Ambiente
No seu Space, vá em "Settings" > "Variables" e adicione:
- `GEMINI_API_KEY`: Sua chave da API do Google Gemini
- `APIFY_API_TOKEN`: Seu token da API da Apify

### Passo 4: Aguardar o Deploy
O Hugging Face irá automaticamente construir e deployar sua aplicação. Isso leva cerca de 2-5 minutos.

## Uso Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export GEMINI_API_KEY="sua-chave-gemini"
export APIFY_API_TOKEN="seu-token-apify"

# Rodar a aplicação
python app.py
```

Acesse http://localhost:8080

## Estrutura dos Arquivos

- `app.py` - Backend Flask com APIs de scraping e análise
- `index.html` - Frontend HTML/CSS/JS
- `requirements.txt` - Dependências Python
- `Dockerfile` - Configuração para deploy no Hugging Face
- `README.md` - Este arquivo

## Licença

MIT
