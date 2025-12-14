// 드래그 앤 드롭 기능 초기화 - v2.0
document.addEventListener('DOMContentLoaded', function() {
    initializeDragAndDrop();
});

// 정보 모달 열기
function showInfoModal() {
    document.getElementById('infoModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // 스크롤 방지
}

// 정보 모달 닫기
function closeInfoModal() {
    document.getElementById('infoModal').classList.add('hidden');
    document.body.style.overflow = 'auto'; // 스크롤 복원
}

// 모달 외부 클릭 시 닫기
document.addEventListener('click', function(e) {
    const modal = document.getElementById('infoModal');
    if (modal && e.target === modal) {
        closeInfoModal();
    }
});

// ESC 키로 모달 닫기
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeInfoModal();
    }
});

// 토스트 알림 표시 함수
function showToast(message) {
    // 기존 토스트 제거
    const existingToast = document.getElementById('toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    // 새 토스트 생성
    const toast = document.createElement('div');
    toast.id = 'toast-notification';
    toast.className = 'fixed bottom-8 right-8 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4 rounded-lg shadow-2xl flex items-center space-x-3 z-50 animate-slide-in-right';
    toast.innerHTML = `
        <span class="text-lg">${message}</span>
        <button onclick="this.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">✕</button>
    `;
    
    document.body.appendChild(toast);
    
    // 5초 후 자동 제거
    setTimeout(() => {
        if (toast && toast.parentElement) {
            toast.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

function initializeDragAndDrop() {
    const uploadBoxes = document.querySelectorAll('.upload-box');
    
    uploadBoxes.forEach(box => {
        const dropzone = box.querySelector('.dropzone');
        const input = box.querySelector('input[type="file"]');
        const category = box.dataset.category;
        
        // 클릭 이벤트
        dropzone.addEventListener('click', () => {
            input.click();
        });
        
        // 파일 선택 이벤트 (클릭으로 선택 시)
        input.addEventListener('change', () => {
            if (input.files && input.files[0]) {
                previewImage(input, category);
            }
        });
        
        // 드래그 오버
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('drag-over');
        });
        
        // 드래그 떠남
        dropzone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('drag-over');
        });
        
        // 드롭
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                
                // 이미지 파일 체크
                if (file.type.startsWith('image/')) {
                    // input에 파일 할당
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    input.files = dataTransfer.files;
                    
                    // 미리보기
                    previewImage(input, category);
                } else {
                    alert('이미지 파일만 업로드 가능합니다.');
                }
            }
        });
    });
}

// 이미지 미리보기
function previewImage(input, category) {
    const previewContainer = document.getElementById(`preview-${category}`);
    const uploadBox = input.closest('.upload-box');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            previewContainer.innerHTML = `
                <img src="${e.target.result}" alt="${category} preview" class="rounded-lg shadow-md">
                <button type="button" onclick="removeImage('${category}')" 
                        class="mt-2 text-xs text-red-600 hover:text-red-800 font-medium">
                    ❌ 삭제
                </button>
            `;
            uploadBox.classList.add('has-image');
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// 이미지 삭제
function removeImage(category) {
    const input = document.querySelector(`input[name="${category}"]`);
    const previewContainer = document.getElementById(`preview-${category}`);
    const uploadBox = input.closest('.upload-box');
    
    input.value = '';
    previewContainer.innerHTML = '';
    uploadBox.classList.remove('has-image');
}

// 폼 제출
document.getElementById('outfitForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // 로딩 표시
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    
    // 스크롤
    document.getElementById('loading').scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // FormData 생성
    const formData = new FormData();
    
    // 기본 정보
    const gender = document.querySelector('input[name="gender"]:checked')?.value;
    const ageGroup = document.querySelector('select[name="age_group"]').value;
    const bodyType = document.querySelector('select[name="body_type"]').value;
    const tpo = document.querySelector('select[name="tpo"]').value;
    
    if (!gender || !ageGroup || !bodyType || !tpo) {
        alert('기본 정보를 모두 입력해주세요!');
        document.getElementById('loading').classList.add('hidden');
        return;
    }
    
    formData.append('gender', gender);
    formData.append('age_group', ageGroup);
    formData.append('body_type', bodyType);
    formData.append('tpo', tpo);
    
    // 옷 이미지
    const categories = ['outer', 'inner1', 'inner2', 'bottom'];
    let hasImage = false;
    
    categories.forEach(category => {
        const input = document.querySelector(`input[name="${category}"]`);
        console.log(`${category}: files =`, input.files, 'length =', input.files?.length);
        if (input && input.files && input.files.length > 0) {
            formData.append(category, input.files[0]);
            hasImage = true;
            console.log(`✓ ${category} 이미지 추가됨`);
        }
    });
    
    console.log('hasImage:', hasImage);
    
    if (!hasImage) {
        alert('최소 1개 이상의 옷 사진을 업로드해주세요!');
        document.getElementById('loading').classList.add('hidden');
        return;
    }
    
    try {
        // API 호출
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('서버 오류가 발생했습니다.');
        }
        
        const data = await response.json();
        
        // 디버깅: 서버 응답 확인
        console.log('서버 응답 데이터:', data);
        console.log('업로드된 아이템:', data.uploaded_items);
        
        // 결과 표시
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert('오류가 발생했습니다: ' + error.message);
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
});

