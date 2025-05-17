document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatLog = document.getElementById('chat-log');
    const inputArea = document.querySelector('.input-area');

    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(`${sender}-message`);
        messageDiv.innerHTML = text; // Usar innerHTML para renderizar links
        chatLog.appendChild(messageDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            appendMessage('user', message);
            userInput.value = '';

            fetch('/enviar_mensagem', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 'message': message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.response) {
                    appendMessage('chatbot', data.response);
                    if (data.next_step === 'gerando_pdf') {
                        userInput.disabled = true;
                        sendButton.disabled = true;
                        userInput.placeholder = 'Gerando currículo em PDF... aguarde.';
                        fetch('/gerar_pdf', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ 'html_curriculo': data.html_curriculo })
                        })
                        .then(response => response.json())
                        .then(pdf_data => {
                            if (pdf_data.response && pdf_data.next_step === 'buscar_vagas') {
                                appendMessage('chatbot', pdf_data.response);
                                fetch('/buscar_vagas', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    }
                                })
                                .then(response => response.json())
                                .then(vagas_data => {
                                    if (vagas_data.messages) {
                                        vagas_data.messages.forEach(msg => {
                                            appendMessage(msg.role, msg.content);
                                        });
                                        userInput.disabled = false;
                                        sendButton.disabled = false;
                                        userInput.placeholder = 'Digite sua mensagem...';
                                    } else if (vagas_data.error) {
                                        appendMessage('chatbot', vagas_data.error);
                                        userInput.disabled = false;
                                        sendButton.disabled = false;
                                        userInput.placeholder = 'Digite sua mensagem...';
                                    } else if (vagas_data.response) { // Fallback para resposta de texto única
                                        appendMessage('chatbot', vagas_data.response);
                                        userInput.disabled = false;
                                        sendButton.disabled = false;
                                        userInput.placeholder = 'Digite sua mensagem...';
                                    }
                                })
                                .catch(error => {
                                    console.error('Erro ao buscar vagas:', error);
                                    appendMessage('chatbot', 'Erro ao buscar vagas de emprego.');
                                    userInput.disabled = false;
                                    sendButton.disabled = false;
                                    userInput.placeholder = 'Digite sua mensagem...';
                                });
                            } else if (pdf_data.error) {
                                appendMessage('chatbot', pdf_data.error);
                                userInput.disabled = false;
                                sendButton.disabled = false;
                                userInput.placeholder = 'Digite sua mensagem...';
                            }
                        })
                        .catch(error => {
                            console.error('Erro ao gerar PDF:', error);
                            appendMessage('chatbot', 'Erro ao gerar o PDF do currículo.');
                            userInput.disabled = false;
                            sendButton.disabled = false;
                            userInput.placeholder = 'Digite sua mensagem...';
                        });
                    } else if (data.next_step === 'continuar_conversa') {
                        userInput.disabled = false;
                        sendButton.disabled = false;
                        userInput.placeholder = 'Digite sua mensagem...';
                    }
                } else if (data.error) {
                    appendMessage('chatbot', data.error);
                }
            })
            .catch(error => {
                console.error('Erro ao enviar mensagem:', error);
                appendMessage('chatbot', 'Erro ao enviar a mensagem.');
            });
        }
    }

    // Variável global para armazenar o histórico do chat no frontend
    const user_data = { historico_chat: [] };

    // Adicionar a primeira mensagem do chatbot ao histórico
    const firstChatMessage = document.querySelector('.chatbot-message');
    if (firstChatMessage) {
        user_data.historico_chat.push({ role: 'chatbot', content: firstChatMessage.textContent });
    }

    // Capturar as mensagens do usuário para o histórico
    const originalSendMessage = sendMessage;
    sendMessage = function() {
        const message = userInput.value.trim();
        if (message) {
            user_data.historico_chat.push({ role: 'user', content: message });
        }
        originalSendMessage();
    };
});