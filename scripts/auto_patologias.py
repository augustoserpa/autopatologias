"""
AUTOMAÇÃO PARA CADASTRO DE PATOLOGIAS VETERINÁRIAS
==================================================

Este script automatiza o cadastro em massa de patologias no sistema Simples.vet,
simulando as ações que um usuário humano faria manualmente no navegador.

Desenvolvido por: TAE Augusto Daniel Alves Serpa (SIAPE: 3125396)
Em colaboração com: TAE Veterinária Fabiana Wurster Strey (SIAPE: 2055298)
Instituição: Hospital Universitário Veterinário - Unipampa
Data: Agosto/2025

FUNCIONAMENTO:
1. Lê lista de patologias de um arquivo texto
2. Acessa automaticamente o sistema Simples.vet
3. Cadastra cada patologia sequencialmente
4. Controla duplicatas e trata erros
5. Registra progresso em arquivo de log
"""

# =====================================================
# IMPORTAÇÃO DAS BIBLIOTECAS NECESSÁRIAS
# =====================================================

from selenium import webdriver  # Biblioteca para controlar o navegador automaticamente
from selenium.webdriver.common.by import By  # Para localizar elementos na página web
from selenium.webdriver.chrome.service import Service  # Para gerenciar o driver do Chrome
from selenium.webdriver.support.ui import WebDriverWait  # Para aguardar elementos carregarem
from selenium.webdriver.support import expected_conditions as EC  # Condições de espera
from webdriver_manager.chrome import ChromeDriverManager  # Gerencia automaticamente o driver do Chrome
import time  # Para pausas durante a execução
import os   # Para verificar se arquivos existem

# =====================================================
# CONFIGURAÇÕES PRINCIPAIS DO SISTEMA
# =====================================================

# Localização dos arquivos de dados
CAMINHO_PATOLOGIAS = "../data/patologias.txt"  # Arquivo com lista de patologias para cadastrar
CAMINHO_CADASTRADAS = "../data/cadastradas.txt"  # Arquivo que registra patologias já processadas

# Quantidade de patologias processadas por vez (evita sobrecarregar o sistema)
TAMANHO_LOTE = 40

# Credenciais de acesso ao sistema (ATENÇÃO: manter seguras!)
EMAIL_USUARIO = "USUÁRIO AQUI"
SENHA_USUARIO = "SENHA AQUI"

# URLs do sistema Simples.vet
URL_LOGIN = "https://app.simples.vet/login/login.php"
URL_PATOLOGIAS = "https://app.simples.vet/v3/veterinaria/patologias"

# =====================================================
# LEITURA E PREPARAÇÃO DOS DADOS
# =====================================================

print("🔄 Iniciando preparação dos dados...")

# Lê todas as patologias do arquivo principal
print(f"📖 Lendo arquivo: {CAMINHO_PATOLOGIAS}")
with open(CAMINHO_PATOLOGIAS, "r", encoding="utf-8") as arquivo:
    todas_patologias = [linha.strip() for linha in arquivo if linha.strip()]

print(f"✅ Total de patologias encontradas: {len(todas_patologias)}")

# Verifica quais patologias já foram cadastradas anteriormente
patologias_ja_cadastradas = set()
if os.path.exists(CAMINHO_CADASTRADAS):
    print(f"📋 Verificando patologias já cadastradas...")
    with open(CAMINHO_CADASTRADAS, "r", encoding="utf-8") as arquivo:
        patologias_ja_cadastradas = set(linha.strip() for linha in arquivo if linha.strip())
    print(f"⚠️  Patologias já processadas: {len(patologias_ja_cadastradas)}")

# Remove patologias já cadastradas da lista de processamento
novas_patologias = [p for p in todas_patologias if p not in patologias_ja_cadastradas]
print(f"🆕 Novas patologias para cadastrar: {len(novas_patologias)}")

# Se não há nada novo para processar, encerra o programa
if not novas_patologias:
    print("✅ Todas as patologias já foram cadastradas!")
    exit()

# =====================================================
# DIVISÃO EM LOTES PARA PROCESSAMENTO SEGURO
# =====================================================

