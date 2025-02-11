import time
from instagrapi import Client

USERNAME = "matheusteste03"
PASSWORD = "testeinsta123"
TWO_FA_CODE = "<2FA CODE HERE>"  
TARGET_USER = "instagram"

def login():
    cl = Client()
    try:
        cl.load_settings("session.json")
        cl.login(USERNAME, PASSWORD, verification_code=TWO_FA_CODE)
    except Exception as e:
        print("Erro durante o login com sessão salva, tentando novamente:", e)
        cl.login(USERNAME, PASSWORD, verification_code=TWO_FA_CODE)
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
                time.sleep(50) 
            except Exception as e:
                print(f"Erro ao seguir {user_id}: {e}")
        print("Aguardando 15 minutos antes de seguir mais pessoas...")
        time.sleep(900)
    print("Fim do script")