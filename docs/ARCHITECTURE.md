# 서비스 구조와 담당 범위

## 백엔드가 두 대였습니다

React 프론트엔드가 **서로 다른 두 백엔드**를 호출합니다.

```
[React 프론트엔드]  ← 팀원
   │
   ├─ REACT_APP_BACK   → 인증 서버   /register · /login     ← 팀원
   │                      FastAPI · MongoDB(motor) · JWT HS256 · bcrypt
   │
   └─ REACT_APP_AI_API → ⭐ AI 서버  /convert · /draw       ← 본인
                          FastAPI · boto3 · DALL·E 2
                             ├─ /convert → SVC/RVC + HuBERT 음색 변환 → S3
                             └─ /draw    → DALL·E 2 앨범 커버 생성 → S3
```

| 구성요소 | 담당 |
|---|---|
| **AI 서버** — 음성 변환 · 앨범 커버 · S3 연동 | ⭐ **본인** |
| 인증 서버 — 회원가입 · 로그인 | 팀원 |
| React 프론트엔드 · Docker Compose · EC2 배포 | 팀원 |

> **「백엔드를 전담했다」는 정확하지 않습니다.** 인증 서버는 팀원이 만들었습니다.
> **「AI 서버를 직접 구축했다」** 가 정확하고, 담당 전문성도 더 잘 드러납니다.

## 왜 FastAPI였나

원래 백엔드 담당이 아니었고, 백엔드 인력 이탈로 급하게 서버를 만들어야 하는 상황이었습니다.

| 이유 | |
|---|---|
| **Python 생태계** | 추론 코드가 이미 Python — 모델을 서버에 붙이는 비용이 가장 낮았습니다 |
| **학습 곡선** | 남은 일정이 2주 남짓이라 빠르게 익힐 수 있는 것이 중요했습니다 |
| **자동 문서화** | 프론트엔드와 API 스펙을 맞춰야 했는데 문서를 따로 쓸 시간이 없었습니다 |

## 사용자 동선

```
가입/로그인 → 아티스트 선택 → 곡 업로드 → /convert
                                    → 커버 스케치 → /draw
                                    → 결과 화면 (음원 + 커버)
```

## 파일 전송 — 구조를 바꾼 지점

### BEFORE — 서버 경유 ([`src/legacy_flask_upload.py`](../src/legacy_flask_upload.py))

```
클라이언트 → [Flask 서버가 파일 전체 수신·저장] → 로컬 디스크
```

음원 한 곡이 수십 MB인데 서버가 전 구간을 받아 들고 있어야 했습니다.
**ffmpeg 청크 분할**로 쪼개 보냈지만 조립·타임아웃 문제로 실패했습니다.

### AFTER — S3 직접 업로드 ([`src/s3_upload_api.py`](../src/s3_upload_api.py))

```
클라이언트 ──────── 파일 전체 ────────→ AWS S3
           └─ 경로(key) ─→ [FastAPI 서버]
```

```python
@app.post("/upload/")
async def upload_image(file: UploadFile):
    s3_key = f"uploads/{file.filename}"
    s3.upload_fileobj(file.file, AWS_BUCKET_NAME, s3_key)
    image_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    return {"file_name": file.filename, "image_url": image_url}
```

**서버가 파일 트래픽에서 완전히 빠졌습니다.**

### 핵심은 로직이 아니라 전제였습니다

청크 분할을 계속 다듬는 대신 이렇게 물었습니다.

> *"서버가 파일을 받아야 하는가?" → 아니오. 클라이언트가 S3에 직접 올리고, 서버는 경로만 안다.*

### 다만 정답은 매번 달랐습니다

| 프로젝트 | 방식 | 우선한 것 |
|---|---|---|
| **Dream Shaper** (2023.09) | 클라이언트 → S3 직접 | 서버 부하 |
| **Blind Dating** (2026.06) | 워커 → 백엔드 → S3 | **GPU 서버에 자격증명을 두지 않기** |
| **Emour** (2026.08) | `FileStorage` 인터페이스 추상화 | DB에 전체 URL이 아니라 key만 |

Blind Dating에서는 **반대로 백엔드를 경유하게 했습니다.** 자격증명 보관 지점을 하나로 줄이는 것이 서버 부하보다 중요했기 때문입니다.

**"서버를 거치지 않는다"가 항상 정답은 아니고, 무엇을 지켜야 하는지에 따라 답이 달라집니다.**

## 배포

| 항목 | |
|---|---|
| 프론트 · 인증 서버 | Docker Compose (client:3000 / back:8000) · AWS EC2 |
| **AI 서버** | **로컬 실행** — GPU가 필요해 EC2에 올리지 않았습니다 |

## 코드 확보 현황

| 항목 | 상태 |
|---|---|
| FastAPI + boto3 S3 업로드 | ✅ [`src/s3_upload_api.py`](../src/s3_upload_api.py) |
| DALL·E 2 앨범 커버 생성 | ✅ [`src/dalle_cover.py`](../src/dalle_cover.py) |
| 서버 경유 전송 (폐기 버전) | ✅ [`src/legacy_flask_upload.py`](../src/legacy_flask_upload.py) |
| `/convert`·`/draw` 를 합친 **완성 서버** | 🔴 **미확보** |

**구성요소 코드는 모두 남아 있지만, 두 엔드포인트를 하나로 묶은 완성본은 찾지 못했습니다.**
엔드포인트 개수 · `BackgroundTasks` 사용 여부 · presigned URL 사용 여부 등 구현 세부는 **주장하지 않습니다.**
