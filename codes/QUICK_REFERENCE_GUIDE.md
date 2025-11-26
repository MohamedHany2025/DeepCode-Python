# QUICK REFERENCE GUIDE - DeepCode Python Projects
# Fast lookup for common tasks and patterns

## 📋 Table of Contents
- [Project Quick Access](#quick-access)
- [Installation Commands](#installation)
- [Common Patterns](#patterns)
- [Troubleshooting](#troubleshooting)
- [Performance Tips](#performance)

---

## Quick Access <a name="quick-access"></a>

### FastAPI Dashboard
- **File**: `fastapi_dashboard.py`
- **Dependencies**: FastAPI, SQLAlchemy, psycopg2
- **Language**: Python
- **Main Concepts**: REST API, JWT Auth, Database
- **Start Command**: `uvicorn fastapi_dashboard:app --reload`

### Web Scraper Pro
- **File**: `web_scraper_pro.py`
- **Dependencies**: aiohttp, BeautifulSoup4
- **Language**: Python
- **Main Concepts**: Async/Await, Rate Limiting, Data Transform
- **Start Command**: `python web_scraper_pro.py`

### ML Image Classifier
- **File**: `ml_image_classifier.py`
- **Dependencies**: TensorFlow, numpy, matplotlib
- **Language**: Python
- **Main Concepts**: Transfer Learning, CNN, Deep Learning
- **Start Command**: Run training in notebook or script

### ORM Framework
- **File**: `orm_framework.py`
- **Dependencies**: sqlite3, typing
- **Language**: Python
- **Main Concepts**: Database abstraction, Query Builder
- **Start Command**: Import as library

### Deployment Automation
- **File**: `deployment_automation.py`
- **Dependencies**: docker, kubernetes, pyyaml
- **Language**: Python
- **Main Concepts**: CI/CD, Docker, K8s
- **Start Command**: `asyncio.run(deploy())`

### NLP Text Analyzer
- **File**: `nlp_text_analyzer.py`
- **Dependencies**: nltk, spacy, scikit-learn
- **Language**: Python
- **Main Concepts**: NLP, Sentiment, Entity Recognition
- **Start Command**: `analyzer = TextAnalyzer()`

---

## Installation Commands <a name="installation"></a>

### Complete Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Download required ML models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt')"
```

### Project-Specific Installations

```bash
# FastAPI Dashboard only
pip install fastapi uvicorn sqlalchemy psycopg2 python-jose passlib

# Web Scraper only
pip install aiohttp beautifulsoup4 lxml

# ML Classifier only
pip install tensorflow numpy opencv-python pillow matplotlib

# NLP Analyzer only
pip install nltk spacy scikit-learn

# Deployment only
pip install docker kubernetes pyyaml httpx
```

---

## Common Patterns <a name="patterns"></a>

### Async Function Pattern

```python
import asyncio

async def async_operation():
    # Your async code here
    await asyncio.sleep(1)
    return "Result"

# Run it
result = asyncio.run(async_operation())
```

### Database Query Pattern

```python
from orm_framework import Model, Database

db = Database("app.db")

class User(Model):
    __tablename__ = "users"

User.set_database(db)

# CRUD operations
users = User.all()
user = User.find(1)
user.save()
user.delete()
```

### API Endpoint Pattern

```python
from fastapi import FastAPI, Depends

app = FastAPI()

async def get_current_user(token: str):
    # Verify token
    return user

@app.get("/api/endpoint")
async def endpoint(user = Depends(get_current_user)):
    return {"data": user}
```

### Model Training Pattern

```python
from ml_image_classifier import ImageClassifier

classifier = ImageClassifier()
classifier.build_model()
classifier.compile_model()
classifier.train(X_train, y_train, X_val, y_val)
metrics = classifier.evaluate(X_test, y_test)
classifier.save_model()
```

### Web Scraping Pattern

```python
import asyncio
from web_scraper_pro import WebScraper

async def scrape():
    async with WebScraper(config) as scraper:
        result = await scraper.scrape(url, extractors)
        return result

asyncio.run(scrape())
```

### Text Analysis Pattern

```python
from nlp_text_analyzer import TextAnalyzer

analyzer = TextAnalyzer()
result = analyzer.analyze(text)

sentiment = result.sentiment
entities = result.named_entities
summary = result.summary
keywords = result.keywords
```

---

## Troubleshooting <a name="troubleshooting"></a>

### Issue: "ModuleNotFoundError: No module named 'X'"
**Solution**: 
```bash
pip install module_name
pip list  # Verify installation
```

### Issue: "Connection refused" (Database)
**Solution**:
```bash
# Check database service
psql -U user -d database  # PostgreSQL
sqlite3 app.db           # SQLite
```

### Issue: "CUDA not found" (ML projects)
**Solution**:
```bash
# Install CPU version
pip install tensorflow-cpu

# Or GPU version (requires CUDA)
pip install tensorflow
```

### Issue: "Port already in use"
**Solution**:
```bash
# Change port
uvicorn fastapi_dashboard:app --port 8001

# Or find and kill process
lsof -i :8000
kill -9 <PID>
```

### Issue: "Out of memory" (ML training)
**Solution**:
```python
# Reduce batch size
config.batch_size = 8  # Instead of 32

# Use data generators
classifier.train_generator(generator)
```

### Issue: "Timeout" (Web Scraping)
**Solution**:
```python
config = ScraperConfig()
config.timeout = 30      # Increase timeout
config.max_retries = 5   # More retries
```

---

## Performance Tips <a name="performance"></a>

### FastAPI Performance

```python
# Use async functions
@app.get("/")
async def fast_endpoint():
    pass

# Add caching
from fastapi_cache import cached

@cached(expire=3600)
@app.get("/cache-me")
async def cached_endpoint():
    pass
```

### Database Performance

```python
# Use indexing
Column("email", "TEXT", unique=True, index=True)

# Batch operations
for record in records:
    record.save()

# Use joins instead of N+1 queries
query = "SELECT * FROM users JOIN posts ON users.id = posts.user_id"
```

### ML Model Performance

```python
# Use GPU
import tensorflow as tf
tf.config.list_physical_devices('GPU')

# Reduce model size
classifier.build_model(use_pretrained=True)  # Transfer learning

# Batch prediction
results = classifier.predict_batch(images)
```

### Web Scraping Performance

```python
# Concurrent requests
await asyncio.gather(*tasks)

# Rate limiting
config.rate_limit_requests = 100

# Efficient parsing
soup.select_one("selector")  # Single element
soup.select("selector")      # Multiple elements
```

### NLP Performance

```python
# Cache results
@lru_cache(maxsize=1000)
def analyze_text(text):
    return analyzer.analyze(text)

# Batch processing
results = [analyzer.analyze(t) for t in texts]
```

---

## Environment Variables Template

Create `.env` file:

```
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname
DB_ECHO=False

# API
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log

# Deployment
DOCKER_REGISTRY=docker.io
KUBERNETES_CONTEXT=minikube
NAMESPACE=default

# API Keys
API_KEY=your-api-key
API_SECRET=your-api-secret
```

---

## File Structure Summary

```
codes/
├── Python Projects (6 files)
│   ├── fastapi_dashboard.py           (FastAPI REST API)
│   ├── web_scraper_pro.py            (Async Web Scraper)
│   ├── ml_image_classifier.py         (Deep Learning)
│   ├── orm_framework.py               (Database ORM)
│   ├── deployment_automation.py       (CI/CD Pipeline)
│   └── nlp_text_analyzer.py          (NLP Processing)
│
├── Documentation (4 files)
│   ├── README.md                      (Main documentation)
│   ├── TUTORIALS_AND_GUIDES.md        (6 complete tutorials)
│   ├── PROJECT_DOCUMENTATION.md       (Detailed project guides)
│   └── BEST_PRACTICES_GUIDE.md        (Professional practices)
│
└── Quick Reference (this file)
    └── QUICK_REFERENCE_GUIDE.md
```

---

## Useful Commands Cheat Sheet

### Python/Virtual Environment
```bash
python -m venv venv           # Create virtual env
source venv/bin/activate      # Activate (Linux/Mac)
venv\\Scripts\\activate        # Activate (Windows)
pip install -r requirements.txt
pip freeze > requirements.txt
```

### Git
```bash
git clone <repo-url>
git add .
git commit -m "message"
git push origin main
git pull origin main
```

### FastAPI
```bash
uvicorn main:app --reload           # Development
uvicorn main:app --host 0.0.0.0    # Production
```

### Docker
```bash
docker build -t image-name .
docker run -d -p 8000:8000 image-name
docker ps
docker logs container-id
```

### Kubernetes
```bash
kubectl apply -f deployment.yaml
kubectl get deployments
kubectl scale deployment myapp --replicas=3
kubectl rollout status deployment/myapp
kubectl rollout undo deployment/myapp
```

### Testing
```bash
pytest tests/
pytest tests/ -v
pytest tests/ --cov=src
pytest tests/test_file.py::TestClass::test_method
```

---

## Debugging Tips

### Python Debugger

```python
import pdb

pdb.set_trace()  # Stop here
# In debugger: c=continue, n=next, l=list, p=print

# Or use breakpoint() in Python 3.7+
breakpoint()
```

### Logging Debug

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### API Testing

```bash
# Using curl
curl -X GET http://localhost:8000/api/endpoint

# Using httpie
http GET http://localhost:8000/api/endpoint

# Using Python requests
import requests
response = requests.get("http://localhost:8000/api/endpoint")
```

---

## Resources Summary

### Documentation Files
- **README.md** - Main overview and quick start
- **TUTORIALS_AND_GUIDES.md** - 6 comprehensive tutorials
- **PROJECT_DOCUMENTATION.md** - Detailed project guides
- **BEST_PRACTICES_GUIDE.md** - Professional development guide
- **QUICK_REFERENCE_GUIDE.md** - This file

### Project Files
1. **fastapi_dashboard.py** (380+ lines) - REST API with authentication
2. **web_scraper_pro.py** (300+ lines) - Intelligent web scraping
3. **ml_image_classifier.py** (400+ lines) - Deep learning models
4. **orm_framework.py** (350+ lines) - Database abstraction
5. **deployment_automation.py** (300+ lines) - CI/CD automation
6. **nlp_text_analyzer.py** (350+ lines) - NLP processing

---

## Next Steps

1. **Read** the main `README.md`
2. **Choose** a project that interests you
3. **Read** the detailed guide in `PROJECT_DOCUMENTATION.md`
4. **Install** dependencies
5. **Run** the examples
6. **Modify** and experiment
7. **Build** your own projects

---

## Support & Contact

- **YouTube**: [@DeepCode-Python](https://www.youtube.com/@DeepCode-Python)
- **GitHub**: [deepcode-python](https://github.com/deepcode-python)
- **Email**: contact@deepcode.com
- **LinkedIn**: [DeepCode Python](https://linkedin.com/company/deepcode-python)

---

**Last Updated**: November 2025  
**Version**: 1.0.0  
**License**: MIT
