from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from flask_bootstrap import Bootstrap
from dog_breed_analyzer import analyze_dog_breed
from flask_cors import CORS

app = Flask(__name__)
Bootstrap(app)
CORS(app)  # CORS 지원 추가
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 모델 로드
model = MobileNetV2(weights='imagenet')

# 업로드 폴더 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/service', methods=['POST'])
def service():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '선택된 파일이 없습니다.'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # 이미지 예측 수행
            predictions = predict(file)
            
            if predictions and len(predictions) > 0:
                # 가장 높은 신뢰도를 가진 품종 분석
                top_breed = predictions[0]['breed']
                breed_analysis = analyze_dog_breed(top_breed)

                # 분석 결과를 적절한 구조로 변환
                result = {
                    'predictions': predictions,
                    'breed_analysis': breed_analysis
                }
                return jsonify(result)
            else:
                return jsonify({'error': '이미지 분석에 실패했습니다.'}), 500
        except Exception as e:
            print(f"Error in service function: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': '허용되지 않는 파일 형식입니다.'}), 400

def predict(file):
    try:
        # 이미지 전처리
        img = Image.open(file).resize((224, 224))
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # 예측
        predictions = model.predict(img_array)
        decoded_predictions = decode_predictions(predictions, top=3)[0]
        
        # 결과 처리
        results = []
        for _, label, prob in decoded_predictions:
            # 라벨을 한국어로 변환
            korean_label = translate_breed_to_korean(label)
            results.append({
                'breed': korean_label,
                'confidence': float(prob)
            })
        
        return results
    except Exception as e:
        print(f"Error in predict function: {str(e)}")
        return []

def translate_breed_to_korean(english_breed):
    # 간단한 번역 매핑 (실제로는 더 많은 품종이 필요할 수 있습니다)
    breed_translation = {
        'golden_retriever': '골든 리트리버',
        'labrador_retriever': '래브라도 리트리버',
        'german_shepherd': '저먼 셰퍼드',
        'bulldog': '불독',
        'poodle': '푸들',
        'beagle': '비글',
        'chihuahua': '치와와',
        'shih_tzu': '시츄',
        'maltese': '말티즈',
        'pomeranian': '포메라니안'
    }
    return breed_translation.get(english_breed.lower(), english_breed)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5001, debug=True) 