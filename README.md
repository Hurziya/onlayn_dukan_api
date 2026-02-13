
Proektti Iske Tusiriw (Instrukciya)
Kompuyterinizde Docker ornatilgan boliwi kerek
Repozitoriyani juklep aliw:

git clone https://github.com/Hurziya/onlayn_dukan_api.git
cd onlayn_dukan_api

Migraciyalardi qollaw ham admin jaratiw
docker-compose exec web python manage.py migrate

docker-compose exec web python manage.py createsuperuser
API Endpointler (Swagger)
Server iske tuskennen keyin, API hujjetlerin tomendegi silteme arqali koriwiniz mumkin:
Swagger: http://127.0.0.1:8000/api/docs/


