from src.service.board_service import BoardService
from .introduce_service import introduce_bp
from .mypage_service import mypage_bp
from .admin_service import admin_bp
from .faq_service import faq_bp
from .tip_service import tip_bp
from .ai_model_service import model_bp
from .profile_service import profile_bp

__all__ = [
    'BoardService',
    'mypage_bp',
    'introduce_bp',
    'admin_bp',
    'faq_bp',
    'tip_bp',
    'model_bp',
    'profile_bp'
]