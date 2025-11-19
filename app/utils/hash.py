from passlib.context import CryptContext

# This tells passlib which hashing algorithm to use
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash passwords
def hash_password(password: str):
    # bcrypt supports max 72 bytes → ensure safe length
    return pwd_context.hash(password)

