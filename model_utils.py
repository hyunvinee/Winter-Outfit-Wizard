import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image
import os
from pathlib import Path


class ClothingClassifier:
    """ML 모델을 사용한 의류 분류기"""
    
    def __init__(self, model_dir="models"):
        self.model_dir = Path(model_dir)
        self.models = {}
        self.load_models()
        
        # 카테고리별 클래스 레이블 (폴더명 알파벳순으로 정렬된 순서와 매칭)
        # 학습 시 ImageDataGenerator가 자동으로 알파벳순 정렬하므로 순서 중요!
        self.labels = {
            "outer": [
                "블루종/MA-1",      # blouson_ma1
                "코트",             # coat
                "플리스",           # fleece
                "레더/라이더 자켓", # leather_jacket
                "경량 패딩",        # light_padding
                "롱패딩",           # long_padding
                "무스탕",           # mustang
                "패딩 베스트",      # padding_vest
                "숏패딩"            # short_padding
            ],
            "inner1": [
                "카디건",           # cardigan
                "후드티",           # hoodie
                "니트/스웨터",      # knit
                "맨투맨/스웨트"     # sweatshirt
            ],
            "inner2": [
                "긴팔티",           # long_sleeve
                "셔츠",             # shirt
                "반팔티",           # short_sleeve
                "목폴라/터틀넥"     # turtleneck
            ],
            "bottom": [
                "카고팬츠",         # cargo
                "코듀로이",         # corduroy
                "면바지/치노",      # cotton_chino
                "청바지/데님",      # jeans
                "롱스커트",         # long_skirt
                "미디스커트",       # midi_skirt
                "미니스커트",       # mini_skirt
                "슬랙스",           # slacks
                "트레이닝/조거 팬츠" # training_jogger
            ],
            "pattern": [
                "카모",             # camo
                "체크",             # check
                "그래픽/레터링",    # graphic
                "로고",             # logo
                "무지",             # plain
                "스트라이프"        # stripe
            ]
        }
    
    def create_model_architecture(self, num_classes):
        """모델 구조 생성 (학습 시와 동일한 구조)"""
        base_model = keras.applications.MobileNetV2(
            input_shape=(224, 224, 3),
            include_top=False,
            weights='imagenet'
        )
        base_model.trainable = False
        
        model = keras.Sequential([
            keras.layers.Input(shape=(224, 224, 3)),
            base_model,
            keras.layers.GlobalAveragePooling2D(),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(512, activation='relu'),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        return model
    
    def load_models(self):
        """저장된 모델 로드"""
        import tempfile
        import shutil
        
        try:
            # 각 카테고리별 클래스 수
            num_classes_map = {
                "outer": 9,
                "inner1": 4,  # 수정: 카디건, 후드티, 니트, 맨투맨
                "inner2": 4,  # 수정: 긴팔티, 셔츠, 반팔티, 목폴라
                "bottom": 9,  # 수정: 카고, 코듀로이, 면바지, 청바지, 롱스커트, 미디스커트, 미니스커트, 슬랙스, 조거팬츠
                "pattern": 6
            }
            
            # 각 카테고리별 가중치 로드
            weight_files = {
                "outer": "outer_best.h5",
                "inner1": "inner1_best.h5",
                "inner2": "inner2_best.h5",
                "bottom": "bottom_best.h5",
                "pattern": "pattern_best.h5"
            }
            
            for category, filename in weight_files.items():
                try:
                    weights_path = self.model_dir / filename
                    if weights_path.exists():
                        # 모델 구조 생성
                        num_classes = num_classes_map[category]
                        model = self.create_model_architecture(num_classes)
                        
                        # 가중치 로드
                        model.load_weights(str(weights_path))
                        self.models[category] = model
                        print(f"✓ {category} 모델 로드 완료: {filename}")
                    else:
                        print(f"⚠ {category} 가중치 파일 없음: {filename} (Gemini로 대체)")
                        self.models[category] = None
                except Exception as e:
                    print(f"⚠ {category} 모델 로드 실패: {e}")
                    self.models[category] = None
        
        except Exception as e:
            print(f"모델 로드 중 전체 오류: {e}")
    
    def preprocess_image(self, image_path, target_size=(224, 224)):
        """이미지 전처리"""
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize(target_size)
            img_array = np.array(img) / 255.0  # 정규화
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
        except Exception as e:
            print(f"이미지 전처리 오류: {e}")
            return None
    
    def classify_item(self, image_path, category):
        """의류 아이템 분류"""
        if category not in self.models or self.models[category] is None:
            # 모델이 없으면 기본값 반환
            return {
                "label": "분류 불가 (모델 로드 실패)",
                "confidence": 0
            }
        
        try:
            # 이미지 전처리
            img_array = self.preprocess_image(image_path)
            if img_array is None:
                return "이미지 처리 실패"
            
            # 예측
            model = self.models[category]
            predictions = model.predict(img_array, verbose=0)
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            
            # 레이블 가져오기
            if category in self.labels and predicted_class < len(self.labels[category]):
                label = self.labels[category][predicted_class]
            else:
                label = f"클래스_{predicted_class}"
            
            return {
                "label": label,
                "confidence": round(confidence * 100, 2)
            }
        
        except Exception as e:
            print(f"분류 중 오류: {e}")
            return {"label": "분류 실패", "confidence": 0}
    
    def classify_pattern(self, image_path):
        """무늬 패턴 분류"""
        if "pattern" not in self.models or self.models["pattern"] is None:
            return {
                "label": "분류 불가 (모델 로드 실패)",
                "confidence": 0
            }
        
        try:
            # 이미지 전처리
            img_array = self.preprocess_image(image_path)
            if img_array is None:
                return "이미지 처리 실패"
            
            # 예측
            model = self.models["pattern"]
            predictions = model.predict(img_array, verbose=0)
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            
            # 레이블 가져오기
            if predicted_class < len(self.labels["pattern"]):
                label = self.labels["pattern"][predicted_class]
            else:
                label = f"패턴_{predicted_class}"
            
            return {
                "label": label,
                "confidence": round(confidence * 100, 2)
            }
        
        except Exception as e:
            print(f"무늬 분류 중 오류: {e}")
            return {"label": "분류 실패", "confidence": 0}
