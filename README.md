# 📘 Libris – Sistema de Recomendação de Livros com IA

🚀 Aplicação desenvolvida em Python que utiliza integração com APIs, processamento de dados e técnicas de recomendação para sugerir livros personalizados com base nas preferências do usuário.

---

## 👨‍💻 Sobre o Projeto

Projeto desenvolvido com foco na construção de um sistema inteligente de recomendação, utilizando dados reais de APIs públicas e técnicas de análise de dados.

Responsável pela integração com APIs, processamento de dados e desenvolvimento da lógica de recomendação.

---

## 🎯 Objetivo

Criar um sistema capaz de recomendar livros de forma personalizada com base em:
- Preferências do usuário  
- Histórico de busca  
- Similaridade entre livros  

---

## 🧠 Problema e Solução

### ❌ Problema
Dificuldade em encontrar livros relevantes diante de muitas opções disponíveis.

### ✅ Solução
Sistema de recomendação que analisa dados de livros e gera sugestões personalizadas de forma automatizada.

---

## ⚙️ Funcionalidades

- 🔎 Busca de livros por nome
- 🌐 Integração com APIs externas (Google Books e Open Library)
- 🧠 Sistema de recomendação baseado em similaridade
- 📊 Manipulação e análise de dados
- 💾 Armazenamento de informações
- 🖥️ Interface interativa com Streamlit

---

## 🧠 Conceitos Aplicados

- Integração com APIs REST
- Manipulação de dados (pandas, numpy)
- Sistemas de recomendação
- Processamento de Linguagem Natural (NLP)
- Estruturas de dados
- Arquitetura modular

---

## 🧩 Desafios

- Trabalhar com dados inconsistentes de APIs externas
- Criar lógica de recomendação eficiente
- Processar e analisar grandes volumes de dados
- Integrar múltiplas bibliotecas de Machine Learning

---

## 🛠️ Tecnologias

- **Python 3**
- **Pandas / NumPy**
- **Scikit-learn**
- **Streamlit**
- **Requests**
- **NLTK / spaCy**
- **APIs REST (Google Books / Open Library)**

---

## 📁 Estrutura do Projeto

```bash
libris/
├── data/
├── notebooks/
├── src/
│   ├── api/
│   ├── model/
│   ├── nlp/
│   └── interface/
└── docs/
```

## 📦 requirements.txt

```txt
pandas
pymongo
numpy
scikit-learn
lightfm
surprise
requests
streamlit
matplotlib
spacy
nltk
transformers
```
---

🚀 Como Rodar o Projeto
1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/Libris--Recomendation-IA.git
cd libris
```
2. Crie o ambiente virtual
```bash
python3 -m venv libris-env
source libris-env/bin/activate
```
3. Instale as dependências
```bash
pip install -r requirements.txt
```
4. Configure o NLP
```bash
python -m nltk.downloader all
python -m spacy download pt_core_news_sm
```
5. Execute a interface
```bash
streamlit run src/interface/app.py
```
---

## 📊 Fluxo de Funcionamento

- Coleta de Dados – Scripts em src/api/ acessam APIs como Google Books e Open Library.

- Processamento – Dados são limpos e armazenados em data/.

- Treinamento do Modelo – Algoritmos em src/model/ geram recomendações.

- Análise de Texto – src/nlp/ processa sinopses e resenhas.

- Interface – src/interface/ exibe as recomendações ao usuário

---

## 💡 Diferencial

Este projeto demonstra na prática:

- Construção de aplicações com integração de APIs
- Desenvolvimento de sistemas de recomendação
- Manipulação e análise de dados
- Aplicação de conceitos de IA em um sistema real

---

## 👨‍💻 Autores

**Wallace lopes da silva e lucas basseto**
  
- LinkedIn: https://linkedin.com/in/lucasrodrigodev  
- LinkedIn: https://www.linkedin.com/in/wallace-lopes-3926aa343/
- GitHub: https://github.com/Bassetin
- GitHub: https://github.com/Gremoryxzz
---
