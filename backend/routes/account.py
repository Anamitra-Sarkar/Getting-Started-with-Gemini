from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from ..models import engine, Account, Organization, CreditTransaction
from ..auth.firebase import firebase_auth_required

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/me")
def get_me(user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        acct = session.exec(select(Account).where(Account.user_id == user["uid"]).limit(1)).first()
        if not acct:
            acct = Account(user_id=user["uid"], credits=0.0, role="member")
            session.add(acct)
            session.commit()
            session.refresh(acct)
        return {"account": acct.dict()}


@router.post("/credits/add")
def add_credits(body: dict, user=Depends(firebase_auth_required)):
    amount = float(body.get("amount", 0))
    reason = body.get("reason")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")
    with Session(engine) as session:
        acct = session.exec(select(Account).where(Account.user_id == user["uid"]).limit(1)).first()
        if not acct:
            acct = Account(user_id=user["uid"], credits=0.0, role="member")
            session.add(acct)
            session.commit()
            session.refresh(acct)
        acct.credits += amount
        session.add(acct)
        tx = CreditTransaction(account_id=acct.id, amount=amount, reason=reason)
        session.add(tx)
        session.commit()
        return {"ok": True, "credits": acct.credits}


@router.get("/transactions")
def list_transactions(user=Depends(firebase_auth_required)):
    with Session(engine) as session:
        acct = session.exec(select(Account).where(Account.user_id == user["uid"]).limit(1)).first()
        if not acct:
            return {"transactions": []}
        txs = session.exec(select(CreditTransaction).where(CreditTransaction.account_id == acct.id)).all()
        return {"transactions": [t.dict() for t in txs]}
