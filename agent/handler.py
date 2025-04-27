"""
Handler module for the GitHub Repository Analysis Agent.
Manages agent initialization and processing user queries.
"""
import logging
import os
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.memory.v2.db.mongodb import MongoMemoryDb 
from agno.memory.v2.memory import Memory
from .tools.github_tools import GithubTools
from .tools.npm_tools import NpmTools
from agno.storage.mongodb import MongoDbStorage
                
                

logger = logging.getLogger(__name__)

# Singleton instance of the agent
_agent_instance = None

def get_agent():
    """
    Get or create the agent singleton instance.
    Uses lazy initialization to create the agent only when needed.
    """
    global _agent_instance
    
    if _agent_instance is None:
        logger.info("Initializing GitHub Repo Analysis Agent")
        
        # Initialize tools
        github_tools = GithubTools()
        npm_tools = NpmTools()
        
        # Initialize models
        claude_model = Claude(id="claude-3-5-sonnet-20240620")
        
        connection_string = os.getenv("MONGO_DB_URL")
        
        if not connection_string:
            # Default to localhost with standard port
            connection_string = "mongodb://localhost:27017/agno"
            logger.info(f"Using local MongoDB: {connection_string}")
            
        memory_db = MongoMemoryDb(db_url=connection_string, collection_name="agno_memory")
        memory = Memory(db=memory_db)    
        
        # Create and configure the agent
        _agent_instance = Agent(
            instructions=[
                "Use your tools to answer questions about any GitHub repository.",
                "If the user question does not specify a repository in the format <owner>/<repo>, ask them to clarify.",
                "You can analyze contributors, repositories, issues, and more.",
                "Do not create any issues or pull requests unless explicitly asked to do so.",
                "You can also search for NPM packages and their information.",
                "Please liven up the response with emojis and other visual elements."
            ],
            model=claude_model,
            tools=[github_tools, npm_tools],
            show_tool_calls=True,
            add_history_to_messages=True,
            session_id="github_repo_analysis",
            storage=MongoDbStorage(db_url=connection_string, collection_name="agno_contexts"),
            num_history_runs=3,
            enable_agentic_memory=True,
            memory=memory
        )
        
    return _agent_instance

def handle_user_input(user_input: str) -> str:
    """
    Process user input through the agent and return the response.
    
    Args:
        user_input: The user's query text
        
    Returns:
        The agent's response as a string or an object with a get_content_as_string method
    """
    try:
        agent = get_agent()
        logger.debug(f"Processing user input: {user_input}")
        response = agent.run(user_input, markdown=True)
        return response
    except Exception as e:
        logger.error(f"Error in agent processing: {e}")
        raise