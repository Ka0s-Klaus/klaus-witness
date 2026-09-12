from celery import Celery, shared_task
from config import settings
from core.database import SessionLocal
from core.models import User
from core.consolidator.consolidator import BeliefConsolidator
from core.adapters.anthropic_adapter import AnthropicProvider
import logging

logger = logging.getLogger(__name__)

app = Celery("testigo")
app.conf.broker_url = settings.redis_url
app.conf.result_backend = settings.redis_url

@shared_task
def consolidate_all_users():
    """Job que corre a las 2 AM: consolidar todos los usuarios"""
    if not settings.consolidation_enabled:
        logger.info("Consolidación deshabilitada")
        return

    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()

        for user in users:
            consolidate_user_task.delay(str(user.id))

        logger.info(f"Lanzados trabajos de consolidación para {len(users)} usuarios")
        return {"users_scheduled": len(users)}
    finally:
        db.close()

@shared_task
def consolidate_user_task(user_id: str):
    """Consolidar un usuario específico"""
    db = SessionLocal()
    try:
        llm_provider = AnthropicProvider()
        consolidator = BeliefConsolidator(db=db, llm_provider=llm_provider)

        import asyncio
        result = asyncio.run(consolidator.consolidate_user(user_id))

        # Cada 3 consolidaciones, versionar persona
        consolidations_count = 12  # Simulado
        if consolidations_count % 3 == 0:
            version_result = asyncio.run(consolidator.version_persona(user_id))
            logger.info(f"Persona versionada para {user_id}: {version_result}")

        return result
    except Exception as e:
        logger.error(f"Error consolidando usuario {user_id}: {e}")
        raise
    finally:
        db.close()
