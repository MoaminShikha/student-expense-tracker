from __future__ import annotations

import calendar
import os as _os
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .composition import build_services
from ..domain.models import (
    FuzzyChargeStatus,
    IncomeSourceTag,
    TransactionCategory,
)
from ..shared.exceptions import ApplicationError, ValidationError

_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"

app = FastAPI(title="Mizan Expense Tracker API")

_CORS_ORIGINS = _os.environ.get(
    "MIZAN_CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

_services = None


def _get_services():
    global _services
    if _services is None:
        _services = build_services(_DATA_DIR)
    return _services


def _require_session():
    svc = _get_services()
    session = svc.session_service.get_active()
    if session is None:
        raise HTTPException(status_code=400, detail="No active session.")
    return session


def _parse_decimal(value: str, field: str) -> Decimal:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        raise HTTPException(status_code=422, detail=f"{field} must be a valid decimal number.")


def _parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"{field} must be ISO 8601 date (YYYY-MM-DD).")


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class SessionInitBody(BaseModel):
    opening_balance: str


class IncomeBody(BaseModel):
    amount: str
    source_tag: str
    date: str


class SpendBody(BaseModel):
    amount: str
    description: str
    category: str | None = None
    date: str


class ChargeBody(BaseModel):
    name: str
    amount: str
    due_date: str
    recurring: bool = False
    day_of_month: int | None = None


class FuzzyChargeBody(BaseModel):
    name: str
    expected_date: str | None = None
    estimated_amount: str | None = None


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    svc = _get_services()
    session = svc.session_service.get_active()
    return {"status": "ok", "session": session is not None}


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

@app.post("/api/session/init")
def init_session(body: SessionInitBody):
    svc = _get_services()
    amount = _parse_decimal(body.opening_balance, "opening_balance")
    try:
        svc.session_service.init_session(amount)
    except (ValidationError, ApplicationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "created"}


# ---------------------------------------------------------------------------
# Balance
# ---------------------------------------------------------------------------

@app.get("/api/balance")
def get_balance():
    session = _require_session()
    svc = _get_services()

    today = date.today()
    year, month = today.year, today.month
    days_in_month = calendar.monthrange(year, month)[1]
    day_of_month = today.day

    caution_threshold = session.opening_balance * Decimal("0.2")
    snapshot = svc.balance_service.aggregate_and_build_snapshot(
        session.session_id, caution_threshold, session.opening_balance
    )

    monthly_budget = snapshot.monthly_budget
    timeline_spent_pct = float(
        (snapshot.monthly_spent / monthly_budget * 100) if monthly_budget > 0 else Decimal("0")
    )
    timeline_committed_pct = 0.0
    if monthly_budget > 0:
        charges_this_month = sum(
            (c.amount for c in svc.charge_service.list_all_for_month(session.session_id, year, month)),
            Decimal("0"),
        )
        timeline_committed_pct = float(charges_this_month / monthly_budget * 100)

    timeline_today_pct = (day_of_month / days_in_month) * 100

    upcoming_sorted = sorted(svc.charge_service.list_upcoming(session.session_id), key=lambda c: c.due_date)
    next_due = upcoming_sorted[0] if upcoming_sorted else None

    month_label = today.strftime("%B %Y")

    return {
        "free_money": str(snapshot.free_money),
        "monthly_budget": str(snapshot.monthly_budget),
        "monthly_spent": str(snapshot.monthly_spent),
        "monthly_left": str(snapshot.monthly_left),
        "on_track_state": snapshot.on_track_state.value,
        "balance_state": snapshot.balance_state.value,
        "timeline_spent_pct": round(timeline_spent_pct, 2),
        "timeline_committed_pct": round(timeline_committed_pct, 2),
        "timeline_today_pct": round(timeline_today_pct, 2),
        "days_in_month": days_in_month,
        "day_of_month": day_of_month,
        "month_label": month_label,
        "next_due_charge": {
            "charge_id": str(next_due.charge_id),
            "name": next_due.name,
            "amount": str(next_due.amount),
            "due_date": next_due.due_date.isoformat(),
            "status": next_due.status.value,
        } if next_due else None,
    }


# ---------------------------------------------------------------------------
# Charges
# ---------------------------------------------------------------------------

