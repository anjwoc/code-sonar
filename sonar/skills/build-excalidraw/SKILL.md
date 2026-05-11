# Build Excalidraw Skill

Mermaid 또는 텍스트 설명으로부터 Excalidraw 다이어그램을 생성한다. 아래 Visual Style Guidelines를 반드시 따른다.

## 실행 워크플로우

### STEP 1: Mermaid 정제

기존 Mermaid 코드에서 스타일/색상/classDef를 제거하고 컴포넌트 관계만 남긴다.

```
기존 mermaid 코드에서 스타일 제거하고 각 컴포넌트의 관계만 고려해서 재작성해줘
```

정제 규칙:
- `classDef`, `style`, `class`, `%%{init}%%` 블록 제거
- 노드 라벨은 짧고 명확하게 유지
- edge label은 프로토콜/목적만 남김 (e.g. `HTTPS`, `Feign`, `JDBC/JPA`, `Kafka`)
- `flowchart LR`로 방향 고정

### STEP 2: Excalidraw 생성

정제된 Mermaid를 기반으로 Excalidraw JSON을 생성한다.

```
(개정된 mermaid 코드를 가지고) <output>.excalidraw를 아래 mermaid 참고해서 그려줘
```

**CLI 우선 사용:**
```bash
node scripts/render-excalidraw-from-mermaid.js --input "<index.md>" --output "<diagram.excalidraw>"
```

CLI가 불가한 경우 아래 Visual Style Guidelines에 따라 JSON을 직접 생성한다.

---

## Visual Style Guidelines

### 1. Arrow Styling & Color Palette

- **Default State:** Grayscale (`#868e96`, `#adb5bd`) — 일반 연결선
- **Highlight State:** 강조 필요한 화살표만 Pastel 사용
- **Arrow Pastel Palette:**
  ```
  ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF",
   "#D5AAFF", "#F8BBD0", "#B2EBF2", "#C8E6C9", "#FFE0B2"]
  ```

프로토콜별 기본 배정:
| 프로토콜 | Arrow Color | Label Fill |
|---|---|---|
| neutral / general | `#868e96` | `#f8f9fa` |
| feign / route | `#adb5bd` | `#f8f9fa` |
| HTTPS / HTTP | `#BAFFC9` | `#ebfbee` |
| WebClient | `#BAE1FF` | `#e7f5ff` |
| Kafka / Pub-Sub | `#B2EBF2` | `#e3fafc` |
| JDBC / JPA | `#BAE1FF` | `#e7f5ff` |
| Redis | `#FFB3BA` | `#fff5f5` |
| Spring Data / Mongo | `#D5AAFF` | `#f3f0ff` |
| Elasticsearch | `#FFDFBA` | `#fff9db` |

### 2. Box & Container Specifications

- **Edges:** `roundness: { type: 3 }` — 반드시 Rounded
- **Roughness:** `roughness: 1` (Medium)
- **같은 행의 박스:** 동일 height 유지 (`rowInFrame` 패턴)
- **Y-Axis Alignment:**
  - 최상위 Group Box 행: `y: 60` 기준 정렬
  - 내부 컴포넌트: `y: 130` 기준 정렬
- **Color Logic:**
  - Group container와 내부 박스는 같은 색조 공유
  - Group Box: 동일 색조의 pale 버전 (낮은 opacity)
- **Box Palette (Group & 내부 컴포넌트):**
  ```
  ["#F9F9F9", "#F0F4F8", "#E8F5E9", "#FFF3E0", "#F3E5F5",
   "#E1F5FE", "#FBE9E7", "#EFEBE9", "#F1F8E9", "#E0F2F1"]
  ```
- **Vertical Padding:** Group Box 상단과 첫 컴포넌트 사이 최소 **50px**

