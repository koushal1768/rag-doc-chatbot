from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schema.config import ClientConfigOut, ClientConfigUpdate
from app.services.config_service import get_user_config, update_user_config

router = APIRouter()


@router.get("", response_model=ClientConfigOut)
def get_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves the current user's chatbot and model configuration."""
    return get_user_config(db, current_user.id)


@router.put("", response_model=ClientConfigOut)
def update_config(
    config_in: ClientConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Updates the current user's model selection, system prompt, or API key preferences."""
    return update_user_config(db, current_user.id, config_in)