"""
Main entry point for the GitHub Repo Analyzer application.
Manages all communication channels including CLI, Telegram, and API.
"""
import argparse
import threading
import os
import logging
import asyncio
import signal
from communication.cli import start_cli
from communication.telegram_bot import start_telegram_bot
from communication.api_server import start_api_server

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments to determine which components to start."""
    parser = argparse.ArgumentParser(description="GitHub Repo Analyzer")
    parser.add_argument("--cli", action="store_true", help="Start CLI interface")
    parser.add_argument("--telegram", action="store_true", help="Start Telegram bot")
    parser.add_argument("--api", action="store_true", help="Start API server")
    parser.add_argument("--all", action="store_true", help="Start all components")
    
    args = parser.parse_args()
    
    # If no specific component is selected, default to CLI
    if not (args.cli or args.telegram or args.api or args.all):
        args.cli = True
        
    return args

def start_component(start_func, component_name):
    """Start a component in a separate thread and handle exceptions."""
    try:
        logger.info(f"Starting {component_name}...")
        start_func()
    except Exception as e:
        logger.error(f"Error in {component_name}: {e}")

def main():
    """Main function to start and manage all communication channels."""
    args = parse_arguments()
    
    # Determine which components to start
    start_cli_interface = args.cli or args.all
    start_telegram_interface = args.telegram or args.all
    start_api_interface = args.api or args.all
    
    # Telegram bot must run in the main thread, so handle it differently
    if start_telegram_interface:
        # Check for Telegram token
        if not os.getenv('TELEGRAM_BOT_TOKEN'):
            logger.error("TELEGRAM_BOT_TOKEN environment variable not set. Telegram bot will not start.")
            start_telegram_interface = False
    
    # If only Telegram bot is requested, run it directly in the main thread
    if start_telegram_interface and not (start_cli_interface or start_api_interface):
        start_telegram_bot()
        return
    
    # If Telegram bot and other components are requested, we need to run other components in threads
    threads = []
    
    if start_cli_interface:
        cli_thread = threading.Thread(target=start_component, args=(start_cli, "CLI interface"))
        cli_thread.daemon = True
        threads.append(cli_thread)
    
    if start_api_interface:
        api_thread = threading.Thread(target=start_component, args=(start_api_server, "API server"))
        api_thread.daemon = True
        threads.append(api_thread)
    
    # Start threads for non-Telegram components
    for thread in threads:
        thread.start()
    
    # Run Telegram bot in the main thread if needed
    if start_telegram_interface:
        try:
            logger.info("Starting Telegram bot in main thread...")
            start_telegram_bot()
        except Exception as e:
            logger.error(f"Error in Telegram bot: {e}")
    else:
        # Wait for other threads if no Telegram bot
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    main()