import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
import json

# Telegram Bot Token
BOT_TOKEN = '7452333934:AAFpN7f3-QFMiTsJkT_yic8DL29v5cCR9RQ'

# Owner's Telegram User ID
OWNER_ID = 6099745136

# Discord Webhooks
SUPPORT_WEBHOOK_URL = 'https://discord.com/api/webhooks/1254051219098566807/ky_stPjKsBWY3RvYAsDxrH0NOGROEbn0GPZE9c4PMxSMqm6f8_ByAzVIoJZ7DWLWZGMj'
LOGGING_WEBHOOK_URL = 'https://discord.com/api/webhooks/1254051339466440734/unl7DHYtGftDJCFemvTKeoky3ulxpLRFq2KRg1AEq4ZXixIO36g1CSYLCZknfcQH4weT'

# Create updater and dispatcher
updater = Updater(BOT_TOKEN)
dispatcher = updater.dispatcher

# Command handlers
def start(update, context):
    update.message.reply_text('Welcome to Temp Mail Bot! Use /help to see available commands.')

def help_command(update, context):
    # Display help message
    help_message = """
    Available commands:
    /help - Show this help message
    /support <message> - Send a message to the owner
    /send_webhook <webhook_url> <message> - Send a message to a webhook URL
    /webhook_spam <webhook_url> <amount> <message> - Send multiple messages to a webhook URL
    /delete <webhook_url> - Delete a webhook URL
    """
    update.message.reply_text(help_message)

def support(update, context):
    # Notify bot owner and send support message to Discord webhook
    if len(context.args) > 0:
        support_text = ' '.join(context.args)
        context.bot.send_message(OWNER_ID, f"Support message from user {update.message.from_user.id}: {support_text}")
        update.message.reply_text('Support message sent to the owner.')

        # Send support message to Discord webhook
        payload = {'content': f"Support message from {update.message.from_user.username}:\n{support_text}"}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(SUPPORT_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        if response.status_code != 200:
            print(f"Failed to send support message to Discord webhook: {response.text}")

    else:
        update.message.reply_text('Please use /support <message> to send a support message.')

def send_webhook(update, context):
    # Check if webhook URL and message are provided
    if len(context.args) < 2:
        update.message.reply_text('Usage: /send_webhook <webhook_url> <message>')
        return
    
    webhook_url = context.args[0]
    message = ' '.join(context.args[1:])
    
    # Send message to the specified webhook URL
    payload = {'content': message}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 204:
        update.message.reply_text('Message sent to webhook successfully!')
    else:
        update.message.reply_text(f'Failed to send message to webhook. Status code: {response.status_code}')

def webhook_spam(update, context):
    # Check if webhook URL, amount, and message are provided
    if len(context.args) != 3:
        update.message.reply_text('Usage: /webhook_spam <webhook_url> <amount> <message>')
        return
    
    webhook_url = context.args[0]
    amount = int(context.args[1])
    message = context.args[2]
    
    # Limit amount to 100 messages
    amount = min(amount, 100)
    
    # Send multiple messages to the specified webhook URL
    for _ in range(amount):
        payload = {'content': message}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        
        if response.status_code != 204:
            update.message.reply_text(f'Failed to send message {message} to webhook. Status code: {response.status_code}')
            return
    
    update.message.reply_text(f'Successfully sent {amount} messages to webhook!')

def delete_webhook(update, context):
    # Check if webhook URL is provided
    if len(context.args) != 1:
        update.message.reply_text('Usage: /delete <webhook_url>')
        return
    
    webhook_url = context.args[0]
    
    # Attempt to delete the specified webhook URL
    response = requests.delete(webhook_url)
    
    if response.status_code == 204:
        update.message.reply_text('Webhook deleted successfully!')
    else:
        update.message.reply_text(f'Failed to delete webhook. Status code: {response.status_code}')

# Add command handlers to dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_command))
dispatcher.add_handler(CommandHandler('support', support, pass_args=True))
dispatcher.add_handler(CommandHandler('send_webhook', send_webhook, pass_args=True))
dispatcher.add_handler(CommandHandler('webhook_spam', webhook_spam, pass_args=True))
dispatcher.add_handler(CommandHandler('delete', delete_webhook, pass_args=True))

# Handle unknown commands and non-command messages
def handle_unknown(update, context):
    update.message.reply_text('Unknown command. Use /help to see available commands.')

dispatcher.add_handler(MessageHandler(Filters.command, handle_unknown))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_unknown))

# Start the bot
updater.start_polling()
updater.idle()