// 결과 표시
function displayResults(data) {
    // 데이터 저장 (재추천용)
    window.lastAnalysisData = data;
    
    const resultsDiv = document.getElementById('results');
    const contentDiv = document.getElementById('recommendationContent');
    
    if (!data.success) {
        contentDiv.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                오류가 발생했습니다. 다시 시도해주세요.
            </div>
        `;
        resultsDiv.classList.remove('hidden');
        return;
    }
    
    let html = '';
    
    // 사용자 정보
    html += `
        <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 mb-6">
            <h3 class="font-bold text-lg mb-3 text-gray-800">👤 입력하신 정보</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div><span class="font-semibold">성별:</span> ${data.user_info.gender}</div>
                <div><span class="font-semibold">연령대:</span> ${data.user_info.age_group}</div>
                <div><span class="font-semibold">체형:</span> ${data.user_info.body_type}</div>
                <div><span class="font-semibold">TPO:</span> ${data.user_info.tpo}</div>
            </div>
        </div>
    `;
    
    // 업로드된 아이템 분석 결과
    html += '<h3 class="font-bold text-lg mb-4 text-gray-800">📸 업로드하신 옷 분석 결과</h3>';
    html += '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">';
    
    const categoryNames = {
        'outer': '🧥 아우터',
        'inner1': '👕 이너1 (겉 상의)',
        'inner2': '👔 이너2 (속 상의)',
        'bottom': '👖 하의',
        'shoes': '👟 신발'
    };
    
    for (const [category, name] of Object.entries(categoryNames)) {
        if (data.uploaded_items[category]) {
            const item = data.uploaded_items[category];
            
            // 디버깅: 아이템 데이터 확인
            console.log(`${category} 아이템:`, item);
            console.log(`${category} 색상:`, item.colors);
            
            const colors = item.colors && Array.isArray(item.colors) && item.colors.length > 0 ? item.colors.map(c => {
                const rgb = c.rgb && Array.isArray(c.rgb) ? c.rgb.join(',') : '128,128,128';
                return `<span class="color-badge" style="background-color: rgba(${rgb}, 0.2); color: rgb(${rgb});">
                    ${c.name || '알 수 없음'} (${c.percentage || 0}%)
                </span>`;
            }).join('') : '<span class="text-gray-500">색상 정보 없음</span>';
            
            html += `
                <div class="result-card bg-white border-2 border-gray-200 rounded-xl p-4">
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="font-semibold text-gray-800">${name}</h4>
                        <button onclick="editItem('${category}')" class="text-blue-600 hover:text-blue-800 text-sm">
                            ✏️ 수정
                        </button>
                    </div>
                    <div class="space-y-2 text-sm" id="${category}-display">
                        <div><span class="font-medium">종류:</span> <span id="${category}-type-display">${item.type.label}</span> <span class="text-gray-500">(${item.type.confidence}%)</span></div>
                        <div><span class="font-medium">색상:</span> <div class="mt-1">${colors}</div></div>
                        <div><span class="font-medium">무늬:</span> <span id="${category}-pattern-display">${item.pattern.label}</span> <span class="text-gray-500">(${item.pattern.confidence}%)</span></div>
                    </div>
                    <div class="space-y-3 mt-3 hidden" id="${category}-edit">
                        <div>
                            <label class="font-medium text-sm">종류:</label>
                            <select id="${category}-type-select" class="w-full mt-1 p-2 border rounded">
                                ${getTypeOptions(category, item.type.label)}
                            </select>
                        </div>
                        <div>
                            <label class="font-medium text-sm">무늬:</label>
                            <select id="${category}-pattern-select" class="w-full mt-1 p-2 border rounded">
                                ${getPatternOptions(item.pattern.label)}
                            </select>
                        </div>
                        <div class="flex gap-2">
                            <button onclick="saveEdit('${category}')" class="flex-1 bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700">
                                ✓ 저장
                            </button>
                            <button onclick="cancelEdit('${category}')" class="flex-1 bg-gray-300 text-gray-700 px-3 py-2 rounded hover:bg-gray-400">
                                취소
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    html += '</div>';
    
    // AI 추천
    if (data.recommendation) {
        html += '<h3 class="font-bold text-lg mb-4 text-gray-800">✨ AI 코디 추천</h3>';
        
        // 스타일 방향성
        if (data.recommendation.style_direction) {
            html += `
                <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 mb-4">
                    <h4 class="font-semibold text-gray-800 mb-2">💡 전체 스타일 방향</h4>
                    <p class="text-gray-700">${data.recommendation.style_direction}</p>
                </div>
            `;
        }
        
        // 아이템별 추천
        if (data.recommendation.recommendations) {
            html += '<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">';
            
            for (const [category, name] of Object.entries(categoryNames)) {
                const rec = data.recommendation.recommendations[category];
                if (rec && !rec.uploaded) {
                    // 신발은 패턴 없이 표시
                    if (category === 'shoes') {
                        html += `
                            <div class="result-card bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-4">
                                <h4 class="font-semibold text-gray-800 mb-3">${name}</h4>
                                <div class="space-y-2 text-sm">
                                    <div><span class="font-medium">추천 아이템:</span> ${rec.item}</div>
                                    <div><span class="font-medium">추천 색상:</span> ${rec.color}</div>
                                    <div class="mt-3 pt-3 border-t border-green-200">
                                        <span class="font-medium">추천 이유:</span>
                                        <p class="text-gray-700 mt-1">${rec.reason}</p>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else {
                        html += `
                            <div class="result-card bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-4">
                                <h4 class="font-semibold text-gray-800 mb-3">${name}</h4>
                                <div class="space-y-2 text-sm">
                                    <div><span class="font-medium">추천 아이템:</span> ${rec.item}</div>
                                    <div><span class="font-medium">추천 색상:</span> ${rec.color}</div>
                                    <div><span class="font-medium">추천 무늬:</span> ${rec.pattern}</div>
                                    <div class="mt-3 pt-3 border-t border-blue-200">
                                        <span class="font-medium">추천 이유:</span>
                                        <p class="text-gray-700 mt-1">${rec.reason}</p>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                }
            }
            
            html += '</div>';
        }
        
        // 스타일링 팁
        if (data.recommendation.styling_tips && data.recommendation.styling_tips.length > 0) {
            html += `
                <div class="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-300 rounded-xl p-6 shadow-lg">
                    <h4 class="font-bold text-lg text-gray-800 mb-4 flex items-center">
                        <span class="text-2xl mr-2">💡</span>
                        스타일링 팁
                    </h4>
                    <ul class="space-y-3">
                        ${data.recommendation.styling_tips.map(tip => {
                            // **텍스트** 형식을 <strong>텍스트</strong>로 변환
                            const formattedTip = tip.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
                            return `
                            <li class="flex items-start bg-white rounded-lg p-3 shadow-sm">
                                <span class="text-yellow-500 text-xl mr-3 mt-0.5">✓</span>
                                <span class="text-gray-700 flex-1">${formattedTip}</span>
                            </li>
                        `}).join('')}
                    </ul>
                </div>
            `;
        }
    }
    
    contentDiv.innerHTML = html;
    
    // 재추천 버튼 컨테이너 추가 (기존 버튼이 있으면 제거)
    const oldBtnContainer = document.getElementById('re-recommend-btn');
    if (oldBtnContainer) {
        oldBtnContainer.remove();
    }
    
    resultsDiv.classList.remove('hidden');
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 아이템 종류 옵션 생성
function getTypeOptions(category, currentType) {
    const types = {
        'outer': ['패딩', '코트', '자켓', '점퍼', '가디건', '후드집업', '플리스', '무스탕', '기타'],
        'inner1': ['맨투맨', '후드티', '니트', '셔츠', '기타'],
        'inner2': ['반팔티', '긴팔티', '니트', '셔츠', '기타'],
        'bottom': ['청바지', '면바지', '슬랙스', '조거팬츠', '트레이닝팬츠', '반바지', '치마', '레깅스', '미디스커트']
    };
    
    return types[category].map(type => 
        `<option value="${type}" ${type === currentType ? 'selected' : ''}>${type}</option>`
    ).join('');
}

// 무늬 옵션 생성
function getPatternOptions(currentPattern) {
    const patterns = ['무지', '스트라이프', '체크', '도트', '그래픽', '기타'];
    return patterns.map(pattern =>
        `<option value="${pattern}" ${pattern === currentPattern ? 'selected' : ''}>${pattern}</option>`
    ).join('');
}

// 수정 모드 활성화
function editItem(category) {
    document.getElementById(`${category}-display`).classList.add('hidden');
    document.getElementById(`${category}-edit`).classList.remove('hidden');
}

// 수정 취소
function cancelEdit(category) {
    document.getElementById(`${category}-display`).classList.remove('hidden');
    document.getElementById(`${category}-edit`).classList.add('hidden');
}

// 수정 저장 및 재추천
async function saveEdit(category) {
    const newType = document.getElementById(`${category}-type-select`).value;
    const newPattern = document.getElementById(`${category}-pattern-select`).value;
    
    // 화면 업데이트
    document.getElementById(`${category}-type-display`).textContent = newType;
    document.getElementById(`${category}-pattern-display`).textContent = newPattern;
    
    // 편집 모드 종료
    cancelEdit(category);
    
    // 저장 확인 메시지
    const itemName = {'outer': '아우터', 'inner1': '이너1', 'inner2': '이너2', 'bottom': '하의'}[category];
    console.log(`✅ ${itemName} 수정 완료: ${newType} / ${newPattern}`);
    
    // 저장된 데이터에서 해당 아이템 업데이트
    if (window.lastAnalysisData && window.lastAnalysisData.uploaded_items[category]) {
        window.lastAnalysisData.uploaded_items[category].type.label = newType;
        window.lastAnalysisData.uploaded_items[category].pattern.label = newPattern;
    }
    
    // 재추천 버튼 표시
    showReRecommendButton();
}

// 재추천 버튼 표시
function showReRecommendButton() {
    // 기존 버튼 제거
    const oldBtn = document.getElementById('re-recommend-btn');
    if (oldBtn) {
        return; // 이미 버튼이 있으면 그대로 유지
    }
    
    // 화면 하단에 고정되는 버튼 생성
    const reRecBtn = document.createElement('div');
    reRecBtn.id = 're-recommend-btn';
    reRecBtn.className = 'fixed bottom-0 left-0 right-0 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 px-6 shadow-2xl z-40 animate-slide-up';
    reRecBtn.innerHTML = `
        <div class="container mx-auto flex items-center justify-between max-w-6xl">
            <div class="flex items-center space-x-3">
                <span class="text-2xl animate-bounce">✏️</span>
                <span class="font-semibold">수정사항이 저장되었습니다!</span>
            </div>
            <button onclick="reRecommend()" class="bg-white text-purple-600 px-6 py-2 rounded-lg font-bold hover:bg-gray-100 transition-all hover:scale-105 shadow-lg">
                🔄 수정된 정보로 다시 추천받기
            </button>
        </div>
    `;
    document.body.appendChild(reRecBtn);
}

// 재추천 요청
async function reRecommend() {
    if (!window.lastAnalysisData) {
        alert('데이터가 없습니다. 다시 업로드해주세요.');
        return;
    }
    
    // 로딩 표시
    const loadingDiv = document.getElementById('loading');
    loadingDiv.classList.remove('hidden');
    
    // 로딩 영역으로 부드럽게 스크롤
    loadingDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    try {
        // Gemini API에 수정된 데이터로 재요청
        const response = await fetch('/api/re-recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_info: window.lastAnalysisData.user_info,
                uploaded_items: window.lastAnalysisData.uploaded_items
            })
        });
        
        if (!response.ok) {
            throw new Error('재추천 요청 실패');
        }
        
        const data = await response.json();
        
        // 기존 데이터 유지하고 recommendation만 업데이트
        window.lastAnalysisData.recommendation = data.recommendation;
        
        // 재추천 버튼 제거
        const reRecBtn = document.getElementById('re-recommend-btn');
        if (reRecBtn) {
            reRecBtn.remove();
        }
        
        // 결과 다시 표시
        displayResults(window.lastAnalysisData);
        
        // 성공 메시지
        alert('✅ 새로운 코디 추천을 받았습니다!');
        
    } catch (error) {
        console.error('Error:', error);
        alert('재추천 중 오류가 발생했습니다: ' + error.message);
    } finally {
        loadingDiv.classList.add('hidden');
    }
}

