import time
from instagrapi import Client

# Configurações de login
USERNAME = "seu_usuario"
PASSWORD = "sua_senha"
TARGET_USER = "perfil_alvo"  

# Handler para desafios de autenticação
def challenge_handler(username, choice):
    code = input(f"Digite o código de verificação enviado por {choice}: ")
    return code

# Inicializar cliente
def login():
    cl = Client()
    cl.challenge_code_handler = challenge_handler  # Define o handler para desafios
    try:
        cl.load_settings("session.json")  # Tenta carregar sessão salva
        cl.login(USERNAME, PASSWORD)
    except Exception:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings("session.json")  # Salva sessão para reutilização
    return cl

# Obter seguidores do perfil
def get_followers(cl, username, amount=100):
    user_id = cl.user_id_from_username(username)
    followers = cl.user_followers(user_id, amount=amount)
    return list(followers.keys())

# Seguir seguidores
if __name__ == "__main__":
    cl = login()
    followers = get_followers(cl, TARGET_USER, amount=100)
    
    for i in range(0, len(followers), 20):
        batch = followers[i:i+20]
        for user_id in batch:
            try:
                cl.user_follow(user_id)
                print(f"Seguiu: {user_id}")
                time.sleep(50)  # Pequeno intervalo para evitar detecção
            except Exception as e:
                print(f"Erro ao seguir {user_id}: {e}")
        print("Aguardando 15 minutos...")
        time.sleep(900)  # Espera 15 minutos antes do próximo lote