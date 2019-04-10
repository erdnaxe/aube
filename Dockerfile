FROM debian:buster-slim

# Django code will be in /usr/src/app/
# During development you should mount the git code there,
# During production you should copy the code in the image.
WORKDIR /var/www/aube

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update \
    && apt install -y TODO \
    && rm -rf /var/lib/apt/lists/*

# Pass only port 8080
EXPOSE 8080

# Set entrypoint : make migrations and collect statics
COPY update.sh ./
ENTRYPOINT [ "./update.sh" ]

# Start Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
