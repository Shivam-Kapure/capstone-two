"""FastAPI service for demo payments and notifications.

All data lives in process memory: nothing is persisted and no real money moves.
"""

import os
from datetime import datetime, timezone
from decimal import Decimal
from itertools import count
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, StringConstraints

from app import __version__

app = FastAPI(title="Payment & Notification Engine", version=__version__)

# CORS is opt-in: the frontend reaches the API through its own nginx proxy, so it is not needed by default.
_cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]
Amount = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
Currency = Literal["INR", "USD", "EUR"]


class PaymentIn(BaseModel):
    payer: Name
    payee: Name
    amount: Amount
    currency: Currency


class Payment(BaseModel):
    id: int
    payer: str
    payee: str
    amount: float
    currency: Currency
    status: Literal["COMPLETED", "PENDING", "FAILED"]
    created_at: str


class Notification(BaseModel):
    id: int
    payment_id: int
    message: str
    created_at: str


_payments: dict[int, Payment] = {}
_notifications: list[Notification] = []
_payment_ids = count(1)
_notification_ids = count(1)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _record(payer: str, payee: str, amount: Decimal, currency: str, status: str) -> Payment:
    payment = Payment(
        id=next(_payment_ids),
        payer=payer,
        payee=payee,
        amount=float(amount),
        currency=currency,
        status=status,
        created_at=_now(),
    )
    _payments[payment.id] = payment
    _notifications.append(
        Notification(
            id=next(_notification_ids),
            payment_id=payment.id,
            message=f"Payment #{payment.id} of {amount:.2f} {currency} from {payer} to {payee} is {status}",
            created_at=payment.created_at,
        )
    )
    return payment


_record("Asha Rao", "Acme Supplies", Decimal("1250.00"), "INR", "COMPLETED")
_record("Daniel Kim", "Cloud Hosting Ltd", Decimal("89.99"), "USD", "PENDING")
_record("Marie Dubois", "Rail Europe", Decimal("42.50"), "EUR", "FAILED")


@app.get("/")
def root():
    return {"service": "payment-notification-engine", "version": __version__, "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy", "version": __version__}


@app.get("/api/payments", response_model=list[Payment])
def list_payments():
    return list(_payments.values())


@app.get("/api/payments/{payment_id}", response_model=Payment)
def get_payment(payment_id: int):
    payment = _payments.get(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
    return payment


@app.post("/api/payments", response_model=Payment, status_code=201)
def create_payment(body: PaymentIn):
    # Demo engine: new payments are accepted immediately; there is no real processor behind it.
    return _record(body.payer, body.payee, body.amount, body.currency, "COMPLETED")


@app.get("/api/notifications", response_model=list[Notification])
def list_notifications():
    return sorted(_notifications, key=lambda n: n.id, reverse=True)
