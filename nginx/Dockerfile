# Stage for Nginx
FROM nginx:1.23.3-alpine-slim as prod

RUN rm /etc/nginx/conf.d/default.conf
COPY project.conf /etc/nginx/conf.d/