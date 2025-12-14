from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
from pathlib import Path

from model_utils import ClothingClassifier
from color_extractor import ColorExtractor
from gemini_service import GeminiStyleAdvisor

app = FastAPI(title="Winter Outfit Wizard")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
classifier = ClothingClassifier()
color_extractor = ColorExtractor()
gemini_advisor = GeminiStyleAdvisor()

# Upload folder
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze")
async def analyze_outfit(
    gender: str = Form(...),
    age_group: str = Form(...),
    body_type: str = Form(...),
    tpo: str = Form(...),
    outer: Optional[UploadFile] = File(None),
    inner1: Optional[UploadFile] = File(None),
    inner2: Optional[UploadFile] = File(None),
    bottom: Optional[UploadFile] = File(None),
):
    """
    사용자 입력 분석 및 코디 추천
    """
    try:
        # 업로드된 옷 분석
        uploaded_items = {}
        
        for category, file in [("outer", outer), ("inner1", inner1), ("inner2", inner2), ("bottom", bottom)]:
            if file and file.filename:
                # 파일 저장
                file_path = UPLOAD_FOLDER / f"{category}_{file.filename}"
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                
                # 옷 종류 및 무늬 분석 (ML 모델)
                clothing_type = classifier.classify_item(str(file_path), category)
                pattern = classifier.classify_pattern(str(file_path))
                
                # 색상 추출 (OpenCV)
                colors = color_extractor.extract_dominant_colors(str(file_path))
                
                uploaded_items[category] = {
                    "type": clothing_type,
                    "colors": colors,
                    "pattern": pattern,
                    "image_path": str(file_path)
                }
                
                print(f"✓ {category} 처리 완료 - 색상: {colors}")
        
        # 사용자 정보
        user_info = {
            "gender": gender,
            "age_group": age_group,            'body_type': body_type,            "tpo": tpo
        }
        
        # Gemini API로 코디 추천
        print(f"\n📊 Gemini API 호출 시작...")
        print(f"   사용자 정보: {user_info}")
        print(f"   업로드된 아이템: {list(uploaded_items.keys())}")
        
        recommendation = await gemini_advisor.get_recommendation(
            user_info=user_info,
            uploaded_items=uploaded_items
        )
        
        print(f"✓ Gemini 추천 완료")
        print(f"   추천 항목 수: {len(recommendation.get('recommendations', {}))}")
        
        # 최종 응답 데이터 로깅
        response_data = {
            "success": True,
            "user_info": user_info,
            "uploaded_items": uploaded_items,
            "recommendation": recommendation
        }
        print(f"\n📤 클라이언트로 전송하는 데이터:")
        print(f"   uploaded_items 키: {list(uploaded_items.keys())}")
        for cat, item in uploaded_items.items():
            print(f"   {cat}: colors={item.get('colors')}")
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "service": "Winter Outfit Wizard"}


# 재추천 요청 모델
class ReRecommendRequest(BaseModel):
    user_info: Dict[str, Any]
    uploaded_items: Dict[str, Any]


@app.post("/api/re-recommend")
async def re_recommend(request: ReRecommendRequest):
    """
    수정된 아이템 정보로 Gemini에 재추천 요청
    """
    try:
        print("\n🔄 재추천 요청 받음")
        print(f"   User info: {request.user_info}")
        print(f"   Items: {list(request.uploaded_items.keys())}")
        
        # Gemini에 재추천 요청
        recommendation = await gemini_advisor.get_recommendation(
            request.user_info,
            request.uploaded_items
        )
        
        print(f"✅ 재추천 완료")
        
        return JSONResponse(content={"recommendation": recommendation})
        
    except Exception as e:
        print(f"❌ 재추천 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
