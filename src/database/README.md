# Database Module

This module provides database schema, connection management, and migration utilities for the Google Trends Website Builder.

## Components

### Models (`models.py`)
- **TrendKeywordModel**: Stores trending keywords with search volume and metadata
- **KeywordDetailsModel**: Detailed keyword information including interest over time
- **DomainInfoModel**: Domain availability and pricing information
- **KeywordAnalysisModel**: Analysis results for keywords including potential scores
- **TrendsReportModel**: Generated reports combining keyword data and analysis
- **DataQualityLog**: Tracks data quality issues and resolutions
- **SystemMetrics**: System performance and monitoring metrics

### Connection Management (`connection.py`)
- **DatabaseManager**: Handles database connections, sessions, and health checks
- Connection pooling with automatic reconnection
- Session management with automatic rollback on errors
- Health check functionality
- Event listeners for monitoring

### Migrations (`migrations.py`)
- **MigrationManager**: Handles database schema migrations
- Version tracking and rollback capabilities
- Built-in migrations for initial schema and indexes
- Data quality constraints

## Setup

### Prerequisites
1. PostgreSQL server running
2. Python dependencies installed: `pip install -r requirements.txt`

### Environment Configuration
Copy `.env.example` to `.env` and configure database settings:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trends_db
DB_USER=postgres
DB_PASSWORD=password
```

### Database Initialization

#### Option 1: Automatic Setup (Recommended)
```bash
python scripts/setup_database.py
```
This script will:
- Create the database if it doesn't exist
- Run all migrations
- Verify the setup

#### Option 2: Manual Setup
1. Create the database:
   ```sql
   CREATE DATABASE trends_db;
   ```

2. Initialize the database:
   ```bash
   python src/database/init_db.py
   ```

## Usage

### Basic Connection
```python
from src.database.connection import db_manager

# Initialize database
db_manager.initialize()

# Use session context manager
with db_manager.get_session() as session:
    # Your database operations here
    keyword = TrendKeywordModel(keyword="python", ...)
    session.add(keyword)
    # Automatic commit on success, rollback on error
```

### Health Check
```python
from src.database.connection import check_database_health

if check_database_health():
    print("Database is healthy")
else:
    print("Database connection issues")
```

### Migrations
```python
from src.database.migrations import run_migrations, get_migration_status

# Run all pending migrations
run_migrations()

# Check migration status
status = get_migration_status()
print(f"Applied: {status['applied_count']}, Pending: {status['pending_count']}")
```

## Database Schema

### Core Tables
- `trend_keywords`: Trending keyword data with search volumes
- `keyword_details`: Detailed keyword information and time series data
- `keyword_analyses`: Analysis results and scoring
- `trends_reports`: Generated reports and recommendations
- `domain_info`: Domain availability and pricing data

### Monitoring Tables
- `data_quality_logs`: Data quality issues tracking
- `system_metrics`: Performance and system metrics
- `schema_migrations`: Migration version tracking

### Indexes
The schema includes optimized indexes for:
- Keyword searches by region and timestamp
- Analysis results by score and competition level
- Time-based queries for trends and reports
- Data quality monitoring

## Testing

Run the database tests:
```bash
python -m pytest tests/test_database.py -v
```

The tests cover:
- Model creation and relationships
- Connection management and pooling
- Session handling and error recovery
- Migration system functionality

## Performance Considerations

- Connection pooling with 10 base connections, 20 overflow
- Automatic connection recycling every hour
- Pre-ping validation to handle stale connections
- Optimized indexes for common query patterns
- JSON columns for flexible metadata storage

## Monitoring

The database module includes built-in monitoring:
- Connection pool status tracking
- Query performance logging (in debug mode)
- Data quality issue logging
- System metrics collection

Access monitoring data through:
```python
info = db_manager.get_connection_info()
print(f"Pool status: {info['pool_info']}")
```