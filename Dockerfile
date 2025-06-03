ARG PYTHON_VERSION=3.13.3

FROM python:${PYTHON_VERSION}ve-slim AS builder

WORKDIR /student-organizer

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

COPY requirments.txt .

RUN pip install --upgrade pip 
RUN python -m pip install --no-cache-dir -r requirments.txt

COPY . .

EXPOSE 8000

# CREATING USER
ARG UID=10001
RUN adduser \
    --uid "${UID}" \
    oranizeruser
    
USER oranizeruser

CMD [ "python", "manage.py", "runserver" ]