from app.database import Base, engine, SessionLocal
from app.models import User, Resume

def init_db():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        print("Database connection test successful!")
        db.close()
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise e

if __name__ == "__main__":
    init_db()