import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://mood_user:mood_pass@localhost:3306/mood_diary"
)