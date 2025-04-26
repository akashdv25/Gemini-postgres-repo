const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');

function formatTimestamp(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

function addMessage(message, isUser, timestamp = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const messageContent = document.createElement('div');
    messageContent.textContent = message;
    messageDiv.appendChild(messageContent);

    if (timestamp) {
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-timestamp';
        timeDiv.textContent = formatTimestamp(timestamp);
        messageDiv.appendChild(timeDiv);
    }

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function loadChatHistory() {
    try {
        const response = await fetch('/api/chat-history');
        const data = await response.json();
        
        if (data.status === 'success') {
            // Clear existing messages
            chatBox.innerHTML = '';
            
            // Add messages in reverse order (oldest first)
            data.history.reverse().forEach(chat => {
                addMessage(chat.user_message, true, chat.timestamp);
                addMessage(chat.bot_response, false, chat.timestamp);
            });
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

async function handleUserMessage() {
    const message = userInput.value.trim();
    if (message === '') return;

    // Add user message to chat
    addMessage(message, true);
    userInput.value = '';

    try {
        // Show loading state
        sendButton.disabled = true;
        userInput.disabled = true;

        // Make API call to Flask backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Add bot response to chat with timestamp
        addMessage(data.response, false, data.timestamp);
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, something went wrong. Please try again.', false);
    } finally {
        // Reset loading state
        sendButton.disabled = false;
        userInput.disabled = false;
    }
}

sendButton.addEventListener('click', handleUserMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleUserMessage();
    }
});

// Load chat history when the page loads
document.addEventListener('DOMContentLoaded', loadChatHistory); 