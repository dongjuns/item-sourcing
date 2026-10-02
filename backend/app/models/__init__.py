"""마이그레이션이 모든 테이블을 찾도록 모델을 모은다."""

from app.models.ai_call import AICall
from app.models.asset import Asset
from app.models.base import Base
from app.models.job import Job
from app.models.listing import Listing
from app.models.product import Product
from app.models.registration import Registration
from app.models.setting import Setting

__all__ = ["AICall", "Asset", "Base", "Job", "Listing", "Product", "Registration", "Setting"]
