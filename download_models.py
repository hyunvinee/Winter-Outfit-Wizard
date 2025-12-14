import os
import gdown

# Google Drive 파일 ID와 저장 경로
MODEL_FILES = {
    "bottom_best.h5": "1GHbg0IqtoNZg__SEAsdJ2t2ennE6M-ED",
    "inner1_best.h5": "1mPdUcp6k0a1eotr016NS-j-3Z_s04JXg",
    "inner2_best.h5": "1qjjNcXq3Dyy162REjU-IMmGptg65c7th",
    "outer_best.h5": "1kSi8pwJSbpFP8I2wq67v1WgBK6_MUAwf",
    "pattern_best.h5": "1INIHjprBAGtUYxyrBtWGb3VA1Sib45MZ"
}

def download_models():
    """Google Drive에서 모델 파일 다운로드"""
    models_dir = "models"
    
    # models 디렉토리 생성
    os.makedirs(models_dir, exist_ok=True)
    
    print("Checking and downloading model files from Google Drive...")
    
    for filename, file_id in MODEL_FILES.items():
        file_path = os.path.join(models_dir, filename)
        
        # 파일이 이미 존재하면 건너뛰기
        if os.path.exists(file_path):
            print(f"✓ {filename} already exists")
            continue
        
        # Google Drive에서 다운로드
        print(f"Downloading {filename}...")
        url = f"https://drive.google.com/uc?id={file_id}"
        
        try:
            gdown.download(url, file_path, quiet=False)
            print(f"✓ {filename} downloaded successfully")
        except Exception as e:
            print(f"✗ Failed to download {filename}: {e}")
            raise
    
    print("All model files are ready!")

if __name__ == "__main__":
    download_models()
