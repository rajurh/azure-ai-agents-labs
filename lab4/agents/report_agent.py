import os
from semantic_kernel.functions import kernel_function
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

load_dotenv()

class ReportAgent:
    """An agent that helps write detailed reports about health plans."""

    @kernel_function(description="Agent that helps write detailed reports about health plans")
    def write_report(self, plan: str) -> str:
        """Writes a report"""
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=os.environ["PROJECT_CONNECTION_STRING"],
            )

        report_agent = project_client.agents.create_agent(
        model="gpt-4o", name="my-agent", instructions="You are a helpful agent")
        # Create thread for communication
        thread = project_client.agents.create_thread()
        # Create message to thread
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=f"Write a detailed report about {plan}.",
        )

        # Create and process agent run in thread with tools
        run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=report_agent.id)

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Delete the agent when done
        project_client.agents.delete_agent(report_agent.id)

        # Fetch and log all messages
        messages = project_client.agents.list_messages(thread_id=thread.id)
        #print(f"Messages: {messages}")
        last_msg = messages.get_last_text_message_by_role("assistant")
        if last_msg:
            return last_msg

