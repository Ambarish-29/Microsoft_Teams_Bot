from my_agents.openai_agents import GeminiAgent
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from openai import AsyncOpenAI
import os

class AgentRouter:
    def __init__(self):
        # Load vectorstores once
        print("[AgentRouter] Loading vectorstores once at startup...")
        hr_vectorstore = FAISS.load_local("vectorstores/hr_bot", 
                                          SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2"),
                                          allow_dangerous_deserialization=True)
        team_vectorstore = FAISS.load_local("vectorstores/team_help_bot", 
                                            SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2"),
                                            allow_dangerous_deserialization=True)
        print("[AgentRouter] Loading vectorstores done at startup...")
        self.agents = [
            GeminiAgent(
                name="Payroll_and_Meeting_Bot",
                instructions="You are a helpful assistant for payroll and meeting related questions.",
                tool_description="Answers Internal Team related queries",
                vectorstore=team_vectorstore,  # local FAISS index folder
                model_name="gemini-2.0-flash"
            ),
            GeminiAgent(
                name="HRBot",
                instructions="You answer only HR and leave-related queries. Say you don't know for anything else.",
                tool_description="Answers HR and leave related queries",
                vectorstore=hr_vectorstore,
                model_name="gemini-2.0-flash"
            )
        ]

        self.tools = [agent.agent_tool for agent in self.agents]
        print(f"Tools Provided: {self.tools}")
        self.main_agent_instructions = f"""
        You are a helpful assistant for get answers to your work-related queries.
        if anything related to payroll or meeeting user asked, you should route to the "Payroll_and_Meeting_Bot" tool.
        if anything related to hr or leave user asked, you should route to the "HRBot" tool.
        You never solve queries on your own, you always route to the appropriate tools only.
        You should not give any other information than the answer to the user.
        """
        self.gemini_client = AsyncOpenAI(
            base_url=os.getenv("GEMINI_BASE_URL"),
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=self.gemini_client)
        

        self.main_agent = Agent(
            name="QueryMate Agent",
            instructions=self.main_agent_instructions,
            tools=self.tools,
            model=self.gemini_model
        )

        self.openai_agent = Agent(
            name="WorkBot Agent",
            instructions=self.main_agent_instructions,
            tools=self.tools,
            model="gpt-4o-mini"
        )
        

    async def route(self, question: str) -> str:
        try:
            result = await Runner.run(self.main_agent, question)
            return result.final_output
        except Exception as e:
            print(f"[AgentRouter] Error: {e}")
            return "Sorry, something went wrong while trying to answer your question."
