from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core import mail
from django.test import TestCase

User = get_user_model()

class UserTests(APITestCase): # UserTests APITestCase-dan miras aladı, bu API testleri uchun maxsus sinifdir.
    def setUp(self): # Test baslanbastan burın ishletiladigan metod, testler uchun umumiy tayyorgarlık ishlerini bajaradi.
        self.client = APIClient() # APIClient obyekti yaratadi, bu testler davomida API chaqiriqlari uchun ishlatiladi.
        self.register_url = reverse('user-list')  # 'user-list' URL nomi bilan ro'yxatdan o'tish endpointini olish uchun reverse funksiyasidan foydalaniladi.
        self.me_url = reverse('user-manage-profile') # 'user-manage-profile' URL nomi bilan foydalanuvchi profilini boshqarish endpointini olish uchun reverse funksiyasidan foydalaniladi.
        self.logout_url = reverse('user-logout') # 'user-logout' URL nomi bilan foydalanuvchi logout endpointini olish uchun reverse funksiyasidan foydalaniladi.
        
        self.user_data = { # Test uchun foydalanuvchi ma'lumotlari, bu ma'lumotlar ro'yxatdan o'tish testida ishlatiladi.
            "phone_number": "+998901112233",
            "email": "testuser@gmail.com", # Shın email
            "password": "password123",
            "first_name": "Atabek",
            "last_name": "Jalgasov"
        }

        self.user = User.objects.create_user(**self.user_data)
        self.logout_url = reverse('user-logout')
        

    def test_create_user_manager(self): # UserManager sinifining create_user metodini test qiladi, bu metod foydalanuvchi yaratishda email maydonini None qilishini tekshiradi.
        """UserManager avtomat email jaratpawın (None bolıwın) tekseriw"""
        user = User.objects.create_user(phone_number="+998900000000", password="pass")
        self.assertEqual(user.phone_number, "+998900000000") # Telefon raqami to'g'ri saqlanganligini tekshiradi.
        self.assertIsNone(user.email) # Endi bul jer None bolıwı kerek


    def test_user_registration(self): # Ro'yxatdan o'tish jarayonini test qiladi, bu test API orqali foydalanuvchi yaratishni tekshiradi.
        """API arqalı dizimnen ótiw"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], self.user_data['email'])

    def test_user_logout(self):
            """Logout API arqalı sistemadan shıǵıw"""
            # Aldın login qılamız (bazada bar user menen)
            self.client.login(phone_number=self.user_data['phone_number'], password=self.user_data['password'])
            
            response = self.client.post(self.logout_url)
            
            # Logout ádette 200 yamasa 204 qaytaradı
            self.assertEqual(response.status_code, status.HTTP_200_OK) 
            
            # Haqıyqattan shıqqanın tekseriw ushın:
            response_me = self.client.get(reverse('user-manage-profile'))
            self.assertEqual(response_me.status_code, status.HTTP_401_UNAUTHORIZED)

class UserSignalTest(TestCase):
    def test_welcome_email_signal_sent(self): # User yaratılganda welcome email signalining ishletilishini test qiladi, bu test foydalanuvchi yaratishda email maydoniga qiymat berilganda email xabarining yuborilishini tekshiradi.
        """Email kiritilse xat ketiwi kerek"""
        mail.outbox = [] # Django test muhitida yuborilgan email xabarlarini saqlaydigan outbox ro'yxatini tozalaydi.
        # UserManager bul jerde email-dı None qılmaydı, shuning uchun signaldaǵı 'if instance.email' sharti bajariladi va email xabari yuboriladi.
        User.objects.create_user(
            phone_number="+998908887766",
            email="realuser@gmail.com",
            password="password123"
        )
        self.assertEqual(len(mail.outbox), 1) # Email xabarining yuborilganligini tekshiradi, bu yerda 1 bo'lishi kerek, chunki email maydoniga qiymat berildi va signal ishletildi.

    def test_email_not_sent_if_no_email(self):
        """Email kiritilmese (None bolsa) xat ketpewi kerek"""
        mail.outbox = [] # Django test muhitida yuborilgan email xabarlarini saqlaydigan outbox ro'yxatini tozalaydi.
        # UserManager bul jerde email-dı None qıladı
        User.objects.create_user(
            phone_number="+998904445566",
            password="password123"
        )
        # Email None bolǵanı ushın signaldaǵı 'if instance.email' islemeydi
        self.assertEqual(len(mail.outbox), 0)

        """
        1-Bólim: Django Signals (Tiykarlar)
