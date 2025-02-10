import time
from instagrapi import Client

USERNAME = "seu_usuario"
PASSWORD = "sua_senha"
TARGET_USER = "perfil_alvo"

def login():
    cl = Client()
    cl.login(USERNAME, PASSWORD)
    return cl

def get_followers(cl, username, amount=100):
    user_id = cl.user_id_from_username(username)
    followers = cl.user_followers(user_id, amount=amount)
    return list(followers.keys())

if __name__ == "__main__":
    cl = login()
    followers = get_followers(cl, TARGET_USER, amount=100)
    
    for i in range(0, len(followers), 20):
        batch = followers[i:i+20]
        for user_id in batch:
            try:
                cl.user_follow(user_id)
                print(f"Seguiu: {user_id}")
                time.sleep(30)  # Pequeno intervalo para evitar detecção
            except Exception as e:
                print(f"Erro ao seguir {user_id}: {e}")
        print("Aguardando 15 minutos...")
        time.sleep(900)  # Espera 15 minutos antes do próximo lote
    print("Concluído!")