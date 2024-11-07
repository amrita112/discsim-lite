import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import engine, Base, UploadedFile

# Drop the specific table
print("Dropping the 'uploaded_files' table...")
UploadedFile.__table__.drop(bind=engine, checkfirst=True)
print("Table dropped.")

# Recreate the table with the new schema
print("Creating the 'uploaded_files' table with new schema...")
Base.metadata.create_all(bind=engine)
print("Table created.")