// 이미지로 다운로드
async function downloadAsImage() {
    const content = document.getElementById('downloadableContent');
    
    try {
        // 로딩 표시
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'text-center py-4 text-blue-600';
        loadingMsg.textContent = '이미지 생성 중...';
        content.appendChild(loadingMsg);
        
        // 폰트 로딩 대기
        await document.fonts.ready;
        
        // html2canvas로 캡처 (고해상도 설정)
        const canvas = await html2canvas(content, {
            scale: 3,
            backgroundColor: '#ffffff',
            logging: false,
            useCORS: true,
            allowTaint: false,
            imageTimeout: 15000,
            letterRendering: true,
            removeContainer: false,
            scrollY: -window.scrollY,
            scrollX: -window.scrollX,
            windowWidth: document.documentElement.scrollWidth,
            windowHeight: document.documentElement.scrollHeight
        });
        
        // 로딩 메시지 제거
        loadingMsg.remove();
        
        // 고품질 이미지로 변환 및 다운로드
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            const date = new Date().toISOString().slice(0, 10);
            link.download = `Winter_Outfit_Recommendation_${date}.png`;
            link.href = url;
            link.click();
            URL.revokeObjectURL(url);
        }, 'image/png', 1.0);
        
    } catch (error) {
        console.error('이미지 생성 오류:', error);
        alert('이미지 생성 중 오류가 발생했습니다.');
    }
}

