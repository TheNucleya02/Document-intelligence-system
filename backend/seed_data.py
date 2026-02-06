from app.database import SessionLocal
from app.models import User
from app.core.security import hash_password

SEED_EMAIL = "demo@example.com"
SEED_PASSWORD = "demo-password"


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == SEED_EMAIL).first()
        if existing:
            print("Seed user already exists")
            return
        user = User(email=SEED_EMAIL, password_hash=hash_password(SEED_PASSWORD))
        db.add(user)
        db.commit()
        print("Seed user created:", SEED_EMAIL)
    finally:
        db.close()


if __name__ == "__main__":
    main()
