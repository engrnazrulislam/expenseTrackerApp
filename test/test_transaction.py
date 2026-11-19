from fastapi import status
from fastapi.testclient import TestClient
from main import app
from router.auth import get_current_user
from database import SessionLocal
from model import Transaction

client = TestClient(app)

def override_get_current_user():
    return {
        "id": 1,
        "username": "testuser"
    }

def test_transaction():
    db = SessionLocal()
    # remove old testing data if it's exists
    db.query(Transaction).filter(Transaction.id == 99).delete()
    transaction = Transaction(
        id=99,
        title="Test Transaction",
        amount=99,
        type="expense",
        category="Test Category",
        date="2026-11-19",
        owner_id=1
    )
    db.add(transaction)
    db.commit()

app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_transaction():
    response = client.get("/transactions")
    assert response.status_code == status.HTTP_200_OK
    
def test_get_transaction_by_id():
    response = client.get("/transactions/99")
    assert response.status_code == status.HTTP_200_OK
    
def test_create_transaction():
    db = SessionLocal()
    # remove old testing data if it's exists
    db.query(Transaction).filter(Transaction.id == 100).delete()
    transaction_data = {
        "id": 99,
        "title": "Test Transaction",
        "amount": 99,
        "type": "expense",
        "category": "Test Category",
        "date": "2026-11-19"
    }
    response = client.post("/transactions", json=transaction_data)
    assert response.status_code == status.HTTP_201_CREATED

def test_update_transaction():
    transaction_data = {
        "amount": 100
    }
    response = client.put("/transactions/99", json=transaction_data)
    assert response.status_code == status.HTTP_200_OK

def test_delete_transaction():
    response = client.delete("/transactions/99")
    assert response.status_code == status.HTTP_200_OK