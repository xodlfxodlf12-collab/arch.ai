// Real Estate & Cadastral Portfolio Data & Logic
const projectsData = [
    {
        id: 1,
        title: "QGIS 지적재조사 및 경계 불부합 정밀 보정",
        category: "cadastral",
        year: "2025.Fall (4학년 2학기)",
        location: "서울시 성동구 성수동 준공업지역 일대",
        area: "대상 필지 48필지 / 총 면적 18,450 ㎡",
        structure: "QGIS 3.34 + UAV 드론 정사영상(GSD 2cm) + GNSS RTK 측량",
        concept: "구도심 지적공부와 실제 현황 경계가 일치하지 않는 지적불부합 문제를 해소하기 위해, UAV 드론 정사영상과 GNSS RTK 측량 좌표를 QGIS(EPSG:5186) 환경에 중첩하여 필지 경계 오차를 2cm 이내로 정밀 보정하고 속성 DB를 구축한 프로젝트입니다.",
        images: [
            "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1524661135-423995f22d0b?auto=format&fit=crop&w=1200&q=80"
        ]
    },
    {
        id: 2,
        title: "역세권 청년주택 개발 타당성 & DCF 분석",
        category: "valuation",
        year: "2025.Spring (4학년 1학기)",
        location: "서울시 동작구 노량진역 반경 350m 역세권",
        area: "대지면적 2,840 ㎡ / 용적률 480% (공공기여 포함)",
        structure: "DCF(현금흐름할인법) + 헤도닉 가격모형 + Python 민감도 분석",
        concept: "용도지역 종상향(제2종일반주거 → 준주거지역)에 따른 공공기여 비율과 임대수익률(Cap Rate), 공사비 상승 민감도를 다변량 분석하여, 사업 시행자와 지자체 모두가 윈-윈(Win-Win)할 수 있는 최적 용적률 및 분양·임대 믹스 전략을 도출했습니다.",
        images: [
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80"
        ]
    },
    {
        id: 3,
        title: "QGIS 기반 1인 가구 생활SOC 입지 최적화",
        category: "gis",
        year: "2024.Fall (3학년 2학기)",
        location: "서울시 관악구 신림·봉천동 일대",
        area: "격자 단위(100m × 100m) 1,240개 셀 분석",
        structure: "QGIS + Python(GeoPandas) + 도보 네트워크 Isochrone 분석",
        concept: "통신사 유동인구, 카드 매출, 건축물대장 노후도 데이터를 100m 격자로 결합하여 1인 가구 밀집 지역의 생활SOC(공유오피스·무인택배·치안거점) 사각지대를 도출하고, 국공유지 유휴 필지를 활용한 최적 입지 3곳을 제안했습니다.",
        images: [
            "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=1200&q=80"
        ]
    }
];

