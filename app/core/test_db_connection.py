from database import engine

try:
    with engine.connect() as connection:
        print("✅ Connected to AWS RDS successfully!")
except Exception as e:
    print("❌ Connection failed:", e)