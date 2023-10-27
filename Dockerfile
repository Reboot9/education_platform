FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1 \
    POETRY_VERSION=1.4.2 \
    POETRY_VIRTUALENVS_CREATE="false"

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /education_platform

COPY pyproject.toml poetry.lock docker-entrypoint.sh ./

RUN poetry install --no-interaction --no-ansi --no-dev

COPY . /education_platform

RUN chmod +x wait-for-it.sh

# COPY ./static ./static

#VOLUME ["/education_platform/static"]
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]

CMD ["gunicorn", "education_platform.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "4", "--threads", "4"]

#CMD ["daphne", "-u", "/education_platform/daphne.sock", "education_platform.asgi:application", "-p", "8001"]
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8001", "education_platform.asgi:application"]