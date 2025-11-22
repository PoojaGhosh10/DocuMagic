import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

with engine.connect() as conn:
    print("FastAPI connected to PostgreSQL SUCCESSFULLY!")
