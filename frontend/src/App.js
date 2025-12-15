// frontend/src/App.js
import React, { useState } from 'react';
import axios from 'axios';
 

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! Welcome to My Xerox Shop. How many pages do you need to print?" }
  ]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // 1. Add User Message to Chat
    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    
    const currentInput = input;
    setInput(""); // Clear input box

    try {
      // 2. Send to Python Backend
      const response = await axios.post("http://localhost:8000/chat", {
        message: currentInput
      });

      // 3. Add AI Response to Chat
      const botMessage = { sender: "bot", text: response.data.reply };
      setMessages((prev) => [...prev, botMessage]);

    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [...prev, { sender: "bot", text: "Sorry, I am having trouble connecting to the shop server." }]);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "50px auto", border: "1px solid #ddd", borderRadius: "10px", padding: "20px" }}>
      <h2>🖨️ Shop Assistant</h2>
      
      <div style={{ height: "400px", overflowY: "scroll", borderBottom: "1px solid #eee", marginBottom: "10px" }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ textAlign: msg.sender === "user" ? "right" : "left", margin: "10px" }}>
            <span style={{ 
              background: msg.sender === "user" ? "#007bff" : "#f1f1f1", 
              color: msg.sender === "user" ? "white" : "black",
              padding: "8px 15px", 
              borderRadius: "15px",
              display: "inline-block"
            }}>
              {msg.text}
            </span>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: "10px" }}>
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about printing prices..."
          style={{ flex: 1, padding: "10px" }}
        />
        <button onClick={sendMessage} style={{ padding: "10px 20px" }}>Send</button>
      </div>
    </div>
  );
}

export default App;