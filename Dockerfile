FROM python:3.12-slim

# Install system dependencies for geospatial libraries
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone the repository
RUN git clone https://github.com/marceloprates/prettymaps.git /app

# OVERWRITE the default app.py with our customized version
COPY prettymaps/app.py /app/app.py

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
