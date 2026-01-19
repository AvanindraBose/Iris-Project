import mlflow
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

_model = None


def load_model():
    """
    Loads the Production model from MLflow Registry.
    Cached at process level.
    """
    global _model

    if _model is not None:
        return _model

    try:
        logger.info("Loading model from MLflow Registry")

        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)

        _model = mlflow.pyfunc.load_model(
            model_uri=f"models:/{settings.MODEL_NAME}/Production"
        )

        logger.info("Model loaded successfully from MLflow")

        return _model

    except Exception as e:
        logger.critical("Failed to load ML model from MLflow", exc_info=True)
        raise RuntimeError("Model initialization failed") from e
