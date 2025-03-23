# 베이스 이미지 선택
FROM python:3.12-slim

# 작업 디렉터리 설정
WORKDIR /backend/batch /app

# 필요한 파일 복사
COPY main.py .
COPY .env .

# 필요한 파이썬 패키지 설치
# requirements.txt 파일이 있는 경우, 해당 파일을 복사하고 패키지를 설치합니다.
COPY requirements.txt .
RUN pip install -r requirements.txt

# 애플리케이션 실행 명령
CMD ["python", "main.py"]
