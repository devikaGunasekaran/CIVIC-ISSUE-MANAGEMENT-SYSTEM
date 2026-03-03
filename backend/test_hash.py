import time
import timeit
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

start = time.time()
hash = pwd_context.hash("testpassword123")
print(f"Hashing took: {time.time() - start:.4f} seconds")
