# Squad-ai - Sistema de Recomendação de Desafios Fitness

Este projeto implementa um sistema de recomendação baseado em conteúdo para sugerir desafios fitness personalizados aos usuários com base em seus perfis e características dos desafios disponíveis.

## 🔧 Como Executar

---

1. Clone o repositório:

```bash
    git clone https://github.com/seu-usuario/Squad-ai.git
    cd Squad-ai
``` 

2. Crie e ative o ambiente virtual:
````
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
````

3. Instale as dependências:
````
pip install -r requirements.txt
````

4. Execução local

````
# backend;
uvicorn src.main:app --reload
````
````
# app;
streamlit run src/app.py
````
ou

````
# Docker build - (1 container com Supervisor)
docker build -t squad-app .
docker run -p 9000:8000 squad-app
````
````
# Docker-compose - (serviços separados)
docker-compose up --build
````

```
Documentação de endpoints
http://localhost:8000/docs
```
---
Nota de atualizações

05-08-2025
* adicionado documentação swagger de endpoints e schemas. (http://localhost:8000/docs)
---
## 📁 Estrutura do Projeto

```  Squad-ai/
    │
    ├── .venv/ # Ambiente virtual Python
    ├── dataframes/ # Contém os arquivos CSV com dados de entrada
    ├── recommendation_system/ # Módulo de recomendação
    │ ├── _tower_cliente.py # Geração de embeddings para usuários
    │ ├── _tower_model.py # Geração de embeddings para desafios
    │ ├── Content_Filter.py # Script principal de recomendação
    │ ├── Content_Filter.ipynb # Versão notebook do sistema de recomendação
    │ └── curatorship.py # Processamento e curadoria de dados
    ├── Readme.md # Este arquivo
```

| Tipo                              | Baseado em...                       | Exemplos de dados usados                    |
| --------------------------------- | ----------------------------------- | ------------------------------------------- |
| **Filtragem baseada em conteúdo** | Atributos do item e/ou do usuário   | Tipo, descrição, categoria, perfil          |
| **Filtragem colaborativa**        | Interações usuário-item (ex: notas) | Histórico de uso: avaliações, cliques, etc. |
| **Híbrido**                       | Combinação de ambos os métodos      | Atributos + histórico de interações         |


## 🚀 Funcionalidades

- Geração de embeddings vetoriais para usuários e desafios
- Normalização e redução de dimensionalidade via PCA
- Cálculo de similaridade do cosseno entre usuários e desafios
- Retorno dos desafios mais relevantes com base nas preferências estimadas do usuário