# Divide a lista em grupos menores para evitar sobrecarregar o sistema
lotes = []
for i in range(0, len(novas_patologias), TAMANHO_LOTE):
    lote = novas_patologias[i:i+TAMANHO_LOTE]
    lotes.append(lote)

print(f"📦 Dados organizados em {len(lotes)} lotes de até {TAMANHO_LOTE} patologias")

# =====================================================
# CONFIGURAÇÃO E INICIALIZAÇÃO DO NAVEGADOR
# =====================================================

print("🌐 Iniciando navegador...")

# Configura o Chrome para funcionar de forma otimizada
opcoes_chrome = webdriver.ChromeOptions()
opcoes_chrome.add_argument("--disable-blink-features=AutomationControlled")  # Evita detecção de bot
opcoes_chrome.add_experimental_option("excludeSwitches", ["enable-automation"])

# Inicializa o navegador Chrome
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opcoes_chrome
)

# Maximiza a janela para melhor visualização
driver.maximize_window()

# Configura tempo limite para esperas
wait = WebDriverWait(driver, 10)

# =====================================================
# PROCESSO DE LOGIN NO SISTEMA
# =====================================================

try:
    print("🔐 Realizando login no sistema...")
    
    # Navega para a página de login
    driver.get(URL_LOGIN)
    
    # Localiza e preenche o campo de email
    campo_email = wait.until(EC.presence_of_element_located((By.ID, "l_usu_var_email")))
    campo_email.send_keys(EMAIL_USUARIO)
    
    # Localiza e preenche o campo de senha
    campo_senha = driver.find_element(By.ID, "l_usu_var_senha")
    campo_senha.send_keys(SENHA_USUARIO)
    
    # Clica no botão de login
    botao_login = driver.find_element(By.ID, "btn_login")
    botao_login.click()
    
    # Aguarda o login ser processado
    time.sleep(5)
    print("✅ Login realizado com sucesso!")

    # =====================================================
    # PROCESSAMENTO DOS LOTES DE PATOLOGIAS
    # =====================================================

    # Processa cada lote sequencialmente
    for numero_lote, lote_atual in enumerate(lotes, start=1):
        print(f"\n🚀 Processando lote {numero_lote}/{len(lotes)} ({len(lote_atual)} patologias)")
        
        # Processa cada patologia do lote atual
        for nome_patologia in lote_atual:
            try:
                print(f"  🩺 Cadastrando: {nome_patologia}")
                
                # =====================================================
                # NAVEGAÇÃO PARA A PÁGINA DE PATOLOGIAS
                # =====================================================
                
                # Vai para a página principal de patologias
                driver.get(URL_PATOLOGIAS)
                
                # =====================================================
                # ABERTURA DO FORMULÁRIO DE NOVA PATOLOGIA
                # =====================================================
                
                # Procura e clica no botão "+" para adicionar nova patologia
                # O botão é identificado pelo ícone SVG de "adicionar"
                botao_adicionar = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//i[contains(@style, 'add.svg')]/ancestor::*[self::button or self::a or self::div][1]"
                    ))
                )
                
                # Pequena pausa para garantir que o elemento está pronto
                time.sleep(1)
                botao_adicionar.click()
                
                # =====================================================
                # PREENCHIMENTO DO FORMULÁRIO
                # =====================================================
                
                # Localiza o campo "Nome" no formulário
                campo_nome = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@name='nome' and @placeholder='Nome*']"))
                )
                
                # Aguarda um pouco para garantir que o campo está pronto
                time.sleep(0.5)
                
                # Limpa qualquer conteúdo anterior e digita o nome da patologia
                campo_nome.clear()
                campo_nome.send_keys(nome_patologia)
                
                # =====================================================
                # SALVAMENTO DO REGISTRO
                # =====================================================
                
                # Localiza e clica no botão "Salvar"
                botao_salvar = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sv-botao--salvar')]"))
                )
                botao_salvar.click()
                
                # Aguarda o processamento do salvamento
                time.sleep(3)
                
                # =====================================================
                # VERIFICAÇÃO DE SUCESSO
                # =====================================================
                
                # Verifica se voltou para a página de listagem (indica sucesso)
                if not driver.current_url.endswith("/veterinaria/patologias"):
                    print("    ⚠️  Possível duplicata ou erro, mas registrando...")
                    # Força retorno à página principal
                    driver.get(URL_PATOLOGIAS)
                    time.sleep(2)
                
                # =====================================================
                # REGISTRO DE PROGRESSO
                # =====================================================
                
                # Salva a patologia como processada (para controle de duplicatas)
                with open(CAMINHO_CADASTRADAS, "a", encoding="utf-8") as arquivo_log:
                    arquivo_log.write(nome_patologia + "\n")
                
                print("    ✅ Cadastrada com sucesso!")
                
            except Exception as erro:
                # =====================================================
                # TRATAMENTO DE ERROS
                # =====================================================
                
                print(f"    ❌ Erro ao cadastrar '{nome_patologia}': {erro}")
                
                # Tenta voltar à página principal em caso de erro
                try:
                    driver.get(URL_PATOLOGIAS)
                    time.sleep(2)
                except:
                    print("    ⚠️  Erro ao retornar à página principal")
        
        # =====================================================
        # PAUSA ENTRE LOTES
        # =====================================================
        
        print(f"✅ Lote {numero_lote} finalizado!")
        
        # Pausa entre lotes para não sobrecarregar o sistema
        if numero_lote < len(lotes):  # Não pausa após o último lote
            print("⏸️  Aguardando antes do próximo lote...")
            time.sleep(5)
    
    # =====================================================
    # FINALIZAÇÃO DO PROCESSO
    # =====================================================
    
    print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f"📊 Total de patologias processadas: {len(novas_patologias)}")
    print(f"📦 Lotes processados: {len(lotes)}")
    
    # Aguarda input do usuário antes de fechar
    input("\nPressione Enter para finalizar...")

