import requests, json

URL = "http://192.168.0.168:8000/api/v1/weather-check"


lat = 50.103
lon = 14.403

response = requests.post(URL, json={"latitude": lat, "longitude": lon})
data = response.json()

print(json.dumps(data,indent=4))

