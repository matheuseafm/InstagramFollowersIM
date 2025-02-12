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
    print(f"Simulando visita ao perfil por {duration:.2f} seg...")
    time.sleep(duration)
    return duration

def simulate_feed_scrolling(delay_range=(10, 20)):
    duration = random.uniform(*delay_range)
    print(f"Simulando rolagem do feed por {duration:.2f} seg...")
    time.sleep(duration)
    return duration

def simulate_typing(delay_range=(5, 10)):
    duration = random.uniform(*delay_range)
    print(f"Simulando digitação por {duration:.2f} seg...")
    time.sleep(duration)
    return duration

def simulate_view_stories(delay_range=(10, 30)):
    duration = random.uniform(*delay_range)
    print(f"Simulando visualização de stories por {duration:.2f} seg...")
    time.sleep(duration)
    return duration

def simulate_like_post(cl, user_id):
    try:
        medias = cl.user_medias(user_id, amount=3)
        if medias:
            media = random.choice(medias)
            cl.media_like(media.id)
            duration = random.uniform(5, 10)
            print(f"Curti a publicação {media.id} do usuário {user_id}. Esperando {duration:.2f} seg.")
            time.sleep(duration)
            return duration
        else:
            return 0
    except Exception as e:
        print(f"Erro ao curtir publicação do usuário {user_id}: {e}")
        return 0

def simulate_random_behavior(cl, user_id, total_target):
    """
    Seleciona aleatoriamente de 1 a 3 ações entre:
      - Visitar o perfil
      - Rolagem do feed
      - Digitação
      - Visualização de stories
      - Curtir uma publicação
    Executa as ações e, se o tempo total for menor que 'total_target' segundos,
    aguarda o tempo restante.
    """
    actions = [
        ("visita", lambda: simulate_profile_visit(cl, user_id)),
        ("rolagem", simulate_feed_scrolling),
        ("digitação", simulate_typing),
        ("stories", simulate_view_stories),
        ("curtir", lambda: simulate_like_post(cl, user_id))
    ]
    
    num_actions = random.randint(1, 3)
    selected_actions = random.sample(actions, num_actions)
    
    total_time = 0
    print(f"\nIniciando simulação (alvo: {total_target:.2f} seg) para o usuário {user_id}. Ações: {[name for name, _ in selected_actions]}")
    for name, action in selected_actions:
        t = action()
        total_time += t
    
    if total_time < total_target:
        extra = total_target - total_time
        print(f"Pausa adicional de {extra:.2f} seg para completar {total_target:.2f} seg.")
        time.sleep(extra)
        total_time += extra
        
    print(f"Simulação completa para o usuário {user_id}: {total_time:.2f} seg.\n")
    return total_time

if __name__ == "__main__":
    cl = login()
    followers = get_followers(cl, TARGET_USER, amount=100)
    
    # Para seguir 1 pessoa a cada 10 minutos:
    for user_id in followers:
        try:
            # Define um tempo alvo de simulação aleatório entre 60 e 90 segundos
            simulation_target = random.uniform(60, 90)
            simulation_duration = simulate_random_behavior(cl, user_id, total_target=simulation_target)
            cl.user_follow(user_id)
            print(f"Seguiu: {user_id}")
            # Calcula o tempo de espera para completar 10 minutos (600 seg)
            post_follow_delay = 600 - simulation_duration
            print(f"Aguardando {post_follow_delay:.2f} seg para seguir a próxima pessoa.\n")
            time.sleep(post_follow_delay)
        except Exception as e:
            print(f"\nErro ao seguir {user_id}: {e}")
            error_delay = random.uniform(120, 180)
            print(f"Pausa de {error_delay:.2f} seg devido ao erro.\n")
            time.sleep(error_delay)