1-Soraw: Django Signals (Signallar) degen ne?
Juwap: Signallar — bul Djangonıń "Observer" (kuzatuvchi) modeli bolıp, ilovanıń bir bóliminde birer is (event) júz bergende (mısalı, model saqlanǵanda), basqa bólimine xabar jiberiw mexanizmi.
2-Soraw: Signaldıń 3 tiykarǵı qatnasıwshısı kim?
Juwap:
Sender (Jo'natuvchi): Signaldı jibergen obyekt (mısalı, User modeli).
Signal: Bolıp atırǵan waqıya (mısalı, post_save).
Receiver (Qabul qiluvchi): Signal kelgende isleytuǵın funksiya.
3-Soraw: post_save hám pre_save signallarınıń ayırmashılıǵı ne?
Juwap:
pre_save: Maǵlıwmat bazaga saqlanıwdan aldın isleydi.
post_save: Maǵlıwmat bazaga saqlanıp bolınǵannan keyin isleydi.
4-Soraw: post_save signalındaǵı created parametri ne ushın kerek?
Juwap: Bul True yamasa False qaytaradı. Eger jańa obyekt jaratılsa True, bar obyekt ózgertilse (update) False boladı.
5-Soraw: Signallardı qayerde dizimge alıw kerek hám ne ushın?
Juwap: apps.py faylındıǵı ready() metodı ishinde. Sebebi Django iske túskende signallardıń "qulaǵı" (receiver) ashıq bolıwı kerek.
2-Bólim: Kod boyınsha sorawlar
6-Soraw: @receiver(post_save, sender=User) dekoratorı ne xızmet etedi?
Juwap: Bul dekorator User modelinde post_save (saqlaw) isi júz beriwi menen, tómendegi funksiyanı iske túsir degen buyruqtı beredi.
7-Soraw: Signallardı isletiwdiń qanday qáwpi bar (Infinite loop)?
Juwap: Eger siz post_save funksiyasınıń ishinde taǵı sol modeldi .save() qılsańız, signal sheksiz qaytalana beredi (Infinite loop). Bunıń aldın alıw ushın save() qılǵanda shárt qoyıw yamasa created parametrinen paydalanıw kerek.
8-Soraw: Signallardıń qanday paydası bar?
Juwap: Kodtı ajıratıwǵa (Decoupling) járdem beredi. Mısalı: User modeli menen Email jiberiw kodı bir-birine aralasıp ketpeydi, hár biri óz ornında turadı.
3-Bólim: Testlew (Testing)
9-Soraw: setUp() metodı ne ushın kerek?
Juwap: Hár bir test funksiyası islewinen aldın ulıwma maǵlıwmatlardı (mısalı, User jaratıw, URL-lerdi tayarlaw) bir márte tayarlap alıw ushın isletiledi.
10-Soraw: reverse() funksiyası ne ushın isletiledi?
Juwap: URL mánzilin urls.py degi atı (name) boyınsha tawıp beriw ushın. Mısalı: reverse('user-list') -> '/api/users/'.
11-Soraw: mail.outbox testi ne ushın kerek?
Juwap: Django test waqtında haqıyqıy email jibermeydi. Olardı mail.outbox degen dizimge saladı. Biz sol dizimniń uzınlıǵı 1 me yamasa 0 me ekenin tekserip, xat ketti me degen sorawǵa juwap alamız.
12-Soraw: APITestCase hám TestCase ayırmashılıǵı ne?
Juwap:
TestCase: Standart Django testleri ushın (Database, Models).
APITestCase: Django Rest Framework (DRF) testleri ushın (API requests, status codes).
13-Soraw: Testte fail_silently=True nege kerek?
Juwap: Eger xat jiberiwde qáte shıqsa, programmanı toqtatıp qoymastan, qáteni jasırıp ketiw ushın.
4-Bólim: Qıyınlaw sorawlar (Pro dáreje)
14-Soraw: Nege signallardan hámme waqıt paydalanıw usınıs etilmeydi?
Juwap: Sebebi signallar "jasırın" isleydi. Úlken proektlerde qaysı kod qayerden islep atırǵanın tabıw qıyınlasıp ketedi (Hidden logic). Geyde modeldiń save() metodın override qılıw jaqsıraq bolıwı múmkin.
15-Soraw: Testte self.client.login() ne qıladı?
Juwap: Test dástúrine "bul paydalanıwshı sistemaga kirdi" dep xabar beredi. Usız biz IsAuthenticated (tek dizimnen ótkenler kirsin) degen jerlerdi testley almaymız.
Yadlaw ushın kishi "shpagalka":
Created = True -> Jańa adam keldi (Welcome email kerek).
Created = False -> Bar adam profilin jańaladı (Welcome email kerek emes).
mail.outbox = 0 -> Xat ketpedi.
mail.outbox = 1 -> 1 dana xat ketti.
401 Unauthorized -> Login qılınbaǵan.
201 Created -> Maǵlıwmat tabıslı jaratıldı.
Bulardı qaytalap turıń, Django boyınsha bilimlerińiz bekkemlenedi! Taqı basqa sorawlar bolsa, tartınbay sorań."""