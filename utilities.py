import time
from functools import wraps
rate_limit_store = {}
def rate_limit(limit: int, per: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            now = time.time()
            times = rate_limit_store.get(user_id, [])
            times = [t for t in times if now - t < per]
            if len(times) >= limit:
                return
            times.append(now)
            rate_limit_store[user_id] = times
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator
def safe_execute(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            import logging
            logging.exception("Error")
    return wrapper
translations = {
    "en": {
        "ticket_forwarded": "Your message has been forwarded to our support team.",
        "no_valid_user": "No valid users assigned.",
        "assigned": "Assigned: ",
        "removed": "Removed: ",
        "not_authorized": "Not authorized",
        "already_claimed": "Already claimed",
        "dashboard": "Dashboard\nTickets: {tickets}\nResponse Time: {response_time}",
        "no_stats": "No stats available.",
        "new_ticket": "Ticket from {name} (ID: {id}):\n{content}",
        "claimed_by": "Claimed by {name}",
        "ticket_closed": "Ticket closed. Please rate the support.",
        "enter_rating": "Please enter a rating (1-5) and feedback separated by a space.",
        "reply_sent": "Your reply has been sent."
    },
    "es": {
        "ticket_forwarded": "Tu mensaje ha sido reenviado a nuestro equipo de soporte.",
        "no_valid_user": "Ningún usuario válido asignado.",
        "assigned": "Asignado: ",
        "removed": "Eliminado: ",
        "not_authorized": "No autorizado",
        "already_claimed": "Ya reclamado",
        "dashboard": "Panel\nTickets: {tickets}\nTiempo de respuesta: {response_time}",
        "no_stats": "No hay estadísticas disponibles.",
        "new_ticket": "Ticket de {name} (ID: {id}):\n{content}",
        "claimed_by": "Reclamado por {name}",
        "ticket_closed": "Ticket cerrado. Por favor califica el soporte.",
        "enter_rating": "Ingresa una calificación (1-5) y comentarios separados por un espacio.",
        "reply_sent": "Tu respuesta ha sido enviada."
    }
}
