# MonthVest — Multi-User Investment Tracking Platform

> A multi-user web platform for tracking personal investments, monitoring real-time stock prices, and analysing portfolio trends over time.

---

## 📌 One-Paragraph Description

**Recruiter-friendly:**
MonthVest is a web application where multiple users can track their investment portfolios, view real-time stock prices, and analyse how their investments have performed over time. Each user's data is completely isolated from other users, and the platform fetches live stock prices from a third-party API. It is built with Node.js and Express on the backend and uses Supabase (PostgreSQL) as the database, tested with 20 user accounts to verify concurrent data isolation.

**Technical:**
MonthVest is a REST API-backed investment tracking platform built on Node.js/Express with a Supabase (PostgreSQL) relational backend. The schema enforces strict per-user data isolation at the database level, preventing cross-account data leakage under concurrent access. A decoupled data-fetching layer integrates third-party real-time stock price APIs, isolating external failures from the presentation layer. Consent-based historical logging enables trend analysis with storage-aware query design, validated across 20 mock user accounts.

---

## What Problem It Solves

Most individuals track investments across spreadsheets or disconnected apps with no historical trend visibility. MonthVest centralises:
- Investment records across multiple assets in one place
- Real-time price data without manual lookup
- Historical performance trends over time
- Multi-user access with strict data privacy between accounts

---

## ✨ Key Features

- **Multi-user architecture** — each user's portfolio is fully isolated; no data leakage across accounts
- **Real-time stock prices** — third-party API integration via a decoupled fetching layer
- **Historical trend logging** — consent-based logging of investment data for trend analysis
- **Concurrent access safe** — tested with 20 user accounts for isolation integrity
- **Decoupled API layer** — external API failures do not crash or corrupt the presentation layer
- **Relational schema** — normalised PostgreSQL schema via Supabase for clean data integrity

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Node.js, Express.js |
| Database | Supabase (PostgreSQL) |
| API Integration | Third-party stock price REST API |
| Language | JavaScript |
| Auth | [Add your auth method here — e.g. Supabase Auth / JWT] |

---

## 🏗 Architecture & Design

```
┌─────────────────────────────────────────────────┐
│                  Frontend / Client               │
│           (Dashboard, Portfolio View)            │
└────────────────────┬────────────────────────────┘
                     │ HTTP / REST
┌────────────────────▼────────────────────────────┐
│            Express.js API Layer                  │
│   /portfolio  │  /prices  │  /history  │  /auth  │
└────────────────────┬────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
┌─────────▼──────┐   ┌──────────▼──────────────────┐
│  Supabase DB   │   │  Stock Price Fetcher Layer   │
│  (PostgreSQL)  │   │  (decoupled from API layer)  │
│  per-user RLS  │   │  external API failures       │
│  isolation     │   │  caught here, not upstream   │
└────────────────┘   └─────────────────────────────┘
```

### Key Design Decision — Decoupled Data-Fetching Layer

The stock price fetcher is a separate service module, not called directly from route handlers. This means if the external stock API is down or slow, the error is caught and handled at the fetcher layer — the rest of the API continues serving portfolio and history data without crashing. This pattern is standard in production systems where third-party reliability cannot be guaranteed.

### Per-User Data Isolation

All investment records are scoped to a `user_id` foreign key at the schema level. Supabase Row Level Security (RLS) policies [add if applicable] enforce that users can only read and write their own records — isolation is enforced at the database layer, not just the application layer.

---

## ⚙️ How It Works

1. User registers/logs in and receives an authenticated session
2. User adds investments (asset name, quantity, purchase price, date)
3. The platform fetches the current price of each asset from the stock price API
4. Historical price snapshots are logged on a consent basis for trend analysis
5. The dashboard displays current portfolio value, gain/loss, and trend charts

---

## 📦 Installation

### Prerequisites
- Node.js 18+
- Supabase account (or local Supabase CLI)

### Setup

```bash
# Clone the repository
git clone https://github.com/shrush-04/monthvest.git
cd monthvest

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Fill in your Supabase URL, Supabase anon key, and stock API key

# Start the server
npm start
```

Server runs at `http://localhost:3000`

### Environment Variables

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
STOCK_API_KEY=your_stock_api_key
PORT=3000
```

---

## 🚀 Usage

```bash
# Register a new user
POST /api/auth/register
{ "email": "user@example.com", "password": "yourpassword" }

# Add an investment
POST /api/portfolio
{ "asset": "RELIANCE", "quantity": 10, "purchasePrice": 2450.00 }

# Get current portfolio with live prices
GET /api/portfolio

# Get historical trend for an asset
GET /api/history?asset=RELIANCE
```

---

## 📁 Folder Structure

```
monthvest/
├── src/
│   ├── routes/
│   │   ├── auth.js
│   │   ├── portfolio.js
│   │   └── history.js
│   ├── services/
│   │   ├── stockPriceFetcher.js    # Decoupled external API layer
│   │   └── portfolioService.js
│   ├── middleware/
│   │   └── authMiddleware.js
│   ├── db/
│   │   └── supabaseClient.js
│   └── app.js
├── .env.example
├── package.json
└── README.md
```

---

## 🗄 Database Schema (Simplified)

```sql
-- Users (managed by Supabase Auth)
users (id, email, created_at)

-- Investment records (per-user isolated)
investments (
  id          UUID PRIMARY KEY,
  user_id     UUID REFERENCES users(id),  -- strict per-user scope
  asset       TEXT,
  quantity    NUMERIC,
  purchase_price NUMERIC,
  currency    TEXT DEFAULT 'INR',
  created_at  TIMESTAMPTZ
)

-- Historical price snapshots (consent-based)
price_history (
  id          UUID PRIMARY KEY,
  user_id     UUID REFERENCES users(id),
  asset       TEXT,
  price       NUMERIC,
  recorded_at TIMESTAMPTZ
)
```

---

## 🖼 Screenshots

> 📸 Add your screenshots here.

| Screen | Description |
|---|---|
| `docs/screenshots/dashboard.png` | Portfolio overview dashboard |
| `docs/screenshots/add-investment.png` | Add investment form |
| `docs/screenshots/trend.png` | Historical trend chart |

---

## ✅ TODO (Before Submission)

- [ ] Add `.env.example` file to the repository
- [ ] Add README screenshots
- [ ] Add sample seed data script for demo (20 mock users)
- [ ] Document all API endpoints in `docs/api.md`
- [ ] Add error handling documentation

---

## 🔮 Future Improvements

- Portfolio performance charts (Chart.js / Recharts)
- Email alerts for significant price movements
- Support for mutual funds and crypto assets
- Export portfolio report as PDF
- Multi-currency portfolio support

---

## 💡 Why This Project Matters

Investment tracking is a real, everyday need — and most existing tools are either too complex or don't support multiple family members sharing one platform safely. MonthVest explores the engineering challenges of multi-user data isolation, third-party API reliability, and consent-aware data logging in a practical, relatable domain.

---

## 👩‍💻 My Contribution

I designed and built this project independently. The decision I focused most on was the multi-user data isolation model — it would have been simpler to build a single-user app, but designing the schema and API to support concurrent multi-user access with strict isolation forced me to think carefully about database-level scoping versus application-level filtering. I also chose to decouple the stock price fetcher into its own service layer after encountering rate-limiting errors from the external API — separating it meant I could handle those failures gracefully without affecting the rest of the platform.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built by [Shrushti Mangalekar](https://www.linkedin.com/in/shrushti-mangalekar-bbb016248/) · [GitHub](https://github.com/shrush-04)*
