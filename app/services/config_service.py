from sqlalchemy.orm import Session
from app.models.client_config import ClientConfig
from app.schema.config import ClientConfigUpdate


def get_user_config(db: Session, user_id: str) -> ClientConfig:
    """Retrieves or auto-initializes default config for a user."""
    config = db.query(ClientConfig).filter(ClientConfig.user_id == user_id).first()
    if not config:
        config = ClientConfig(user_id=user_id)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def update_user_config(db: Session, user_id: str, config_in: ClientConfigUpdate) -> ClientConfig:
    """Updates the user's configuration parameters."""
    config = get_user_config(db, user_id)
    
    update_data = config_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
        
    db.commit()
    db.refresh(config)
    return config