# Microsoft Teams Bot Integration with LLMs

This repository demonstrates the integration of Large Language Models (LLMs) with Microsoft Teams to build an intelligent virtual assistant. The bot is designed to answer employee queries about company policies, reducing the dependency on HR personnel or team leads.

![image](https://github.com/user-attachments/assets/3b44ea74-7729-4566-b79d-c94f6bc17b56)
![image](https://github.com/user-attachments/assets/a7717edb-1ad4-4672-83bb-c272400cbc51)


---

## 🔧 Setup Steps

### 1. **Deploy a Publicly Accessible Backend App**

To integrate with Microsoft Teams, you need a backend server that is accessible over HTTPS and can accept POST requests from Teams.

- You can use any backend framework. In this project, I’ve used **Python Flask**.
- For development and testing, I used **[ngrok](https://ngrok.com/)** to expose my local Flask app to the internet.
  - This allows routing local traffic (e.g., `localhost:5000`) to a public ngrok URL.
  - **Note:** ngrok is suitable for development only and **not recommended** for production deployments.

---

### 2. **Integrate the Backend App with Microsoft Teams**

#### ✅ Create a Bot in Teams

Once your backend is publicly accessible:

1. Go to **Teams > Manage Team > Apps**.
2. Click **Create an outgoing webhook**.
3. Fill in the following:
   - **Bot Name**
   - **Callback URL** → your backend webhook endpoint (e.g., `https://<ngrok-id>.ngrok.io/webhook`)
   - **Description**
   - **Profile Picture** (optional)
4. After creation, Teams will provide a **Security Token** – save this securely, as you'll need it in your backend.


#### 🔐 Secure the Endpoint (HMAC Verification)

To ensure the bot only accepts requests from Microsoft Teams:

- Microsoft Teams includes a header:


- In your Flask app, implement an HMAC-based authentication mechanism.
- This will compare the request body against the HMAC signature using the security token.
- See the `verify_hmac()` function in `app.py` for the implementation.

---

### 3. **Test the Bot Integration**

- Create a channel inside the same team where the webhook is registered.
- Mention your bot (e.g., `@AgentRouterBot`) and post a message.
- Your backend should log and process the request if the integration is successful.

💡 **Tip:** Add logging inside your Flask route to verify message receipt and authentication.

---

### 4. **Integrate Large Language Models**

Once integration is complete, you can plug in any LLM for advanced functionality.

- This project uses:
- **OpenAI SDK** for agent logic and tools
- **Gemini (free API key)** for LLM responses

#### 🧠 Agent Setup

- I created two specialized tools:
- `HRAgent`
- `PayrollAgent`
- A master agent dynamically chooses the correct tool based on the user's question to provide accurate responses.

---

## 🚀 Future Scope

Now that the Teams bot integration is complete, you can:
- Add more LLM tools (e.g., IT support, travel policy).
- Connect to internal company databases or APIs.
- Enhance response formatting and UI in Teams.
- If user question cannot be answered by agent, create a handoff that sends a email/push notification to the respective team for the query.

## ENV File

ENV File should contain the following

GEMINI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_API_KEY='<your gemini api key>'
SECURITY_TOKEN='<your micrsoft bot token>'
