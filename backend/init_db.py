#!/usr/bin/env python3
"""Initialize the database with all tables."""

from app.db.session import engine
from app.models.db import Base

# Create all tables
print("Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database initialized successfully!")
print(f"📊 Created {len(Base.metadata.tables)} tables")
