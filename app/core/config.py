# app/core/config.py

# IMPORTANT: Change SECRET_KEY to a strong, random string in production!
SECRET_KEY = "your-super-secret-key-replace-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(60)# Token expires in 60 minutes

# You can add other configuration variables here as needed
# For example, database settings could also be defined here if not using environment variables directly