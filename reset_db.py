"""
Reset PostgreSQL Database - Drop all tables and recreate fresh
"""

from sqlalchemy import text, inspect
from db_config import engine, Base, SessionLocal

def reset_database():
    """Drop all tables and recreate fresh"""
    
    print("=" * 60)
    print("MHM Hub - Database Reset")
    print("=" * 60)
    
    try:
        with engine.begin() as connection:
            # Drop all existing tables
            print("\n🗑️  Dropping existing tables...")
            Base.metadata.drop_all(bind=engine)
            print("   ✅ All tables dropped")
            
        # Recreate all tables
        print("\n🔨 Creating fresh tables...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ All tables created fresh")
        
        print("\n" + "=" * 60)
        print("✨ Database reset complete!")
        print("=" * 60)
        print("\n📋 Ready for fresh user registration\n")
        
    except Exception as e:
        print(f"\n❌ Error during database reset:")
        print(f"   {type(e).__name__}: {e}\n")
        return False
    
    return True

if __name__ == "__main__":
    reset_database()
