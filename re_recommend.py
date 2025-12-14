"""
재추천 기능 - 수정된 정보로 Gemini API 재호출
"""
from gemini_service import get_outfit_recommendation

async def get_re_recommendation(user_info: dict, uploaded_items: dict) -> dict:
    """
    수정된 아이템 정보로 Gemini에 재추천 요청
    
    Args:
        user_info: 사용자 정보 (성별, 나이, 스타일, 날씨)
        uploaded_items: 수정된 아이템 정보 (outer, inner1, inner2, bottom, colors)
    
    Returns:
        Gemini의 추천 결과
    """
    try:
        recommendation = await get_outfit_recommendation(user_info, uploaded_items)
        return {"recommendation": recommendation}
    except Exception as e:
        raise Exception(f"재추천 실패: {str(e)}")
