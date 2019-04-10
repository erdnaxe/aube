FROM debian:buster-slim

# Django code will be in /usr/src/app/
# During development you should mount the git code there,
# During production you should copy the code in the image.
WORKDIR /var/www/aube

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY apt_requirements.txt ./
RUN apt update \
    && apt install -y $(cat ./apt_requirements.txt) \
    && rm -rf /var/lib/apt/lists/*

# Pass only port 8080
EXPOSE 8080

# Set entrypoint : make migrations and collect statics
COPY . ./
ENTRYPOINT [ "./update.sh" ]

# Start Django app
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]
