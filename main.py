import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from levels import levels

def start(bot, update):
    update.message.reply_text('Hello! I am the geographical test-bot. You can test your geography skills here. '
                              'What`s your name?')
    return 1


def help(bot, update):
    update.message.reply_text("""Throughout the game you will meet such commands:
    /start_test - start pass test
    /close - close keyboard
    /end_test - end pass test""", reply_markup=back_markup)
    return 4


def start_test(bot, update, user_data):
    name = user_data["name"]
    update.message.reply_text("Welcome to geographical test! "
                              "Before starting the game, {}, please, choose the difficulty level.".format(name),
                              reply_markup=markup_difficult)

    return 3


def get_ll_spn(toponym):
    ll = ",".join(toponym["Point"]["pos"].split())
    lower_corner = [float(c) for c in toponym["boundedBy"]["Envelope"]["lowerCorner"].split()]
    upper_corner = [float(c) for c in toponym["boundedBy"]["Envelope"]["upperCorner"].split()]

    spn = ",".join([str((upper_corner[0] - lower_corner[0])/3), str((upper_corner[1]-lower_corner[1])/3)])

    return ll, spn


def geocoder(bot, updater, args):
    geocoder_uri = "http://geocode-maps.yandex.ru/1.x/"
    response = requests.get(geocoder_uri, params={
        "format": "json",
        "geocode": ", ".join(args)
    })

    toponym = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

    ll, spn = get_ll_spn(toponym)

    static_api_server = "http://static-maps.yandex.ru/1.x/?l={}&ll={}&spn={}&pt={}"
    static_api_params = {"ll": ll,
                         "l": "sat",
                         "spn": spn,
                         "pt": ll+","+"flag"}

    print(static_api_server.format(static_api_params["l"], static_api_params["ll"],
                                 static_api_params["spn"], static_api_params["pt"]))
    bot.sendPhoto(
        updater.message.chat.id,
        static_api_server.format(static_api_params["l"], static_api_params["ll"],
                                 static_api_params["spn"], static_api_params["pt"])
    )


def end_test(bot, update):
    update.message.reply_text(
        "Too bad, that you stopped taking the test. He's so interesting! You can try again. '/start'", reply_markup=start_markup)

    # close_keyboard(bot, update)
    return ConversationHandler.END  # Константа, означающая конец диалога.


def menu(bot, update, user_data):
    user_data["name"] = update.message.text
    user_data["result"] = 0
    name = user_data["name"]
    update.message.reply_text("{}, you can start a new game '/start_test'".format(name), reply_markup=markup)
    return 2

def back(bot, update):
    update.message.reply_text("You are back in the menu", reply_markup=markup)
    return 2



def close_keyboard(bot, update):
    update.message.reply_text("", reply_markup=ReplyKeyboardRemove())


back_keyboard = [["/back"]]
back_markup = ReplyKeyboardMarkup(back_keyboard, one_time_keyboard=True, resize_keyboard=True)

start_keyboard = [["/start"]]
start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)

reply_keyboard = [['/start_test', '/help']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

keyboard_difficult = [["easy(+)", "medium(-)", "hard(-)"]]
markup_difficult = ReplyKeyboardMarkup(keyboard_difficult, one_time_keyboard=True)

# easy:

lev1_markup = ReplyKeyboardMarkup(levels["easy"][1], one_time_keyboard=True)
lev2_markup = ReplyKeyboardMarkup(levels["easy"][2], one_time_keyboard=True)
lev3_markup = ReplyKeyboardMarkup(levels["easy"][3], one_time_keyboard=True)


def difficult_level(bot, update, user_data):
    user_data["difficulty"] = update.message.text
    difficulty = user_data["difficulty"]

    update.message.reply_text("You have chosen the difficulty level: {}. Good luck! "
                              "During the test, you can complete it ahead of time '/end_test'".format(difficulty))

    update.message.reply_text("Level1\nChoose the correct answer.\ntip: The capital of Russia", reply_markup=lev1_markup)
    geocoder(bot, update, "Москва")

    return 4


def level1(bot, update, user_data):
    # difficulty = user_data["difficulty"]
    # name = user_data["name"]
    user_data["level1"] = update.message.text

    answer_for_level1 = user_data["level1"]

    if answer_for_level1 == "Moscow":
        user_data["result"] += 1

    update.message.reply_text("Right answer - Moscow.")

    update.message.reply_text("Level2\nChoose the correct answer.\ntip: no comments", reply_markup=lev2_markup)
    geocoder(bot, update, "Австралия")

    return 5


def level2(bot, update, user_data):
    # difficulty = user_data["difficulty"]
    # name = user_data["name"]
    user_data["level2"] = update.message.text

    answer_for_level2 = user_data["level2"]

    if answer_for_level2 == "Australia":
        user_data["result"] += 1

    update.message.reply_text("Right answer - Australia.")

    update.message.reply_text("Level3\nChoose the correct answer.\ntip: near the Sochi", reply_markup=lev3_markup)
    geocoder(bot, update, "Черное море")

    return 6


def level3(bot, update, user_data):
    # difficulty = user_data["difficulty"]
    # name = user_data["name"]
    user_data["level3"] = update.message.text

    answer_for_level3 = user_data["level3"]

    if answer_for_level3 == "Black sea":
        user_data["result"] += 1


    if user_data["result"] == 3:
        update.message.reply_text("Right answer - Black sea. Thanks for listening. "
                                  "You give {} correct answers.  You made a great job with the test."
                                  "Goodbye!".format(user_data["result"]))
    else:
        update.message.reply_text("Right answer - Black sea. Thanks for listening. "
                                  "You give {} correct answers.  You are fine fellow, but you have a mistakes. "
                                  "Goodbye!".format(user_data["result"]))

    return ConversationHandler.END


def main():
    updater = Updater("552686153:AAER6lE-lZkWSoECoVQGAn_S0Mwrl0pHFEg")

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае команда /start. Она задает первый вопрос.
        entry_points=[CommandHandler('start', start)],

    # Состояния внутри диалога. В данном случае два обработчика сообщений, фильтрующих текстовые сообщения.
    states = {
                1: [MessageHandler(Filters.text, menu, pass_user_data=True)],

                2: [CommandHandler("start_test", start_test, pass_user_data=True),
                    CommandHandler("help", help)],

                3: [MessageHandler(Filters.text, difficult_level, pass_user_data=True)],

                4: [CommandHandler("back", back)],

                5: []

             },

             # Точка прерывания диалога. В данном случае команда /stop.
             fallbacks = [CommandHandler('end_test', end_test)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()

    print("Bot is running")

    updater.idle()


if __name__ == '__main__':
    main()