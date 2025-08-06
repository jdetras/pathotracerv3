#!/usr/bin/env python3
"""
Simple Setup Script for PathoTracer v2
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("PathoTracer v2 Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create directories
    print("\n📁 Creating directories...")
    directories = [
        'config', 'database', 'models', 'utils', 'data', 
        'backups', 'logs', 'temp', 'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    # Create __init__.py files
    print("\n📝 Creating Python packages...")
    init_files = [
        'database/__init__.py',
        'models/__init__.py', 
        'utils/__init__.py',
        'config/__init__.py'
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"   ✅ {init_file}")
    
    # Create requirements.txt
    print("\n📋 Creating requirements.txt...")
    requirements = """streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.21.0
plotly>=5.15.0
psycopg2-binary>=2.9.0
sqlalchemy>=1.4.0
scikit-learn>=1.3.0
scipy>=1.9.0
openpyxl>=3.0.0
reportlab>=3.6.0
matplotlib>=3.5.0
seaborn>=0.11.0
Pillow>=9.0.0
python-dotenv>=0.19.0
python-dateutil>=2.8.0"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("   ✅ requirements.txt created")
    
    # Create .env template
    print("\n🔧 Creating environment template...")
    env_template = """# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pathotracer
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here

# Application Settings
PATHOTRACER_DEBUG=false
PATHOTRACER_LOG_LEVEL=INFO"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    print("   ✅ .env.template created")
    
    # Create docker-compose.yml
    print("\n🐳 Creating Docker configuration...")
    docker_compose = """version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: pathotracer
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: pathotracer123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  pathotracer:
    build: .
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      POSTGRES_DB: pathotracer
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: pathotracer123
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./backups:/app/backups
      - ./logs:/app/logs
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose)
    print("   ✅ docker-compose.yml created")
    
    # Create Dockerfile
    dockerfile = """FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data models backups logs temp

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)
    print("   ✅ Dockerfile created")
    
    # Create .gitignore
    print("\n📝 Creating .gitignore...")
    gitignore = """__pycache__/
*.py[cod]
*.so
.Python
build/
dist/
*.egg-info/
.env
config/pathotracer_config.json
logs/*.log
temp/*
backups/*.sql
models/*.pkl
models/*.h5
data/uploads/*
.DS_Store
Thumbs.db
.pytest_cache/
.coverage"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore)
    print("   ✅ .gitignore created")
    
    # Create sample data
    print("\n📊 Creating sample data...")
    sample_data = """sample_id,location_name,variety_name,pathogen_name,confidence_score,risk_level,severity,affected_area,temperature,humidity,rainfall
SAMPLE001,Field A,IR64,Magnaporthe oryzae,0.85,High,7,35,25.5,85,15.2
SAMPLE002,Field B,PSB Rc82,Rhizoctonia solani,0.92,High,8,45,28.0,90,8.5
SAMPLE003,Field A,NSIC Rc222,Xanthomonas oryzae,0.78,Medium,5,20,32.1,78,22.1"""
    
    with open('data/sample_diagnoses.csv', 'w') as f:
        f.write(sample_data)
    print("   ✅ Sample data created")
    
    # Create README
    print("\n📖 Creating README...")
    readme = """# PathoTracer v2 - Python Implementation

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
"""
    
    with open('README.md', 'w') as f:
        f.write(readme)
    print("   ✅ README.md created")
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    
    print("\n🚀 Next Steps:")
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("")
    print("2. Copy and configure environment:")
    print("   cp .env.template .env")
    print("   # Edit .env with your database settings")
    print("")
    print("3. Run the application:")
    print("   streamlit run main.py")
    print("")
    print("🐳 Alternative - Use Docker:")
    print("   docker-compose up -d")
    print("   # Access at http://localhost:8501")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)