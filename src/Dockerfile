FROM python:3.6

# Create directories for Flask
RUN mkdir -p /usr/flask-app/ignore
WORKDIR /usr/flask-app

# Copy requirements.txt
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy app
COPY ./ ./

# Solve import-error for package hierarchy
ENV PYTHONPATH="$PYTHONPATH:."

# Run webserver
CMD ["python", "-m", "webserver.wsgi"]
