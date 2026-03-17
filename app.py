import os
from flask import Flask, render_template, g
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')

from flask import Flask
from flask_caching import Cache

app = Flask(__name__)

# Cache 설정 (여기에 두세요!)
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# [중요] Blueprint 등록
from LMS.service.MemberService import member_bp
app.register_blueprint(member_bp)

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# 메인 페이지 라우트
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/member')
def member(): return render_template('member.html')

@app.route('/board')
def board(): return render_template('board.html')

# 서버 실행부 (하나로 통합)
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,      # 팀원 합의에 따라 5000으로 고정
        debug=True      # 개발 시에는 True가 편합니다
    )