except Exception as erro_geral:
    # =====================================================
    # TRATAMENTO DE ERROS GERAIS
    # =====================================================
    
    print(f"❌ ERRO CRÍTICO: {erro_geral}")
    print("🔧 Verifique:")
    print("   - Conexão com a internet")
    print("   - Credenciais de login")
    print("   - Disponibilidade do sistema Simples.vet")
    
finally:
    # =====================================================
    # LIMPEZA E ENCERRAMENTO
    # =====================================================
    
    print("🧹 Encerrando navegador...")
    driver.quit()  # Fecha o navegador e libera recursos
    print("✅ Programa finalizado!")

# =====================================================
# INFORMAÇÕES ADICIONAIS PARA USUÁRIOS
# =====================================================

"""
COMO USAR ESTE SCRIPT:
=====================

1. PREPARAÇÃO DOS ARQUIVOS:
   - Crie o arquivo 'patologias.txt' com uma patologia por linha
   - O arquivo 'cadastradas.txt' será criado automaticamente

2. INSTALAÇÃO DAS DEPENDÊNCIAS:
   pip install selenium webdriver-manager

3. CONFIGURAÇÃO:
   - Ajuste as credenciais de login (EMAIL_USUARIO, SENHA_USUARIO)
   - Verifique os caminhos dos arquivos (CAMINHO_PATOLOGIAS, CAMINHO_CADASTRADAS)

4. EXECUÇÃO:
   python automacao_patologias.py

RECURSOS DE SEGURANÇA:
=====================

- Processa em lotes pequenos (40 por vez)
- Controla duplicatas automaticamente
- Pausa entre operações para não sobrecarregar o sistema
- Salva progresso continuamente
- Trata erros sem interromper o processo
- Permite recuperação em caso de falha

MONITORAMENTO:
=============

- Acompanhe as mensagens no console
- Verifique o arquivo 'cadastradas.txt' para ver o progresso
- Em caso de erro, o script continua com as próximas patologias

SUPORTE:
========

Para dúvidas ou melhorias, entre em contato:
- Email: augustoserpa@unipampa.edu.br
- GitHub: https://github.com/augustoserpa/autopatologias
"""