레이어 → 색상 매핑:
| 레이어 | Fill | Stroke |
|---|---|---|
| External / EXT | `#FFF3E0` | `#c9966b` |
| Frontend / App | `#F0F4F8` | `#74a8c9` |
| Gateway | `#F3E5F5` | `#b39ddb` |
| Backend / Core | `#E1F5FE` | `#5baed1` |
| Event / Kafka | `#F1F8E9` | `#82b56e` |
| Batch | `#FFF3E0` | `#c9a83e` |
| Storage / DB | `#E8F5E9` | `#6ca876` |

### 3. Typography & Text Handling

- **Font Family:** `"fontFamily": 1` (ExcaliFont) — 모든 텍스트 요소 통일
- **Native Text Binding:**
  - 부모 rect: `"boundElements": [{ "type": "text", "id": "<text_id>" }]`
  - 텍스트 element: `"containerId": "<parent_id>"`, `"type": "text"`
- **일반 박스:** `textAlign: "center"`, `verticalAlign: "middle"`
- **Group Box 라벨:** `textAlign: "left"`, `verticalAlign: "top"` (상단 좌측)
- **Text Color:** 박스 palette 색상의 더 어두운 high-contrast 버전
- **Text Wrapping:** 박스 너비 초과 시 word 단위 wrapping

### 4. Connection & Routing Logic

- **Input:** 컴포넌트 **왼쪽**에서 진입
- **Output:** 컴포넌트 **오른쪽**에서 출발
- **Origin Spacing:** 같은 source에서 출발하는 화살표는 일정 간격으로 분산

**Zero-Crossing Parallel Highway 규칙:**
- 평행 직각 선의 굽힘 X 좌표를 **10-20px 간격**으로 stagger
- **Bending Swap Rule (같은 수직 방향):**
  - 낮은 Y 목적지 → 더 일찍 굽힘 (source에 가깝게)
  - 높은 Y 목적지 → 더 늦게 굽힘 (source에서 멀게)

**Destination Port Y-Axis Priority Sorting:**
- 동일 destination의 왼쪽 edge 진입 포트 Y 좌표를 source Y에 비례해 정렬
- 가장 높은 source → 가장 높은 포트, 가장 낮은 source → 가장 낮은 포트

**충돌 방지:**
- 화살표가 박스를 관통하면 안 됨
- 평행 화살표 사이 빈 공간 유지

**Label 위치:**
- 수평 segment 중간점에서 **15px 위**에 float
- 화살표 선과 label 텍스트가 교차하면 안 됨

### 5. Horizontal Margins & Spacing

| Gap | 위치 | 최소 거리 |
|---|---|---|
| Gap 1 | Source → 첫 Group Box | **120px** (HTTPS 라벨 공간) |
| Gap 2 | Component → Component (group 간) | **100px** (Feign/WebClient 라벨 공간) |
| Gap 3 | Backend → Storage | **140-170px** (staggered bend + driver 라벨 공간) |

### 6. Technical Implementation

JSON 직접 생성 시:
1. 박스 `width`/`height`를 텍스트 길이와 행 정렬 기반으로 **먼저 계산**한 후 element 생성
2. `strokeColor`, `backgroundColor`, `roundness`, `roughness` 매핑을 위 정의대로 적용
3. 모든 arrow: `elbowed: true`, `roundness: null`
4. Arrow `points`: 수평/수직 segment만 (`[x,y] → [x2,y] → [x2,y2]`)
5. Frame `name`: 빈 문자열 (`""`) — `appState.frameRendering.name: false`

### 7. QA 체크리스트

생성 후 반드시 확인:

| 항목 | 기준 |
|---|---|
| Arrow 수 | Mermaid edge 수와 일치 |
| Segment 방향 | 모든 segment가 수평 또는 수직 |
| 노드 관통 | source/target 외 bbox 관통 0건 |
| Label 겹침 | arrow label과 node bbox 겹침 0건 |
| Text overflow | 컴포넌트 박스를 넘치는 node label 0건 |
| Padding | frame-child padding ≥50px top, ≥48px side |
| Storage edge | 프로토콜별로 서로 다른 색상 (모두 동일색 금지) |
| roughness | 모든 element `roughness: 1` |
| fontFamily | 모든 text element `fontFamily: 1` |
