FROM nginx:1.23.1

# Remove the default Nginx configuration file (if it exists)
# RUN rm /etc/nginx/conf.d/default.conf
#
## Copy your custom Nginx configuration file
COPY config/nginx/conf.d /etc/nginx/conf.d/default.conf
COPY ./static ./education_platform/static

CMD ["nginx", "-g", "daemon off;"]