import os
from semantic_kernel.functions import kernel_function
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchTool

load_dotenv()

class SearchAgent:
    """An agent that is able to search health plan documents."""

    @kernel_function(description="Agent that searches health plan documents")
    def search_plan_docs(self, plan: str) -> str:
        """Searches an Azure AI Search index for health plan documents."""
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=os.environ["PROJECT_CONNECTION_STRING"],
            )
        
        conn_id = "/subscriptions/2d0ee675-17ff-4b13-a230-e84531ba4eab/resourceGroups/rg-mani-ai-demos/providers/Microsoft.MachineLearningServices/workspaces/ai-agent-sample/connections/aisearch-mani-demos-eastus2"
        ai_search = AzureAISearchTool(index_connection_id=conn_id, index_name="health-plan")

        search_agent = project_client.agents.create_agent(
            model="gpt-4o",
            name="my-assistant",
            instructions="You are a helpful assistant.",
            tools=ai_search.definitions,
            tool_resources = ai_search.resources,
        )       
        # Create thread for communication
        thread = project_client.agents.create_thread()
        # Create message to thread
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=f"Tell me about the {plan} plan.",
        )

        # Create and process agent run in thread with tools
        run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=search_agent.id)

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Delete the agent when done
        project_client.agents.delete_agent(search_agent.id)

        # Fetch and log all messages
        messages = project_client.agents.list_messages(thread_id=thread.id)
        #print(f"Messages: {messages}")
        last_msg = messages.get_last_text_message_by_role("assistant")
        if last_msg:
            return last_msg

