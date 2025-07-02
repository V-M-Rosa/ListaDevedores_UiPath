import os
import time
import shutil
import pandas as pd
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, StringVar, BooleanVar, Checkbutton
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


# URL e caminhos
URL = "https://www.listadevedores.pgfn.gov.br/"
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "Lista_PGFN")
LOG_FILE = os.path.join(DOWNLOAD_DIR, "log_execucao.txt")

# Função de log
def escrever_log(mensagem):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {mensagem}\n")

# Função principal 
def iniciar_automacao():
    valor_maximo = valor_maximo_var.get().replace(",", "").strip()
    usar_estado = usar_estado_var.get()
    estado = estado_var.get().strip().upper() if usar_estado else ""

    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    start_time = datetime.now()

    # Limpa pasta de download
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)
    os.makedirs(DOWNLOAD_DIR)

    escrever_log("Início da execução")
    escrever_log(f"Filtro: valor_maximo={valor_maximo}, estado={estado if usar_estado else 'N/A'}")

    try:
        driver.get(URL)

        # Preencher valor
        campo_valor = wait.until(EC.presence_of_element_located((By.ID, "faixaMaximaInput")))
        campo_valor.clear()
        campo_valor.send_keys(valor_maximo)

        # Preencher estado 
        if usar_estado:
            select_estado = Select(wait.until(EC.presence_of_element_located((By.ID, "ufInput"))))
            select_estado.select_by_value(estado)

        # Clicar em Consultar
        botao = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Consultar')]")))
        driver.execute_script("arguments[0].click();", botao)
        escrever_log("Consulta enviada")

    except Exception as e:
        escrever_log(f"Erro durante automação: {str(e)}")
        driver.quit()
        raise

    
# Habilita/desabilita campo do estado
def alternar_estado():
    if usar_estado_var.get():
        entry_estado.config(state="normal")
    else:
        entry_estado.config(state="disabled")

# Interface gráfica
janela = Tk()
janela.title("Consulta Devedores")

largura_janela = 400
altura_janela = 250
largura_tela = janela.winfo_screenwidth()
altura_tela = janela.winfo_screenheight()
pos_x = (largura_tela // 2) - (largura_janela // 2)
pos_y = (altura_tela // 2) - (altura_janela // 2)
janela.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

Label(janela, text="Valor Máximo da Dívida (ex: 350000)").pack()
valor_maximo_var = StringVar()
Entry(janela, textvariable=valor_maximo_var).pack()

usar_estado_var = BooleanVar()
Checkbutton(janela, text="Filtrar por Estado", variable=usar_estado_var, command=alternar_estado).pack()

Label(janela, text="Estado (ex: SC)").pack()
estado_var = StringVar()
entry_estado = Entry(janela, textvariable=estado_var, state="disabled")
entry_estado.pack()

Button(janela, text="Consultar", command=iniciar_automacao).pack(pady=10)

janela.mainloop()
