from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from router.auth import get_current_user, get_db
from model import User, Transaction
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field
from datetime import date as Date

transaction_router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TransactionCreate(BaseModel):
    title: str
    amount: float=Field(gt=0, description="Amount must be positive number")
    type: Literal["income", "expense"]=Field(default="expense")
    category: str
    date : Optional[Date]=Field(default=None, description="Date in YYYY-MM-DD format")

class TransactionUpdate(BaseModel):
    title: Optional[str]=Field(default=None)
    amount: Optional[float]=Field(default=None, gt=0, description="Amount must be positive number")
    type: Optional[Literal["income", "expense"]]=Field(default=None)
    category: Optional[str]=Field(default=None)
    date : Optional[Date]=Field(default=None, description="Date in YYYY-MM-DD format")

@transaction_router.post("/transactions")
def create_transaction(user: user_dependency, db: db_dependency, new_transaction: TransactionCreate):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    transaction_model = Transaction(**new_transaction.model_dump(), owner_id=user.get('id'))
    db.add(transaction_model)
    db.commit()
    
    return JSONResponse(status_code=201, content={"message": "Transaction created successfully"})
    

@transaction_router.get("/transactions")
def get_transactrions(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    all_transactions = db.query(Transaction).filter(Transaction.owner_id==user.get('id')).all()
    return all_transactions

@transaction_router.get("/transactions/filter")
def filter_transactions(
    user: user_dependency, 
    db: db_dependency, 
    type: Optional[Literal["income", "expense"]]=None, 
    category: Optional[str]=None,
    minimum_amount: Optional[float]=None,
    maximum_amount: Optional[float]=None
    ):
    
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    query = db.query(Transaction).filter(Transaction.owner_id==user.get('id'))
    if type:
        query = query.filter(Transaction.type==type)
    if category:
        query = query.filter(Transaction.category==category)
    if minimum_amount is not None:
        query = query.filter(Transaction.amount >= minimum_amount)
    if maximum_amount is not None:  
        query = query.filter(Transaction.amount <= maximum_amount)
    
    return query.all()

@transaction_router.get("/transactions/{transaction_id}")
def get_transaction_by_id(transaction_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    transaction = db.query(Transaction).filter(Transaction.owner_id==user.get('id')).filter(Transaction.id==transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@transaction_router.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, user: user_dependency, db: db_dependency, update_transaction: TransactionUpdate):
    if user is None:
        raise HTTPException(status_code=404, detail="Authentication required")
    transaction = db.query(Transaction).filter(Transaction.owner_id==user.get('id')).filter(Transaction.id==transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    update_data = update_transaction.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transaction, key, value)
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Transaction updated successfully"})

@transaction_router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    transaction = db.query(Transaction).filter(Transaction.owner_id==user.get('id')).filter(Transaction.id==transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.query(Transaction).filter(Transaction.owner_id==user.get('id')).filter(Transaction.id==transaction_id).delete()
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Transaction deleted successfully"})

