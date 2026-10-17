FROM python:3.14-slim AS runtime
WORKDIR /app
COPY src/ ./src/
ENV PORT=8080
EXPOSE 8080
USER nobody
CMD ["python3", "-m", "src.app"]
