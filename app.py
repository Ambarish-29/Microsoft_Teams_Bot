from flask import Flask, request, jsonify, abort
import hmac
import hashlib
import base64
import re
import asyncio
from my_agents.router import AgentRouter
from dotenv import load_dotenv
import os
app = Flask(__name__)

load_dotenv()
SECURITY_TOKEN = os.getenv("SECURITY_TOKEN")


def verify_hmac(signature, body, secret_base64):
    if not signature or not signature.startswith("HMAC "):
        return False
    signature = signature[5:]  # Remove "HMAC " prefix

    try:
        signature_bytes = base64.b64decode(signature)
    except Exception as e:
        print("Failed to decode signature:", e)
        return False

    # Decode the secret from base64 to bytes
    secret_bytes = base64.b64decode(secret_base64)
    digest = hmac.new(secret_bytes, body, hashlib.sha256).digest()

    match = hmac.compare_digest(digest, signature_bytes)
    return match


agent_router = AgentRouter()



@app.route('/webhook', methods=['POST'])
def handle_webhook():
    auth_header = request.headers.get('Authorization')
    raw_body = request.get_data()
    if not verify_hmac(auth_header, raw_body, SECURITY_TOKEN):
        print("Unauthorized access")
        abort(401)
    data = request.json
    print("Received webhook data from Teams auth")
    user_text = data.get('text', 'dummy')
    question = user_text.split(' ', 1)[-1].strip()  # remove @BotName if mentioned
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(agent_router.route(question))
    print(result)
    return jsonify({"type": "message", "text": result})

if __name__ == '__main__':
    app.run(port=5000)