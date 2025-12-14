import cv2
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter


class ColorExtractor:
    """OpenCV를 사용한 색상 추출기"""
    
    def __init__(self):
        # 한글 색상 이름 매핑
        self.color_names = {
            "black": "블랙",
            "white": "화이트",
            "gray": "그레이",
            "red": "레드",
            "orange": "오렌지",
            "yellow": "옐로우",
            "green": "그린",
            "blue": "블루",
            "navy": "네이비",
            "purple": "퍼플",
            "pink": "핑크",
            "brown": "브라운",
            "beige": "베이지",
            "khaki": "카키"
        }
    
    def extract_dominant_colors(self, image_path, n_colors=3):
        """주요 색상 추출 (K-means 클러스터링)"""
        try:
            # 이미지 읽기
            image = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if image is None:
                print(f"⚠ 이미지 읽기 실패: {image_path}")
                # WebP 등 특수 형식은 imdecode로 시도
                try:
                    import numpy as np
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
                    if image is None:
                        return [{"name": "색상 추출 실패", "rgb": [128, 128, 128], "percentage": 100}]
                except Exception as e:
                    print(f"⚠ imdecode 실패: {e}")
                    return [{"name": "색상 추출 실패", "rgb": [128, 128, 128], "percentage": 100}]
            
            # RGB로 변환
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 이미지를 1차원 배열로 변환
            pixels = image.reshape(-1, 3)
            
            # K-means 클러스터링으로 주요 색상 찾기
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # 클러스터 중심 (주요 색상)
            colors = kmeans.cluster_centers_
            
            # 각 클러스터의 픽셀 수
            labels = kmeans.labels_
            label_counts = Counter(labels)
            
            # 색상을 픽셀 비율 순으로 정렬
            sorted_colors = sorted(
                zip(colors, [label_counts[i] for i in range(n_colors)]),
                key=lambda x: x[1],
                reverse=True
            )
            
            # RGB 값을 색상 이름으로 변환
            color_names = []
            for color, count in sorted_colors:
                r, g, b = color
                color_name = self.rgb_to_color_name(r, g, b)
                percentage = (count / len(labels)) * 100
                
                # 상위 3개 색상은 비율 관계없이 모두 포함 (최소 10% 조건 제거)
                if percentage > 5:  # 5% 이상인 색상만 포함 (기준 완화)
                    color_names.append({
                        "name": color_name,
                        "rgb": [int(r), int(g), int(b)],
                        "percentage": round(percentage, 1)
                    })
            
            # 최소 1개 색상은 반환
            if not color_names and sorted_colors:
                r, g, b = sorted_colors[0][0]
                color_names.append({
                    "name": self.rgb_to_color_name(r, g, b),
                    "rgb": [int(r), int(g), int(b)],
                    "percentage": round((sorted_colors[0][1] / len(labels)) * 100, 1)
                })
            
            print(f"  색상 추출 결과 ({image_path}): {color_names}")
            return color_names if color_names else [{"name": "기타", "rgb": [128, 128, 128], "percentage": 100}]
        
        except Exception as e:
            print(f"⚠ 색상 추출 중 오류 ({image_path}): {e}")
            import traceback
            traceback.print_exc()
            return [{"name": "색상 추출 실패", "rgb": [128, 128, 128], "percentage": 100}]
    
    def rgb_to_color_name(self, r, g, b):
        """RGB 값을 색상 이름으로 변환"""
        # 흑백 판별
        if r < 50 and g < 50 and b < 50:
            return self.color_names["black"]
        if r > 200 and g > 200 and b > 200:
            return self.color_names["white"]
        if abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30:
            return self.color_names["gray"]
        
        # 색상 판별
        if r > g and r > b:
            if g > 100 and b < 100:
                return self.color_names["orange"]
            elif b > g:
                return self.color_names["purple"]
            else:
                return self.color_names["red"]
        
        elif g > r and g > b:
            if r > 100:
                return self.color_names["yellow"]
            else:
                return self.color_names["green"]
        
        elif b > r and b > g:
            if b > 150 and r < 100:
                return self.color_names["navy"]
            else:
                return self.color_names["blue"]
        
        # 갈색/베이지 계열
        if r > b and g > b:
            if r > 150 and g > 120:
                return self.color_names["beige"]
            elif r > 100 and g > 80:
                return self.color_names["brown"]
            else:
                return self.color_names["khaki"]
        
        # 핑크
        if r > 150 and g < 150 and b > 100 and b < 200:
            return self.color_names["pink"]
        
        return "기타"
    
    def get_hex_color(self, r, g, b):
        """RGB를 HEX 코드로 변환"""
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
