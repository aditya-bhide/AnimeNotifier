from multiprocessing import Pool
import AnimeSearch as ans
import logging
import telegram
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, ConversationHandler
import time
from pymongo import MongoClient

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

ADD, DELETE = range(2)

#########bot initials########
# Token = 88513######
my_token = 'your token'
updater = Updater(my_token)
bot = telegram.Bot(my_token)

#########mongodb Database########
# myclient = MongoClient("mongodb://localhost:27017/")
myclient = MongoClient("")myclient = MongoClient("")


mydb = myclient['AnimeNotifier']
animelist = mydb.animelist

def delete_anime(bot, update, user_data):
    chatid = update.message.chat_id
    arr = []
    i = 1
    msg = "Choose by number\n"
    for id in animelist.find({"users": chatid}):
        arr.append(id["anime"])
        msg = msg + str(i)+ ". " + id["anime"] + "\n"
        i += 1

    #print(arr)
    user_data['data'] = arr
    bot.sendMessage(chat_id=chatid, text=msg)
    return DELETE

def is_int_number(num):
    return num.strip().lstrip('-+').isdigit() and num.count('-') + num.count('+') <= 1

def delete_anime_name(bot , update, user_data):
    chatid = update.message.chat_id
    data = user_data['data']
    # print(chatid)
    # print(data)

    index = update.message.text
    if is_int_number(index):
        index = int(index)
        id = int(update.message.text)
        # print(id)
        if index > len(data):
            update.message.reply_text("Number not in the list.")
        else:
            update.message.reply_text(str(data[(index-1)])+" Deleted")
            animelist.update({"anime":data[(index-1)]}, {"$pull": {"users": chatid}})
            for i in animelist.find({"anime":data[(index-1)]}):
                if i['users'] == []:
                    animelist.remove({"anime":data[(index-1)]})
    else:
        update.message.reply_text("You didn't enter a number.")

    return ConversationHandler.END

def show_anime(bot, update):
    chatid = update.message.chat_id
    # print(chatid)
    msg = ""
    i = 1
    for id in animelist.find({"users": chatid}):
        msg = msg+ str(i)+ ". " + str(id["anime"]) + "\n"
        i+=1

    if msg == "":
        msg = "You haven't added anything"
    update.message.reply_text(msg)

def add_anime(bot,update):
    chatid = update.message.chat_id
    # print(update.message.text)
    update.message.reply_text("Enter the anime name exactly like on the website")
    return ADD

def add_anime_name(bot, update):
    chatid = update.message.chat_id
    csvData = str(update.message.text)
    if ans.check_anime_exists(csvData):
        # print(chatid)
        # print(csvData)
        if animelist.count_documents({"anime": csvData}) == 0:
            post = {"anime": csvData, "users": [chatid]}
            animelist.insert_one(post)
            update.message.reply_text(csvData + " added to the list")
            temp = ans.call_url(csvData,1)
            if temp !=0:
                bot.sendMessage(chat_id=chatid, text=str(temp))
        else:
            if animelist.count_documents({"anime": csvData, "users":chatid}) == 0:
                animelist.update({"anime":csvData},{"$push":{"users":chatid}})
                update.message.reply_text(csvData + " added to the list")
                temp = ans.call_url(csvData, 1)
                if temp != 0:
                    bot.sendMessage(chat_id=chatid, text=str(temp))
            else:
                update.message.reply_text("Anime already exists.")
    else:
        bot.sendMessage(chat_id=chatid, text="Anime not found")
    return ConversationHandler.END

def begin_bot_work():
    dp = updater.dispatcher
    conv_handler_add_anime = ConversationHandler(
        entry_points=[CommandHandler('add_anime', add_anime)],

        states={
            ADD: [MessageHandler(Filters.text, add_anime_name)],
        },
        fallbacks=[]
    )
    conv_handler_delete_anime = ConversationHandler(
        entry_points=[CommandHandler('delete_anime', delete_anime, pass_user_data= True)],
        states={
            DELETE: [MessageHandler(Filters.text, callback=delete_anime_name, pass_user_data= True)],
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler_add_anime)
    dp.add_handler(conv_handler_delete_anime)
    dp.add_handler(CommandHandler('show_anime', show_anime))
    updater.start_polling()
    updater.idle()
    updater.stop()

def web_caller():
    while(True):
        for i in animelist.find({}):
            href = ans.call_url(str(i["anime"]),0)
            if href != 0:
                for j in range(0, len(i["users"])):
                    bot.sendMessage(chat_id=i["users"][j], text=str(href))
        time.sleep(60)

def main():
    pool = Pool(processes=2)
    ping_site = pool.apply_async(web_caller)
    print("started pinging")
    run_bot = pool.apply_async(begin_bot_work)
    pool.close()
    pool.join()
    begin_bot_work()

if __name__ == '__main__':
    main()