@app.get("/api/charges/upcoming")
def get_upcoming_charges():
    session = _require_session()
    svc = _get_services()
    charges_sorted = sorted(svc.charge_service.list_upcoming(session.session_id), key=lambda c: c.due_date)
    return [
        {
            "charge_id": str(c.charge_id),
            "session_id": str(c.session_id),
            "name": c.name,
            "amount": str(c.amount),
            "due_date": c.due_date.isoformat(),
            "status": c.status.value,
            "recurring_rule_id": str(c.recurring_rule_id) if c.recurring_rule_id else None,
        }
        for c in charges_sorted
    ]


@app.post("/api/charge")
def add_charge(body: ChargeBody):
    svc = _get_services()
    amount = _parse_decimal(body.amount, "amount")

    try:
        if body.recurring:
            if body.day_of_month is None:
                raise HTTPException(status_code=422, detail="day_of_month is required for recurring charges.")
            charge = svc.charge_service.add_recurring_charge(
                name=body.name,
                amount=amount,
                day_of_month=body.day_of_month,
            )
        else:
            due = _parse_date(body.due_date, "due_date")
            charge = svc.charge_service.add_charge(name=body.name, amount=amount, due_date=due)
    except (ValidationError, ApplicationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "charge_id": str(charge.charge_id),
        "name": charge.name,
        "amount": str(charge.amount),
        "due_date": charge.due_date.isoformat(),
        "status": charge.status.value,
    }


