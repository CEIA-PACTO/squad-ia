# 🎯 Squad IA - Sistema de Recomendação de Desafios Fitness

Sistema inteligente de recomendação de desafios fitness baseado no modelo HEXAD de gamificação, integrando dados do dataset Amnesia com algoritmos de similaridade.

## 🚀 Funcionalidades

### ✨ Sistema de Recomendação
- **Perfil HEXAD**: Análise completa dos 6 tipos de jogador
- **Personalização**: Recomendações baseadas em dados demográficos e fitness
- **Algoritmo**: Similaridade de cosseno com dataset de 100 usuários
- **Desafios**: 24 desafios categorizados por tipo HEXAD

### 🎮 Gamificação
- **6 Tipos HEXAD**: Philanthropist, Socialiser, Free Spirit, Achiever, Player, Disruptor
- **Scores Personalizados**: 0-7 para cada tipo de jogador
- **Desafios Alinhados**: Baseados nas preferências do usuário

### 📊 Sistema de Avaliação
- **Feedback Completo**: Sucesso, streak, progresso, rating, tempo
- **Histórico**: Armazenamento em CSV com rastreamento por usuário
- **Melhoria Contínua**: Dados para otimização do algoritmo

## 🏗️ Arquitetura

### Backend (FastAPI)
- **Porta**: 8000
- **APIs**: Recomendação e Avaliação
- **Dataset**: recommendation_dataset.csv (100 usuários)
- **Desafios**: challenges.json (24 desafios)

### Frontend (Streamlit)
- **Porta**: 8501
- **Interface**: Formulário de cadastro e visualização
- **Integração**: Comunicação com APIs FastAPI

## 📁 Estrutura do Projeto

```
squad-ia/
├── src/
│   ├── app.py                    # Interface Streamlit
│   ├── main.py                   # API FastAPI
│   ├── endpoint/
│   │   ├── formulario.py         # Modelos de dados
│   │   └── recomendador.py       # Lógica de recomendação
│   ├── page/
│   │   └── pages.py              # Páginas da interface
│   └── dataframe/
│       ├── recommendation_dataset.csv  # Dataset principal
│       └── challenges.json             # Desafios disponíveis
├── test_integration.py           # Script de teste
└── README.md                     # Documentação
```

## 🛠️ Instalação e Execução

### 1. Configurar Ambiente
```bash
# Ativar ambiente conda
conda activate ceia-pacto

# Instalar dependências
pip install fastapi uvicorn streamlit pandas scikit-learn requests
```

### 2. Executar Serviços
```bash
# Terminal 1: FastAPI (Backend)
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Streamlit (Frontend)
streamlit run src/app.py --server.port=8501
```

### 3. Acessar Sistema
- **Interface**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 🧪 Testes

Execute o script de teste para verificar a integração:
```bash
python test_integration.py
```

## 📊 Dataset

### recommendation_dataset.csv
- **100 usuários** com perfis HEXAD completos
- **Dados demográficos**: idade, altura, peso, sexo
- **Dados fitness**: objetivo, dias de treino, tempo, experiência
- **Scores HEXAD**: 6 scores (0-7) para cada tipo
- **Desafios recomendados**: Lista de desafios por usuário

### challenges.json
- **24 desafios** categorizados por tipo HEXAD
- **Metadados**: descrição, duração, sessões alvo
- **Dificuldade**: Variada para diferentes níveis

## 🔧 APIs

### POST /recomendar
```json
{
  "usuario": "string",
  "senha": "string",
  "age": 25,
  "height": 170,
  "weight": 70,
  "body_type": "Masculino",
  "goal": "Emagrecimento",
  "training_days": 3,
  "training_time": 60,
  "experience_level": "Iniciante",
  "score_philanthropist": 5.0,
  "score_socialiser": 4.0,
  "score_free_spirit": 3.0,
  "score_achiever": 6.0,
  "score_player": 4.5,
  "score_disruptor": 2.0
}
```

### POST /avaliar
```json
{
  "usuario": "string",
  "senha": "string",
  "success": 8,
  "streak": 5,
  "progress_pct": 75,
  "rating": 4,
  "time": 45
}
```

## 🎯 Algoritmo de Recomendação

1. **Normalização**: Dados numéricos padronizados
2. **Codificação**: Variáveis categóricas convertidas
3. **Similaridade**: Cálculo de similaridade de cosseno
4. **Seleção**: Top 3 usuários mais similares
5. **Recomendação**: Desafios dos usuários similares
6. **Fallback**: Desafios aleatórios se necessário

## 🔄 Fluxo do Usuário

1. **Login**: Cadastro de usuário e senha
2. **Perfil HEXAD**: Avaliação dos 6 tipos de jogador
3. **Dados Fitness**: Informações demográficas e objetivos
4. **Recomendação**: Recebimento de desafios personalizados
5. **Avaliação**: Feedback sobre os desafios realizados

## 📈 Melhorias Futuras

- [ ] Interface mais moderna e responsiva
- [ ] Sistema de badges e conquistas
- [ ] Recomendações em tempo real
- [ ] Análise de progresso e tendências
- [ ] Integração com wearables
- [ ] Machine Learning avançado

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Equipe

- **Squad IA** - Desenvolvimento e implementação
- **CEIA-PACTO** - Coordenação e supervisão

---

**🎯 Transformando fitness em gamificação inteligente!**
