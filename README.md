# Bug Report Telegram Bot

A production-ready Telegram bot for streamlined bug reporting with an intuitive user experience. Built with Python and the python-telegram-bot library.

## Features

- 🎯 **Interactive Bug Reporting** - Step-by-step guided process
- 📸 **Screenshot Support** - Attach multiple screenshots per bug
- 🔐 **User Authorization** - Restrict access to specific Telegram users
- 🌍 **Environment Tracking** - Distinguish between DEV and PROD bugs
- 🎨 **Priority Levels** - LOW, MEDIUM, HIGH, CRITICAL
- 📊 **Statistics** - View overall bug metrics
- 🔄 **Retry Logic** - Resilient API communication with exponential backoff
- 🐳 **Docker Ready** - Easy deployment with Docker Compose

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and instructions |
| `/bug` | Start interactive bug report creation |
| `/mybugs` | View your recent bug reports |
| `/stats` | View overall bug statistics |
| `/help` | Show help message |
| `/cancel` | Cancel current operation |

## Prerequisites

- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Backend API running (see backend requirements)
- Docker & Docker Compose (for containerized deployment)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/vitaliiserbynassisterr/bug-report-bot.git
cd bug-report-bot
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Telegram Bot Token from @BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Backend API Configuration
BACKEND_API_URL=https://api.yourdomain.com/api/v1
BACKEND_INTERNAL_TOKEN=your-backend-token

# Authorized Telegram User IDs (comma-separated)
ALLOWED_USER_IDS=123456789,987654321

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### 3. Get Your Telegram User ID

