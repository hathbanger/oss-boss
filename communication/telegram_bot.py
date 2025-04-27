"""
Telegram bot interface for the GitHub Repo Analyzer.
"""
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from agent.handler import handle_user_input
import telegram

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text('Hello! I am the GitHub Repo Analyzer bot. Ask me anything about GitHub repositories!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages and respond using the agent handler."""
    user_input = update.message.text
    try:
        # Send a "typing" action to show the bot is processing
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Use asyncio to run the potentially blocking handle_user_input function
        run_response = await asyncio.to_thread(handle_user_input, user_input)
        
        # Get the content as string using the built-in method
        response = run_response.get_content_as_string() if hasattr(run_response, 'get_content_as_string') else str(run_response)
        
        # Handle long responses by splitting if needed
        if len(response) > 4096:  # Telegram message limit
            chunks = [response[i:i+4096] for i in range(0, len(response), 4096)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response)
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text('Sorry, an error occurred while processing your request.')

def start_telegram_bot():
    """Start the Telegram bot using the provided token."""
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not telegram_bot_token:
        raise RuntimeError('TELEGRAM_BOT_TOKEN environment variable not set.')
        
    application = ApplicationBuilder().token(telegram_bot_token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler for conflicts
    application.add_error_handler(error_handler)
    
    logger.info('Starting Telegram bot...')
    application.run_polling()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the telegram bot."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Handle conflict errors specifically
    if isinstance(context.error, telegram.error.Conflict):
        logger.critical("Telegram conflict error: Another instance is already running!")
        # Optionally terminate this instance
        import sys
        sys.exit(1)