from flask import Flask, render_template, request, jsonify, redirect, url_for
import google.generativeai as genai
from weasyprint import HTML
import os
import webbrowser
from agents.agent_buscador import AgenteBuscadorDeVagas
from dotenv import load_dotenv

load_dotenv()

agente_buscador = AgenteBuscadorDeVagas()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

app = Flask(__name__)

# Variável global para armazenar as informações do usuário e histórico do chat (para uma única interação)
user_data = {'historico_chat': []}
MAX_INTERACTIONS_ENTREVISTA = 5
FIM_BUSCA_VAGAS = False # Flag para indicar se a busca de vagas já ocorreu

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/iniciar_processo', methods=['POST'])
def iniciar_processo():
    if request.method == 'POST':
        user_data['nome'] = request.form['nome']
        user_data['email'] = request.form['email']
        user_data['objetivo'] = request.form['objetivo']
        user_data['link1'] = request.form['link1']
        user_data['link2'] = request.form['link2']
        user_data['link3'] = request.form['link3']
        user_data['experiencia'] = request.form['experiencia']
        user_data['formacao'] = request.form['formacao']
        user_data['habilidades'] = request.form['habilidades']
        user_data['historico_chat'] = []
        global FIM_BUSCA_VAGAS
        FIM_BUSCA_VAGAS = False # Reinicia a flag para uma nova interação

        print("Informações do Usuário Recebidas:")
        for key, value in user_data.items():
            print(f"{key}: {value}")

        initial_prompt_agente1 = f"""Você é o Agente 1, um entrevistador amigável e perspicaz.
        Seu objetivo é coletar informações detalhadas do usuário para a criação de um currículo eficaz.
        Baseie-se nas informações iniciais fornecidas:
        Nome do entrevistado: {user_data['nome']}
        Objetivo: {user_data['objetivo']}
        Experiência: {user_data['experiencia']}
        Formação Acadêmica: {user_data['formacao']}
        Habilidades: {user_data['habilidades']}

        Faça a primeira pergunta para entender melhor o histórico profissional e as aspirações do usuário em relação ao objetivo declarado.
        Mantenha as perguntas concisas, relevantes e sucintas. Fale de forma simples, curta e objetiva.
        Não retorne nada em negrito ou itálico.
        Tenha em mente que as informações tiradas será usadas para criar um currículo posteriormente, e ele terá seções como Informações Pessoais, Objetivo, Experiência Profissional, Habilidades e Formação Acadêmica, com base nas informações fornecidas.
        """

        try:
            response = model.generate_content(initial_prompt_agente1)
            first_question = response.text
            user_data['historico_chat'].append({'role': 'chatbot', 'content': first_question})
            return redirect(url_for('chat'))
        except Exception as e:
            print(f"Erro ao gerar a primeira pergunta (Agente 1): {e}")
            return jsonify({'error': 'Ocorreu um erro ao iniciar a entrevista.'}), 500
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    first_question = ""
    if user_data.get('historico_chat'):
        first_question = user_data['historico_chat'][0].get('content', '')
    return render_template('chat.html', first_question=first_question)

