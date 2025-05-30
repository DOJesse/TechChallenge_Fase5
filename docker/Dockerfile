FROM python:3.9-slim

# Evita buffering de logs
ENV PYTHONUNBUFFERED=1

# Define diretório de trabalho
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto
COPY . .

# Expõe a porta da API
EXPOSE 5000

# Comando de inicialização da API
CMD ["python", "-u", "src/api/api.py"]