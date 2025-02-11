import time
import os
from instagrapi import Client

USERNAME = "iknowwhatudid_123"
PASSWORD = "mem040503"
TARGET_USER = "instagram"

def login():
    cl = Client()
    
    # Tenta carregar a sessão, se existir
    if os.path.exists("session.json"):
        try:
            cl.load_settings("session.json")
        except Exception as e:
            print("Erro ao carregar a sessão:", e)
    
    # Tenta realizar o login com um código 2FA fixo (se você tiver um código válido no momento)
    try:
        # Substitua "<2FA CODE HERE>" por um código válido ou deixe-o vazio para forçar a exceção
        cl.login(USERNAME, PASSWORD, verification_code="<2FA CODE HERE>")
    except Exception as e:
        print("Erro durante o login:", e)
        # Se o código não for aceito, solicita manualmente o código 2FA atualizado:
        new_code = input("Digite o código 2FA atual: ").strip()
        try:
            cl.login(USERNAME, PASSWORD, verification_code=new_code)
        except Exception as e2:
            print("Novo erro durante o login:", e2)
            raise e2

    cl.dump_settings("session.json")
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
                time.sleep(50)  # Ajuste o tempo conforme necessário
            except Exception as e:
                print(f"Erro ao seguir {user_id}: {e}")
        print("Aguardando 15 minutos...")
        time.sleep(900)
