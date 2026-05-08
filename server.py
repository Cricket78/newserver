import http.server
import socketserver
import os
import json
from groq import Groq

# 1. Динамічне визначення порту (Критично для роботи на Alwaysdata) [1, 3]
# Сервер Alwaysdata сам призначить порт через перемінну оточення PORT.
PORT = int(os.environ.get("PORT", 8100))

# 2. API-ключі (Їх потрібно додати в панелі Alwaysdata: Web > Sites > [Ваш сайт] > Environment variables) 
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GUARDIAN_API_KEY = os.environ.get("GUARDIAN_API_KEY")

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Якщо користувач заходить на головну сторінку, відкриваємо news_app.html
        if self.path == '/':
            self.path = 'news_app.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        # Маршрут для аналізу новин через Groq AI (виклик з вашого JS на фронтенді)
        if self.path == '/analyze':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Перевірка наявності ключа Groq
            if not GROQ_API_KEY:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Error: GROQ_API_KEY is missing in server environment.")
                return

            # Ініціалізація Groq AI клієнта
            try:
                client = Groq(api_key=GROQ_API_KEY)
                # Тут розмістіть ваш код обробки тексту або запитів до моделі
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {"status": "success", "message": "Backend connected successfully"}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Server Error: {str(e)}".encode())

# 3. Запуск сервера
if __name__ == "__main__":
    # Використовуємо "0.0.0.0", щоб Alwaysdata міг перенаправляти зовнішній трафік на ваш скрипт 
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
        print(f"Сервер запущено: http://0.0.0.0:{PORT}")
        httpd.serve_forever()