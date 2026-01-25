FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt constraints.txt ./

RUN pip install --upgrade pip setuptools wheel && \
    pip install \
      --prefer-binary \
      --only-binary=:all: \
      -r requirements.txt \
      -c constraints.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
