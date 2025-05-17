# Emprega.AI - Seu Assistente de Carreira com IA

[![Status do Projeto](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)](https://github.com/mathgoms02/EmpregaAI.git)

## Descrição

O VagaBot é um chatbot inteligente desenvolvido para auxiliar candidatos em todas as etapas da busca de emprego, desde a preparação do currículo até a procura por vagas e dicas para entrevistas. Utilizando o poder da IA do Google Gemini, o VagaBot oferece uma experiência personalizada e eficiente para otimizar sua jornada profissional.

## Funcionalidades

* **Entrevista Virtual:** O VagaBot realiza uma entrevista inicial para coletar informações detalhadas sobre sua experiência, habilidades e objetivos de carreira.
* **Currículo Inteligente:** Com base nas informações coletadas, o bot gera um currículo profissional em HTML, pronto para ser convertido em PDF.
* **Vagas Sob Medida:** Receba sugestões de vagas de emprego relevantes, de acordo com o seu perfil e preferências.
* **Suporte Profissional:** Tire suas dúvidas sobre o mercado de trabalho, processos seletivos e dicas de carreira.

## Tecnologias

* **Backend:** Flask (Python)
* **IA:** Google Gemini
* **Geração de PDF:** WeasyPrint
* **Frontend:** HTML, CSS, JavaScript

## Como Usar

1.  **Clone o Repositório:**

    ```bash
    git clone [https://github.com/seu-nome-de-usuario/nome-do-projeto.git](https://github.com/seu-nome-de-usuario/nome-do-projeto.git)
    cd nome-do-projeto
    ```

2.  **Configure o Ambiente:**

    * Crie um arquivo `.env` na raiz do projeto.
    * Adicione sua chave da API do Google Gemini ao arquivo `.env`:

        ```
        GOOGLE_API_KEY=SUA_CHAVE_API_GEMINI
        ```

3.  **Instale as Dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o Aplicativo:**

    ```bash
    python app.py
    ```

5.  **Acesse no Navegador:**

    * Abra seu navegador e acesse o endereço fornecido (geralmente `http://127.0.0.1:5000/`).

## Estrutura do Projeto

    EmpregaAI/
    ├── app.py          # Aplicativo principal Flask
    ├── agents/         # Agentes de IA
    │   └── agente_buscador.py
    ├── static/        # Arquivos estáticos (CSS, JS, imagens)
    │   ├── css/
    │   │   └── style.css
    │   ├── js/
    │   │   └── script.js
    ├── templates/     # Templates HTML
    │   ├── chat.html
    │   └── index.html
    ├── .env            # Configuração de variáveis de ambiente
    ├── requirements.txt # Lista de dependências
    └── README.md       # Este arquivo

## Contribuição

Contribuições são sempre bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.


## Autor

Matheus Filipe da Silva Gomes
