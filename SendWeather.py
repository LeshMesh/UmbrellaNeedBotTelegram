import requests

body = {'q': "И", 'limit': 1, 'appid': "d491912f4c590c59b48e8f977324a8e2"}
r = requests.get("http://api.openweathermap.org/geo/1.0/direct", params=body)
r_dict = r.json()[0]
lat = r_dict['lat']
lon = r_dict['lon']
print(lat, lon)
print(r_dict['local_names']['ru'])

body2 = {'lat': lat, 'lon': lon}
head = {'X-Yandex-API-Key': "dfc4c800-e690-42c6-be72-9113abcdbeca"}
r2 = requests.get("https://api.weather.yandex.ru/v2/informers", params=body2, headers=head)
print(r2.status_code)
print(r2.json()['fact']['temp'])