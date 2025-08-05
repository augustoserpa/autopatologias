from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# === Configurações ===
CAMINHO_PATOLOGIAS = "../data/patologias.txt"
CAMINHO_CADASTRADAS = "../data/cadastradas.txt"
TAMANHO_LOTE = 40

# === Lê a lista original ===
with open(CAMINHO_PATOLOGIAS, "r", encoding="utf-8") as f:
    todas = [linha.strip() for linha in f if linha.strip()]

# === Lê o arquivo de já cadastradas (se existir) ===
if os.path.exists(CAMINHO_CADASTRADAS):
    with open(CAMINHO_CADASTRADAS, "r", encoding="utf-8") as f:
        ja_cadastradas = set(linha.strip() for linha in f if linha.strip())
else:
    ja_cadastradas = set()

# === Remove duplicadas ===
novas_patologias = [p for p in todas if p not in ja_cadastradas]

print(f"\n🧾 Total de novas patologias a cadastrar: {len(novas_patologias)}")

# === Fraciona em lotes ===
lotes = [novas_patologias[i:i+TAMANHO_LOTE] for i in range(0, len(novas_patologias), TAMANHO_LOTE)]

# === Inicia o navegador ===
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
wait = WebDriverWait(driver, 10)

try:
    # Login
    driver.get("https://app.simples.vet/login/login.php")
    wait.until(EC.presence_of_element_located((By.ID, "l_usu_var_email"))).send_keys("augustoserpa@unipampa.edu.br")
    driver.find_element(By.ID, "l_usu_var_senha").send_keys("38659103")
    driver.find_element(By.ID, "btn_login").click()
    time.sleep(5)

    # Processa cada lote
    for i_lote, lote in enumerate(lotes, start=1):
        print(f"\n🚀 Lote {i_lote}/{len(lotes)} - {len(lote)} patologias")

        for nome_patologia in lote:
            try:
                print(f"🩺 {nome_patologia}")

                # Vai para a página de patologias
                driver.get("https://app.simples.vet/v3/veterinaria/patologias")

                # Espera o botão "+" aparecer e estar visível
                botao_add = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//i[contains(@style, 'add.svg')]/ancestor::*[self::button or self::a or self::div][1]"
                    ))
                )
                time.sleep(1)
                botao_add.click()

                # Espera o campo de nome estar interativo
                campo_nome = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@name='nome' and @placeholder='Nome*']"))
                )
                time.sleep(0.5)
                campo_nome.clear()
                campo_nome.send_keys(nome_patologia)

                # Clica em salvar
                botao_salvar = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sv-botao--salvar')]"))
                )
                botao_salvar.click()
                time.sleep(3)

                # Verifica se voltou pra página de patologias
                if not driver.current_url.endswith("/veterinaria/patologias"):
                    print("⚠️ Já existe ou erro, mas registrando mesmo assim.")
                    driver.get("https://app.simples.vet/v3/veterinaria/patologias")
                    time.sleep(2)

                # Registra como já processado
                with open(CAMINHO_CADASTRADAS, "a", encoding="utf-8") as f:
                    f.write(nome_patologia + "\n")

            except Exception as e:
                print(f"❌ Erro ao processar '{nome_patologia}': {e}")
                driver.get("https://app.simples.vet/v3/veterinaria/patologias")
                time.sleep(2)

        print(f"⏸️ Lote {i_lote} finalizado. Aguardando antes de continuar...")
        time.sleep(5)  # pausa entre lotes

    print("\n✅ Fim do processo. Todas as patologias foram tentadas.")

    input("Pressione Enter para sair...")

finally:
    driver.quit()
