"""
CLI interface for the GitHub Repo Analyzer.
"""
import logging
from agent.handler import handle_user_input

logger = logging.getLogger(__name__)

def start_cli():
    """Start the CLI interface for the GitHub Repo Analyzer."""
    logger.info("Starting CLI interface")
    print("Enhanced GitHub Repo Analyzer (type 'exit' to quit)")
    
    while True:
        user_input = input("\nAsk a question (include <owner>/<repo> if needed): ")
        
        if user_input.strip().lower() == 'exit':
            print("Goodbye!")
            break
            
        try:
            response = handle_user_input(user_input)
            print(response)
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            print(f"Sorry, an error occurred: {e}")