"""
Initialize PostgreSQL Database for MHM Hub
Run this script to create all tables in the careforher database
"""

from db_config import engine
from app import app, db

if __name__ == "__main__":
    print("=" * 60)
    print("MHM Hub - PostgreSQL Database Initialization")
    print("=" * 60)
    
    try:
        # Drop all existing tables and recreate only the required ones
        with app.app_context():
            db.metadata.reflect(bind=engine)
            db.metadata.drop_all(bind=engine)
            db.create_all()
        
        print("\n✅ Database initialization successful!")
        print("\nTables created:")
        print("   1. users - Stores user profile and authentication data")
        print("   2. period_track_history - Stores period cycle tracking history")
        
        print("\n📋 User Table Schema:")
        print("   - id (Primary Key)")
        print("   - name, email, phone, password")
        print("   - age, gender, height, weight, cycle_length")
        
        print("\n📊 Period Track History Table Schema:")
        print("   - id (Primary Key)")
        print("   - user_id or user_name")
        print("   - last_period, cycle_length, next_period")
        
        print("\n" + "=" * 60)
        print("✨ Ready to use! You can now integrate this with your Flask app.")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during database initialization:")
        print(f"   {type(e).__name__}: {e}")
        print("\nPlease ensure:")
        print("   - PostgreSQL is running on localhost:5433")
        print("   - Database 'careforher' exists")
        print("   - Credentials are correct (postgres/root)")
