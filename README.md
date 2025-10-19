# Projeto Análise de CNPJ - Carolina Moraes

Este projeto realiza a **análise automatizada de empresas a partir do CNPJ**, integrando uma **interface Tkinter**, uma **API de consulta (CNPJA)** e **agentes inteligentes do framework CrewAI** para processar, organizar e exibir os resultados de forma clara e acessível.



## 💡 Visão Geral

O **Analisador de CNPJ** é uma ferramenta criada para automatizar a coleta e análise de informações de empresas registradas no Brasil.
Ele utiliza a **API CNPJA** para obter dados e emprega **agentes inteligentes (CrewAI)** para tratar e enriquecer as informações obtidas.

A aplicação possui uma interface gráfica simples desenvolvida com **Tkinter**, onde o usuário insere um CNPJ e recebe um relatório detalhado da empresa.

Documentação completa e DEMO: https://drive.google.com/drive/folders/1VbvpMHM_l2jTf77T-VMXbneZUxg5vrlO?usp=sharing



## 🧩 Arquitetura do Projeto

<img width="737" height="591" alt="Diagrama sem nome drawio (1)" src="https://github.com/user-attachments/assets/1a35c01a-06f2-4259-8855-b2292c305aa2" />


**Fluxo resumido:**

1. O usuário informa o CNPJ pela interface.
2. O sistema envia a requisição à **API CNPJA**.
3. Os **agentes CrewAI** processam as informações.
4. Os dados são organizados e exibidos de forma legível.



## ⚙️ Tecnologias Utilizadas

* **Python >=3.10 and <3.14**
* **Tkinter** → Interface gráfica
* **Requests** → Requisições à API CNPJA
* **CrewAI** → Criação e orquestração de agentes de IA
* **dotenv** → Gerenciamento de variáveis de ambiente



## 🚀 Instalação e Configuração

### 1. Clone o repositório

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte formato (Chave OPENAI: https://platform.openai.com/docs/overview):

```env
OPENAI_API_KEY=sua_chave_aqui
```



## ▶️ Como Executar o Projeto

Após instalar as dependências e configurar o `.env`, execute o projeto com:

```bash
python main.py
```

A interface gráfica será aberta.
Basta inserir um **CNPJ válido** para iniciar a análise.


## 📁 Estrutura de Pastas

```
📦 analise-cnpj
├── 📄 main.py               # Arquivo principal (integra interface e lógica)
├── 📄 crew.py               # Configuração e execução dos agentes CrewAI
├── 📄 data.py               # Funções para buscar e processar dados da CNPJA API
├── 📄 .env                  # Variáveis de ambiente 
├── 📄 requirements.txt      # Dependências do projeto
└── 📄 README.md             # Este arquivo
```


## 🧪 Exemplo de Execução

1. Usuário abre o programa.
2. Digita o CNPJ: `12.345.678/0001-99`.
3. O sistema consulta a API e retorna informações como:

   * **Razão social**
   * **Endereço**
   * **Situação cadastral**
   * **CNAE principal e secundários**
   * **Data de abertura**
4. Os agentes da CrewAI analisam e formatam o resultado, exibindo-o na tela.



## 📜 Licença

Este projeto foi desenvolvido para o **Processo Seletivo - Analista de Inteligência Artificial Júnior (Multiagentes)**.  

É distribuído sob a licença **MIT**, permitindo que você use, modifique e distribua o código livremente.

---

**Desenvolvido por Carolina Moraes**
