FROM python:3.12.4-alpine3.20

# curl for the health check
RUN apk --no-cache add curl

WORKDIR /app

# copy dependencies to working dir
COPY requirements.txt . 

# install dependencies
RUN pip install -r requirements.txt

# copies app source independently > improve build time by using cache if no dependencies are added
COPY app.py .

# gunicorn is a webserver
CMD [ "gunicorn", "--bind", "0.0.0.0:8080", "app:app" ]