// --- 1. Project Modal Logic ---
function openProjectModal(id) {
    const project = projectsData.find(p => p.id === id);
    if (!project) return;

    const modalBody = document.getElementById('modal-content-body');
    modalBody.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
            <span style="color: var(--accent); font-size: 0.85rem; font-weight: 600;">${project.category.toUpperCase()} | ${project.year}</span>
            <h2 style="font-family: var(--font-heading); font-size: 2rem; margin: 0.4rem 0 1rem 0;">${project.title}</h2>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; background: rgba(0,0,0,0.3); padding: 1.2rem; border-radius: var(--radius-sm); border: 1px solid var(--border);">
            <div><strong>대상 지역:</strong> <span style="color: var(--text-secondary);">${project.location}</span></div>
            <div><strong>규모/면적:</strong> <span style="color: var(--text-secondary);">${project.area}</span></div>
            <div style="grid-column: span 2;"><strong>분석 기법 및 툴:</strong> <span style="color: var(--text-secondary);">${project.structure}</span></div>
        </div>

        <div style="margin-bottom: 2rem;">
            <h4 style="margin-bottom: 0.5rem; color: var(--accent);">연구 및 분석 개요 (Executive Summary)</h4>
            <p style="color: var(--text-secondary); line-height: 1.8;">${project.concept}</p>
        </div>

        <div style="display: flex; flex-direction: column; gap: 1.2rem;">
            <h4 style="margin-bottom: 0.2rem; color: var(--accent);">주요 공간분석 및 시각화 자료</h4>
            ${project.images.map(img => `<img src="${img}" style="width: 100%; border-radius: 8px; border: 1px solid var(--border);" loading="lazy">`).join('')}
        </div>
        
        <div style="margin-top: 2rem; text-align: right;">
            <a href="#analysis-briefing" class="btn-secondary" onclick="closeProjectModal()" style="display: inline-flex; text-decoration: none;">
                <span class="sparkle">✦</span> 관점별 핵심 분석 해설 보기 ↗
            </a>
        </div>
    `;

    document.getElementById('project-modal').classList.add('show');
}

function closeProjectModal(e) {
    if (!e || e.target.id === 'project-modal' || e.target.classList.contains('btn-close') || e.target.tagName === 'A') {
        document.getElementById('project-modal').classList.remove('show');
    }
}

// --- 2. Filter Button Logic ---
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const filter = btn.dataset.filter;
        document.querySelectorAll('.project-card').forEach(card => {
            if (filter === 'all' || card.dataset.category === filter) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
});

// --- 3. QGIS Interactive Spatial Analysis & Cadastral Viewer ---
const parcelAttributes = {
    p1: {
        title: "성수동1가 656-12 (준주거지역)",
        desc: "지목: 대 | 면적: 1,120㎡ | 개별공시지가: 9,850,000원/㎡ | 역세권 350m 이내 국공유지 유휴 필지로 1인 가구 생활SOC 복합개발 1순위 후보지입니다."
    },
    p2: {
        title: "성수동1가 656-15 (준주거지역)",
        desc: "지목: 대 | 면적: 1,480㎡ | 개별공시지가: 10,200,000원/㎡ | 인접 도로 폭원 12m 확보 및 100m 격자 유동인구 상위 10% 구간에 속하는 민간 개발 가능 필지입니다."
    },
    p3: {
        title: "성수동1가 642-08 (제2종일반주거)",
        desc: "지목: 대 | 면적: 840㎡ | 개별공시지가: 7,420,000원/㎡ | 국공유지 유휴 부지로 도보 10분 서비스 권역 내 무인택배·치안거점 2순위 후보지입니다."
    },
    p4: {
        title: "성수동1가 642-11 (준주거지역)",
        desc: "지목: 대 | 면적: 1,050㎡ | 개별공시지가: 11,100,000원/㎡ | 역세권 핵심 보행축 인접 필지로 GNSS RTK 측량 결과 경계 불부합 오차 1.4cm로 정밀 보정되었습니다."
    },
    p5: {
        title: "성수동1가 642-19 (근린상업지역)",
        desc: "지목: 대 | 면적: 990㎡ | 개별공시지가: 12,600,000원/㎡ | 카드 매출 빅데이터 상권 활성도 최상위 구역으로 상업시설 임대수익률(Cap Rate)이 가장 높습니다."
    },
    p6: {
        title: "성수동1가 658-03 (제3종일반주거)",
        desc: "지목: 잡종지 | 면적: 1,620㎡ | 개별공시지가: 6,950,000원/㎡ | 공유오피스 및 청년 주거 복합화 시 공공기여를 통한 용적률 인센티브 확보가 유리한 국공유지 3순위 후보지입니다."
    }
};

const qgisLayerState = {
    parcels: true,
    heatmap: true,
    buffer: true,
    candidates: true
};

const layerLabels = {
    parcels: "📐 연속지적도 필지 경계",
    heatmap: "🔥 100m 격자 밀도 히트맵",
    buffer: "⭕ 역세권 도보권 버퍼",
    candidates: "📍 국공유지 후보지 마커"
};

function initQgisViewer() {
    selectParcel('p1');
    // Check if user placed maps/qgis_map.png in maps/ directory
    checkStaticQgisMap('maps/qgis_map.png');
}

function selectParcel(parcelId) {
    document.querySelectorAll('.qgis-parcel').forEach(el => {
        el.classList.toggle('active', el.dataset.parcel === parcelId);
    });

    const info = parcelAttributes[parcelId];
    if (info) {
        document.getElementById('anno-title').innerText = info.title;
        document.getElementById('anno-desc').innerText = info.desc;
    }
}

function toggleQgisLayer(layerKey, btnEl) {
    // Ensure interactive SVG map is visible if user was viewing uploaded image
    showInteractiveSvgMap();

    qgisLayerState[layerKey] = !qgisLayerState[layerKey];
    const isVisible = qgisLayerState[layerKey];

    const layerGroup = document.getElementById(`layer-${layerKey}`);
    if (layerGroup) {
        layerGroup.style.display = isVisible ? 'inline' : 'none';
    }

    if (btnEl) {
        btnEl.classList.toggle('active', isVisible);
        btnEl.innerText = `${layerLabels[layerKey]} ${isVisible ? 'ON' : 'OFF'}`;
    }
}

function showInteractiveSvgMap() {
    const svgMap = document.getElementById('qgis-svg-map');
    const uploadedWrap = document.getElementById('qgis-uploaded-wrap');
    const hudBottom = document.getElementById('qgis-hud-bottom');
    if (svgMap) svgMap.style.display = 'block';
    if (uploadedWrap) uploadedWrap.style.display = 'none';
    if (hudBottom) hudBottom.style.display = 'flex';
}

function resetQgisView() {
    showInteractiveSvgMap();

    Object.keys(qgisLayerState).forEach(key => {
        qgisLayerState[key] = true;
        const layerGroup = document.getElementById(`layer-${key}`);
        if (layerGroup) layerGroup.style.display = 'inline';

        const btn = document.getElementById(`btn-layer-${key}`);
        if (btn) {
            btn.classList.add('active');
            btn.innerText = `${layerLabels[key]} ON`;
        }
    });

    selectParcel('p1');
}

function checkStaticQgisMap(imageUrl) {
    const testImg = new Image();
    testImg.onload = function() {
        applyUploadedQgisImage(imageUrl, '사용자 로컬 QGIS 지도 (qgis_map.png)');
    };
    testImg.onerror = function() {
        console.log('No local maps/qgis_map.png found. Using interactive QGIS vector map.');
    };
    testImg.src = imageUrl;
}

function handleQgisImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        applyUploadedQgisImage(e.target.result, file.name);
    };
    reader.readAsDataURL(file);
}

function applyUploadedQgisImage(src, fileName) {
    const svgMap = document.getElementById('qgis-svg-map');
    const uploadedWrap = document.getElementById('qgis-uploaded-wrap');
    const uploadedImg = document.getElementById('qgis-uploaded-img');
    const hudBottom = document.getElementById('qgis-hud-bottom');

    if (svgMap) svgMap.style.display = 'none';
    if (hudBottom) hudBottom.style.display = 'none';
    if (uploadedImg) uploadedImg.src = src;
    if (uploadedWrap) uploadedWrap.style.display = 'flex';

    document.getElementById('anno-title').innerText = `QGIS 결과물 로드 완료: ${fileName}`;
    document.getElementById('anno-desc').innerText = `학생이 QGIS 인쇄 조판에서 내보낸 공간분석 주제도가 뷰어에 적용되었습니다. [기본 QGIS 맵으로 초기화] 버튼을 누르면 인터랙티브 필지 레이어로 돌아갑니다.`;
}

// --- 4. Audience-Tailored Evaluator Briefing Switcher ---
const briefingData = {
    cadastral: {
        tag: "CADASTRAL SURVEY & PRECISION",
        title: "GNSS RTK·드론 측량 기반 경계 정밀 보정 및 QGIS 지적 DB 구축",
        bullets: [
            "지적불부합 지역에 대해 UAV 드론 정사영상(GSD 2cm급)과 네트워크 RTK 측량을 병행하여 필지 경계 좌표를 정밀 등록했습니다.",
            "QGIS(EPSG:5186) 환경에서 연속지적도와 현황 측량 레이어를 중첩해 경계 침범 및 면적 증감 필지를 자동 탐지했습니다.",
            "토지대장·건축물대장 속성 테이블을 필지 고유번호(PNU) 기준으로 결합해 정밀 공간 데이터베이스를 구축했습니다."
        ]
    },
    valuation: {
        tag: "REAL ESTATE VALUATION & FEASIBILITY",
        title: "헤도닉 가격모형과 DCF(현금흐름할인법) 기반의 정량적 사업성 검증",
        bullets: [
            "국토교통부 실거래가 5개년 데이터를 활용한 헤도닉 회귀모형(R²=0.84)으로 역세권 거리·노후도·향별 가격 결정 요인을 도출했습니다.",
            "용도지역 종상향(2종→준주거)에 따른 공공기여 비율(15%~25%)과 공사비 변동에 따른 IRR(내부수익률) 민감도 매트릭스를 구축했습니다.",
            "임대수익률(Cap Rate) 4.6% 기준, 공공임대와 민간분양의 최적 면적 배분 비율(6:4)을 산출하여 사업 타당성을 입증했습니다."
        ]
    },
    gis: {
        tag: "QGIS LOCATION & TRADE AREA ANALYSIS",
        title: "100m 격자 빅데이터와 도보 네트워크(Isochrone) 기반 입지 최적화",
        bullets: [
            "통신사 생활인구, 카드 소비 매출, 건축물 노후도 데이터를 100m×100m 격자 셀(1,240개)에 공간 조인(Spatial Join)하여 수요 밀도를 시각화했습니다.",
            "직선 반경이 아닌 실제 도로망 경사와 횡단보도를 반영한 도보 10분 서비스 권역(Isochrone) 분석으로 생활SOC 사각지대를 정밀 탐지했습니다.",
            "국공유지 유휴 필지 레이어를 중첩 필터링하여 토지 매입 비용을 최소화할 수 있는 최적 후보지 3곳을 최종 선정했습니다."
        ]
    },
    proptech: {
        tag: "PROPTECH & SPATIAL DATA TOOLCHAIN",
        title: "QGIS·Python(GeoPandas)·Web을 결합한 프롭테크 분석 파이프라인",
        bullets: [
            "QGIS 및 Python(GeoPandas, Shapely, Scikit-learn)을 활용해 대용량 연속지적도와 실거래가 데이터를 자동 전처리하고 공간통계를 수행합니다.",
            "Excel/Python 기반 자동화 DCF 재무모델을 통해 금리·공실률 시나리오별 NPV(순현재가치)를 실시간 시뮬레이션합니다.",
            "QGIS 인쇄 조판 주제도(Thematic Map) 및 인터랙티브 레이어 뷰어를 웹 포트폴리오에 탑재해 누구나 직관적으로 검토할 수 있습니다."
        ]
    }
};

function switchBriefing(type) {
    document.querySelectorAll('.r-tab').forEach(btn => btn.classList.remove('active'));
    event?.currentTarget?.classList.add('active');

    const data = briefingData[type];
    if (!data) return;

    const display = document.getElementById('briefing-display');
    display.innerHTML = `
        <div class="briefing-box">
            <span class="briefing-tag">${data.tag}</span>
            <h4 class="briefing-heading">${data.title}</h4>
            <ul class="briefing-list">
                ${data.bullets.map(b => `<li><span class="bullet-dot">▸</span> <span>${b}</span></li>`).join('')}
            </ul>
        </div>
    `;
}

// ==========================================================================
// 🤖 5. Floating AI Docent Chatbot Logic (하이브리드: 룰베이스 B + Gemini A)
// ==========================================================================

let userGeminiApiKey = localStorage.getItem('geo_gemini_key') || '';

// 5-1. 시나리오 룰베이스 답변 데이터베이스 (옵션 B: 키 없이 100% 동작)
const scenarioResponses = [
    {
        keywords: ["지적재조사", "불부합", "경계", "필지", "드론", "rtk", "성수", "pnu"],
        answer: "QGIS 지적재조사 프로젝트는 구도심의 지적불부합 문제를 해결하기 위해 UAV 드론 정사영상(GSD 2cm급)과 GNSS RTK 측량 좌표를 QGIS(EPSG:5186)에 중첩한 연구입니다. 연속지적도와 현황 경계를 비교해 오차를 2cm 이내로 정밀 보정하고 PNU 기준 속성 DB를 구축했습니다."
    },
    {
        keywords: ["역세권", "사업성", "타당성", "dcf", "노량진", "청년주택", "수익률", "용적률"],
        answer: "노량진 역세권 청년주택 타당성 분석에서는 용도지역 종상향(2종→준주거, 용적률 480%) 시 공공기여 비율과 공사비 변동에 따른 수익률(IRR, Cap Rate 4.6%) 민감도를 시뮬레이션했습니다. 공공임대와 민간분양을 6:4로 믹스할 때 시행자와 지자체 모두 최적의 효용을 얻는 것으로 분석되었습니다."
    },
    {
        keywords: ["gis", "qgis", "입지", "1인", "가구", "빅데이터", "격자", "신림", "상권"],
        answer: "QGIS 1인 가구 생활SOC 입지분석은 통신사 유동인구, 카드 매출, 건축물 노후도를 100m×100m 격자 1,240개 셀에 결합해 분석했습니다. 도보 10분 네트워크 권역(Isochrone) 분석으로 사각지대를 찾고, 국공유지 유휴 필지를 매칭해 최적 입지 3곳을 도출했습니다."
    },
    {
        keywords: ["연락처", "이메일", "링크드인", "sns", "커피챗", "문의", "메일", "전화"],
        answer: "박서준 학생의 포트폴리오에 관심을 가져주셔서 감사합니다! 📧 이메일: geo.seojun@example.ac.kr | 💼 LinkedIn: @geo_seojun 으로 연락 주시면 상세한 분석 리포트 공유나 커피챗이 가능합니다."
    }
];

// 5-2. 챗봇 열기/닫기 토글
function toggleChatbot() {
    const windowEl = document.getElementById('chatbot-window');
    windowEl.classList.toggle('open');
    if (windowEl.classList.contains('open')) {
        document.getElementById('chatbot-input').focus();
    }
}

// 5-3. 추천 질문 칩 클릭 시 질문 자동 전송
function askChip(questionText) {
    appendChatMessage('user', questionText);
    processChatQuery(questionText);
}

// 5-4. 입력창 Submit 이벤트
function handleChatSubmit(e) {
    e.preventDefault();
    const inputEl = document.getElementById('chatbot-input');
    const text = inputEl.value.trim();
    if (!text) return;

    inputEl.value = '';
    appendChatMessage('user', text);
    processChatQuery(text);
}

// 5-5. 메시지 화면 렌더링
function appendChatMessage(role, text) {
    const messagesWrap = document.getElementById('chatbot-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `cb-msg ${role}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'cb-msg-bubble';
    bubble.innerHTML = text.replace(/\n/g, '<br>');

    msgDiv.appendChild(bubble);
    messagesWrap.appendChild(msgDiv);
    messagesWrap.scrollTop = messagesWrap.scrollHeight;
    return bubble;
}

