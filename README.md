# PathoTracer v2 - Python Implementation

Rice Disease Decision Support System converted from R Shiny to Python/PostgreSQL.

## Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database:**
   ```bash
   cp .env.template .env
   # Edit .env with your database settings
   ```

3. **Run Application:**
   ```bash
   streamlit run main.py
   ```

## Docker Installation

```bash
docker-compose up -d
```

Access at: http://localhost:8501

## Features

- Disease diagnostics with ML models
- Resistance profile analysis
- Environmental impact analysis
- Interactive dashboard
- PDF report generation
- PostgreSQL database integration

## Project Structure

- `main.py` - Main Streamlit application
- `database/` - Database management
- `models/` - ML models for pathogen prediction
- `utils/` - Data processing utilities
- `config/` - Configuration management
- `data/` - Data storage
- `models/` - Trained models
