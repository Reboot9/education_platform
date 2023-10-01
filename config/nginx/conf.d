server {
    listen 80;
    server_name education_platform_web_1;
    error_log stderr warn;
    access_log /dev/stdout main;

    location / {
        proxy_pass http://education_platform_web_1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
    }

    location /static/ {
        alias /education_platform/static/;
    }

    location /media/ {
        alias /education_platform/media/;
    }

    types {
        text/javascript js;
        application/javascript js;
        text/css css;
    }
}