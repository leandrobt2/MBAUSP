# Frontend
FROM nginx:alpine

COPY public /usr/share/nginx/html/public
COPY admin /usr/share/nginx/html/admin

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]