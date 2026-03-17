from .MemberService import member_bp
from .introduce import introduce_bp
# from .BoardService import board_bp  # 만약 BoardService에도 bp가 있다면
# from .PostService import post_bp    # 만약 PostService에도 bp가 있다면

# 외부에서 접근하기 편하게 리스트업
__all__ = ['member_bp','introduce_bp']