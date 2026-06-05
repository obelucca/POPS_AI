FROM python:3.10

# Instala Supervisor e outras ferramentas básicas
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crie um arquivo de configuração para o Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# O CMD final do Dockerfile executa o Supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]