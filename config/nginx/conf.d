upstream webapp {
    server education_platform_web_1:8000;
}

server {
    listen 80;
    server_name localhost;
    error_log stderr warn;
    access_log /dev/stdout main;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_redirect off;
    }

    location /static/ {
        autoindex on;
        alias /education_platform/static/;
    }

    location /media/ {
        alias /education_platform/media/;
    }

}