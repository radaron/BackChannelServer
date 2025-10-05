import base64
import getpass

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(passw: str) -> str:
    return pwd_context.hash(passw)


if __name__ == "__main__":
    password = getpass.getpass("Enter password to hash: ")
    print(base64.b64encode(hash_password(password).encode()).decode())
