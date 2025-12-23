from sqlalchemy import text
from src.core.database import engine

def migrate():
    with engine.connect() as connection:
        # Sử dụng text() để khai báo SQL raw safely
        # Thêm cột owner_id nếu chưa tồn tại
        print("Migrating: Adding owner_id column to projects table...")
        try:
            connection.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS owner_id VARCHAR"))
            connection.commit()
            print("Migration successful: Added owner_id column.")
        except Exception as e:
            print(f"Migration failed or column already exists: {e}")

if __name__ == "__main__":
    migrate()
