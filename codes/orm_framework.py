# ORM Framework - Lightweight but Powerful Object-Relational Mapping
# Project: ORM Framework
# Language: Python
# Description: Lightweight but powerful ORM library with query optimization and migration tools

from typing import Type, List, Optional, Dict, Any, Generic, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3
import json

# ==================== Type Definitions ====================
T = TypeVar('T')

@dataclass
class Column:
    name: str
    type: str
    primary_key: bool = False
    unique: bool = False
    nullable: bool = True
    default: Any = None
    index: bool = False

@dataclass
class ForeignKey:
    column: str
    reference_table: str
    reference_column: str

# ==================== Connection Pool ====================
class ConnectionPool:
    def __init__(self, database: str, pool_size: int = 5):
        self.database = database
        self.pool_size = pool_size
        self.connections = []
        self._initialize_pool()
    
    def _initialize_pool(self):
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.database)
            conn.row_factory = sqlite3.Row
            self.connections.append(conn)
    
    def get_connection(self):
        if self.connections:
            return self.connections.pop()
        return sqlite3.connect(self.database)
    
    def return_connection(self, conn):
        if len(self.connections) < self.pool_size:
            self.connections.append(conn)
        else:
            conn.close()
    
    def close_all(self):
        for conn in self.connections:
            conn.close()

# ==================== Query Builder ====================
class QueryBuilder:
    def __init__(self, table: str):
        self.table = table
        self.select_fields = ["*"]
        self.where_clauses = []
        self.where_values = []
        self.joins = []
        self.order_by_clause = None
        self.limit_value = None
        self.offset_value = None
    
    def select(self, *fields: str):
        self.select_fields = list(fields)
        return self
    
    def where(self, condition: str, *values):
        self.where_clauses.append(condition)
        self.where_values.extend(values)
        return self
    
    def join(self, other_table: str, on: str):
        self.joins.append(f"JOIN {other_table} ON {on}")
        return self
    
    def left_join(self, other_table: str, on: str):
        self.joins.append(f"LEFT JOIN {other_table} ON {on}")
        return self
    
    def order_by(self, field: str, direction: str = "ASC"):
        self.order_by_clause = f"ORDER BY {field} {direction}"
        return self
    
    def limit(self, limit: int):
        self.limit_value = limit
        return self
    
    def offset(self, offset: int):
        self.offset_value = offset
        return self
    
    def build(self) -> tuple:
        sql = f"SELECT {', '.join(self.select_fields)} FROM {self.table}"
        
        if self.joins:
            sql += " " + " ".join(self.joins)
        
        if self.where_clauses:
            sql += " WHERE " + " AND ".join(self.where_clauses)
        
        if self.order_by_clause:
            sql += f" {self.order_by_clause}"
        
        if self.limit_value:
            sql += f" LIMIT {self.limit_value}"
        
        if self.offset_value:
            sql += f" OFFSET {self.offset_value}"
        
        return sql, tuple(self.where_values)

# ==================== Query Cache ====================
class QueryCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        
        if (datetime.now() - self.timestamps[key]).seconds > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any):
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.timestamps, key=self.timestamps.get)
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
    
    def clear(self):
        self.cache.clear()
        self.timestamps.clear()

# ==================== Database ====================
class Database:
    def __init__(self, database: str):
        self.pool = ConnectionPool(database)
        self.cache = QueryCache()
        self.tables = {}
    
    def execute(self, sql: str, params: tuple = ()) -> Any:
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor
        finally:
            self.pool.return_connection(conn)
    
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict]:
        cache_key = f"{sql}:{params}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            result = dict(row) if row else None
            if result:
                self.cache.set(cache_key, result)
            return result
        finally:
            self.pool.return_connection(conn)
    
    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict]:
        cache_key = f"{sql}:{params}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            if results:
                self.cache.set(cache_key, results)
            return results
        finally:
            self.pool.return_connection(conn)
    
    def create_table(self, table_name: str, columns: List[Column]):
        col_defs = []
        
        for col in columns:
            col_def = f"{col.name} {col.type}"
            
            if col.primary_key:
                col_def += " PRIMARY KEY AUTOINCREMENT"
            
            if not col.nullable:
                col_def += " NOT NULL"
            
            if col.unique:
                col_def += " UNIQUE"
            
            if col.default is not None:
                col_def += f" DEFAULT {col.default}"
            
            col_defs.append(col_def)
        
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)})"
        self.execute(sql)
        self.cache.clear()
    
    def close(self):
        self.pool.close_all()

