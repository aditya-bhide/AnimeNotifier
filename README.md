# AnimeNotifier
Sends Anime notification from https://www17.gogoanimes.tv website. You can manage your own anime list through the bot. You can also share this with friends or on groups.

Prerequisites:
```bash
pip install pymongo
pip install telegram
pip install telegram-ext
```
MongoDB:
Create 'AnimeNotifier' database
Add 'animelist' and 'logs' as collections

Installation:-
Step1 : 
Create your own telegram bot for reference follow this 1 minute link  http://techthoughts.info/how-to-create-a-telegram-bot-and-send-messages-via-api/

Step2 : 
Run /setcommands choose your bot and send these commands 
"add_anime - Adds anime to the notification list
show_anime - Display the list of added animes
delete_anime - Remove anime from list"
(Wait for a few minutes commands will be added to your bot in some minutes)

Step3 : 
Run /token to get your bot token

Step4 : 
Add the bot token to my_token variable in TelegramMessage.py

Step5 : 
Run TelegramMessage.py on any cloud server or your local server which can run a python code 24/7 and you are good to go!!


(The code or specifically web scraping part will work only till basic main site structure is same.)



(Or you can directly use the bot by searching @aditya_uchiha_notifier_bot in telegram)
