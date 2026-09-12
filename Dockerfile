FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user matching a typical host UID/GID (1000) so files this
# container writes into the bind-mounted repo (generated_teams/, migrations)
# aren't left root-owned on the host.
RUN groupadd -g 1000 app && useradd -u 1000 -g app -m app && chown -R app:app /app
USER app

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
