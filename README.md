# Crypto Price Alert Bot

A web application that monitors cryptocurrency prices and sends phone call alerts when target prices are reached using Twilio.

## Features

- Real-time cryptocurrency price monitoring
- Support for multiple popular cryptocurrencies (BTC, ETH, XRP, etc.)
- Customizable price alerts (above/below target price)
- Phone call notifications via Twilio
- User-friendly web interface

## Prerequisites

- Python 3.8 or higher
- Twilio account with:
  - Account SID
  - Auth Token
  - Phone Number
  - Studio Flow SID

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd Crypto-Price-Alert-Bot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Configure your `.env` file with your Twilio credentials:
```
ACCOUNT_SID=your_account_sid
AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone
STUDIO_FLOW_SID=your_studio_flow_sid
```

## Running the Application

Start the server using uvicorn:

```bash
uvicorn asgi:asgi_app --host 0.0.0.0 --port 8000
```

Access the web interface at: `http://localhost:8000`

## Usage

1. Select a cryptocurrency from the dropdown menu
2. Enter your target price in USD
3. Choose whether to alert when price goes above or below target
4. Enter your phone number (in international format: +1234567890)
5. Set the price check interval (in seconds)
6. Click "Start Price Alert Bot" to begin monitoring

## API Endpoints

- `POST /api/start-monitor`: Start price monitoring
- `POST /api/stop-monitor/<monitor_id>`: Stop price monitoring
- `GET /api/status/<monitor_id>`: Get monitor status
- `POST /api/make-test-call`: Make a test call

## Tech Stack

- Backend: Flask/ASGI
- Frontend: HTML, CSS, JavaScript
- Price Data: CoinGecko API
- Notifications: Twilio API

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Use environment variables for sensitive credentials in production
- Implement rate limiting and authentication for production use


