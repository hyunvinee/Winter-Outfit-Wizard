# Winter Outfit Wizard ❄️

대학생을 위한 AI 기반 겨울 코디 추천 웹 애플리케이션

## 📋 프로젝트 개요

사용자가 보유한 겨울 옷 사진을 업로드하면, 머신러닝 모델로 옷의 종류, 색상, 무늬를 분석하고, Gemini API를 활용하여 업로드하지 않은 아이템에 대한 코디를 추천해주는 웹 서비스입니다.

## ✨ 주요 기능

1. **사용자 정보 입력**
   - 성별, 연령대(20대 초반/중반/후반), TPO(상황) 선택

2. **옷 사진 업로드**
   - 아우터, 이너1(겉 상의), 이너2(속 상의), 하의
   - 원하는 만큼만 업로드 가능

3. **AI 분석**
   - **ML 모델**: 옷 종류, 무늬 판별
   - **OpenCV**: 주요 색상 추출
   - **Gemini API**: 업로드하지 않은 아이템 추천

4. **코디 추천**
   - 전체 스타일 방향성 제시
   - 아이템별 상세 추천 (종류, 색상, 무늬, 추천 이유)
   - 스타일링 팁 제공

## 🛠️ 기술 스택

### 백엔드
- **FastAPI**: 빠른 비동기 웹 프레임워크
- **TensorFlow/Keras**: ML 모델 로딩 및 추론
- **OpenCV**: 이미지 색상 분석
- **Google Generative AI (Gemini)**: 코디 추천

### 프론트엔드
- **HTML5**: 구조
- **Tailwind CSS**: 세련된 UI 디자인
- **JavaScript**: 동적 기능 및 API 통신

## 📁 프로젝트 구조

```
Winter Outfit Wizard/
├── models/                    # 학습된 ML 모델
│   ├── outer_best.h5
│   ├── inner1_best.h5
│   ├── inner2_best.h5
│   ├── bottom_best.h5
│   └── pattern_best.h5
├── templates/
│   └── index.html            # 메인 페이지
├── static/
│   ├── css/
│   │   └── style.css        # 커스텀 스타일
│   └── js/
│       └── main.js          # JavaScript 로직
├── uploads/                  # 업로드된 이미지 저장
├── app.py                    # FastAPI 메인 애플리케이션
├── model_utils.py           # ML 모델 유틸리티
├── color_extractor.py       # 색상 추출기
├── gemini_service.py        # Gemini API 통합
├── requirements.txt         # Python 패키지
├── .env                     # 환경 변수 (생성 필요)
├── .env.example             # 환경 변수 예시
└── README.md
```

## 🚀 설치 및 실행

### 1. 환경 설정

```powershell
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
.\venv\Scripts\Activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성:

```bash
# .env.example을 복사하여 .env 파일 생성
copy .env.example .env
```

`.env` 파일 수정:

```
GEMINI_API_KEY=여기에_실제_API_키_입력
MODEL_PATH=./models
```

**Gemini API 키 발급 방법:**
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Create API Key" 클릭
3. 발급된 키를 `.env` 파일에 입력

### 3. 서버 실행

```powershell
python app.py
```

서버가 실행되면 브라우저에서 접속:
```
http://localhost:8000
```

## 📖 사용 방법

1. **기본 정보 입력**
   - 성별 선택
   - 연령대 선택 (20대 초반/중반/후반)
   - TPO 선택 (캠퍼스 일상, 데이트, 면접 등)

2. **옷 사진 업로드**
   - 원하는 카테고리에 옷 사진 업로드
   - 최소 1개 이상 업로드 필요
   - 업로드하지 않은 아이템은 AI가 추천

3. **AI 코디 추천 받기**
   - "AI 코디 추천 받기" 버튼 클릭
   - 분석 결과 및 추천 코디 확인

## 🎨 ML 모델 정보

프로젝트에 포함된 모델:

- `outer_best.h5`: 아우터 종류 분류
- `inner1_best.h5`: 이너1 (겉 상의) 종류 분류
- `inner2_best.h5`: 이너2 (속 상의) 종류 분류
- `bottom_best.h5`: 하의 종류 분류
- `pattern_best.h5`: 무늬 패턴 분류

각 모델은 224x224 크기의 RGB 이미지를 입력받습니다.

## 🔧 주요 설정

### model_utils.py
실제 모델 학습 시 사용한 클래스 레이블에 맞게 수정 필요:

```python
self.labels = {
    "outer": ["패딩", "코트", "자켓", "야상", "무스탕", "점퍼"],
    "inner1": ["후드티", "맨투맨", "니트", "셔츠", "카디건"],
    # ... 실제 레이블로 수정
}
```

### color_extractor.py
색상 추출 개수 조정:

```python
def extract_dominant_colors(self, image_path, n_colors=3):
    # n_colors를 조정하여 추출할 색상 개수 변경 가능
```

## 🐛 문제 해결

### 모델 로딩 오류
- `models/` 폴더에 모든 `.h5` 파일이 있는지 확인
- TensorFlow 버전 호환성 확인

### Gemini API 오류
- `.env` 파일의 API 키 확인
- API 키 할당량 확인

### 이미지 업로드 오류
- 지원 형식: JPG, JPEG, PNG, GIF
- 파일 크기 제한 확인

## 📝 라이센스

이 프로젝트는 대학 과제용으로 제작되었습니다.

## 👥 기여

개선 사항이나 버그 리포트는 이슈로 등록해주세요.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 언제든지 연락주세요.

---

**Made with ❤️ for college students**
