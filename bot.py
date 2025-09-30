from __future__ import annotations
import asyncio
import logging
from typing import Any

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.config import load_config
from app.assistants import AssistantRunner, ToolCall
from app.sheets_tool import SheetsClient
from app.thread_store import ThreadStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_tool_dispatch(sheets: SheetsClient):
    def dispatch(tc: ToolCall) -> str | dict[str, Any]:
        if tc.name == "save_booking_data":
            logger.info("Tool call received: %s args=%s", tc.name, tc.arguments)
            args = tc.arguments or {}
            result = sheets.save_booking_data(
                name=args.get("name", ""),
                phone=args.get("phone", ""),
                service=args.get("service", ""),
                datetime=args.get("datetime", ""),
                master_category=args.get("master_category", ""),
                comments=args.get("comments", ""),
            )
            if isinstance(result, dict) and result.get("status") != "ok":
                logger.error("Sheets append failed: %s", result)
            else:
                logger.info("Sheets append ok: %s", result)
            return result
        # Unknown tool requested by the assistant
        logger.warning("Unknown tool requested: %s", tc.name)
        return {"error": f"Unknown tool: {tc.name}"}

    return dispatch


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здравствуйте! Я помогу с записью и вопросами.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    cfg = context.application.bot_data["config"]
    runner: AssistantRunner = context.application.bot_data["runner"]
    threads: ThreadStore = context.application.bot_data["threads"]
    tool_dispatch = context.application.bot_data["tool_dispatch"]

    chat_id = update.message.chat_id
    text = update.message.text

    await update.message.chat.send_action("typing")

    try:
        # get or create thread for this chat
        thread_id = threads.get(chat_id)
        if not thread_id:
            thread_id = runner.create_thread()
            threads.set(chat_id, thread_id)

        reply = await asyncio.to_thread(
            runner.send_and_respond,
            thread_id,
            text,
            tool_dispatch,
        )
        if not reply:
            reply = "(Нет ответа от ассистента)"
        await update.message.reply_text(reply, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.exception("Error while handling message")
        await update.message.reply_text(
            "Извините, возникла ошибка при обработке запроса. Попробуйте ещё раз.")


def main():
    cfg = load_config()

    threads = ThreadStore("data/threads.json")
    runner = AssistantRunner(api_key=cfg.openai_api_key, assistant_id=cfg.openai_assistant_id)
    sheets = SheetsClient(cfg.gsa_file, cfg.sheet_id, worksheet_title=cfg.sheet_worksheet)

    tool_dispatch = make_tool_dispatch(sheets)

    app = Application.builder().token(cfg.tg_bot_token).build()
    app.bot_data.update({
        "config": cfg,
        "runner": runner,
        "threads": threads,
        "tool_dispatch": tool_dispatch,
    })

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.exception("Unhandled error in application", exc_info=context.error)
        try:
            if isinstance(update, Update) and update.effective_message:
                await update.effective_message.reply_text(
                    "Сервис временно недоступен. Пожалуйста, попробуйте позже.")
        except Exception:
            pass

    app.add_error_handler(on_error)

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
