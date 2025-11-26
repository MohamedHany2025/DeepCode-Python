# BEST PRACTICES GUIDE - Professional Python Development
# Complete Reference for Writing Production-Ready Code

## Table of Contents
1. [Code Style & Formatting](#code-style)
2. [Error Handling](#error-handling)
3. [Logging](#logging)
4. [Performance Optimization](#performance)
5. [Security Best Practices](#security)
6. [Documentation](#documentation)
7. [Version Control](#version-control)
8. [Testing Strategy](#testing)

---

## 1. Code Style & Formatting <a name="code-style"></a>

### PEP 8 Standards

Follow PEP 8 for Python code style:

```python
# Good: Clear variable names
user_profile = get_user_profile(user_id)

# Bad: Ambiguous names
up = get_up(u)

# Good: Proper spacing
result = (a + b) * c

# Bad: Inconsistent spacing
result=(a+b)*c
```

### Naming Conventions

```python
# Constants: UPPER_CASE
MAX_RETRIES = 3
API_TIMEOUT = 30

# Classes: PascalCase
class UserManager:
    pass

# Functions/methods: snake_case
def process_user_data():
    pass

# Private methods: _leading_underscore
def _internal_helper():
    pass

# Dunder methods: __double_underscore__
def __init__(self):
    pass
```

### Code Organization

```python
# 1. Module docstring
\"\"\"User management module.\"\"\"

# 2. Imports (standard library first, then third-party, then local)
import os
from typing import List, Dict

import requests
import numpy as np

from . import utils
from .models import User

# 3. Constants
DEFAULT_TIMEOUT = 30

# 4. Classes
class UserManager:
    pass

# 5. Functions
def process_users():
    pass

# 6. Main execution
if __name__ == "__main__":
    main()
```

---

## 2. Error Handling <a name="error-handling"></a>

### Exception Hierarchy

```python
# Good: Specific exception catching
try:
    result = int(user_input)
except ValueError:
    print("Please enter a valid number")
except TypeError:
    print("Input must be a string")

# Bad: Catching all exceptions
try:
    result = int(user_input)
except Exception:
    print("Error occurred")
```

### Custom Exceptions

```python
class ValidationError(Exception):
    \"\"\"Raised when validation fails\"\"\"
    pass

class DatabaseError(Exception):
    \"\"\"Raised when database operation fails\"\"\"
    pass

# Usage
def validate_email(email):
    if '@' not in email:
        raise ValidationError("Invalid email format")
    return email
```

### Context Managers

```python
# Good: Automatic resource cleanup
from contextlib import contextmanager

@contextmanager
def database_connection(url):
    conn = create_connection(url)
    try:
        yield conn
    finally:
        conn.close()

# Usage
with database_connection("postgresql://...") as conn:
    conn.execute("SELECT * FROM users")
```

---

## 3. Logging <a name="logging"></a>

### Setup Logging

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = RotatingFileHandler(
        'app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()
```

### Logging Best Practices

```python
# Good: Include context and details
logger.info(f"Processing user {user_id} with email {email}")

# Bad: Vague messages
logger.info("Processing user")

# Good: Use appropriate log levels
logger.debug("Variable x = 5")
logger.info("Server started successfully")
logger.warning("Retry attempt 3 of 5")
logger.error("Database connection failed", exc_info=True)
logger.critical("Out of disk space")
```

---

## 4. Performance Optimization <a name="performance"></a>

### Use Generators for Large Data

```python
# Bad: Loads everything into memory
def read_file(filename):
    with open(filename) as f:
        return f.readlines()

# Good: Memory efficient
def read_file(filename):
    with open(filename) as f:
        for line in f:
            yield line
```

### Optimize Database Queries

```python
# Bad: N+1 query problem
users = User.all()
for user in users:
    posts = Post.where("user_id = ?", user.id)  # Query per user!

# Good: Single query with JOIN
posts = Post.join(User).all()
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(n):
    \"\"\"Results are cached\"\"\"
    return sum(range(n))

# For class methods
from functools import cached_property

class User:
    @cached_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

---

## 5. Security Best Practices <a name="security"></a>

### Never Hardcode Secrets

```python
# Bad
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"

# Good
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
```

### Input Validation

```python
def validate_user_input(data):
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    
    required_fields = {'name', 'email'}
    if not required_fields.issubset(data.keys()):
        raise ValueError(f"Missing required fields: {required_fields}")
    
    if len(data['name']) > 100:
        raise ValueError("Name too long")
    
    return data
```

### SQL Injection Prevention

```python
# Bad: String concatenation
query = f"SELECT * FROM users WHERE id = {user_id}"

# Good: Parameterized queries
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

# Hash password
hashed = pwd_context.hash("user_password")

# Verify password
is_valid = pwd_context.verify("user_password", hashed)
```

---

## 6. Documentation <a name="documentation"></a>

### Module Docstrings

```python
\"\"\"
User management module.

This module provides functionality for managing user accounts,
including creation, authentication, and profile management.

Example:
    >>> user = User.create(email="user@example.com", password="secure")
    >>> user.authenticate("secure")
    True
\"\"\"
```

### Function Docstrings (Google Style)

```python
def process_user_data(user_id: int, include_posts: bool = False) -> Dict:
    \"\"\"Process user data and return structured result.
    
    Args:
        user_id: The unique identifier of the user.
        include_posts: Whether to include user posts. Defaults to False.
    
    Returns:
        A dictionary containing processed user data.
    
    Raises:
        ValueError: If user_id is invalid.
        DatabaseError: If database query fails.
    
    Example:
        >>> result = process_user_data(123, include_posts=True)
        >>> result['name']
        'John Doe'
    \"\"\"
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("user_id must be a positive integer")
    
    try:
        user = User.find(user_id)
        data = {'name': user.name, 'email': user.email}
        
        if include_posts:
            data['posts'] = user.get_posts()
        
        return data
    except DatabaseError as e:
        raise DatabaseError(f"Failed to process user {user_id}: {e}")
```

### Type Hints

```python
from typing import List, Dict, Optional, Callable, Union

def fetch_users(
    limit: int = 10,
    offset: int = 0,
    sort_by: Optional[str] = None
) -> List[Dict[str, Union[int, str]]]:
    \"\"\"Fetch users with pagination.\"\"\"
    pass

def register_handler(callback: Callable[[str], None]) -> None:
    \"\"\"Register event handler.\"\"\"
    pass
```

---

## 7. Version Control <a name="version-control"></a>

### Commit Messages

```
Good:
  Add user authentication with JWT tokens
  Fix database connection timeout issue
  Refactor user service class structure
  Update dependencies to latest versions

Bad:
  bug fix
  changes
  wip
  final final changes
```

### .gitignore Template

```
# Virtual Environment
venv/
env/

# Python
__pycache__/
*.py[cod]
*.egg-info/

# Environment Variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Cache
.cache/
*.cache
```

---

## 8. Testing Strategy <a name="testing"></a>

### Unit Tests

```python
import unittest
from user_service import UserService

class TestUserService(unittest.TestCase):
    def setUp(self):
        \"\"\"Set up test fixtures\"\"\"
        self.service = UserService()
        self.test_user = {'name': 'John', 'email': 'john@example.com'}
    
    def test_user_creation(self):
        \"\"\"Test creating a new user\"\"\"
        result = self.service.create_user(self.test_user)
        self.assertEqual(result['name'], 'John')
    
    def test_invalid_email(self):
        \"\"\"Test validation of invalid email\"\"\"
        invalid_user = {'name': 'Jane', 'email': 'invalid'}
        with self.assertRaises(ValueError):
            self.service.create_user(invalid_user)

if __name__ == '__main__':
    unittest.main()
```

### Pytest Fixtures

```python
import pytest

@pytest.fixture
def user_service():
    return UserService()

@pytest.fixture
def sample_user():
    return {'name': 'John', 'email': 'john@example.com'}

def test_user_creation(user_service, sample_user):
    result = user_service.create_user(sample_user)
    assert result['name'] == 'John'
```

### Test Coverage

```bash
# Run tests with coverage
pytest --cov=src tests/

# Generate coverage report
coverage html
```

---

## 🎯 Code Review Checklist

- [ ] Code follows PEP 8 standards
- [ ] All functions have docstrings
- [ ] Type hints are used appropriately
- [ ] Error handling is comprehensive
- [ ] No hardcoded secrets
- [ ] Input validation is present
- [ ] Tests cover main functionality
- [ ] No unnecessary dependencies
- [ ] Logging is appropriate
- [ ] Documentation is updated

---

## 📚 Tools & Extensions

### Development Tools
- **black**: Code formatter
- **flake8**: Style guide enforcement
- **isort**: Import sorting
- **mypy**: Type checking
- **pylint**: Code analysis

### Installation
```bash
pip install black flake8 isort mypy pylint
```

### Pre-commit Hook
```bash
pip install pre-commit
# Create .pre-commit-config.yaml with hooks
pre-commit install
```

---

**Remember**: Good code is not just code that works—it's code that's readable, maintainable, and secure.
