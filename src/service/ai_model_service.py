import cv2
import os
import datetime
import shutil
from flask import Blueprint, render_template, request, jsonify, Response, current_app
from src.common import login_required
from src.common.storage import upload_file
from ultralytics import YOLO

model_bp = Blueprint('model', __name__)

# 1. YOLOv11 모델 로드
MODEL_PATH = 'static/model/best.pt'
model = YOLO(MODEL_PATH)


@model_bp.route('/', methods=['GET'])
@login_required
def get_model_page():
    return render_template('ai_model/model.html')


# 실시간 분석 프레임 생성기
def generate_frames(video_path):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # YOLOv11 분석
        results = model.predict(frame, conf=0.25, verbose=False)
        annotated_frame = results[0].plot()

        # JPEG 인코딩
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret: continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()
    if os.path.exists(video_path):
        os.remove(video_path)


# 실시간 영상 스트리밍 라우트
@model_bp.route('/video_feed/<filename>')
@login_required
def video_feed(filename):
    temp_path = os.path.join('static/temp', filename)
    if not os.path.exists(temp_path):
        return "파일을 찾을 수 없습니다.", 404

    return Response(generate_frames(temp_path),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# 단일 프레임/이미지 탐지 (기존 AJAX 통신용)
@model_bp.route('/detect', methods=['POST'])
@login_required
def detect_objects():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    temp_path = os.path.join('static/temp', 'temp_frame.jpg')
    os.makedirs('static/temp', exist_ok=True)
    file.save(temp_path)

    try:
        results = model.predict(temp_path, conf=0.4, save=False)
        label_map = {'boar': '멧돼지', 'water_deer': '고라니', 'racoon': '너구리'}
        counts = {"멧돼지": 0, "고라니": 0, "너구리": 0}
        detections = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                eng_label = model.names[cls_id]
                kor_label = label_map.get(eng_label, eng_label)
                conf = float(box.conf[0])
                b = box.xyxyn[0].tolist()

                detections.append({
                    'label': kor_label,
                    'conf': f"{conf:.2f}",
                    'bbox': b
                })
                if kor_label in counts:
                    counts[kor_label] += 1

        return jsonify({
            'success': True,
            'counts': [counts["멧돼지"], counts["고라니"], counts["너구리"]],
            'detections': detections
        })
    except Exception as e:
        print(f"Error during detection: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# 결과 저장 및 Cloudinary 업로드 (최종 수정 완료)
@model_bp.route('/save_result', methods=['POST'])
@login_required
def save_result():
    file = request.files.get('merged_image')
    original_filename = request.form.get('original_filename', '')

    if not file:
        return jsonify({"success": False, "message": "데이터가 없습니다."}), 400

    local_path = None
    try:
        # 1. 경로 설정 및 폴더 생성 보장
        save_dir = os.path.join(current_app.root_path, 'static', 'results')
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs('static/temp', exist_ok=True)

        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        is_video = any(original_filename.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv'])

        if is_video:
            # --- [영상 처리 로직] ---
            temp_input = os.path.join('static', 'temp', f"temp_{original_filename}")
            file.save(temp_input)

            # YOLO 결과 저장
            model.predict(source=temp_input, save=True, project=save_dir, name=now_str, conf=0.25)

            # YOLO가 만든 폴더 안의 내용물을 확장자 관계없이 낚아채기
            yolo_output_dir = os.path.join(save_dir, now_str)
            files_in_yolo_dir = os.listdir(yolo_output_dir) if os.path.exists(yolo_output_dir) else []

            filename = f"detection_{now_str}.mp4"
            local_path = os.path.join(save_dir, filename)

            if files_in_yolo_dir:
                yolo_actual_file = files_in_yolo_dir[0]
                yolo_actual_path = os.path.join(yolo_output_dir, yolo_actual_file)
                shutil.move(yolo_actual_path, local_path)
                shutil.rmtree(yolo_output_dir)
            else:
                raise FileNotFoundError(f"YOLO가 결과 영상을 생성하지 못했습니다.")

            if os.path.exists(temp_input):
                os.remove(temp_input)

        else:
            # --- [이미지 처리 로직: 누락됐던 부분 복구] ---
            filename = f"detection_{now_str}.jpg"
            local_path = os.path.join(save_dir, filename)
            file.save(local_path) # 전송된 이미지 파일을 로컬에 저장

        # 2. [공통] Cloudinary 업로드
        if local_path and os.path.exists(local_path):
            with open(local_path, 'rb') as f:
                result_url = upload_file(f, folder="results")

            if result_url:
                return jsonify({
                    "success": True,
                    "url": result_url,
                    "message": "로컬 및 클라우드 저장 성공!"
                })

        return jsonify({"success": False, "message": "업로드 실패 (경로 확인 필요)"}), 500

    except Exception as e:
        print(f"Error during save_result: {e}")
        return jsonify({"success": False, "message": str(e)}), 500