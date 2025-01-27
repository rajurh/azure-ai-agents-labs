import os
import logging
import asyncio
from dotenv import load_dotenv
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.kernel import Kernel
from agents.report_agent import ReportAgent
from agents.search_agent import SearchAgent

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


deployment_name = os.getenv("AZURE_AI_DEPLOYMENT_NAME")
endpoint = os.getenv("AZURE_AI_INFERENCE_ENDPOINT")
api_key = os.getenv("AZURE_AI_INFERENCE_API_KEY")

async def main():
    kernel = Kernel()

    # Add the AzureChatCompletion AI Service to the Kernel
    service_id = "orchestrator_agent"
    kernel.add_service(AzureChatCompletion(service_id=service_id))
    kernel.add_plugin(ReportAgent(), plugin_name="ReportAgent")
    kernel.add_plugin(SearchAgent(), plugin_name="SearchAgent")

    settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
    # Configure the function choice behavior to auto invoke kernel functions
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    agent = ChatCompletionAgent(
        service_id="orchestrator_agent",
        kernel=kernel,
        name="OrchestratorAgent",
        instructions=f"""
            You are an agent designed to create detailed reports about health plans. The user will provide the name of a health plan and you'll use that health paln to create a detailed report. Call the appropriate functions to help write the report. 
            Do not write the report on your own. Your role is to be an orchestrator who will call the appropriate plugins and functions provided to you.""",
        execution_settings=settings,
    )

    history = ChatHistory()
    is_complete: bool = False
    while not is_complete:
        logger.info("Starting Semantic Kernel execution...")

        user_input = input("User:> ")
        if not user_input:
            continue

        if user_input.lower() == "exit":
            is_complete = True
            break
        history.add_message(ChatMessageContent(role=AuthorRole.USER, content=user_input))

        async for response in agent.invoke(history=history):
            print(f"{response.content}")

if __name__ == "__main__":
    asyncio.run(main())