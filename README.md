
Proektti Iske Tusiriw (Instrukciya)
Kompuyterinizde Docker ornatilgan boliwi kerek
Repozitoriyani juklep aliw:

git clone https://github.com/Hurziya/onlayn_dukan_api.git
cd Market_API 
env.example fayli tiykarinda .env faylin jaratiw kerek.


Migraciyalardi qollaw ham admin jaratiw
docker-compose exec web python manage.py migrate

docker-compose exec web python manage.py createsuperuser
API Endpointler (Swagger)
Server iske tuskennen keyin, API hujjetlerin tomendegi siltemeler arqali koriwiniz mumkin:
Swagger UI (Interaktiv): http://127.0.0.1/api/schema/swagger-ui/

Tiykargi Endpointler Dizimi:
Metod URL Tusindirme

POST /api/register/ Jana paydalaniwshi dizimnen otiw

POST /bot/login/ Kiriw (Token aliw)

GET /shop/products/ Barliq onimlerdi koriw (Filter, Search bar)

GET /shop/products/{id}/ Aniq bir onim haqqinda magliwmat

POST /api/cart/add/ Sebetke o'nim qosiw

GET /api/cart/ Oz sebetinizdi koriw

POST /api/orders/checkout/ Buyirtpa beriw (Order jaratiw)

GET /api/orders/ Buyirtpalar tariyxin koriw

POST /api/reviews/ Satip alingan onimge pikir qaldiriw
