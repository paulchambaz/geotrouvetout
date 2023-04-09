# First stage: build
FROM alpine:edge

RUN apk update && apk add --no-cache python3 python3-dev py3-pip py3-wheel g++ make cmake gfortran musl-dev linux-headers geos geos-dev libstdc++ tesseract-ocr tesseract-ocr-dev leptonica leptonica-dev openblas openblas-dev libgomp jpeg-dev zlib-dev libwebp-dev tiff-dev openjpeg-dev freetype-dev proj proj-dev curl git bash gcc bzip2-dev readline-dev sqlite-dev openssl-dev libffi-dev xz-dev proj-dev proj proj-util gdal gdal-dev

# install poetry as we need it to install the program
RUN pip install poetry

# installing pyenv
RUN curl https://pyenv.run | bash
RUN echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && \
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc && \
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

# installs python 3.10
SHELL [ "/bin/bash", "-c" ]
RUN source ~/.bashrc && pyenv install 3.10 && pyenv global 3.10

ENV PROJ_DIR="/usr"
ENV PROJ_LIBDIR="/usr/lib"
ENV PROJ_INCDIR="/usr/include"

COPY pyproject.toml /app/pyproject.toml
WORKDIR /app

# setting up poetry environment and installing libraries
RUN source ~/.bashrc && \
    # poetry config virtualenvs.create false && \
    poetry env use 3.10 && \
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
