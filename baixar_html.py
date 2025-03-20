import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3
import time
import os

# Listas dinâmicas de estados, categorias e tamanhos
estados = ['ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mt', 'ms', 'mg', 'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn', 'rs', 'ro', 'rr', 'sc', 'sp', 'se', 'to']
categorias = ['logistica', 'marketing', 'servicos-financeiros', 'consultoria', 'hospital', 'clinica', 'estoque']
tamanhos = ['grande', 'pequena', 'media', 'micro']

# Configuração do WebDriver (Certifique-se de ter o ChromeDriver instalado)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Executa o navegador em segundo plano (opcional)
driver = webdriver.Chrome(options=options)

# Conectar ao banco SQLite
conn = sqlite3.connect("emails_empresas.db")
cursor = conn.cursor()
conn.commit()

# Caminho da pasta onde os arquivos HTML serão salvos
save_directory = r"E:\BlueSky Project\ASE\sistemas\Emails_auto\urls"

# Certifique-se de que o diretório existe
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Iterar sobre estados, categorias e tamanhos
for estado in estados:
    for categoria in categorias:
        for tamanho in tamanhos:
            # Montar a URL dinamicamente
            url = f"https://www.econodata.com.br/empresas/{estado}/busca-{categoria}/{tamanho}"

            print(f"Abrindo URL: {url}")

            # Fazer a requisição HTTP para a página
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"})

            # Criar um objeto BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Remover CSS, JS, Imagens e Comentários
            for tag in soup(["script", "style", "img", "link", "meta"]):
                tag.decompose()

            # Remover comentários
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.startswith("<!--")):
                comment.extract()

            # Salvar o HTML limpo na pasta especificada
            file_name = f"pagina_econodata_{estado}_{categoria}_{tamanho}.html"
            file_path = os.path.join(save_directory, file_name)

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(soup.prettify())

            print(f"HTML limpo salvo como '{file_path}'.")

            # Abrir a página salva localmente com Selenium
            driver.get(f"file:///{file_path}")  # Abrir o arquivo localmente com Selenium
            time.sleep(3)

            # Extrair empresas pelos links (href)
            empresas_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/consulta-empresa/')]")

            for link in empresas_links:
                href = link.get_attribute("href")  # Obtém o link completo
                href_split = href.split("/")[-1]   # Pega só a parte final do link (CNPJ + Nome)
                
                # Separar CNPJ e Nome da Empresa
                cnpj, nome = href_split.split("-", 1)
                cnpj = cnpj.strip()
                nome = nome.replace("-", " ").strip()  # Formatar nome corretamente

                try:
                    cursor.execute("INSERT INTO empresa (empresa_name, cnpj) VALUES (?, ?)", (nome, cnpj))
                    conn.commit()
                    print(f"✅ Adicionado: {nome} - {cnpj}")
                except sqlite3.IntegrityError:
                    print(f"⚠️ Já existe: {nome} - {cnpj}")

# Fechar conexões
conn.close()
driver.quit()

print("Processo concluído! 🚀")