// PDF로 다운로드
async function downloadAsPDF() {
    const content = document.getElementById('downloadableContent');
    
    try {
        // 로딩 표시
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'text-center py-4 text-red-600';
        loadingMsg.textContent = 'PDF 생성 중...';
        content.appendChild(loadingMsg);
        
        // 폰트 로딩 대기
        await document.fonts.ready;
        
        // html2canvas로 캡처 (고해상도)
        const canvas = await html2canvas(content, {
            scale: 3,
            backgroundColor: '#ffffff',
            logging: false,
            useCORS: true,
            allowTaint: false,
            imageTimeout: 15000,
            letterRendering: true,
            removeContainer: false,
            scrollY: -window.scrollY,
            scrollX: -window.scrollX
        });
        
        // 로딩 메시지 제거
        loadingMsg.remove();
        
        // jsPDF로 PDF 생성
        const { jsPDF } = window.jspdf;
        const imgData = canvas.toDataURL('image/png', 1.0);
        
        // A4 사이즈에 맞게 조정
        const pdf = new jsPDF('p', 'mm', 'a4');
        const imgWidth = 210; // A4 width in mm
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        
        let heightLeft = imgHeight;
        let position = 0;
        
        // 페이지 추가하며 이미지 삽입
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight, undefined, 'FAST');
        heightLeft -= 297; // A4 height
        
        while (heightLeft > 0) {
            position = heightLeft - imgHeight;
            pdf.addPage();
            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight, undefined, 'FAST');
            heightLeft -= 297;
        }
        
        // PDF 다운로드
        const date = new Date().toISOString().slice(0, 10);
        pdf.save(`Winter_Outfit_Recommendation_${date}.pdf`);
        
    } catch (error) {
        console.error('PDF 생성 오류:', error);
        alert('PDF 생성 중 오류가 발생했습니다.');
    }
}

