import asyncio
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from sqlalchemy.exc import SQLAlchemyError
from db import SessionLocal, User, Ticket, TicketMessage, Rating
from config import OWNER_ID
from utilities import translations, safe_execute, rate_limit
from tasks import escalate_ticket
def get_language(session, telegram_id):
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    return user.language if user and user.language else "en"
@safe_execute
@rate_limit(5, 10)
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
        if not user:
            user = User(telegram_id=update.effective_user.id, username=update.effective_user.username, role="user")
            session.add(user)
            session.commit()
        lang = user.language
        if user.role in ["owner", "support"]:
            return
        content = update.message.text if update.message.text else ""
        if update.message.document:
            content += " [document: {}]".format(update.message.document.file_id)
        if update.message.photo:
            content += " [photo]"
        ticket = Ticket(user_id=user.id, content=content, status="unclaimed")
        session.add(ticket)
        session.commit()
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Claim", callback_data="claim:{}".format(ticket.id))]])
        support_users = session.query(User).filter(User.role == "support").all()
        for support in support_users:
            try:
                msg = await context.bot.send_message(chat_id=support.telegram_id, text=translations[lang]["new_ticket"].format(name=update.effective_user.first_name, id=update.effective_user.id, content=content), reply_markup=keyboard)
                tm = TicketMessage(ticket_id=ticket.id, chat_id=support.telegram_id, message_id=msg.message_id)
                session.add(tm)
                session.commit()
            except Exception:
                continue
        await update.message.reply_text(translations[lang]["ticket_forwarded"])
        escalate_ticket.apply_async(args=[ticket.id], countdown=300)
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def claim_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if not data.startswith("claim:"):
        return
    ticket_id = int(data.split(":")[1])
    session = SessionLocal()
    try:
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket or ticket.status != "unclaimed":
            await query.answer(translations["en"]["already_claimed"], show_alert=True)
            return
        user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
        if not user or user.role != "support":
            await query.answer(translations["en"]["not_authorized"], show_alert=True)
            return
        ticket.status = "claimed"
        ticket.claimed_by = user.telegram_id
        session.commit()
        new_kb = InlineKeyboardMarkup([[InlineKeyboardButton(translations["en"]["claimed_by"].format(name=update.effective_user.first_name), callback_data="claimed")]])
        messages = session.query(TicketMessage).filter(TicketMessage.ticket_id == ticket.id).all()
        for m in messages:
            try:
                await context.bot.edit_message_reply_markup(chat_id=m.chat_id, message_id=m.message_id, reply_markup=new_kb)
            except Exception:
                continue
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def assign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    session = SessionLocal()
    try:
        args = context.args
        if not args:
            await update.message.reply_text(translations["en"]["no_valid_user"])
            return
        assigned = []
        for arg in args:
            try:
                tid = int(arg)
            except Exception:
                try:
                    chat = await context.bot.get_chat(arg)
                    tid = chat.id
                except Exception:
                    continue
            user = session.query(User).filter(User.telegram_id == tid).first()
            if not user:
                user = User(telegram_id=tid, username=None, role="support")
                session.add(user)
            else:
                user.role = "support"
            assigned.append(str(tid))
        session.commit()
        await update.message.reply_text(translations["en"]["assigned"] + ", ".join(assigned))
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def unassign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    session = SessionLocal()
    try:
        args = context.args
        if not args:
            await update.message.reply_text(translations["en"]["no_valid_user"])
            return
        removed = []
        for arg in args:
            try:
                tid = int(arg)
            except Exception:
                try:
                    chat = await context.bot.get_chat(arg)
                    tid = chat.id
                except Exception:
                    continue
            user = session.query(User).filter(User.telegram_id == tid).first()
            if user and user.role == "support":
                user.role = "user"
                removed.append(str(tid))
        session.commit()
        await update.message.reply_text(translations["en"]["removed"] + ", ".join(removed))
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    session = SessionLocal()
    try:
        support_users = session.query(User).filter(User.role == "support").all()
        text = ""
        for user in support_users:
            count = session.query(Ticket).filter(Ticket.claimed_by == user.telegram_id).count()
            text += "{}: {}\n".format(user.telegram_id, count)
        if not text:
            text = translations["en"]["no_stats"]
        await update.message.reply_text(text)
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def confidential(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    session = SessionLocal()
    try:
        support_users = session.query(User).filter(User.role == "support").all()
        text = "Support: {}\n".format([u.telegram_id for u in support_users])
        await update.message.reply_text(text)
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def tickets_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    session = SessionLocal()
    try:
        tickets = session.query(Ticket).filter(Ticket.status.in_(["unclaimed", "claimed", "escalated"])).all()
        text = "\n".join(["ID: {} Status: {}".format(t.id, t.status) for t in tickets])
        if not text:
            text = "No unresolved tickets."
        await update.message.reply_text(text)
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def search_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    session = SessionLocal()
    try:
        query = " ".join(context.args)
        if not query:
            await update.message.reply_text("Provide search query.")
            return
        tickets = session.query(Ticket).filter(Ticket.content.ilike(f"%{query}%")).all()
        text = "\n".join(["ID: {} Content: {}".format(t.id, t.content[:50]) for t in tickets])
        if not text:
            text = "No tickets found."
        await update.message.reply_text(text)
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def reply_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    try:
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /reply <ticket_id> <message>")
            return
        ticket_id = int(context.args[0])
        reply_text = " ".join(context.args[1:])
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            await update.message.reply_text("Ticket not found.")
            return
        user = session.query(User).filter(User.id == ticket.user_id).first()
        if not user:
            await update.message.reply_text("User not found.")
            return
        await context.bot.send_message(chat_id=user.telegram_id, text=reply_text)
        await update.message.reply_text(translations["en"]["reply_sent"])
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def close_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    try:
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /close <ticket_id>")
            return
        ticket_id = int(context.args[0])
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            await update.message.reply_text("Ticket not found.")
            return
        ticket.status = "closed"
        session.commit()
        user = session.query(User).filter(User.id == ticket.user_id).first()
        if user:
            await context.bot.send_message(chat_id=user.telegram_id, text=translations["en"]["ticket_closed"])
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def rate_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    try:
        if len(context.args) < 2:
            await update.message.reply_text(translations["en"]["enter_rating"])
            return
        ticket_id = int(context.args[0])
        rating_value = int(context.args[1])
        feedback = " ".join(context.args[2:]) if len(context.args) > 2 else ""
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            await update.message.reply_text("Ticket not found.")
            return
        if ticket.status != "closed":
            await update.message.reply_text("Ticket is not closed.")
            return
        if not (1 <= rating_value <= 5):
            await update.message.reply_text("Rating must be 1-5.")
            return
        r = Rating(ticket_id=ticket.id, rating=rating_value, feedback=feedback)
        session.add(r)
        session.commit()
        await update.message.reply_text("Thank you for your feedback.")
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    try:
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /setlang <language_code>")
            return
        lang = context.args[0]
        user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
        if not user:
            user = User(telegram_id=update.effective_user.id, username=update.effective_user.username, role="user", language=lang)
            session.add(user)
        else:
            user.language = lang
        session.commit()
        await update.message.reply_text("Language set to {}".format(lang))
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
@safe_execute
async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    session = SessionLocal()
    try:
        total_tickets = session.query(Ticket).count()
        claimed_tickets = session.query(Ticket).filter(Ticket.status == "claimed").count()
        response_time = "N/A"
        text = translations["en"]["dashboard"].format(tickets=f"{claimed_tickets}/{total_tickets}", response_time=response_time)
        await update.message.reply_text(text)
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()
