"""HTML routes for plan creation, feedback, and saved-user browsing."""
import json
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_groq
from .groq_client import GroqError, log_provider_error
from .models import FitnessPlan
from .schemas import UserInput, FeedbackInput
from .updated_plan import update_workout_plan
from .config import ROOT_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(ROOT_DIR / "templates"))


def _show_result(request: Request, record: FitnessPlan, error: str | None = None):
    original = json.loads(record.workout_plan)
    revised = json.loads(record.updated_plan) if record.updated_plan else None
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={"record": record, "plan": revised or original,
                 "is_updated": revised is not None, "error": error},
    )


@router.get("/", response_class=HTMLResponse, tags=["Pages"], summary="Show the FitBuddy plan form")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse, tags=["Plans"], summary="Generate and save a seven-day workout plan")
def generate_workout(request: Request, username: str = Form(...), age: str = Form(...), weight: str = Form(...),
                     goal: str = Form(...), intensity: str = Form(...), db: Session = Depends(get_db)):
    try:
        user = UserInput(username=username, age=age, weight=weight, goal=goal, intensity=intensity)
        plan = generate_workout_groq(user.age, user.weight, user.goal, user.intensity, user.username)
        tip = generate_nutrition_tip_with_flash(user.age, user.weight, user.goal, user.intensity)
        record = FitnessPlan(username=user.username, age=user.age, weight=user.weight, goal=user.goal,
            intensity=user.intensity, workout_plan=json.dumps(plan), nutrition_tip=tip)
        db.add(record)
        db.commit()
        db.refresh(record)
        return _show_result(request, record)
    except GroqError as exc:
        db.rollback()
        return templates.TemplateResponse(request=request, name="index.html", context={
            "error": str(exc),
            "values": {"username": username, "age": age, "weight": weight, "goal": goal, "intensity": intensity},
        }, status_code=400)
    except ValueError:
        db.rollback()
        return templates.TemplateResponse(request=request, name="index.html", context={
            "error": "Please check your details. Age must be 13–100, weight 25–350 kg, and all choices must be valid.",
            "values": {"username": username, "age": age, "weight": weight, "goal": goal, "intensity": intensity},
        }, status_code=400)
    except Exception as exc:
        db.rollback()
        log_provider_error("workout route", exc)
        return templates.TemplateResponse(request=request, name="index.html", context={
            "error": "We could not save or generate your plan. Please try again.",
        }, status_code=500)


@router.post("/update-plan/{plan_id}", response_class=HTMLResponse, tags=["Plans"], summary="Refine a saved plan using feedback")
def update_plan(plan_id: int, request: Request, feedback: str = Form(...), db: Session = Depends(get_db)):
    record = db.get(FitnessPlan, plan_id)
    if record is None:
        return templates.TemplateResponse(request=request, name="index.html", context={
            "error": "That plan could not be found.",
        }, status_code=404)
    try:
        clean = FeedbackInput(feedback=feedback.strip())
        profile = {"username": record.username, "age": record.age, "weight": record.weight,
                   "goal": record.goal, "intensity": record.intensity}
        refined = update_workout_plan(profile, json.loads(record.workout_plan), clean.feedback)
        record.feedback = clean.feedback
        record.updated_plan = json.dumps(refined)
        db.commit()
        db.refresh(record)
        return _show_result(request, record)
    except GroqError as exc:
        return _show_result(request, record, str(exc))
    except ValueError:
        return _show_result(request, record, "Please enter feedback of at least 3 characters (up to 1,000).")
    except Exception:
        db.rollback()
        return _show_result(request, record, "We could not update your plan. Please try again.")


@router.get("/users", response_class=HTMLResponse, tags=["Pages"], summary="Browse saved FitBuddy plans")
def all_users(request: Request, db: Session = Depends(get_db)):
    records = db.query(FitnessPlan).order_by(FitnessPlan.created_at.desc()).all()
    return templates.TemplateResponse(request=request, name="all_users.html", context={"records": records})


@router.get("/plans/{plan_id}", response_class=HTMLResponse, tags=["Plans"], summary="View a saved workout plan")
def saved_plan(plan_id: int, request: Request, db: Session = Depends(get_db)):
    record = db.get(FitnessPlan, plan_id)
    if record is None:
        return templates.TemplateResponse(request=request, name="index.html", context={
            "error": "That plan could not be found.",
        }, status_code=404)
    return _show_result(request, record)