// 5-6. 답변 처리 로직 (옵션 A Gemini API 또는 옵션 B 룰베이스)
async function processChatQuery(userQuery) {
    if (userGeminiApiKey) {
        const loadingBubble = appendChatMessage('bot', 'AI 도슨트가 QGIS·시장 데이터를 분석 중입니다... 💭');
        try {
            const aiAnswer = await fetchGeminiAnswer(userQuery);
            loadingBubble.innerHTML = aiAnswer.replace(/\n/g, '<br>');
        } catch (err) {
            console.error('Gemini API Error:', err);
            loadingBubble.innerHTML = `⚠️ Gemini API 응답 중 오류가 발생했습니다.<br><small style="color:var(--text-muted);">${err.message}</small><br>상단 ⚙️ 설정에서 API 키를 재확인하거나 룰베이스 모드를 이용해주세요.`;
        }
        return;
    }

    const lowerQuery = userQuery.toLowerCase();
    const matched = scenarioResponses.find(item => 
        item.keywords.some(k => lowerQuery.includes(k.toLowerCase()))
    );

    const botResponse = matched 
        ? matched.answer 
        : `좋은 질문 감사합니다! 😊<br><br>현재 <strong>[룰베이스 모드]</strong>로 운영 중입니다. 하단 추천 질문 칩(QGIS 지적재조사, 역세권 사업성, QGIS 입지분석, 연락처)을 클릭하시면 정확한 해설을 확인하실 수 있습니다.<br><br><small style="color:var(--text-muted);">※ 상단 ⚙️ 아이콘에서 Google Gemini API 키를 등록하시면 자유로운 실시간 AI 대화가 활성화됩니다.</small>`;

    const bubble = appendChatMessage('bot', '...');
    setTimeout(() => {
        bubble.innerHTML = botResponse;
        const messagesWrap = document.getElementById('chatbot-messages');
        messagesWrap.scrollTop = messagesWrap.scrollHeight;
    }, 350);
}

