import time
import os
import random
import pyotp  # Para geração automática do código 2FA
from instagrapi import Client

# Configurações de acesso e 2FA
USERNAME = "matheusteste03"
PASSWORD = "testeinsta123"
TARGET_USER = "instagram"
# Substitua pelo seu secret 2FA (em base32) se usar o método TOTP:
TWO_FA_SECRET = "YOUR_2FA_SECRET"  

def get_totp_code(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()

def login():
    # Se necessário, você pode configurar um proxy (exemplo):
    # cl = Client(proxy="http://IP:PORTA")
    cl = Client()
    
    # Tenta carregar a sessão salva para evitar múltiplos logins
    if os.path.exists("session.json"):
        try:
            cl.load_settings("session.json")
        except Exception as e:
            print("Erro ao carregar a sessão:", e)
    
    # Gera o código 2FA atual automaticamente
    current_code = get_totp_code(TWO_FA_SECRET)
    print("Código 2FA gerado:", current_code)
    
    try:
        cl.login(USERNAME, PASSWORD, verification_code=current_code)
    except Exception as e:
        print("Erro durante o login:", e)
        # Caso o código esteja expirado ou inválido, solicita o código manualmente:
        new_code = input("Digite o código 2FA atualizado: ").strip()
        cl.login(USERNAME, PASSWORD, verification_code=new_code)
    
    cl.dump_settings("session.json")
    return cl

def get_followers(cl, username, amount=100):
    user_id = cl.user_id_from_username(username)
    followers = cl.user_followers(user_id, amount=amount)
    return list(followers.keys())

def simulate_human_behavior():
    """
    Função para simular ações de um usuário real, adicionando pequenos atrasos aleatórios.
    """
    additional_delay = random.uniform(5, 15)
    print(f"Simulando comportamento humano... aguardando {additional_delay:.2f} segundos")
    time.sleep(additional_delay)

if __name__ == "__main__":
    cl = login()
    followers = get_followers(cl, TARGET_USER, amount=100)
    
    batch_size = 20  # Número de ações em cada lote
    for i in range(0, len(followers), batch_size):
        batch = followers[i:i+batch_size]
        for user_id in batch:
            try:
                cl.user_follow(user_id)
                print(f"Seguiu: {user_id}")
                simulate_human_behavior()
                # Intervalo aleatório entre 45 e 90 segundos para a próxima ação
                delay = random.uniform(45, 90)
                print(f"Aguardando {delay:.2f} segundos antes da próxima ação.")
                time.sleep(delay)
            except Exception as e:
                print(f"Erro ao seguir {user_id}: {e}")
                # Em caso de erro, aguarda um intervalo maior para evitar bloqueios
                delay_error = random.uniform(60, 120)
                print(f"Aguardando {delay_error:.2f} segundos devido ao erro.")
                time.sleep(delay_error)
        # Intervalo aleatório entre os lotes, entre 10 e 20 minutos
        batch_delay = random.uniform(600, 1200)
        print(f"Aguardando {batch_delay/60:.2f} minutos antes de iniciar o próximo lote.")
        time.sleep(batch_delay)
    print("Fim do script.")