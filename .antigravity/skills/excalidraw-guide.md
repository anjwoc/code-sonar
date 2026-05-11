# Excalidraw Visual Style Guide

Mermaid 또는 컴포넌트 설명에서 Excalidraw 다이어그램을 생성할 때 반드시 따르는 스타일 가이드.

## Workflow

**Step 1 — Mermaid 정제 (LLM에 요청):**
```
기존 mermaid 코드에서 스타일 제거하고 각 컴포넌트의 관계만 고려해서 재작성해줘
```

정제 결과 조건:
- `classDef`, `style`, `class`, `%%{init}%%` 제거
- `flowchart LR` 방향 유지
- edge label: 프로토콜/목적만 (`HTTPS`, `Feign`, `JDBC/JPA`, `Kafka` 등)

**Step 2 — Excalidraw 생성 (MCP 또는 CLI):**
```
(개정된 mermaid 코드를 가지고) <파일명>.excalidraw를 아래 mermaid 참고해서 그려줘
```

CLI:
```bash
node scripts/render-excalidraw-from-mermaid.js --input "<index.md>" --output "<diagram.excalidraw>"
```

---

## 1. Arrow Styling & Color Palette

- **Default:** Grayscale `#868e96`, `#adb5bd`
- **Highlight (강조 필요 시만):** Pastel
  ```
  #FFB3BA #FFDFBA #FFFFBA #BAFFC9 #BAE1FF #D5AAFF #F8BBD0 #B2EBF2 #C8E6C9 #FFE0B2
  ```

| Protocol | strokeColor | labelFill |
|---|---|---|
| neutral | `#868e96` | `#f8f9fa` |
| HTTPS/HTTP | `#BAFFC9` | `#ebfbee` |
| WebClient | `#BAE1FF` | `#e7f5ff` |
| Kafka | `#B2EBF2` | `#e3fafc` |
| JDBC/JPA | `#BAE1FF` | `#e7f5ff` |
| Redis | `#FFB3BA` | `#fff5f5` |
| Spring Data / Mongo | `#D5AAFF` | `#f3f0ff` |
| Elasticsearch | `#FFDFBA` | `#fff9db` |

## 2. Box & Container

- `roundness: { type: 3 }` (Rounded edges)
- `roughness: 1` (Medium)
- 같은 행 박스: 동일 height
- Y-Axis: top-level Group Box `y: 60`, 내부 컴포넌트 `y: 130`
- Group Box opacity: 낮게 (pale version of tone)

**Box Palette:**
```
#F9F9F9  #F0F4F8  #E8F5E9  #FFF3E0  #F3E5F5
#E1F5FE  #FBE9E7  #EFEBE9  #F1F8E9  #E0F2F1
```

**Vertical Padding:** Group Box 상단 → 첫 컴포넌트 ≥ **50px**

| Layer | fill | stroke |
|---|---|---|
| External | `#FFF3E0` | `#c9966b` |
| Frontend/App | `#F0F4F8` | `#74a8c9` |
| Gateway | `#F3E5F5` | `#b39ddb` |
| Backend/Core | `#E1F5FE` | `#5baed1` |
| Event | `#F1F8E9` | `#82b56e` |
| Batch | `#FFF3E0` | `#c9a83e` |
| Storage | `#E8F5E9` | `#6ca876` |

## 3. Typography

- `fontFamily: 1` (ExcaliFont) — 전체 통일
- Native binding: rect `boundElements` ↔ text `containerId`
- 일반 박스: `textAlign: center`, `verticalAlign: middle`
- Group label: `textAlign: left`, `verticalAlign: top`
- Text color: 박스 색의 high-contrast darker variant

## 4. Connection & Routing

- Input: 컴포넌트 **왼쪽**, Output: **오른쪽**
- 같은 source 화살표: 일정 간격 분산

**Parallel Highway:**
- bending X 좌표: **10-20px step-off** stagger
- Bending Swap (같은 수직 방향):
  - 낮은 Y 목적지 → 더 일찍 굽힘
  - 높은 Y 목적지 → 더 늦게 굽힘
- Destination Port: source Y 높이에 비례해 port Y 정렬

**Label:** 수평 segment 중간점 **15px 위**

## 5. Spacing

| Gap | 최소 |
|---|---|
| Source → 첫 Group Box | **120px** |
| Component → Component | **100px** |
| Backend → Storage | **140-170px** |

## 6. JSON 필수 속성

```json
{
  "elbowed": true,
  "roundness": null,
  "roughness": 1,
  "fontFamily": 1,
  "appState": {
    "currentItemArrowType": "elbow",
    "frameRendering": { "name": false }
  }
}
```

## 7. QA

| 항목 | Pass 조건 |
|---|---|
| Arrow 수 | Mermaid edge 수 일치 |
| Segment | 수평/수직만 |
| 관통 | source/target 외 0건 |
| Label 겹침 | 0건 |
| Text overflow | 0건 |
| Frame padding | top ≥50px, side ≥48px |
| Storage edge | 프로토콜별 다른 색 |
