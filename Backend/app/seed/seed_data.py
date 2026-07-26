"""
Run with: python -m app.seed.seed_data

Inserts a handful of fake customers spanning different account ages,
verification states, and credit limits — enough to demo both an
approval and a rejection live for every one of the three flows.
"""
from app.database import Base, engine, SessionLocal
from app.models.customer import Customer

DEMO_CUSTOMERS = [
    Customer(customer_id="C1001", verification_status="verified", account_age_months=24,
             card_status="active", current_credit_limit=50000),
    Customer(customer_id="C1002", verification_status="verified", account_age_months=3,
             card_status="active", current_credit_limit=15000),
    Customer(customer_id="C1003", verification_status="unverified", account_age_months=18,
             card_status="active", current_credit_limit=30000),
    Customer(customer_id="C1004", verification_status="verified", account_age_months=36,
             card_status="damaged", current_credit_limit=80000),
    Customer(customer_id="C1005", verification_status="verified", account_age_months=8,
             card_status="blocked", current_credit_limit=20000),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for customer in DEMO_CUSTOMERS:
            existing = db.get(Customer, customer.customer_id)
            if not existing:
                db.add(customer)
        db.commit()
        print(f"Seeded {len(DEMO_CUSTOMERS)} demo customers.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
