import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()


class GeminiStyleAdvisor:
    """Gemini API를 사용한 스타일 어드바이저"""
    
    def __init__(self):
        # API 키 설정
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            print("⚠ GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            
            # gemini-2.5-flash 사용
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                print("✓ Gemini 2.5 Flash 모델 초기화 성공")
            except Exception as e:
                print(f"⚠ Gemini 모델 초기화 실패: {e}")
                self.model = None
    
    async def get_recommendation(self, user_info: dict, uploaded_items: dict):
        """
        사용자 정보와 업로드된 옷을 기반으로 코디 추천
        
        Args:
            user_info: {"gender": str, "age_group": str, "tpo": str}
            uploaded_items: {
                "outer": {"type": {...}, "colors": [...], "pattern": {...}},
                ...
            }
        """
        try:
            if not self.model:
                return {
                    "error": "API key not configured",
                    "message": "Gemini API 키가 설정되지 않았습니다.",
                    "recommendations": {},
                    "style_direction": "API 키를 설정하면 AI 추천을 받을 수 있습니다.",
                    "styling_tips": []
                }
            
            # 프롬프트 생성
            prompt = self._create_prompt(user_info, uploaded_items)
            
            # Gemini API 호출 (동기 방식을 비동기로 실행)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self.model.generate_content, 
                prompt
            )
            
            # 응답 파싱
            recommendation = self._parse_response(response.text, uploaded_items)
            
            return recommendation
        
        except Exception as e:
            print(f"Gemini API 호출 오류: {e}")
            import traceback
            traceback.print_exc()
            
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                return {
                    "error": "quota_exceeded",
                    "message": "⚠️ Gemini API 무료 할당량을 초과했습니다. 24시간 후 다시 시도하거나 새 API 키를 발급받아주세요.",
                    "recommendations": {},
                    "style_direction": "Gemini API 할당량 초과로 AI 추천을 제공할 수 없습니다. ML 모델 분석 결과는 정상적으로 표시됩니다.",
                    "styling_tips": []
                }
            
            return {
                "error": str(e),
                "message": "코디 추천을 생성할 수 없습니다.",
                "recommendations": {},
                "style_direction": f"오류 발생: {str(e)}",
                "styling_tips": []
            }
    
    def _create_prompt(self, user_info: dict, uploaded_items: dict):
        """Gemini에게 전달할 프롬프트 생성"""
        
        # 업로드된 아이템 정보 정리
        items_description = []
        missing_items = []
        
        categories = {
            "outer": "아우터",
            "inner1": "이너1 (겉 상의)",
            "inner2": "이너2 (속 상의)",
            "bottom": "하의"
        }
        
        for category, korean_name in categories.items():
            if category in uploaded_items:
                item = uploaded_items[category]
                # 색상 정보 처리
                if isinstance(item.get("colors"), list):
                    colors = ", ".join([c["name"] if isinstance(c, dict) else str(c) for c in item["colors"]])
                else:
                    colors = "정보 없음"
                
                # 타입 정보 처리
                item_type = item.get('type', {})
                type_label = item_type.get('label', '정보 없음') if isinstance(item_type, dict) else str(item_type)
                
                # 패턴 정보 처리
                item_pattern = item.get('pattern', {})
                pattern_label = item_pattern.get('label', '정보 없음') if isinstance(item_pattern, dict) else str(item_pattern)
                
                items_description.append(
                    f"- {korean_name}: {type_label} / 색상: {colors} / 무늬: {pattern_label}"
                )
            else:
                missing_items.append(korean_name)
        
        # 프롬프트 작성
        prompt = f"""
당신은 대학생을 위한 전문 패션 스타일리스트입니다. 
다음 정보를 바탕으로 겨울 코디를 추천해주세요.

**사용자 정보:**
- 성별: {user_info['gender']}
- 연령대: {user_info['age_group']}
- 체형: {user_info['body_type']}
- TPO (상황): {user_info['tpo']}

**현재 가지고 있는 옷:**
{chr(10).join(items_description)}

**추천이 필요한 아이템:**
{', '.join(missing_items)}

**요청사항:**
1. 위의 업로드된 옷들과 잘 어울리는 {', '.join(missing_items)}를 구체적으로 추천해주세요.
2. 전체 코디에 어울리는 신발을 추천해주세요 (스니커즈, 부츠, 로퍼 등).
3. 사용자의 체형({user_info['body_type']})을 고려하여 가장 잘 어울리는 핏과 스타일을 추천해주세요:
   - 슬림: 레이어드와 볼륨감으로 균형을 맞추세요
   - 보통: 다양한 스타일 자유롭게 소화 가능
   - 건장/근육질: 넉넉한 핏과 테일러드 아이템으로 스타일리시하게
   - 통통: 세로 라인 강조, 오버핏으로 편안하면서 세련되게
4. 각 추천 아이템(신발 포함)에 대해 다음을 포함해주세요:
   - 아이템 종류 (예: 청바지, 코트, 첼시부츠 등)
   - 추천 색상 (구체적인 색상명)
   - 추천 무늬/패턴
   - 추천 이유 (체형과 TPO를 고려한 이유)
5. 전체 코디의 스타일 방향성을 설명해주세요.
6. 실용적인 스타일링 팁 3-5개를 제공해주세요 (레이어드, 액세서리, 컬러 매칭 등).
7. 대학생에게 어울리고 {user_info['tpo']} 상황에 적절한 실용적인 추천을 해주세요.

**출력 형식:**
다음 JSON 형식으로 답변해주세요:
{{
  "recommendations": {{
    "outer": {{"item": "...", "color": "...", "pattern": "...", "reason": "..."}},
    "inner1": {{"item": "...", "color": "...", "pattern": "...", "reason": "..."}},
    "inner2": {{"item": "...", "color": "...", "pattern": "...", "reason": "..."}},
    "bottom": {{"item": "...", "color": "...", "pattern": "...", "reason": "..."}},
    "shoes": {{"item": "...", "color": "...", "reason": "..."}}
  }},
  "style_direction": "전체 코디 스타일 설명 (컨셉, 무드, 특징 등)",
  "styling_tips": ["실용적인 스타일링 팁1", "팁2", "팁3", "팁4", "팁5"]
}}

이미 업로드된 아이템은 그대로 유지하고, 누락된 아이템만 추천해주세요.
"""
        
        return prompt
    
    def _parse_response(self, response_text: str, uploaded_items: dict):
        """Gemini 응답 파싱"""
        try:
            # ```json 코드 블록 제거
            response_text = response_text.strip()
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            # JSON 부분 추출
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                parsed = json.loads(json_text)
                
                # 이미 업로드된 아이템은 원본 정보 유지
                if "recommendations" in parsed:
                    for category in ["outer", "inner1", "inner2", "bottom"]:
                        if category in uploaded_items:
                            parsed["recommendations"][category] = {
                                "item": uploaded_items[category]["type"]["label"],
                                "color": ", ".join([c["name"] for c in uploaded_items[category]["colors"]]),
                                "pattern": uploaded_items[category]["pattern"]["label"],
                                "reason": "사용자가 업로드한 아이템",
                                "uploaded": True
                            }
                
                return parsed
            else:
                # JSON 형식이 아닌 경우 텍스트 그대로 반환
                print(f"⚠ JSON 파싱 실패. 응답 텍스트:\n{response_text[:500]}")
                return {
                    "recommendations": {},
                    "style_direction": "AI가 JSON 형식으로 응답하지 않았습니다. 다시 시도해주세요.",
                    "styling_tips": [],
                    "raw_response": response_text[:1000]
                }
        
        except Exception as e:
            print(f"응답 파싱 오류: {e}")
            print(f"응답 텍스트:\n{response_text[:500]}")
            return {
                "recommendations": {},
                "style_direction": "응답 파싱 중 오류가 발생했습니다.",
                "styling_tips": [],
                "parse_error": str(e),
                "raw_response": response_text[:1000]
            }
