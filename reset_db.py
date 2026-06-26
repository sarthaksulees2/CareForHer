"""
Reset Database - Drop all tables and recreate fresh
"""

from app import app, db

def reset_database():
    print("=" * 50)
    print("MHM Hub - Database Reset")
    print("=" * 50)

    with app.app_context():
        db.drop_all()
        print("✅ All tables dropped")

        db.create_all()
        print("✅ Fresh tables created")

    print("=" * 50)
    print("✨ Database reset complete! Ready for fresh registration.")
    print("=" * 50)

if __name__ == "__main__":
    reset_database()
