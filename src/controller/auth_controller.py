# src/controller/auth_controller.py
from datetime import date
from flask import (
    Blueprint, request, session, flash,
    render_template, redirect, url_for
)
from src.service.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    try:
        member = auth_service.login(
            uid      = request.form.get('uid'),
            password = request.form.get('upw'),
        )
        # session 저장은 Controller 책임
        session.update(member.to_session())
        return redirect(url_for('index'))


    except PermissionError as e:

        return f"""
            <script>
                alert('비활성화 처리된 계정입니다.');
                location.href = '/auth/login';
            </script>
        """


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    auth_service.logout()
    session.clear()
    flash('로그아웃 되었습니다.')
    return redirect(url_for('auth.login'))


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('auth/signup.html', year_now=date.today().year)

    try:
        auth_service.signup(
            uid         = request.form.get('uid'),
            password    = request.form.get('password'),
            name        = request.form.get('name'),
            nickname    = request.form.get('nickname'),
            birth_year  = request.form.get('birth_year'),
            birth_month = request.form.get('birth_month'),
            birth_day   = request.form.get('birth_day'),
        )
        return '<script>alert("가입 완료!"); location.href="/auth/login";</script>'

    except PermissionError as e:
        # 만 14세 미만
        return f"<script>alert('{e}'); history.back();</script>"
    except ValueError as e:
        # 중복 UID, 누락 입력, 잘못된 날짜
        return f"<script>alert('{e}'); history.back();</script>"
    except Exception as e:
        print(f"가입 에러: {e}")
        return '가입 중 오류 발생'