Send a message to [@userinfobot](https://t.me/userinfobot) to get your Telegram user ID.

### 4. Run with Docker (Recommended)

```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

Stop the bot:
```bash
docker-compose down
```

### 5. Run Locally (Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

## Project Structure

```
telegram-bug-bot/
├── bot.py                  # Main entry point
├── config/
│   └── settings.py         # Configuration & environment variables
├── handlers/
│   ├── start.py            # /start and /help commands
│   ├── bug_report.py       # Bug creation conversation flow
│   ├── my_bugs.py          # /mybugs command
│   └── stats.py            # /stats command
├── services/
│   ├── backend_client.py   # HTTP client for backend API
│   └── bug_formatter.py    # Format bugs for display
├── utils/
│   ├── auth.py             # User authorization checks
│   └── keyboards.py        # Telegram inline keyboards
├── tests/
│   └── test_handlers.py    # Unit tests
├── .env.example            # Environment variables template
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Backend API Requirements

The bot expects the following API endpoints:

### POST `/bugs`
Create a new bug report.

**Request Body:**
```json
{
  "title": "Bug description",
  "environment": "PROD",
  "priority": "HIGH",
  "screenshots": [
    {
      "file_id": "telegram-file-id",
      "file_unique_id": "unique-id",
      "width": 1920,
      "height": 1080,
      "file_size": 123456
    }
  ],
  "console_logs": "Optional console logs",
  "tags": ["UI", "mobile"],
  "reporter": {
    "telegram_id": 123456789,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Response:**
```json
{
  "id": "BUG-042",
  "status": "OPEN",
  "created_at": "2025-11-22T10:30:00Z"
}
```

### GET `/bugs?reporter.telegram_id={user_id}`
Get bugs by Telegram user ID.

**Query Parameters:**
- `reporter.telegram_id`: Telegram user ID
- `limit`: Maximum number of bugs to return
- `sort`: Sort order (e.g., `-created_at` for newest first)

**Response:**
```json
{
  "data": [
    {
      "id": "BUG-042",
      "title": "Transfer button not visible",
      "status": "OPEN",
      "priority": "HIGH",
      "environment": "PROD",
      "created_at": "2025-11-22T10:30:00Z"
    }
  ]
}
```

### GET `/bugs/stats`
Get overall bug statistics.

**Response:**
```json
{
  "total": 150,
  "by_status": {
    "OPEN": 45,
    "IN_PROGRESS": 20,
    "FIXED": 80,
    "CLOSED": 5
  },
  "by_priority": {
    "LOW": 30,
    "MEDIUM": 60,
    "HIGH": 45,
    "CRITICAL": 15
  },
  "by_environment": {
    "DEV": 70,
    "PROD": 80
  }
}
```

## Configuration

### Settings (`config/settings.py`)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | ✅ | - |
| `BACKEND_API_URL` | Backend API base URL | ✅ | - |
| `BACKEND_INTERNAL_TOKEN` | Authentication token for backend | ✅ | - |
| `ALLOWED_USER_IDS` | Comma-separated Telegram user IDs | ✅ | - |
| `LOG_LEVEL` | Logging level | ❌ | INFO |
| `MAX_RETRIES` | API retry attempts | ❌ | 3 |
| `RETRY_DELAY` | Initial retry delay (seconds) | ❌ | 1.0 |
| `RETRY_BACKOFF` | Exponential backoff multiplier | ❌ | 2.0 |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | ❌ | 30 |

## User Flow

1. User sends `/bug`
2. Bot asks for bug description
3. Bot asks for screenshots (can send multiple or skip)
4. Bot shows inline keyboard for environment (DEV/PROD)
5. Bot shows inline keyboard for priority (LOW/MEDIUM/HIGH/CRITICAL)
6. Bot asks for console logs (optional)
7. Bot asks for tags (optional)
8. Bot shows summary with confirmation buttons
9. User confirms → Bug is submitted to backend
10. Bot shows success message with bug ID

## Error Handling

- **Network Errors**: Automatic retry with exponential backoff
- **API Errors**: User-friendly error messages
- **Invalid Input**: Validation with helpful prompts
- **Unauthorized Users**: Polite rejection message

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_handlers.py -k test_start_command
```

## Deployment

### Docker Deployment (Production)

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f telegram-bot

# Restart
docker-compose restart

# Stop
docker-compose down
```

### VPS Deployment

1. Clone repository on VPS
2. Set up `.env` file
3. Run with Docker Compose
4. (Optional) Set up systemd service for auto-restart

### Monitoring

Check bot status:
```bash
docker-compose ps
```

View resource usage:
```bash
docker stats bug-report-bot
```

## Security Considerations

- ✅ User authorization via Telegram user IDs
- ✅ Non-root user in Docker container
- ✅ Environment variables for sensitive data
- ✅ Input validation on all user inputs
- ✅ No file downloads (screenshots stored as Telegram file IDs)
- ✅ Request timeout to prevent hanging
- ✅ Resource limits in Docker Compose

## Troubleshooting

### Bot not responding

1. Check if bot is running: `docker-compose ps`
2. View logs: `docker-compose logs -f`
3. Verify `TELEGRAM_BOT_TOKEN` is correct
4. Ensure bot is started in BotFather

### "Not authorized" message

- Verify your Telegram user ID is in `ALLOWED_USER_IDS`
- Check `.env` file format (comma-separated, no spaces)

### Backend API errors

1. Check `BACKEND_API_URL` is correct
2. Verify `BACKEND_INTERNAL_TOKEN` matches backend
3. Ensure backend is accessible from bot server
4. Check backend logs for errors

### "Failed to submit bug report"

- Check backend API is running
- Verify network connectivity
- Review bot logs for detailed error messages
- Check backend API authentication

## Development

### Adding New Commands

1. Create handler in `handlers/` directory
2. Import handler in `bot.py`
3. Add command handler to application
4. Update README with new command

### Adding New Fields to Bug Report

1. Update conversation states in `handlers/bug_report.py`
2. Add new handler function for the field
3. Update `format_bug_summary()` in `services/bug_formatter.py`
4. Update backend API documentation

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please open an issue on GitHub.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

Built with ❤️ using [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
