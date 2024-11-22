from telegram.ext import Updater, CommandHandler
import requests
import json
import time
import os.path
import re
import logging
from web3 import Web3
from fernet import Fernet

# Configure logging
logging.basicConfig(filename='log.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Update the following variables with your own Etherscan and BscScan API keys and Telegram bot token
ETHERSCAN_API_KEY = 'PH84WF3RJR72KMJ259WVPPXIGNDPTZ2UJS'
BSCSCAN_API_KEY = 'SEXHD1MET8J3UDJBJN82FTP9FR6Y6RRUVW'
TELEGRAM_BOT_TOKEN = '7607138331:AAGWqzxovVyamtpQRJyVW7SiUeMIxvHzXRE'
TELEGRAM_CHAT_ID = '-4599799577'

# Define some helper functions
def get_wallet_transactions(wallet_address, blockchain):
    if blockchain == 'eth':
        url = f'https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&sort=desc&apikey={ETHERSCAN_API_KEY}'
    elif blockchain == 'bnb':
        url = f'https://api.bscscan.com/api?module=account&action=txlist&address={wallet_address}&sort=desc&apikey={BSCSCAN_API_KEY}'
    else:
        logging.error('Invalid blockchain specified')
        raise ValueError('Invalid blockchain specified')

    logging.debug(f"Fetching transactions for {wallet_address} on {blockchain} using URL: {url}")
    response = requests.get(url)
    data = json.loads(response.text)

    logging.info(f"Response from API: {data}")
    result = data.get('result', [])
    if not isinstance(result, list):
        logging.error(f"Error fetching transactions: {data}")
        return []

    logging.info(f"Found {len(result)} transactions")
    return result

def send_telegram_notification(message, value, usd_value, tx_hash, blockchain):
    if blockchain == 'eth':
        etherscan_link = f'<a href="https://etherscan.io/tx/{tx_hash}">Etherscan</a>'
    elif blockchain == 'bnb':
        etherscan_link = f'<a href="https://bscscan.com/tx/{tx_hash}">BscScan</a>'
    else:
        logging.error('Invalid blockchain specified')
        raise ValueError('Invalid blockchain specified')

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': f'{TELEGRAM_CHAT_ID}',
        'text': f'{message}: {etherscan_link}\nValue: {value:.6f} {blockchain.upper()} (${usd_value:.2f})',
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    logging.info(f"Telegram notification sent with message: {message}, value: {value} {blockchain.upper()} (${usd_value:.2f})")

def monitor_wallets():
    latest_tx_hashes = {}
    latest_tx_hashes_path = "latest_tx_hashes.json"
    if os.path.exists(latest_tx_hashes_path):
        with open(latest_tx_hashes_path, "r") as f:
            latest_tx_hashes = json.load(f)

    while True:
        try:
            with open("watched_wallets.txt", "r") as f:
                wallets = [line.strip().split(":") for line in f if line.strip()]

            for blockchain, wallet_address in wallets:
                transactions = get_wallet_transactions(wallet_address, blockchain)
                if not transactions:
                    continue

                for tx in transactions:
                    tx_hash = tx['hash']
                    if tx_hash not in latest_tx_hashes.get(wallet_address, []):
                        if wallet_address not in latest_tx_hashes:
                            latest_tx_hashes[wallet_address] = []
                        latest_tx_hashes[wallet_address].append(tx_hash)

                        # Get the current price of ETH/BNB in USD
                        if blockchain == 'eth':
                            price_url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
                        else:
                            price_url = 'https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd'
                        
                        price_response = requests.get(price_url)
                        price_data = json.loads(price_response.text)
                        if blockchain == 'eth':
                            current_price = price_data['ethereum']['usd']
                        else:
                            current_price = price_data['binancecoin']['usd']

                        # Convert value from Wei to ETH/BNB
                        value = float(tx['value']) / 10**18
                        usd_value = value * current_price

                        # Check if it's an incoming or outgoing transaction
                        if tx['to'].lower() == wallet_address.lower():
                            message = f'🚨 Incoming transaction detected on {wallet_address}'
                        else:
                            message = f'🚨 Outgoing transaction detected on {wallet_address}'

                        send_telegram_notification(message, value, usd_value, tx_hash, blockchain)

            # Save the latest transaction hashes
            with open(latest_tx_hashes_path, "w") as f:
                json.dump(latest_tx_hashes, f)

            time.sleep(60)  # Wait for 60 seconds before checking again
        except Exception as e:
            logging.error(f"Error in monitor_wallets: {str(e)}")
            time.sleep(60)  # Wait for 60 seconds before retrying

def start(update, context):
    """Send a message when the command /start is issued."""
    message = "Bienvenue ! Je suis un bot qui suit les transactions des portefeuilles ETH et BNB.\n\n"
    message += "Commandes disponibles :\n"
    message += "/add <blockchain> <wallet_address> - Ajoute un portefeuille à suivre\n"
    message += "/remove <blockchain> <wallet_address> - Supprime un portefeuille\n"
    message += "/list - Liste les portefeuilles suivis"
    context.bot.send_message(chat_id=update.message.chat_id, text=message)

def add(update, context):
    """Add a wallet to the watch list."""
    if len(context.args) != 2:
        message = "Format incorrect. Utilisez : /add <blockchain> <wallet_address>"
        context.bot.send_message(chat_id=update.message.chat_id, text=message)
        return

    blockchain = context.args[0].lower()
    wallet_address = context.args[1]

    if blockchain not in ['eth', 'bnb']:
        message = "Blockchain non valide. Utilisez 'eth' ou 'bnb'."
        context.bot.send_message(chat_id=update.message.chat_id, text=message)
        return

    # Check wallet address format
    if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
        message = "Format d'adresse de portefeuille non valide."
        context.bot.send_message(chat_id=update.message.chat_id, text=message)
        return

    # Add the wallet to the watch list
    with open("watched_wallets.txt", "a") as f:
        f.write(f"{blockchain}:{wallet_address}\n")

    message = f"Portefeuille {wallet_address} ajouté à la liste de surveillance pour {blockchain.upper()}."
    context.bot.send_message(chat_id=update.message.chat_id, text=message)

def remove(update, context):
    """Remove a wallet from the watch list."""
    if len(context.args) != 2:
        message = "Format incorrect. Utilisez : /remove <blockchain> <wallet_address>"
        context.bot.send_message(chat_id=update.message.chat_id, text=message)
        return

    blockchain = context.args[0].lower()
    wallet_address = context.args[1]

    if blockchain not in ['eth', 'bnb']:
        message = "Blockchain non valide. Utilisez 'eth' ou 'bnb'."
        context.bot.send_message(chat_id=update.message.chat_id, text=message)
        return

    # Remove the wallet from the watch list
    wallets = []
    with open("watched_wallets.txt", "r") as f:
        wallets = [line.strip() for line in f if line.strip()]

    wallet_entry = f"{blockchain}:{wallet_address}"
    if wallet_entry in wallets:
        wallets.remove(wallet_entry)
        with open("watched_wallets.txt", "w") as f:
            for wallet in wallets:
                f.write(f"{wallet}\n")
        message = f"Portefeuille {wallet_address} supprimé de la liste de surveillance pour {blockchain.upper()}."
    else:
        message = f"Portefeuille {wallet_address} non trouvé dans la liste de surveillance pour {blockchain.upper()}."

    context.bot.send_message(chat_id=update.message.chat_id, text=message)

def list_wallets(update, context):
    """List all watched wallets."""
    if os.path.exists("watched_wallets.txt"):
        eth_wallets = []
        bnb_wallets = []
        
        with open("watched_wallets.txt", "r") as f:
            for line in f:
                blockchain, wallet_address = line.strip().split(":")
                if blockchain == 'eth':
                    eth_wallets.append(wallet_address)
                elif blockchain == 'bnb':
                    bnb_wallets.append(wallet_address)

        message = "The following wallets are currently being monitored\n"
        message += "\n"
        if eth_wallets:
            message += "Ethereum Wallets:\n"
            for i, wallet in enumerate(eth_wallets):
                message += f"{i+1}. {wallet}\n"
            message += "\n"
        if bnb_wallets:
            message += "Binance Coin Wallets:\n"
            for i, wallet in enumerate(bnb_wallets):
                message += f"{i+1}. {wallet}\n"
        context.bot.send_message(chat_id=update.message.chat_id, text=message)
    else:
        message = "There are no wallets currently being monitored."
        context.bot.send_message(chat_id=update.message.chat_id, text=message)

# Set up the Telegram bot
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Define the command handlers
start_handler = CommandHandler('start', start)
add_handler = CommandHandler('add', add)
remove_handler = CommandHandler('remove', remove)
list_handler = CommandHandler('list', list_wallets)

# Add the command handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(remove_handler)
dispatcher.add_handler(list_handler)

# Start the bot
updater.start_polling()
logging.info("Telegram bot started.")

try:
    # Run the bot until you press Ctrl-C
    logging.info("Monitoring wallets...")
    monitor_wallets()
except KeyboardInterrupt:
    updater.stop()
    logging.info("Bot stopped manually")