// 5-7. Google Gemini REST API 호출기 (Auto-Context Injection 내장)
function buildCadastralContext() {
    const studentName = document.querySelector('.f-name')?.innerText?.trim() || '부동산지적학도';
    const heroTitle = document.querySelector('.hero-title')?.innerText?.replace(/\n/g, ' ') || '';
    const heroDesc = document.querySelector('.hero-desc')?.innerText?.trim() || '';

    const projectsSummary = projectsData.map((p, idx) => `
[프로젝트 ${idx + 1}: ${p.title}]
- 분야/학기: ${p.category} (${p.year})
- 대상 지역: ${p.location}
- 규모/면적: ${p.area}
- 분석 기법 및 툴: ${p.structure}
- 연구/분석 개요(Summary): ${p.concept}
`).join('\n');

    const parcelsSummary = Object.entries(parcelAttributes || {}).map(([key, val]) => `
• ${val.title}: ${val.desc}`).join('');

    return {
        studentName,
        text: `
[학생 프로필]
- 작성자: ${studentName}
- 전공 및 소개: ${heroTitle} / ${heroDesc}

[등록된 프로젝트 상세 데이터]
${projectsSummary}

[QGIS 필지별 공간분석 속성 데이터]
${parcelsSummary}
`
    };
}

async function resolveWorkingEndpoint(apiKey) {
    let cached = localStorage.getItem('geo_gemini_endpoint');
    if (cached) return cached;

    try {
        const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`);
        if (res.ok) {
            const data = await res.json();
            const genModels = (data.models || []).filter(m => 
                m.supportedGenerationMethods && m.supportedGenerationMethods.includes('generateContent')
            );
            const preferred = genModels.find(m => m.name.includes('3.5') && m.name.includes('lite'))
                           || genModels.find(m => m.name.includes('flash-lite'))
                           || genModels.find(m => m.name.includes('2.0-flash-lite'))
                           || genModels.find(m => m.name.includes('2.0-flash'))
                           || genModels.find(m => m.name.includes('flash'))
                           || genModels[0];
            if (preferred) {
                const endpoint = `https://generativelanguage.googleapis.com/v1beta/${preferred.name}:generateContent`;
                localStorage.setItem('geo_gemini_endpoint', endpoint);
                console.log('[Gemini] Optimal model detected:', preferred.name);
                return endpoint;
            }
        }
    } catch (e) {
        console.warn('[Gemini] ListModels query skipped:', e);
    }

    return "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent";
}

