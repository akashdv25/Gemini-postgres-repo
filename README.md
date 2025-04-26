The flow of the program when a user hits the "send" button is as follows:

1.  **HTML and JavaScript Interaction**:
    

*   The index.html file contains the structure of the chat interface, including the "send" button and the text area for user input.
    
*   The script.js file handles the interaction with the "send" button. When the button is clicked, or the Enter key is pressed, the handleUserMessage function is triggered.
    

2.  **JavaScript Functionality**:
    

*   The handleUserMessage function in script.js retrieves the user's message from the input field.
    
*   It then disables the input field and the send button to prevent multiple submissions while processing.
    
*   The function makes an asynchronous POST request to the /api/chat endpoint on the server, sending the user's message as JSON.
    

3.  **Server-Side Processing**:
    

*   The server receives the request at the /api/chat endpoint. This is  handled by a Flask route in app.py.
    
*   The server processes the message,  using a chatbot 
    
*   The server sends back a JSON response containing the bot's reply and a timestamp.
    

4.  **Displaying the Response**:
    

*   Once the response is received, the handleUserMessage function updates the chat interface by adding the bot's response to the chat box.
    
*   The function also re-enables the input field and the send button, allowing the user to send another message.
    

This flow involves both client-side and server-side components, with the client-side handling user interactions and the server-side processing the chat logic.
