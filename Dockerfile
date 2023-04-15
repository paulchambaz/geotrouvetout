# First stage: build
FROM python:3.10

RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ make cmake gfortran \
    libgeos-dev libtesseract-dev libleptonica-dev \
    libopenblas-dev libgomp1 libjpeg-dev libz-dev libwebp-dev \
    libtiff5-dev libopenjp2-7-dev libfreetype6-dev \
    libproj-dev proj-data proj-bin \
    libgdal-dev gdal-bin \
    git bash gcc libbz2-dev libreadline-dev \
    libsqlite3-dev libssl-dev libffi-dev liblzma-dev libc6 \
    libgl1-mesa-dev tesseract-ocr

RUN pip install --no-cache-dir poetry

ENV PROJ_DIR="/usr" \
    PROJ_LIBDIR="/usr/lib" \
    PROJ_INCDIR="/usr/include"

COPY pyproject.toml /app/pyproject.toml
WORKDIR /app

# setting up poetry environment and installing libraries
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Expose port 8000 for external access
EXPOSE 8000

# Add command to run project
ENTRYPOINT ["poetry", "run", "geotrouvetout"]

# Copy project files
COPY weights /app/weights
COPY stats /app/stats
COPY rest_api /app/rest_api
COPY geotrouvetout /app/geotrouvetout
