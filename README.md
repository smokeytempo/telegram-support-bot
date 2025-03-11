# Telegram Support Bot

A **production-ready Telegram support bot** designed to streamline **customer support operations** while ensuring **privacy and security**. Users can submit **support tickets** directly through the bot, which are forwarded to an **anonymized support team**. The bot allows the owner to **assign/unassign support agents, view statistics, and manage tickets**—all while maintaining strict **privacy standards**.

## 🚀 Features

- **🔒 Anonymized Communication:** Support agents and users do not see each other's real identities.
- **📩 Ticket System:** Users create support tickets that are automatically forwarded to assigned support team members.
- **📝 Claim & Assign Tickets:** Agents can **claim tickets** via inline buttons, updating ticket status in real-time.
- **🛠️ Role-Based Commands:** Owner-only commands for **team management, ticket insights, and administrative controls**.
- **🔎 Advanced Ticket Management:** List, search, reply to, close, and **rate tickets** seamlessly.
- **🌍 Multilingual Support:** Built-in translation system for a better user experience.
- **⚡ Asynchronous Processing:** Uses **Celery** to handle long-running tasks like ticket escalation.
- **🛡️ Enhanced Security & Privacy:** Minimal data retention, ephemeral storage of sensitive data, and **secure routing**.
- **📊 Detailed Statistics & Analytics:** Track **support team performance** with real-time data.
- **📌 Modular Codebase:** Organized into **scalable modules** for easy maintainability.

## 🏗️ Project Structure

```
📂 telegram-support-bot/
├── config.py          # Loads environment configurations
├── db.py              # SQLAlchemy models and database setup
├── utilities.py       # Helper functions (rate limiting, safe execution, translations)
├── tasks.py           # Celery tasks for async operations
├── handlers.py        # Telegram command and message handlers
├── main.py            # Entry point for running the bot
└── README.md          # Documentation
```

## 📌 Prerequisites

- **Python 3.8+**
- **A SQLAlchemy-supported database** (PostgreSQL, MySQL, SQLite)
- **Redis** (for Celery message broker)
- **Telegram Bot API token**
- **Bot owner Telegram ID**

## 📥 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/smokeytempo/telegram-support-bot.git
cd telegram-support-bot
```

### 2️⃣ Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Environment Variables

Create a `.env` file or export the following variables:

```ini
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
OWNER_ID=YOUR_TELEGRAM_ID
DATABASE_URL=YOUR_DATABASE_CONNECTION_STRING
WEBHOOK_URL=YOUR_WEBHOOK_URL
WEBHOOK_PORT=YOUR_WEBHOOK_PORT
WEBHOOK_LISTEN=YOUR_SERVER_LISTEN_IP
REDIS_URL=YOUR_REDIS_CONNECTION_STRING
```

### 5️⃣ Initialize the Database

```bash
python -c "from db import init_db; init_db()"
```

## 🚀 Running the Bot

### **Webhook Mode** (Recommended for Production)
Ensure your `WEBHOOK_URL` is accessible, then start:

```bash
python main.py
```

### **Polling Mode** (Alternative Mode)
Modify `main.py` to use polling:

```python
await app.run_polling()
```

Then run:

```bash
python main.py
```

### **Running the Celery Worker**

Start the Celery worker process:

```bash
celery -A tasks.celery_app worker --loglevel=info
```

## ⚙️ Commands Overview

### 👑 **Owner-Only Commands**

- `/assign <user_id|username>` - Assign a user as a **support team member**.
- `/unassign <user_id|username>` - Remove a user from the **support team**.
- `/stats` - View **support team performance statistics**.
- `/confidential` - Access **restricted support team data**.
- `/tickets` - List **all unresolved support tickets**.
- `/search <query>` - Search tickets based on **keywords**.
- `/dashboard` - View an **aggregated team performance dashboard**.

### 🛠️ **Support Agent Commands**

- `/reply <ticket_id> <message>` - **Reply** to a user support ticket.
- `/close <ticket_id>` - **Close** an active support ticket.
- `/rate <ticket_id> <rating> [feedback]` - **Rate** the support interaction.
- `/setlang <language_code>` - **Set language preference** for multilingual support.

## 🔐 Privacy & Security Features

- **🚫 Anonymity:** Users and support agents interact **without revealing identities**.
- **🔍 Secure Data Handling:** Stores **only necessary, pseudonymous** data.
- **♻️ Ephemeral Storage:** **Sensitive messages auto-expire** after ticket resolution.
- **🔒 Secure Routing:** Messages pass through a **secured proxy layer** to remove metadata.

## 🌍 Deployment (Production-Ready)

For 24/7 uptime, use **PM2**:

```bash
npm install -g pm2
pm2 start main.py --name "telegram-support-bot"
```

## 🤝 Contributing

We welcome contributions! Please **fork the repository** and submit a **pull request**. Ensure your code:
- Adheres to **best practices**
- Includes **test coverage**
- Follows the **project’s coding standards**

## 📜 License

This project is licensed under the **MIT License**.

---

Built with ❤️ using **Python, Telegram API, SQLAlchemy, Celery, and Redis**.

---

### ⭐ Star this project to support ongoing improvements! 🚀
