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

def simulate_profile_visit(cl, user_id, delay_range=(10, 20)):
    print(f"Acessando o perfil do usuário {user_id}...")
    try:
        user_info = cl.user_info(user_id)
        print(f"Perfil: {user_info.username} | Seguidores: {user_info.follower_count}")
    except Exception as e:
        print(f"Erro ao acessar perfil do usuário {user_id}: {e}")
    duration = random.uniform(*delay_range)
    print(f"Simulando visita ao perfil por {duration:.2f} segundos...")
    time.sleep(duration)
    return duration

def simulate_feed_scrolling(delay_range=(10, 20)):
    duration = random.uniform(*delay_range)
    print(f"Simulando rolagem do feed por {duration:.2f} segundos...")
    time.sleep(duration)
    return duration

def simulate_typing(delay_range=(5, 10)):
    duration = random.uniform(*delay_range)
    print(f"Simulando digitação por {duration:.2f} segundos...")
    time.sleep(duration)
    return duration

def simulate_random_behavior(cl, user_id, total_target=60):
    """
    Simula um comportamento aleatório para um usuário.
    O script escolhe aleatoriamente entre as ações:
      - Visitar o perfil
      - Rolagem do feed
      - Digitação
    Nem todas as ações precisam ocorrer a cada execução.
    Ao final, se o tempo total gasto for inferior a 'total_target' segundos,
    aguarda o tempo restante.
    """
    actions = [
        ("visita", lambda: simulate_profile_visit(cl, user_id)),
        ("rolagem", simulate_feed_scrolling),
        ("digitação", simulate_typing)
    ]
    
    num_actions = random.randint(1, len(actions))
    selected_actions = random.sample(actions, num_actions)
    
    total_time = 0
    print(f"\nIniciando simulação de comportamento (alvo: {total_target} segundos). Ações selecionadas: {[name for name, _ in selected_actions]}")
    for name, action in selected_actions:
        t = action()
        total_time += t
    
    if total_time < total_target:
        extra = total_target - total_time
        print(f"Pausa adicional de {extra:.2f} segundos para completar {total_target} segundos de simulação.")
        time.sleep(extra)
        total_time += extra
        
    print(f"Simulação completa: {total_time:.2f} segundos.\n")
    return total_time

if __name__ == "__main__":
    cl = login()
    followers = get_followers(cl, TARGET_USER, amount=100)
    
    batch_size = 20  # Processa os seguidores em lotes de 20
    for i in range(0, len(followers), batch_size):
        batch = followers[i:i+batch_size]
        for user_id in batch:
            try:
                # Executa a simulação de comportamento aleatório (aproximadamente 1 minuto)
                simulate_random_behavior(cl, user_id, total_target=60)
                cl.user_follow(user_id)
                print(f"Seguiu: {user_id}")
                # Aguarda entre 1 a 2 minutos (60 a 120 segundos) após seguir
                post_follow_delay = random.uniform(60, 120)
                print(f"Pausa pós-seguimento de {post_follow_delay:.2f} segundos\n")
                time.sleep(post_follow_delay)
            except Exception as e:
                print(f"\nErro ao seguir {user_id}: {e}")
                error_delay = random.uniform(120, 180)
                print(f"Pausa de {error_delay:.2f} segundos devido ao erro\n")
                time.sleep(error_delay)
        batch_delay = random.uniform(1200, 2400)
        print(f"\nAguardando {batch_delay/60:.2f} minutos antes do próximo lote\n")
        time.sleep(batch_delay)
    print("Fim do script")