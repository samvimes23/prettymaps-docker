FROM python:3.12-slim

# Install system dependencies for geospatial libraries
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone the repository (we clone fresh to ensure we have the app.py)
RUN git clone https://github.com/marceloprates/prettymaps.git /app

# The original app.py needs our layout padding fix and credit=False fix.
# We will use sed to patch it during the build process.
RUN sed -i 's/credit=True/credit=False/g' /app/app.py || true
RUN sed -i 's/pad_inches=1.0/pad_inches=0.4/g' /app/app.py || true
RUN sed -i 's/fontsize=36/fontsize=32/g' /app/app.py || true
RUN sed -i 's/fontsize=14/fontsize=12/g' /app/app.py || true
# Ensure the plot call has credit=False
RUN sed -i '/show=False,/a \                credit=False,' /app/app.py || true


# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
