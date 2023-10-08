FROM nginx:1.23.1

RUN rm /etc/nginx/conf.d/default.conf

# Copy  Nginx configuration file
COPY config/nginx/conf.d /etc/nginx/conf.d/default.conf
COPY ./static ./static



CMD ["nginx", "-g", "daemon off;"]