@app.route('/enviar_mensagem', methods=['POST'])
def enviar_mensagem():
    data = request.get_json()
    user_message = data['message']

    user_data['historico_chat'].append({'role': 'user', 'content': user_message})
    global FIM_BUSCA_VAGAS

    if not FIM_BUSCA_VAGAS:
        if len(user_data['historico_chat']) // 2 >= MAX_INTERACTIONS_ENTREVISTA:
            print("Fim da entrevista (Agente 1). Iniciando Agente 2 (Designer de Currículo HTML)...")
            prompt_agente2 = f"""Você é o Agente 2, um designer de currículos profissional especializado em HTML e CSS.
            Com base na seguinte conversa com o usuário, gere um currículo formatado em HTML e CSS embutido.
            Considere o objetivo profissional do usuário: {user_data['objetivo']}.
            Utilize também as seguintes informações do usuário: 
            Aqui estão as informações coletadas no formulário inicial:
            Nome do entrevistado: {user_data['nome']}
            Objetivo: {user_data['objetivo']}
            Experiência: {user_data['experiencia']}
            Habilidades: {user_data['habilidades']}
            Formação acadêmica: {user_data['formacao']}
            Links: {user_data['link1']} | {user_data['link2']} | {user_data['link3']}
            Email: {user_data['email']}
            """
            for msg in user_data['historico_chat']:
                prompt_agente2 += f"{msg['role']}: {msg['content']}\n"

            prompt_agente2 += "\nCrie um documento HTML completo com estilos CSS embutidos para apresentar o currículo de forma profissional e organizada levando em consideração que terá outro script a parte que pegara esse HTML e irá transformar em um PDF, então formate de acordo. Retorne APENAS o código e de forma textual, sem ser bloco de código. Inclua seções como Informações Pessoais, Objetivo, Experiência Profissional, Habilidades e Formação Acadêmica, com base nas informações fornecidas."

            try:
                response_agente2 = model.generate_content(prompt_agente2)
                html_curriculo = response_agente2.text
                return jsonify({'response': 'Currículo em HTML gerado. Iniciando geração de PDF...', 'next_step': 'gerando_pdf', 'html_curriculo': html_curriculo})
            except Exception as e:
                print(f"Erro ao gerar currículo HTML (Agente 2): {e}")
                return jsonify({'error': 'Ocorreu um erro ao gerar o currículo em HTML.'}), 500
        else:
            prompt_agente1_continuacao = f"""Você é o Agente 1, um entrevistador amigável e perspicaz.
            Continue a entrevista com o usuário para coletar informações detalhadas para a criação do currículo.
            Mantenha as perguntas concisas, relevantes e sucintas. Fale de forma simples, curta e objetiva.
            Não retorne nada em negrito ou itálico.
            Tenha em mente que as informações tiradas será usadas para criar um currículo posteriormente, e ele terá seções como Informações Pessoais, Objetivo, Experiência Profissional, Habilidades e Formação Acadêmica, com base nas informações fornecidas.
            Você podera fazer {MAX_INTERACTIONS_ENTREVISTA - len(user_data['historico_chat']) // 2} perguntas depois dessa.
            Mantenha o histórico da conversa em mente:
            """
            for msg in user_data['historico_chat']:
                prompt_agente1_continuacao += f"{msg['role']}: {msg['content']}\n"

            prompt_agente1_continuacao += "Faça a próxima pergunta relevante para entender melhor o perfil do usuário para o objetivo profissional dele."

            try:
                response = model.generate_content(prompt_agente1_continuacao)
                chatbot_response = response.text
                user_data['historico_chat'].append({'role': 'chatbot', 'content': chatbot_response})
                return jsonify({'response': chatbot_response})
            except Exception as e:
                print(f"Erro ao gerar resposta (Agente 1): {e}")
                return jsonify({'error': 'Ocorreu um erro ao obter a resposta.'}), 500
    else:
        # Agente de suporte e dúvidas
        prompt_suporte = f"""Você é um assistente de empregabilidade. O usuário já passou pela entrevista e recebeu sugestões de vagas.
        Agora, responda às perguntas do usuário, ofereça dicas sobre entrevistas, carreira e qualquer outra dúvida que ele possa ter.
        Mantenha um tom amigável e informativo. Responda de forma sucinta, objetiva e curta. Não coloque nada em Negrito ou Italico. Pode manter os emojis.
        Aqui estão as informações coletadas no formulário inicial, caso precise:
        Nome do entrevistado: {user_data['nome']}
        Objetivo: {user_data['objetivo']}
        Experiência: {user_data['experiencia']}
        Habilidades: {user_data['habilidades']}
        Formação acadêmica: {user_data['formacao']}
        Histórico da conversa:
        """
        for msg in user_data['historico_chat']:
            prompt_suporte += f"{msg['role']}: {msg['content']}\n"
        prompt_suporte += f"Pergunta do usuário: {user_message}"

        try:
            response_suporte = model.generate_content(prompt_suporte)
            resposta_suporte = response_suporte.text
            user_data['historico_chat'].append({'role': 'chatbot', 'content': resposta_suporte})
            return jsonify({'response': resposta_suporte})
        except Exception as e:
            print(f"Erro no agente de suporte: {e}")
            return jsonify({'error': 'Ocorreu um erro ao processar sua pergunta.'}), 500

@app.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    data = request.get_json()
    html_gerado = data.get('html_curriculo', '')

    if html_gerado:
        try:
            pdf_filename = "curriculo.pdf"
            HTML(string=html_gerado).write_pdf(pdf_filename)
            print(f"PDF do currículo gerado com sucesso: {pdf_filename}")
            webbrowser.open_new(pdf_filename)
            return jsonify({'response': 'Currículo em PDF gerado e aberto com sucesso.', 'next_step': 'buscar_vagas'})
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return jsonify({'error': 'Ocorreu um erro ao gerar o PDF do currículo.'}), 500
    else:
        return jsonify({'error': 'HTML do currículo não fornecido para geração do PDF.'}), 400

@app.route('/buscar_vagas', methods=['POST'])
def buscar_vagas():
    dados_do_entrevistado = f"""
        'objetivo': {user_data['objetivo']},
        'experiencia': {user_data['experiencia']},
        'habilidades': {user_data['habilidades']},
        'Formação': {user_data['formacao']}
    """
    try:
        historico = []
        for msg in user_data['historico_chat']:
            historico += f"{msg['role']}: {msg['content']}\n"

        response_agente3 = agente_buscador.buscar_vagas(dados_do_entrevistado, historico)
        print(response_agente3)
        vagas_texto = response_agente3.strip().split('\n')
        print(vagas_texto)
        global FIM_BUSCA_VAGAS
        FIM_BUSCA_VAGAS = True

        pergunta_agente4 = "Você tem mais alguma dúvida que gostaria de esclarecer sobre o currículo, as vagas ou o processo de entrevistas?"

        mensagens_chatbot = []
        for vaga in vagas_texto:
            if ": " in vaga:
                titulo, link = vaga.split(": ", 1)
                link = link.replace("[", "").split("]")
                
                print("\n\nTitulo",titulo,"\n\nLink" ,link,"\n\n")
                mensagens_chatbot.append({'role': 'chatbot', 'content': f'<a href="{link[0]}" target="_blank">{titulo.strip()}</a>'})


        mensagens_chatbot.append({'role': 'chatbot', 'content': pergunta_agente4})

        return jsonify({'messages': mensagens_chatbot, 'next_step': 'continuar_conversa'})
    except Exception as e:
        print(f"Erro ao buscar vagas (Agente 3): {e}")
        return jsonify({'error': 'Ocorreu um erro ao buscar vagas de emprego.'}), 500


if __name__ == '__main__':
    app.run(debug=True)