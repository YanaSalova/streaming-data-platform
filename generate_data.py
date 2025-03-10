import random
import requests
import time


names = ["Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace"]
countries = ["USA", "Canada", "UK", "Germany", "France", "Spain", "Italy"]


url = "http://127.0.0.1:8000/users"

def generate_random_user():
    """Функция для генерации случайного пользователя"""
    return {
        "name": random.choice(names),
        "country": random.choice(countries)
    }

def send_user_data(user_data):
    """Отправляет данные пользователя через POST-запрос на API"""
    response = requests.post(url, json=user_data)
    if response.status_code == 200:
        print("Создан пользователь:", response.json())
    else:
        print("Ошибка создания пользователя:", response.text)

if __name__ == "__main__":
    for _ in range(10):
        user = generate_random_user()
        send_user_data(user)
        time.sleep(1)  
