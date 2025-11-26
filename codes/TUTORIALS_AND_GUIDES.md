# ADVANCED PYTHON TUTORIALS & GUIDES - DeepCode Python
# Complete Learning Resource for Professional Python Development

## TABLE OF CONTENTS
1. [Mastering Async/Await in Python](#async-await)
2. [Factory & Builder Design Patterns](#design-patterns)
3. [Profiling & Optimizing Python Code](#performance)
4. [Building Scalable APIs with FastAPI](#fastapi)
5. [Data Science Pipeline with Pandas & ML](#data-science)
6. [Writing Testable, Clean Python Code](#clean-code)

---

## 1. MASTERING ASYNC/AWAIT IN PYTHON <a name="async-await"></a>

### Understanding Asynchronous Programming

Asynchronous programming allows your Python code to handle multiple operations concurrently without blocking. This is crucial for I/O-bound operations like:
- API calls
- Database queries
- File operations
- Network requests

### Key Concepts

#### 1.1 Event Loop
The event loop is the core of async programming. It monitors coroutines and switches between them when one is waiting.

```python
import asyncio

async def fetch_data(url):
    \"\"\"Async function to fetch data\"\"\"
    print(f"Fetching {url}")
    await asyncio.sleep(2)  # Simulate network delay
    return f"Data from {url}"

async def main():
    \"\"\"Main async function\"\"\"
    # Run multiple coroutines concurrently
    results = await asyncio.gather(
        fetch_data("https://api1.com"),
        fetch_data("https://api2.com"),
        fetch_data("https://api3.com")
    )
    
    for result in results:
        print(result)

# Run the event loop
asyncio.run(main())
```

#### 1.2 async/await Keywords

- **async**: Declares a coroutine function
- **await**: Pauses execution until the awaitable completes

```python
# Without async/await (blocking)
def slow_operation():
    time.sleep(5)
    return "Done"

result = slow_operation()  # Blocks for 5 seconds

# With async/await (non-blocking)
async def fast_operation():
    await asyncio.sleep(5)  # Doesn't block
    return "Done"

result = await fast_operation()
```

#### 1.3 Common Async Patterns

**Pattern 1: Concurrent Execution**
```python
async def concurrent_example():
    # Run all tasks concurrently
    await asyncio.gather(
        task1(),
        task2(),
        task3()
    )
```

**Pattern 2: Sequential with Dependency**
```python
async def sequential_example():
    result1 = await task1()
    result2 = await task2(result1)  # Uses result1
    result3 = await task3(result2)  # Uses result2
    return result3
```

**Pattern 3: Timeout Handling**
```python
async def with_timeout():
    try:
        result = await asyncio.wait_for(slow_task(), timeout=5)
    except asyncio.TimeoutError:
        print("Task took too long!")
```

### Best Practices

1. **Always use async/await**: Don't block the event loop
2. **Use asyncio.gather() for concurrent tasks**: More efficient than sequential
3. **Handle exceptions properly**: Use try/except in async code
4. **Avoid blocking operations**: Use async alternatives
5. **Close resources**: Use context managers (async with)

---

## 2. FACTORY & BUILDER DESIGN PATTERNS <a name="design-patterns"></a>

### Factory Pattern

The Factory Pattern creates objects without specifying the exact classes to create.

```python
from abc import ABC, abstractmethod

class DatabaseConnection(ABC):
    @abstractmethod
    def connect(self):
        pass

class PostgresConnection(DatabaseConnection):
    def connect(self):
        return "Connected to PostgreSQL"

class MongoConnection(DatabaseConnection):
    def connect(self):
        return "Connected to MongoDB"

class DatabaseFactory:
    @staticmethod
    def create_connection(db_type):
        if db_type == "postgres":
            return PostgresConnection()
        elif db_type == "mongo":
            return MongoConnection()
        else:
            raise ValueError(f"Unknown database type: {db_type}")

# Usage
factory = DatabaseFactory()
db = factory.create_connection("postgres")
print(db.connect())
```

### Builder Pattern

The Builder Pattern constructs complex objects step by step.

```python
class QueryBuilder:
    def __init__(self):
        self.sql = "SELECT * FROM users"
        self.conditions = []
        self.joins = []
    
    def where(self, condition):
        self.conditions.append(condition)
        return self
    
    def join(self, table, on):
        self.joins.append(f"JOIN {table} ON {on}")
        return self
    
    def build(self):
        query = self.sql
        if self.joins:
            query += " " + " ".join(self.joins)
        if self.conditions:
            query += " WHERE " + " AND ".join(self.conditions)
        return query

# Usage (Fluent interface)
query = (QueryBuilder()
    .join("posts", "users.id = posts.user_id")
    .where("users.active = 1")
    .where("posts.status = 'published'")
    .build())

print(query)
```

### When to Use Each

**Factory Pattern**:
- When object creation logic is complex
- When you need to support multiple implementations
- When the exact type isn't known until runtime

**Builder Pattern**:
- For objects with many optional parameters
- When you need a readable, fluent interface
- For complex object construction

---

## 3. PROFILING & OPTIMIZING PYTHON CODE <a name="performance"></a>

### Profiling Tools

#### cProfile - Built-in Profiler

```python
import cProfile
import pstats
from io import StringIO

def slow_function():
    total = 0
    for i in range(100000):
        total += i ** 2
    return total

# Profile the function
pr = cProfile.Profile()
pr.enable()

result = slow_function()

pr.disable()
s = StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats()
print(s.getvalue())
```

#### Line Profiler - Line-by-Line Analysis

```python
# Install: pip install line_profiler

@profile  # Add this decorator
def compute():
    total = 0
    for i in range(1000000):
        total += i
    return total

# Run with: kernprof -l -v script.py
```

### Optimization Techniques

#### 1. Use List Comprehensions

```python
# Slow
result = []
for i in range(1000):
    if i % 2 == 0:
        result.append(i * 2)

# Fast
result = [i * 2 for i in range(1000) if i % 2 == 0]
```

#### 2. Use Built-in Functions

```python
# Slow - Python loop
total = 0
for num in numbers:
    total += num

# Fast - Built-in function
total = sum(numbers)
```

#### 3. Avoid Global Lookups in Loops

```python
# Slow - Global lookup in loop
for i in range(1000000):
    result = len(my_list)

# Fast - Store in local variable
length = len(my_list)
for i in range(1000000):
    result = length
```

#### 4. Use Generators for Large Datasets

```python
# Slow - Creates entire list in memory
def get_numbers():
    return [i for i in range(1000000)]

# Fast - Yields one at a time
def get_numbers():
    for i in range(1000000):
        yield i
```

---

## 4. BUILDING SCALABLE APIs WITH FASTAPI <a name="fastapi"></a>

### Project Structure

```
api_project/
├── main.py
├── requirements.txt
├── routers/
│   ├── users.py
│   └── products.py
├── schemas/
│   ├── user.py
│   └── product.py
├── database/
│   ├── models.py
│   └── connection.py
└── utils/
    ├── security.py
    └── validators.py
```

### Basic Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DeepCode API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to DeepCode API"}
```

### Request/Response Models

```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Dependency Injection

```python
from fastapi import Depends, HTTPException

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@app.get("/users/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

---

## 5. DATA SCIENCE PIPELINE WITH PANDAS & ML <a name="data-science"></a>

### Data Loading & Exploration

```python
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('data.csv')

# Explore
print(df.head())
print(df.info())
print(df.describe())
print(df.isnull().sum())
```

### Data Cleaning

```python
# Remove duplicates
df = df.drop_duplicates()

# Handle missing values
df.fillna(df.mean(), inplace=True)

# Remove outliers
Q1 = df['column'].quantile(0.25)
Q3 = df['column'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['column'] >= Q1 - 1.5*IQR) & (df['column'] <= Q3 + 1.5*IQR)]
```

### Feature Engineering

```python
# Create new features
df['age_squared'] = df['age'] ** 2
df['log_income'] = np.log(df['income'])

# Encoding categorical variables
df = pd.get_dummies(df, columns=['category'])

# Scaling features
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
df[['age', 'income']] = scaler.fit_transform(df[['age', 'income']])
```

### Model Training

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Split data
X = df.drop('target', axis=1)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print(f"Precision: {precision_score(y_test, y_pred)}")
print(f"Recall: {recall_score(y_test, y_pred)}")
```

---

## 6. WRITING TESTABLE, CLEAN PYTHON CODE <a name="clean-code"></a>

### Unit Testing with pytest

```python
import pytest

def add(a, b):
    return a + b

class TestMath:
    def test_add_positive(self):
        assert add(2, 3) == 5
    
    def test_add_negative(self):
        assert add(-2, -3) == -5
    
    def test_add_zero(self):
        assert add(0, 5) == 5

# Run: pytest test_math.py -v
```

### Test Fixtures

```python
@pytest.fixture
def sample_user():
    return {"name": "John", "email": "john@example.com"}

def test_user_creation(sample_user):
    assert sample_user["name"] == "John"
```

### Mocking

```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {"id": 1}
    result = get_user_api(1)
    assert result["id"] == 1
```

### Code Quality Principles

1. **Single Responsibility Principle**: Each function/class has one job
2. **DRY (Don't Repeat Yourself)**: Avoid code duplication
3. **KISS (Keep It Simple, Stupid)**: Simple code is better
4. **YAGNI (You Aren't Gonna Need It)**: Don't write unnecessary code
5. **Meaningful Names**: Use clear, descriptive names

---

## CONCLUSION

These patterns and techniques form the foundation of professional Python development. Master them to write scalable, maintainable, and high-performance applications.

For more tutorials and projects, visit: https://www.youtube.com/@DeepCode-Python
