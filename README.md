# Project Skim

A microservices-based news article aggregation and summarization system that collects articles from RSS feeds, scrapes their content, and generates AI-powered summaries using Large Language Models.

## 🚀 Features

- **RSS Feed Aggregation**: Collects articles from multiple news sources (Times of India, The Hindu, India Today, BBC)
- **Web Scraping**: Extracts full article content from URLs
- **AI-Powered Summarization**: Uses Facebook's BART model to generate concise article summaries
- **Message Queue Processing**: Asynchronous processing using RabbitMQ
- **Database Storage**: PostgreSQL for persistent storage
- **Modular Architecture**: Microservices design with independent services

## 📋 Architecture

The system consists of three main microservices that work together:

```
RSS Feeds → Database → Queue → Scraper → Queue → LLM Summarizer → Database
```

### Service Flow

1. **RSS Service (kalinga)**: Aggregates RSS feeds and stores article metadata
2. **Scraping Service (bundelkhand)**: Fetches full article content from URLs
3. **Summarization Service (amarkantak)**: Generates AI-powered summaries

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Database**: PostgreSQL (via SQLAlchemy)
- **Message Queue**: RabbitMQ
- **ML/AI**: Transformers (HuggingFace), PyTorch, BART model
- **Web Scraping**: Scrapy, BeautifulSoup4
- **Database Migrations**: Alembic
- **Containerization**: Docker Compose

## 📦 Prerequisites

- Python 3.8+
- PostgreSQL 15+
- RabbitMQ
- Docker and Docker Compose (optional, for containerized setup)
- `uv` package manager (or pip/venv)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project_skim
   ```

2. **Create a virtual environment**
   ```bash
   make create_venv
   # or manually:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/skim
   ```

5. **Start infrastructure services**

   Start PostgreSQL:
   ```bash
   docker-compose -f docker-compose-db.yml up -d
   ```

   Start RabbitMQ:
   ```bash
   docker-compose -f docker-compose-msg-queue.yml up -d
   ```

6. **Run database migrations**
   ```bash
   make apply-db
   # or manually:
   alembic upgrade head
   ```

## ⚙️ Configuration

### Database Configuration

The database connection is configured via the `DATABASE_URL` environment variable:
```
postgresql://<user>:<password>@<host>:<port>/<database>
```

### Model Configuration

The LLM model settings are in `config/constants.py`:
- Model: `facebook/bart-large-cnn`
- Token size: 1024
- Chunk size: 300
- Device: Auto (GPU if available, else CPU)

### RSS Feed Sources

Configure RSS feed URLs in `rss_feeds/config/feed_urls.py`:
- Times of India
- The Hindu
- India Today
- BBC News

### Message Queues

Queue names are defined in `config/config.py`:
- `rss_to_scraping`: Queue from RSS service to scraper
- `scraping_to_summmarisation`: Queue from scraper to summarization service

### RabbitMQ Access

- Management UI: http://localhost:15672
- Default credentials: `admin` / `admin`
- Port: 5672

## 🚦 Usage

### Running Individual Services

Run RSS feed aggregation service:
```bash
make run-rss
# or manually:
python main.py kalinga
```

Run scraping service:
```bash
make run-scrap
# or manually:
python main.py bundelkhand
```

Run summarization service:
```bash
make run-summ
# or manually:
python main.py amarkantak
```

### Running All Services

```bash
make run-all
# or manually:
python main.py mahabharat
```

### Database Migrations

Generate a new migration:
```bash
make gen-db NAME="description_of_change"
# or manually:
alembic revision --autogenerate -m "description_of_change"
```

Apply migrations:
```bash
make apply-db
# or manually:
alembic upgrade head
```

### Generate Requirements

Update requirements.txt:
```bash
make gen-req
```

## 📁 Project Structure

```
project_skim/
├── article_extractors/     # Article extraction modules
├── config/                 # Configuration files
│   ├── config.py          # Service and queue names
│   ├── constants.py       # Model configuration and prompts
│   └── env.py             # Environment variable handling
├── curncher/              # Task management
├── database/              # Database related code
│   ├── models/           # SQLAlchemy models
│   ├── repository/       # Data access layer
│   └── connection.py     # Database connection handler
├── llm_explorer/          # LLM summarization service
│   ├── main.py           # Service entry point
│   ├── model_handler.py  # Model loading and inference
│   └── helpers.py        # Utility functions
├── migrations/            # Alembic database migrations
├── msg_queue/             # Message queue handlers
├── rss_feeds/             # RSS feed aggregation service
│   ├── parsers/          # RSS feed parsers for different sources
│   ├── core/             # Core aggregation logic
│   └── main.py           # Service entry point
├── scraper/               # Web scraping service
│   ├── pre_processing/   # Article preprocessing modules
│   └── main.py           # Service entry point
├── docker-compose-db.yml           # PostgreSQL Docker setup
├── docker-compose-msg-queue.yml    # RabbitMQ Docker setup
├── main.py                # Main entry point for all services
├── Makefile              # Convenience commands
└── requirements.txt      # Python dependencies
```

## 🔍 Services Details

### RSS Service (kalinga)

- Fetches articles from configured RSS feeds
- Parses feed data using source-specific parsers
- Stores article metadata in the `raw_articles` table
- Publishes articles to the scraping queue

### Scraping Service (bundelkhand)

- Consumes articles from the RSS queue
- Scrapes full article content from URLs
- Handles source-specific preprocessing (e.g., TOI preprocessing)
- Stores article data in the `summarized_articles` table
- Publishes article body to the summarization queue

### Summarization Service (amarkantak)

- Consumes articles from the scraping queue
- Uses BART model to generate summaries
- Handles long articles by chunking when necessary
- Updates articles in the database with summaries

## 🗄️ Database Schema

### Tables

- **raw_articles**: Stores initial RSS feed article metadata
  - id, title, article_url, source, image_url, published_date, processed

- **summarized_articles**: Stores scraped articles with summaries
  - id, title, article_url, source, body, img_src, published_date, category_id, raw_article_id

- **article_category**: Categories for articles
  - id, name, logo_src, description

## 🔐 Environment Variables

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string

## 📝 Notes

- The system processes articles asynchronously through message queues
- Long articles are automatically chunked before summarization
- The BART model requires sufficient GPU memory for optimal performance
- All services log their activities for debugging and monitoring


## 👤 Author

[Bhanupratap Singh](https://github.com/wantedbear007)
[Suraj Pratap Singh](https://github.com/Spsden)


