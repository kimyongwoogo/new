# HTML → MP4 변환기

로컬 HTML 파일을 렌더링해서 MP4로 저장하는 간단한 Python 프로그램입니다.

## 동작 방식

1. Playwright(Chromium)로 HTML 파일을 엽니다.
2. 지정한 FPS/길이에 따라 PNG 프레임을 캡처합니다.
3. ffmpeg로 프레임 시퀀스를 MP4(H.264)로 인코딩합니다.

## 설치

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

추가로 시스템에 `ffmpeg`가 설치되어 있어야 합니다.

## 사용법

```bash
python html_to_mp4.py ./example.html ./out/video.mp4
```

옵션 예시:

```bash
python html_to_mp4.py ./example.html ./out/video.mp4 \
  --size 1920x1080 \
  --fps 60 \
  --duration 8 \
  --wait-before-capture 1.2 \
  --crf 18
```

## 주요 옵션

- `--size`: 해상도 (`WIDTHxHEIGHT`, 기본 `1280x720`)
- `--fps`: 프레임레이트 (기본 `30`)
- `--duration`: 영상 길이(초, 기본 `5`)
- `--wait-before-capture`: 캡처 시작 전 대기 시간(초, 기본 `0.5`)
- `--crf`: H.264 품질값(0~51, 낮을수록 고화질, 기본 `20`)

## 참고

- 동적인 애니메이션/JS 기반 UI도 캡처됩니다.
- 입력 HTML 내 외부 리소스(CDN 이미지/폰트 등)는 네트워크 상태에 영향을 받습니다.
