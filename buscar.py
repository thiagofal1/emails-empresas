import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random

# Função para buscar as informações no site usando o CNPJ
def buscar_info_cnpj(cnpj, user_agent):
    url = f"https://cnpja.com/office/{cnpj}"
    headers = {"User-Agent": user_agent}  # Definir User-Agent
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        email, telefone = None, None

        email_span = soup.find("span", text="E-mail")
        if email_span:
            email_div = email_span.find_next("div")
            if email_div:
                email = email_div.find("span").text.strip()

        telefone_span = soup.find("span", text="Telefone")
        if telefone_span:
            telefone_div = telefone_span.find_next("div")
            if telefone_div:
                telefone = telefone_div.find("span").text.strip()

        return None if email == "-" or not email else email, None if telefone == "-" or not telefone else telefone
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar CNPJ {cnpj}: {e}")
        return None, None

# Lista de User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Conectar ao banco SQLite
conn = sqlite3.connect("emails_empresas.db")
cursor = conn.cursor()

# Buscar apenas CNPJs que tenham email ou telefone como NULL
cursor.execute("SELECT cnpj FROM empresa WHERE email IS NULL OR telefone IS NULL")
empresas = cursor.fetchall()

# Loop para buscar informações
for index, empresa in enumerate(empresas):
    if index % 1 == 0:
        user_agent = random.choice(user_agents)  # Mudar User-Agent a cada 2 buscas
    
    cnpj = empresa[0]
    print(f"Buscando informações para o CNPJ: {cnpj} | User-Agent: {user_agent}")
    
    email, telefone = buscar_info_cnpj(cnpj, user_agent)
    if email or telefone:
        cursor.execute("UPDATE empresa SET email = ?, telefone = ? WHERE cnpj = ?", (email, telefone, cnpj))
        conn.commit()
        print(f"✅ Atualizado: {cnpj} | Email: {email} | Telefone: {telefone}")
    else:
        print(f"⚠️ Nenhuma informação encontrada para {cnpj}")
    
    if index % 2 == 1:
        time.sleep(5 + random.uniform(0, 10))  # Esperar apenas após 2 buscas

conn.close()
