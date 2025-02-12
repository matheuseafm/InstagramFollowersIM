import time
import os
import random
from instagrapi import Client

USERNAME = ""
PASSWORD = ""
TARGET_USER = "instagram"

def login():
    cl = Client()
    
    if os.path.exists("session.json"):
        try:
            cl.load_settings("session.json")
        except Exception as e:
            print("Erro ao carregar a sessão:", e)
    try:
        cl.login(USERNAME, PASSWORD, verification_code="<2FA CODE HERE>")
    except Exception as e:
        print("Erro durante o login:", e)
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

def simulate_profile_visit(cl, user_id):
    """
    Simula a visita ao perfil do usuário, buscando algumas informações
    e aguardando um tempo aleatório para simular a leitura do perfil.
    """
    print(f"Acessando o perfil do usuário {user_id}...")
    try:
        user_info = cl.user_info(user_id)
        print(f"Nome: {user_info.username}, Seguidores: {user_info.follower_count}")
    except Exception as e:
        print(f"Erro ao acessar perfil do usuário {user_id}: {e}")
    delay = random.uniform(3, 10)
    print(f"Simulando leitura do perfil por {delay:.2f} segundos...")
    time.sleep(delay)

def simulate_feed_scrolling():
    """
    Simula a ação de rolar o feed, com um pequeno atraso.
    """
    delay = random.uniform(2, 5)
    print(f"Simulando rolagem do feed por {delay:.2f} segundos...")
    time.sleep(delay)

def simulate_typing():
    """
    Simula a digitação (por exemplo, de um comentário), apenas com atraso.
    """
    delay = random.uniform(1, 3)
    print(f"Simulando digitação por {delay:.2f} segundos...")
    time.sleep(delay)

def simulate_complete_human_behavior(cl, user_id):
    """
    Executa uma série de simulações para imitar o comportamento humano:
      - Visita ao perfil do usuário
      - Rolagem do feed
      - Possível digitação (simulação)
      - Pausa adicional para imitar uma ação realista
    """
    simulate_profile_visit(cl, user_id)
    simulate_feed_scrolling()
    # Com 50% de chance, simula digitação
    if random.choice([True, False]):
        simulate_typing()
    additional_delay = random.uniform(5, 15)
    print(f"Pausa adicional para simulação completa: {additional_delay:.2f} segundos")
    time.sleep(additional_delay)

if __name__ == "__main__":
    cl = login()
    followers = get_followers(cl, TARGET_USER, amount=100)
    
    batch_size = 20  # Processa os seguidores em lotes de 20
    for i in range(0, len(followers), batch_size):
        batch = followers[i:i+batch_size]
        for user_id in batch:
            try:
                # Simula um comportamento completo antes de seguir o usuário
                simulate_complete_human_behavior(cl, user_id)
                cl.user_follow(user_id)
                print(f"Seguiu: {user_id}")
                # Pausa após seguir para imitar um comportamento natural
                post_follow_delay = random.uniform(10, 30)
                print(f"Pausa pós-seguimento de {post_follow_delay:.2f} segundos")
                time.sleep(post_follow_delay)
            except Exception as e:
                print(f"Erro ao seguir {user_id}: {e}")
                error_delay = random.uniform(60, 120)
                print(f"Pausa de {error_delay:.2f} segundos devido ao erro")
                time.sleep(error_delay)
        # Pausa maior entre os lotes de seguidores
        batch_delay = random.uniform(600, 1200)
        print(f"Aguardando {batch_delay/60:.2f} minutos antes do próximo lote")
        time.sleep(batch_delay)
    print("Fim do script")