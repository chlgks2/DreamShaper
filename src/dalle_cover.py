# Dream Shaper — AI 서버 : DALL·E 2 앨범 커버 생성 (2023.09)
#
# 사용자가 마우스로 마스크를 그리면 그 영역을 DALL·E 2 outpainting으로
# 확장해 앨범 커버 5장을 생성합니다. /draw 엔드포인트의 원형입니다.
#
# 2026-09-15 : 하드코딩돼 있던 OpenAI API 키를 .env 로 분리했습니다.

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

import cv2
import numpy as np
import openai
import requests
from PIL import Image
from io import BytesIO

# 마우스 콜백 함수
drawing = False


def draw_with_mouse(event, x, y, flags, param):
    global drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        cv2.circle(mask, (x, y), 35, 0, -1)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cv2.circle(mask, (x, y), 35, 0, -1)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.circle(mask, (x, y), 35, 0, -1)


def generate_outpainted_images(image_path, prompt):
    # OpenAI API 키 설정
    openai.api_key = os.environ["OPENAI_API_KEY"]

    # 이미지 업로드 및 Outpainting 실행
    response = openai.Image.create_edit(
        image=open(image_path, "rb"),
        prompt=prompt,
        n=5,
        size="1024x1024"
    )

    # 생성된 이미지 URL들 가져오기
    image_urls = [img['url'] for img in response.data]

    # 이미지 URL들 출력 및 저장
    saved_paths = []
    for idx, url in enumerate(image_urls):
        print(f"{idx + 1}. {url}")

        # 이미지 다운로드 및 저장
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        save_path = f"generated_image_{idx + 1}.png"
        img.save(save_path)
        saved_paths.append(save_path)

    return saved_paths


# 사용자로부터 이미지 경로 입력 받기
image_path_input = input("Enter the path to your image: ")
img = cv2.imread(image_path_input, cv2.IMREAD_UNCHANGED)

if img is None:
    print("이미지를 불러올 수 없습니다.")
    exit()

h, w = img.shape[:2]
mask = np.ones((h, w), dtype=np.uint8) * 255

cv2.namedWindow('Image')
cv2.setMouseCallback('Image', draw_with_mouse)

while True:
    img_masked = cv2.bitwise_and(img, img, mask=mask)
    cv2.imshow('Image', img_masked)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:  # ESC 키
        break

cv2.destroyAllWindows()

# 마스크를 통해 알파 채널 추가
img_bgra = cv2.merge((img[:, :, 0], img[:, :, 1], img[:, :, 2], mask))
output_path = "output_image.png"
cv2.imwrite(output_path, img_bgra)

# 이제 OpenAI API를 사용하여 이미지 확장
prompt = input("Enter your desired prompt: ")
saved_image_paths = generate_outpainted_images(output_path, prompt)
print(f"Images saved at: {', '.join(saved_image_paths)}")

#City view with brightly shining stars album