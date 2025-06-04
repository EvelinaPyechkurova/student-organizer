ARG PYTHON_VERSION=3.13.3

FROM python:${PYTHON_VERSION}-slim AS builder

WORKDIR /student-organizer

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

COPY requirements.txt .

RUN pip install --upgrade pip 
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    organizeruser

RUN chmod a+x docker-entrypoint.sh

USER organizeruser

EXPOSE 8000

ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]