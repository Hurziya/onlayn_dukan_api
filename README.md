# 🛒 Onlayn Dukan API

Onlayn dúkan ushın arnalǵan RESTful API. Django hám Django REST Framework tiykarında qurılǵan, Docker arqalı iske túsiriw ushın tayarlanǵan.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Django](https://img.shields.io/badge/Django-REST%20Framework-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

## 📋 Mazmunı

- [Aǵza mumkinshilikleri](#-aǵza-mumkinshilikleri)
- [Qollanılǵan texnologiyalar](#-qollanılǵan-texnologiyalar)
- [Ornatıw hám iske túsiriw](#-ornatıw-hám-iske-túsiriw)
- [API dokumentaciyası](#-api-dokumentaciyası)
- [Proekt qurılımı](#-proekt-qurılımı)


## ✨ Aǵza mumkinshilikleri

- Ónimlerdi (products) basqarıw — qosıw, ózgertiw, óshiriw, kóriw
- Kategoriyalar boyınsha filtrlew
- Paydalanıwshı avtorizaciyası hám autentifikaciyası
- Buyırtpalar (orders) sistemasi
- Swagger arqalı avtomatlıq API dokumentaciya




## 🛠 Qollanılǵan texnologiyalar

- **Backend:** Python, Django, Django REST Framework
- **Baza:** PostgreSQL 
- **Konteynerlestiriw:** Docker, Docker Compose
- **API dokumentaciya:** Swagger (drf-spectacular)

## 🚀 Ornatıw hám iske túsiriw

### Talaplar

- [Docker](https://www.docker.com/) hám Docker Compose kompyuterińizde ornatılǵan bolıwı kerek

### Qádemler

**1. Repozitoriyanı juklep alıń:**

```bash
git clone https://github.com/Hurziya/onlayn_dukan_api.git
cd onlayn_dukan_api
```

**2. Konteynerlerdi iske túsiriń:**

```bash
docker-compose up -d --build
```

**3. Migraciyalardı qollań:**

```bash
docker-compose exec web python manage.py migrate
```

**4. Admin paydalanıwshı jaratıń:**

```bash
docker-compose exec web python manage.py createsuperuser
```

Server iske túsken soń, joba tómendegi mánzilde qoljetimli boladı:

```
http://127.0.0.1:8000/
```

## 📖 API dokumentaciyası

API endpointlerdiń tolıq dizimin hám olardı sınap kóriw imkaniyatın Swagger arqalı tabasız:

**Swagger UI:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

## 📁 Proekt qurılımı

```
onlayn_dukan_api/
├── config/              # Proekttiń tiykarǵı sazlawları
├── apps/                # Django qosımshaları (shop, users, bot)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py
```

