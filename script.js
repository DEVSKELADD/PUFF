const home = document.getElementById('home');
const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const btnNew = document.getElementById('btn-new');
const logoLink = document.getElementById('logo-link');
const historyList = document.getElementById('history-list');

let messageCounter = 0;

userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

document.querySelectorAll('.suggestion-card').forEach(card => {
    card.addEventListener('click', () => {
        userInput.value = card.dataset.prompt;
        sendMessage();
    });
});

document.querySelectorAll('.pill').forEach(pill => {
    pill.addEventListener('click', () => {
        userInput.value = `Busco libros de la categoría: ${pill.dataset.cat}`;
        userInput.focus();
    });
});

btnNew.addEventListener('click', resetChat);
logoLink.addEventListener('click', (e) => {
    e.preventDefault();
    resetChat();
});

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    if (sendBtn.disabled) return;

    if (home.style.display !== 'none') {
        home.style.display = 'none';
    }

    appendMessage('user', text);

    userInput.value = '';
    userInput.style.height = 'auto';

    sendBtn.disabled = true;
    userInput.disabled = true;

    const loadingId = appendMessage('ai', 'Pensando...');

    try {
        const response = await fetch('https://asistente-puff-edhgdxgegzeceygk.eastus2-01.azurewebsites.net/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();

        if (response.ok) {
            updateMessage(loadingId, data.reply);
            addToHistory(text);
        } else {
            updateMessage(loadingId, `Error: ${data.error}`);
        }

    } catch (error) {
        updateMessage(loadingId, 'Lo siento, no me pude conectar al servidor. Verifica que Flask esté corriendo.');
        console.error('Error de conexión:', error);
    } finally {
        sendBtn.disabled = false;
        userInput.disabled = false;
        userInput.focus();
    }
}

function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;

    const msgId = 'msg-' + (++messageCounter);
    msgDiv.id = msgId;

    msgDiv.innerHTML = text.replace(/\n/g, '<br>');

    messagesContainer.appendChild(msgDiv);
    const chatArea = document.getElementById('chat-area');
    chatArea.scrollTop = chatArea.scrollHeight;

    return msgId;
}

function updateMessage(id, newText) {
    const msgDiv = document.getElementById(id);
    if (msgDiv) {
        msgDiv.innerHTML = newText.replace(/\n/g, '<br>');
    }
}

function resetChat() {
    messagesContainer.innerHTML = '';
    home.style.display = 'flex';
    userInput.value = '';
    userInput.style.height = 'auto';
}

function addToHistory(text) {
    const excerpt = text.length > 25 ? text.substring(0, 25) + '...' : text;
    const historyItem = document.createElement('div');
    historyItem.className = 'history-item';
    historyItem.innerText = `${excerpt}`;

    historyList.prepend(historyItem);
}