async function fetchGeminiAnswer(prompt) {
    const ctx = buildCadastralContext();
    const systemInstruction = `
당신은 부동산지적학과 학생 '${ctx.studentName}'의 포트폴리오를 대변하는 친절하고 전문적인 'AI 부동산·지적 도슨트'입니다.
다음은 학생이 웹사이트에 직접 등록한 공식 QGIS 공간분석 및 가치평가 프로젝트 데이터입니다:

${ctx.text}

[지침]:
1. 방문자의 질문에 대해 위 등록된 프로젝트 데이터 및 QGIS 필지 분석 정보를 최우선 근거로 활용하여 전문적이면서도 알기 쉽게 설명하세요.
2. 등록되지 않은 허위 사실을 지어내지 마시고, 데이터에 있는 실제 대상 지역, 분석 기법, 수치를 인용하세요.
3. 3~4문장 이내의 친절하고 명확한 한국어로 정중하게(해요체) 답변하세요.
`;

    const requestBody = {
        contents: [
            {
                role: "user",
                parts: [
                    { text: `${systemInstruction}\n\n[방문자 질문]: ${prompt}` }
                ]
            }
        ]
    };

    const candidates = [
        localStorage.getItem('geo_gemini_endpoint'),
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent",
        "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    ].filter(Boolean);

    const uniqueCandidates = [...new Set(candidates)];
    let lastError = null;

    for (const baseEndpoint of uniqueCandidates) {
        try {
            const url = `${baseEndpoint}?key=${userGeminiApiKey}`;
            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestBody)
            });

            if (res.ok) {
                const data = await res.json();
                if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
                    localStorage.setItem('geo_gemini_endpoint', baseEndpoint);
                    return data.candidates[0].content.parts[0].text;
                }
            } else {
                const errJson = await res.json().catch(() => ({}));
                lastError = new Error(errJson.error?.message || `HTTP ${res.status}`);
                if (res.status === 404 || errJson.error?.message?.includes('not found') || errJson.error?.message?.includes('not supported')) {
                    continue;
                } else {
                    throw lastError;
                }
            }
        } catch (err) {
            lastError = err;
            if (err.message?.includes('not found') || err.message?.includes('not supported') || err.message?.includes('404')) {
                continue;
            }
            throw err;
        }
    }

    throw lastError || new Error("지원되는 Gemini 모델을 찾을 수 없습니다.");
}

