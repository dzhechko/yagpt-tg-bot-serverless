import asyncio
import json
import os

#Библиотеки для работы с телеграмм
from telegram import Update, Message, Chat
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

#Библиотеки для YaGPT и Langchain
from yandex_chain import YandexLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я телеграмм-бот на базе YandexGPT. Готов помогать с ответами на вопросы.")

async def process_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # вопрос пользователя
    message_text = update.message.text

    # обращение к модели YaGPT
    yagpt_folder_id = os.environ["YAGPT_FOLDER_ID"]
    yagpt_api_key = os.environ["YAGPT_API_KEY"]
    yagpt_temperature = 0.01
    yagpt_max_tokens = 8000
    yagpt_prompt = "Отвечай на вопросы коротко и точно. Следуй пожеланиям пользователя, до тех пор пока они не выходят за рамки этики. Если не знаешь ответ, вежливо напиши об этом."
    llm = YandexLLM(api_key=yagpt_api_key, folder_id=yagpt_folder_id, temperature = yagpt_temperature, max_tokens=yagpt_max_tokens, use_lite=False)        
    str2 = """Вопрос: {question}
    Твой ответ:"
    """
    template = f"{yagpt_prompt} {str2}"
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    response = llm_chain.run({"question": message_text})

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


bot = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).updater(None).build()

bot.add_handler(CommandHandler("start", start))
bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_text_message))

loop = asyncio.get_event_loop()
loop.run_until_complete(bot.initialize())

async def handler(event, context):
    message = json.loads(event["messages"][0]["details"]["message"]["body"])
    update = Update(
        update_id=message["update_id"],
        message=Message(
            message_id=message["message"]["message_id"],
            date=message["message"]["date"],
            chat=Chat(
                id=message["message"]["chat"]["id"],
                type=message["message"]["chat"]["type"]
            ),
            text=message["message"]["text"],
        )
    )

    await bot.process_update(update)

    return {
        "statusCode": 500,
    }
