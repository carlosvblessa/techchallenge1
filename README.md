
# Tech Challenge 1 - API Embrapa

API desenvolvida com FastAPI para consultar dados públicos de vitivinicultura da Embrapa. Esta API servirá como base de ingestão de dados para um futuro modelo de Machine Learning.

O projeto está disponibilizado no Render através do endereço: https://tech-challenge1-kqz9.onrender.com/docs/

## Estrutura do projeto

```

techchallenge1/
├── app
│   ├── analytics.py                  # Endpoints para análises futuras (ex: previsão, tendências)
│   ├── auth.py                       # Gerenciamento de autenticação de usuários
│   ├── auth_token.py                 # Validação de tokens JWT para proteger endpoints
│   ├── config.py                     # Configurações globais da aplicação (secret key, expiração, etc.)
│   ├── database.py                   # Inicialização do SQLAlchemy e conexão com SQLite
│   ├── __init__.py                   # Inicializador do pacote
│   ├── models.py                     # Modelos de dados SQLAlchemy (produção, comercialização, etc.)
│   ├── models_usuario.py             # Modelo de dados SQLAlchemy específico para usuários
│   ├── routes.py                     # Organização principal dos endpoints e routers, inclui os endpoints analíticos
│   ├── scraper_import_export.py      # Scraper específico para importações e exportações
│   ├── scraper.py                    # Scraper principal para produção, comercialização, processamento
│   └── utils.py                      # Funções auxiliares como criação e validação de tokens JWT
├── dados_embrapa.db                  # Base de dados SQLite com os dados coletados
├── LICENSE                           # Licença do projeto (MIT)
├── main.py                           # Comandos de inicialização do projeto
├── render.yaml                       # Parâmetros de inicialização para o render
├── README.md                         # Instruções do projeto
├── LICENSE                           # MIT license
├── requirements.txt                  # Dependências do projeto
└── .gitignore                        # Ignora arquivos desnecessários

```


## 🧭 Plano Arquitetural do Projeto

Este projeto foi estruturado com foco em modularidade, escalabilidade e segurança no consumo de dados públicos do setor vitivinícola.

### 🔁 Fluxo geral de dados

```
     [ Portal Embrapa ]
           |
           v
  (1) Scraping com BeautifulSoup + requests
           |
           v
  (2) Transformação com pandas
           |
           v
  (3) Persistência com SQLAlchemy (SQLite)
           |
           v
  (4) API RESTful com FastAPI
           |
           v
  (5) Acesso com autenticação via JWT + aprovação por admin
```


---

### 🚀 Endpoints atuais

| Método | Rota                          | Descrição                                                       |
|:-------|:------------------------------|:----------------------------------------------------------------|
| **GET**    | `/`                          | Página inicial em HTML                                          |
| **GET**    | `/health`                    | Health-check da API e do banco                                  |
| **GET**    | `/producao`                  | Extrai dados de produção 🔒                                      |
| **GET**    | `/comercializacao`           | Extrai dados de comercialização 🔒                               |
| **GET**    | `/processamento`             | Extrai dados de processamento 🔒                                 |
| **GET**    | `/importacao`                | Extrai dados de importação 🔒                                   |
| **GET**    | `/exportacao`                | Extrai dados de exportação 🔒                                   |
| **POST**   | `/solicitar-acesso`          | Solicita cadastro de novo usuário                               |
| **POST**   | `/avaliar-acesso`            | Admin: aprova ou rejeita solicitação de acesso                  |
| **POST**   | `/status-acesso`             | Verifica status da solicitação de acesso                        |
| **POST**   | `/solicitacoes-pendentes`    | Admin: lista todos os pedidos de acesso ainda não avaliados     |

---

---

### 🔐 Segurança

- Acesso controlado com fluxo de aprovação
- Tokens JWT com expiração automática
- Proteção de todos os endpoints via `Depends(get_current_user)`

---

## 🧱 Estrutura das Tabelas

Abaixo estão os principais modelos de dados utilizados no banco (via SQLAlchemy), com suas respectivas funções e campos:

---

### 📦 `producao`
Armazena dados históricos de produção de uvas por tipo de produto e ano.

| Campo              | Tipo     | Descrição                            |
|--------------------|----------|----------------------------------------|
| `id`               | Integer  | Identificador único (autoincremento)  |
| `id_original`      | Integer  | ID da fonte original do dado          |
| `control`          | String   | Identificador de controle da Embrapa  |
| `produto`          | String   | Tipo de produto vitivinícola          |
| `ano`              | Integer  | Ano da produção                       |
| `producao_toneladas` | Float | Quantidade produzida em toneladas     |

🔐 Restrição: cada `(id_original, ano)` deve ser único.

---

### 💼 `comercializacao`
Registra o volume de comercialização dos produtos vitivinícolas por ano.