// 5-8. API 설정 오버레이 제어
function openChatConfig() {
    document.getElementById('cfg-gemini-key').value = userGeminiApiKey;
    document.getElementById('cb-config-overlay').classList.add('show');
}

function closeChatConfig() {
    document.getElementById('cb-config-overlay').classList.remove('show');
}

async function saveApiKey() {
    const key = document.getElementById('cfg-gemini-key').value.trim();
    if (!key) {
        alert('API Key를 입력해주세요. 키가 없으시면 [룰베이스 모드로 초기화]를 선택하세요.');
        return;
    }
    userGeminiApiKey = key;
    localStorage.setItem('geo_gemini_key', key);
    localStorage.removeItem('geo_gemini_endpoint');
    
    await resolveWorkingEndpoint(key);
    
    updateModeBadge();
    closeChatConfig();
    appendChatMessage('bot', '✨ <strong>Gemini AI 연동 완료!</strong><br>이제 자유롭게 무엇이든 질문해 보세요. 포트폴리오 도슨트가 실시간으로 분석하여 답해드립니다.');
}

function resetToRuleMode() {
    userGeminiApiKey = '';
    localStorage.removeItem('geo_gemini_key');
    localStorage.removeItem('geo_gemini_endpoint');
    document.getElementById('cfg-gemini-key').value = '';
    updateModeBadge();
    closeChatConfig();
    appendChatMessage('bot', '🔄 <strong>룰베이스 모드로 전환되었습니다.</strong><br>API 키 없이도 주요 추천 질문 칩에 대한 사전 검증된 분석 해설을 언제든 확인하실 수 있습니다.');
}

function updateModeBadge() {
    const badge = document.getElementById('cb-mode-badge');
    if (!badge) return;
    if (userGeminiApiKey) {
        badge.className = 'cb-status ai-mode';
        badge.innerText = '✨ Gemini AI 모드';
    } else {
        badge.className = 'cb-status rule-mode';
        badge.innerText = '🟢 룰베이스 모드';
    }
}

// Init everything once DOM is ready
window.addEventListener('DOMContentLoaded', () => {
    initQgisViewer();
    switchBriefing('cadastral');
    updateModeBadge();
});