@app.post("/api/charge/{charge_id}/mark-paid")
def mark_charge_paid(charge_id: str):
    svc = _get_services()
    try:
        uid = UUID(charge_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid charge ID.")
    try:
        svc.charge_service.mark_paid(uid)
    except (ValidationError, ApplicationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "paid"}


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

@app.get("/api/transactions/recent")
def get_recent_transactions():
    session = _require_session()
    svc = _get_services()
    txs = svc.balance_service.list_all_transactions(session.session_id)
    txs_sorted = sorted(txs, key=lambda t: t.date, reverse=True)[:10]
    return [
        {
            "transaction_id": str(t.transaction_id),
            "amount": str(t.amount),
            "description": t.description,
            "category": t.category.value if t.category else None,
            "date": t.date.isoformat(),
        }
        for t in txs_sorted
    ]


@app.get("/api/transactions/by-category")
def get_transactions_by_category():
    session = _require_session()
    svc = _get_services()
    txs = svc.balance_service.list_all_transactions(session.session_id)

    totals: dict[str, Decimal] = {}
    counts: dict[str, int] = {}
    for tx in txs:
        key = tx.category.value if tx.category else "uncategorized"
        totals[key] = totals.get(key, Decimal("0")) + tx.amount
        counts[key] = counts.get(key, 0) + 1

    grand_total = sum(totals.values(), Decimal("0"))

    return {
        cat: {
            "amount": str(amt),
            "count": counts[cat],
            "pct_of_total": round(float(amt / grand_total * 100), 2) if grand_total > 0 else 0.0,
        }
        for cat, amt in totals.items()
    }


@app.get("/api/transactions/all")
def get_all_transactions():
    session = _require_session()
    svc = _get_services()
    spend_txs = svc.balance_service.list_all_transactions(session.session_id)
    income_entries = svc.balance_service.list_all_income(session.session_id)
    rows = [
        {"entry_id": str(t.transaction_id), "type": "spend", "amount": str(t.amount),
         "description": t.description, "category": t.category.value if t.category else None, "date": t.date.isoformat()}
        for t in spend_txs
    ] + [
        {"entry_id": str(i.income_id), "type": "income", "amount": str(i.amount),
         "description": i.source_tag.value, "category": None, "date": i.date.isoformat()}
        for i in income_entries
    ]
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


@app.get("/api/streak")
def get_streak():
    from datetime import timedelta
    session = _require_session()
    svc = _get_services()
    today = date.today()
    txs = svc.balance_service.list_all_transactions(session.session_id)
    incomes = svc.balance_service.list_all_income(session.session_id)
    active_days = {t.date for t in txs} | {i.date for i in incomes}
    streak = 0
    for offset in range(365):
        if (today - timedelta(days=offset)) in active_days:
            streak += 1
        else:
            break
    return {"streak_days": streak}


@app.get("/api/transactions/weekly-summary")
def get_weekly_summary(weeks: int = 8):
    from datetime import timedelta
    session = _require_session()
    svc = _get_services()
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    txs = svc.balance_service.list_all_transactions(session.session_id)
    result = []
    for i in range(weeks - 1, -1, -1):
        week_start = start_of_week - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        total = sum((t.amount for t in txs if week_start <= t.date <= week_end), Decimal("0"))
        result.append({"week_label": "Now" if i == 0 else f"W{weeks - i}", "week_start": week_start.isoformat(), "total_spend": float(total)})
    return result


@app.delete("/api/entry/{entry_id}")
def delete_entry(entry_id: str, entry_type: Literal["spend", "income"]):
    """Delete a spend or income entry by ID."""
    svc = _get_services()
    try:
        uid = UUID(entry_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid entry_id.")
    if entry_type == "spend":
        removed = svc.balance_service.delete_spend(uid)
    else:
        removed = svc.balance_service.delete_income(uid)
    if not removed:
        raise HTTPException(status_code=404, detail="Entry not found.")
    return {"deleted": entry_id}


@app.post("/api/spend")
def add_spend(body: SpendBody):
    svc = _get_services()
    amount = _parse_decimal(body.amount, "amount")
    spent_on = _parse_date(body.date, "date")

    category = None
    if body.category is not None:
        try:
            category = TransactionCategory(body.category)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid category '{body.category}'.")

    try:
        tx = svc.spend_service.add_transaction(
            amount=amount,
            description=body.description,
            category=category,
            spent_on=spent_on,
        )
    except (ValidationError, ApplicationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "transaction_id": str(tx.transaction_id),
        "amount": str(tx.amount),
        "description": tx.description,
        "category": tx.category.value if tx.category else None,
        "date": tx.date.isoformat(),
    }


# ---------------------------------------------------------------------------
# Income
# ---------------------------------------------------------------------------

@app.post("/api/income")
def add_income(body: IncomeBody):
    svc = _get_services()
    amount = _parse_decimal(body.amount, "amount")
    entry_date = _parse_date(body.date, "date")

    try:
        source_tag = IncomeSourceTag(body.source_tag)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid source_tag '{body.source_tag}'.")

    try:
        entry = svc.income_service.add_income(amount=amount, source_tag=source_tag, entry_date=entry_date)
    except (ValidationError, ApplicationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "income_id": str(entry.income_id),
        "amount": str(entry.amount),
        "source_tag": entry.source_tag.value,
        "date": entry.date.isoformat(),
    }


# ---------------------------------------------------------------------------
# Fuzzy charges
# ---------------------------------------------------------------------------

@app.get("/api/fuzzy-charges/pending")
def get_pending_fuzzy_charges():
    session = _require_session()
    svc = _get_services()
    pending = svc.fuzzy_charge_service.list_pending(session.session_id)
    active = [
        f for f in pending
        if f.status in {FuzzyChargeStatus.PENDING, FuzzyChargeStatus.OVERDUE}
    ]
    return [
        {
            "fuzzy_id": str(f.fuzzy_id),
            "name": f.name,
            "direction": f.direction.value,
            "status": f.status.value,
            "expected_date": f.expected_date.isoformat() if f.expected_date else None,
            "estimated_amount": str(f.estimated_amount) if f.estimated_amount else None,
        }
        for f in active
    ]


@app.post("/api/fuzzy-charge")
def add_fuzzy_charge(body: FuzzyChargeBody):
    svc = _get_services()
    expected_date = _parse_date(body.expected_date, "expected_date") if body.expected_date else None
    estimated_amount = _parse_decimal(body.estimated_amount, "estimated_amount") if body.estimated_amount else None

    try:
        entry = svc.fuzzy_charge_service.add_fuzzy_charge(
            name=body.name,
            expected_date=expected_date,
            estimated_amount=estimated_amount,
        )
    except (ValidationError, ApplicationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "fuzzy_id": str(entry.fuzzy_id),
        "name": entry.name,
        "direction": entry.direction.value,
        "status": entry.status.value,
        "expected_date": entry.expected_date.isoformat() if entry.expected_date else None,
        "estimated_amount": str(entry.estimated_amount) if entry.estimated_amount else None,
    }
