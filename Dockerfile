# Alpine image that already has Python 3.12 + Node 18
FROM nikolaik/python-nodejs:python3.12-nodejs18-alpine

# ---------- FastAPI ----------
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /backend
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY backend/ /backend

# ---------- Next.js ----------
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ /frontend

# ---------- Nginx ----------
RUN apk add --no-cache nginx
RUN mkdir -p /etc/nginx/conf.d
COPY nginx/heroku/nginx.conf /etc/nginx/nginx.conf
COPY nginx/heroku/default.conf /etc/nginx/conf.d/default.conf

# Default command is supplied by heroku.yml
