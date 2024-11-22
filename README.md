<h1 align="center">
Crypto Wallet Transactions Tracker Bot
</h1>

Ce bot Telegram suit les transactions des portefeuilles Ethereum (ETH) et Binance Coin (BNB) ajoutés et envoie des notifications chaque fois qu'une nouvelle transaction se produit. Le bot utilise les API Etherscan et BSCscan pour recueillir des informations sur les transactions, ainsi que CoinGecko pour obtenir les prix actuels de l'ETH et du BNB.

## Commandes

- `/start` : Affiche un message de bienvenue et des instructions sur l'utilisation du bot.
- `/add <blockchain> <wallet_address>` : Ajoute un nouveau portefeuille à suivre. L'adresse du portefeuille doit être fournie dans le format correct (commençant par '0x' pour les portefeuilles ETH et 'bnb' pour les portefeuilles BNB), sinon le bot demandera à l'utilisateur de corriger.
- `/remove <blockchain> <wallet_address>` : Supprime un portefeuille de la liste des portefeuilles suivis. L'utilisateur doit fournir l'adresse du portefeuille dans le format correct.
- `/list` : Affiche la liste des portefeuilles actuellement suivis.

## Fonctionnalités

- **Journalisation** : Le bot enregistre chaque transaction et les erreurs dans un fichier de log.
- **Vérification de format** : Le bot vérifie que l'adresse du portefeuille fournie par l'utilisateur est dans le format correct avant de l'ajouter à la liste des portefeuilles suivis.

## Exigences

Pour exécuter le bot, vous devez avoir Python 3.6 ou une version ultérieure installé sur votre système, sourcez le `requirements.txt` pour installer les dépendances.

Vous devrez également obtenir des clés API pour Etherscan et BSCscan, ainsi qu'un token de bot Telegram. Ces éléments peuvent être obtenus en suivant les instructions sur les sites respectifs.

## Installation

1. Clonez ce dépôt : `git clone <URL_DU_REPO>`
2. Installez les packages requis : `pip install -r requirements.txt`
3. Remplacez les espaces réservés dans le fichier `main.py` par vos clés API et le token du bot :

    ```python
    ETHERSCAN_API_KEY = '<votre_clé_api_etherscan>'
    BSCSCAN_API_KEY = '<votre_clé_api_bscscan>'
    TELEGRAM_BOT_TOKEN = '<votre_token_bot_telegram>'
    TELEGRAM_CHAT_ID = '<votre_id_chat_telegram>'
    ```

4. Démarrez le bot : `python main.py`

## Remarque

Ce bot est fourni à des fins éducatives uniquement et ne doit pas être utilisé comme conseil financier. Le bot n'a pas accès à votre portefeuille.

## Journalisation

Les journaux des transactions et des erreurs sont enregistrés dans le fichier `log.log`. Assurez-vous de vérifier ce fichier pour le débogage et le suivi des activités du bot.

## Fichiers de Configuration

- `watched_wallets.txt` : Contient la liste des portefeuilles suivis.
- `latest_tx_hashes.json` : Stocke les hachages des dernières transactions pour éviter les doublons.
- `last_run_time.txt` : Enregistre le dernier temps d'exécution pour le suivi des transactions.

## License

Distribué sous la licence Apache 2.0. Voir `LICENSE` pour plus d'informations.