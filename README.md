# Google Trends Website Builder

An automated system for analyzing Google Trends data and generating insights for website development.

## Project Structure

```
├── src/
│   ├── models/          # Data models and core types
│   ├── services/        # Business logic services
│   ├── database/        # Database operations
│   ├── api/            # FastAPI REST API
│   ├── web/            # Streamlit web dashboard
│   ├── config.py       # Configuration management
│   └── main.py         # Main application entry point
├── tests/              # Test files
├── requirements.txt    # Production dependencies
├── requirements-dev.txt # Development dependencies
├── pyproject.toml      # Project configuration
└── .env.example        # Environment variables example
```

## Setup

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

### 3. Database Setup

```bash
# PostgreSQL setup (install PostgreSQL first)
createdb trends_db

# Redis setup (install Redis first)
redis-server
```

## Running the Application

### API Server
```bash
python -m src.api.main
# or
uvicorn src.api.main:app --reload
```

### Web Dashboard
```bash
streamlit run src/web/dashboard.py
```

### Main Application
```bash
python -m src.main
```

## Development

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### Testing
```bash
# Run tests
pytest

# With coverage
pytest --cov=src
```

## Core Interfaces

The system is built around these core interfaces:

- `ITrendsDataService`: Google Trends data collection
- `IAnalysisService`: Keyword analysis and evaluation
- `IDataRepository`: Data storage operations
- `ICacheService`: Caching operations
- `IRateLimiter`: Request rate limiting

## Data Models

- `TrendKeyword`: Trending keyword data
- `KeywordAnalysis`: Analysis results
- `TrendsReport`: Complete analysis reports
- `DomainInfo`: Domain availability information

## Next Steps

1. Implement data models and validation (Task 2)
2. Implement Google Trends data collection (Task 3)
3. Develop analysis services (Task 4)
4. Create data storage layer (Task 5)
5. Build web dashboard (Task 6)
6. Implement API endpoints (Task 7)

## License

MIT License