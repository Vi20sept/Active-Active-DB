#Working for Sql db

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    gnupg \
    unixodbc-dev \
    apt-transport-https \
    ca-certificates

# Microsoft repo
RUN mkdir -p /etc/apt/keyrings \
    && curl https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg

RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" \
    > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Python setup
COPY requirements.txt .


RUN pip install --upgrade pip \
    && pip install gunicorn flask pyodbc
    

ENV PATH="/usr/local/bin:$PATH"

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]



#Working for CosmosDb

# FROM python:3.9-slim

# WORKDIR /app

# COPY requirements.txt .

# RUN pip install --upgrade pip \
#     && pip install -r requirements.txt

# COPY . .

# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]