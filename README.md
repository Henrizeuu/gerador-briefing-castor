---
title: Briefing Castor - Scraper & Gerador de Briefing
emoji: 🦫
colorFrom: gray
colorTo: black
sdk: docker
pinned: false
license: mit
---

# Briefing Castor

Uma aplicação completa para extrair dados do Google Maps, gerar briefings profissionais com IA e fazer deploy automático de sites.

## Funcionalidades

- 🗺️ **Scraper Google Maps**: Busca avaliações, notas, fotos e informações de empresas
- 🤖 **IA Gemini**: Gera briefings completos e profissionais automaticamente
- 🚀 **Deploy Automático**: Publica sites no GitHub Pages com um clique
- 🎨 **Frontend Moderno**: Interface clean preto e branco profissional

## Como Usar

1. Configure suas chaves de API nas configurações do Space/Render:
   - `GEMINI_API_KEY`: Sua chave da API Google Gemini
   - `APIFY_API_TOKEN`: Seu token da Apify para scraping

2. Digite o termo de busca do Google Maps (ex: "Advogados") e a localização (ex: "São Paulo SP")

3. Clique em "Extrair Dados" para coletar as informações

4. Gere o briefing com IA ou faça deploy do site

## Tecnologias

- Python + Flask (Backend)
- HTML/CSS/JS (Frontend Profissional)
- Google Gemini (IA)
- Apify (Web Scraping)
- Docker/Gunicorn (Deploy)

## Deploy Gratuito

Esta aplicação pode ser deployada gratuitamente em:
- **Render.com** (Recomendado) - Veja `DEPLOY_RENDER.md`
- Hugging Face Spaces (SDK Docker)
- Fly.io
- Railway.app

## Links Úteis

- [Código Fonte](https://github.com/seu-usuario/briefing-castor)
- [Guia de Deploy Render](DEPLOY_RENDER.md)