# ==================== Model ====================
class Model:
    __tablename__: str
    __db__: Database = None
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def set_database(cls, db: Database):
        cls.__db__ = db
    
    @classmethod
    def query(cls) -> QueryBuilder:
        return QueryBuilder(cls.__tablename__)
    
    @classmethod
    def find(cls, id: int) -> Optional['Model']:
        qb = cls.query().where("id = ?", id)
        sql, params = qb.build()
        row = cls.__db__.fetch_one(sql, params)
        
        if row:
            return cls(**dict(row))
        return None
    
    @classmethod
    def all(cls) -> List['Model']:
        qb = cls.query()
        sql, params = qb.build()
        rows = cls.__db__.fetch_all(sql, params)
        return [cls(**dict(row)) for row in rows]
    
    @classmethod
    def where(cls, condition: str, *values) -> List['Model']:
        qb = cls.query().where(condition, *values)
        sql, params = qb.build()
        rows = cls.__db__.fetch_all(sql, params)
        return [cls(**dict(row)) for row in rows]
    
    @classmethod
    def first(cls, condition: str = None, *values) -> Optional['Model']:
        qb = cls.query()
        if condition:
            qb.where(condition, *values)
        sql, params = qb.build()
        row = cls.__db__.fetch_one(sql, params)
        
        if row:
            return cls(**dict(row))
        return None
    
    def save(self) -> bool:
        attrs = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        
        if hasattr(self, 'id') and self.id:
            # Update
            set_clause = ", ".join([f"{k} = ?" for k in attrs.keys() if k != 'id'])
            values = [v for k, v in attrs.items() if k != 'id']
            values.append(self.id)
            
            sql = f"UPDATE {self.__tablename__} SET {set_clause} WHERE id = ?"
        else:
            # Insert
            columns = ", ".join(attrs.keys())
            placeholders = ", ".join(["?" for _ in attrs])
            values = list(attrs.values())
            
            sql = f"INSERT INTO {self.__tablename__} ({columns}) VALUES ({placeholders})"
        
        self.__db__.execute(sql, tuple(values))
        self.__db__.cache.clear()
        return True
    
    def delete(self) -> bool:
        if not hasattr(self, 'id'):
            return False
        
        sql = f"DELETE FROM {self.__tablename__} WHERE id = ?"
        self.__db__.execute(sql, (self.id,))
        self.__db__.cache.clear()
        return True
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

# ==================== Usage Example ====================
if __name__ == "__main__":
    # Initialize database
    db = Database("deepcode.db")
    
    # Define model
    class User(Model):
        __tablename__ = "users"
    
    User.set_database(db)
    
    # Create table
    db.create_table("users", [
        Column("id", "INTEGER", primary_key=True),
        Column("name", "TEXT", nullable=False),
        Column("email", "TEXT", unique=True, nullable=False),
        Column("created_at", "TIMESTAMP", default=datetime.now),
    ])
    
    # Create user
    user = User(name="Mohamed Hany", email="hany@deepcode.com")
    user.save()
    
    # Query users
    users = User.all()
    print(f"Total users: {len(users)}")
    
    # Find specific user
    found_user = User.find(1)
    if found_user:
        print(f"Found: {found_user.to_json()}")
    
    # Advanced query
    query = User.query().where("email LIKE ?", "%deepcode%").select("name", "email")
    sql, params = query.build()
    results = db.fetch_all(sql, params)
    print(f"Search results: {results}")
    
    db.close()