| Campo                  | Tipo     | Descrição                             |
|------------------------|----------|-----------------------------------------|
| `id`                   | Integer  | Identificador único                    |
| `id_original`          | Integer  | ID da fonte original                   |
| `control`              | String   | Código de controle                     |
| `produto`              | String   | Tipo de produto                        |
| `ano`                  | Integer  | Ano da comercialização                 |
| `volume_comercializado`| Float    | Volume comercializado (litros/toneladas) |

🔐 Restrição: cada `(id_original, ano)` deve ser único.

---

### 🏭 `processamento`
Registra o volume de uvas processadas por cultivar e ano.

| Campo                    | Tipo     | Descrição                             |
|--------------------------|----------|-----------------------------------------|
| `id`                     | Integer  | Identificador único                    |
| `id_original`            | Integer  | ID da fonte original                   |
| `control`                | String   | Código de controle                     |
| `cultivar`               | String   | Tipo da uva                            |
| `ano`                    | Integer  | Ano do processamento                   |
| `volume_processado_litros` | Float  | Volume processado em litros            |

🔐 Restrição: cada `(id_original, ano)` deve ser único.

---

### 🌎 `importacao`
Contém dados de importação de vinhos por país e ano.

| Campo         | Tipo     | Descrição                              |
|---------------|----------|------------------------------------------|
| `id`          | Integer  | Identificador único                     |
| `pais`        | String   | Nome do país de origem                  |
| `ano`         | Integer  | Ano da importação                       |
| `quantidade`  | Float    | Quantidade importada                   |
| `valor_usd`   | Float    | Valor total em dólares                 |

🔐 Restrição: cada `(pais, ano)` deve ser único.

---

### 🌍 `exportacao`
Semelhante à `importacao`, mas referente às exportações por país e ano.

| Campo         | Tipo     | Descrição                              |
|---------------|----------|------------------------------------------|
| `id`          | Integer  | Identificador único                     |
| `pais`        | String   | Nome do país de destino                 |
| `ano`         | Integer  | Ano da exportação                       |
| `quantidade`  | Float    | Quantidade exportada                   |
| `valor_usd`   | Float    | Valor total em dólares                 |

🔐 Restrição: cada `(pais, ano)` deve ser único.

---

### 👤 `usuarios`
Controla os acessos à API via autenticação com aprovação por administrador.

| Campo          | Tipo     | Descrição                              |
|----------------|----------|------------------------------------------|
| `id`           | Integer  | Identificador único                    |
| `username`     | String   | Nome do usuário                        |
| `senha`        | String   | Senha do usuário                       |
| `status`       | String   | `pendente`, `aprovado` ou `rejeitado` |
| `ultimo_token` | String   | Último token gerado (JWT)              |
| `data_token`   | DateTime | Data da última geração de token        |


---

### 🔮 Escalabilidade futura

- Já estruturado para receber modelos de previsão (ML)
- Modularidade para substituição de SQLite por PostgreSQL
- Suporte a deploy em nuvem com Docker ou Vercel


## 🔮 Funcionalidades futuras planejadas

A API está estruturada para expansão futura com inteligência analítica, incluindo:

| Endpoint                                       | Descrição                                                                 |
|------------------------------------------------|---------------------------------------------------------------------------|
| `/analytics/producao/previsao`                | Previsão da produção de uvas com base em séries históricas               |
| `/analytics/exportacao/tendencias`            | Análise de tendências de exportação por país                             |
| `/analytics/comercializacao/ranking-regioes`  | Classificação de regiões por volume de comercialização                   |
| `/analytics/importacao/alerta-estoque`        | Recomendação de ajuste de estoque com base na previsão de importação     |

Esses endpoints estão documentados e estruturados, prontos para integração com modelos de machine learning ou algoritmos estatísticos conforme evolução do projeto.


---

## Pré-requisitos
Para rodar esta API localmente, você precisará dos seguintes itens instalados:
- Python 3.x
- Dependências listadas no arquivo `requirements.txt`

---

## Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/carlosvblessa/techchallenge1.git
   cd techchallenge1
   ```

2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a API:
   ```bash
   gunicorn main:app --reload -k uvicorn.workers.UvicornWorker -b 127.0.0.1:10000
   ```

5. Verifique o status:
   ```bash
   curl http://127.0.0.1:10000/health
   ```

6. Acesse a documentação Swagger ou Redoc:
   ```bash
   http://127.0.0.1:10000/docs
   http://127.0.0.1:10000/redoc
   ```

A API estará disponível em `http://127.0.0.1:10000`.

---

## Uso
- Para testar a API, você pode usar ferramentas como [Postman](https://www.postman.com/) ou [cURL](https://curl.se/) ou ainda em http://127.0.0.1:10000/docs.

---

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE).
