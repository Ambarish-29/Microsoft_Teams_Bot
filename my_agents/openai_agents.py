from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from my_agents.base import BaseAgent
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
import os
import asyncio
from dotenv import load_dotenv



class GeminiAgent(BaseAgent):
    def __init__(self, name, instructions, tool_description, vectorstore=None, model_name="gemini-2.0-flash"):
        self.name = name
        self.instructions = instructions
        self.tool_description = tool_description
        self.client = AsyncOpenAI(
            base_url=os.getenv("GEMINI_BASE_URL"),
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=self.client)
        self.vectorstore = vectorstore
        if self.vectorstore:
            print(f"[{self.name}] Retrieving docs")
            docs = list(self.vectorstore.docstore._dict.values())  # Get all stored documents
            context = "\n\n".join([doc.page_content for doc in docs])
            prompt = (
                f"You are bot with the following instructions: {self.instructions}\n\n"
                f"This is the Context from documents:\n{context}\n\n"
                f"Answer the question asked by the user based on the above context"
            )
        else:
            print(f"[{self.name}] No vectorstore, answering from instructions only.")
            prompt = f"{self.instructions}\n"
        print(f"Prompt: {prompt}")
        self.agent = Agent(
            name=self.name,
            instructions=prompt,
            model=self.model
        )
        self.agent_tool = self.agent.as_tool(tool_name=self.name, tool_description=self.tool_description)
        
    

    async def can_answer(self, question: str) -> bool:
        # For now: always try to answer — we'll refine in Step 6
        return True

    async def answer(self, question: str) -> str:
        if self.vectorstore:
            print(f"[{self.name}] Retrieving docs for question: {question}")
            # Retrieve top 3 relevant docs
            docs = self.vectorstore.similarity_search(question, k=3)
            context = "\n\n".join([doc.page_content for doc in docs])
            prompt = (
                f"{self.instructions}\n\n"
                f"Context from documents:\n{context}\n\n"
                f"Answer the question based on the above context:\n{question}"
            )
        else:
            print(f"[{self.name}] No vectorstore, answering from instructions only.")
            prompt = f"{self.instructions}\n\nUser question:\n{question}"

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]
