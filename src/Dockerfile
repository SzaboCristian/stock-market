FROM python:3.8

# Upgrade pip
RUN pip install --upgrade pip

# Create directories for Flask
RUN mkdir -p /usr/flask-app/ignore
WORKDIR /usr/flask-app

# Copy app
COPY ./ ./

# Install poetry
RUN pip install poetry==1.6.1

# Create lock file and install dependencies
RUN poetry lock
RUN poetry install

# Solve import-error for package hierarchy
ENV PYTHONPATH="$PYTHONPATH:."

# Run webserver
CMD ["poetry", "run", "gunicorn", "-c", "webserver/gunicorn.conf.py", "webserver.wsgi:flask_app"]