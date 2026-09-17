# Dream Shaper — AI 서버 : S3 업로드 (2023.09)
#
# 클라이언트가 올린 파일을 S3에 저장하고 URL(key)만 반환합니다.
# 「서버가 파일을 경유하지 않는다」는 구조 전환의 결과물이며,
# 그 이전 버전이 legacy_flask_upload.py 입니다.
#
# 2026-09-15 : 하드코딩돼 있던 AWS 자격증명을 .env 로 분리했습니다.

# --- 자격증명 분리 (2026-09-15) : 하드코딩 키를 .env로 옮겼습니다 -------------
import os
from pathlib import Path

def _load_dotenv():
    """이 파일 기준 가장 가까운 .env를 찾아 환경변수로 읽어들입니다."""
    here = Path(__file__).resolve().parent
    for d in [here, *here.parents][:4]:
        f = d / ".env"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return

_load_dotenv()
# ---------------------------------------------------------------------------

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import boto3
from fastapi.templating import Jinja2Templates
from starlette.requests import Request 

templates = Jinja2Templates(directory="./")

app = FastAPI()

# AWS S3 관련 설정
AWS_BUCKET_NAME = "sangtes"
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

@app.post("/upload/")
async def upload_image(file: UploadFile):
    # 업로드할 파일의 이름
    file_name = file.filename

    # S3 버킷 내 경로 및 파일 이름 설정
    s3_key = f"uploads/{file_name}"

    # 파일 업로드
    s3.upload_fileobj(file.file, AWS_BUCKET_NAME, s3_key)

    # S3에 업로드된 이미지 URL 생성
    image_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

    return {"file_name": file_name, "image_url": image_url}


# @app.get("/test")
# def sss():
#     image_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/uploads/KakaoTalk_20230926_192420902_01.png"
#     return templates.TemplateResponse("test.html",{ "image" : image_url} )

@app.get("/test", response_class=HTMLResponse)  # response_class를 HTMLResponse로 설정
def sss(request: Request):  # Request를 인자로 추가
    image_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/uploads/KakaoTalk_20230926_192420902_01.png"
    return templates.TemplateResponse("test.html", {"request": request, "image": image_url})