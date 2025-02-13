import time
import os
import random
from instagrapi import Client

USERNAME = "petiress7"        
PASSWORD = "matheusteste123"        
TARGET_USER = "instagram"         

def login():
    cl = Client()  # Usa o user-agent padrão do instagrapi (móvel), o que ajuda a evitar problemas de CSRF.
    
    # Tenta carregar a sessão salva, se existir.
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

def simulate_profile_visit(cl, user_id, delay_range=(5, 15)):
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

def simulate_feed_scrolling(delay_range=(5, 15)):
    duration = random.uniform(*delay_range)
    print(f"Simulando rolagem do feed por {duration:.2f} seg...")
    time.sleep(duration)
    return duration

def simulate_typing(delay_range=(3, 8)):
    duration = random.uniform(*delay_range)
    print(f"Simulando digitação por {duration:.2f} seg...")
    time.sleep(duration)
    return duration

def simulate_view_stories(delay_range=(5, 15)):
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

def simulate_interval_behavior(cl, user_id, total_interval):
    """
    Durante o intervalo total (em segundos), executa ações aleatórias espaçadas por
    intervalos de espera também aleatórios. Isso imita um comportamento humano ao longo do tempo.
    """
    actions = [
        ("visita", lambda: simulate_profile_visit(cl, user_id)),
        ("rolagem", lambda: simulate_feed_scrolling()),
        ("digitação", lambda: simulate_typing()),
        ("stories", lambda: simulate_view_stories()),
        ("curtir", lambda: simulate_like_post(cl, user_id))
    ]
    start = time.time()
    while time.time() - start < total_interval:
        remaining = total_interval - (time.time() - start)
        # Define um tempo de espera aleatório entre 30 seg e 2 minutos, sem exceder o tempo restante
        wait_time = random.uniform(30, min(120, remaining))
        print(f"Aguardando {wait_time:.2f} seg antes da próxima ação aleatória...")
        time.sleep(wait_time)
        action_name, action_func = random.choice(actions)
        print(f"Ação aleatória escolhida: {action_name}")
        action_func()

if __name__ == "__main__":
    cl = login()
    followers = get_followers(cl, TARGET_USER, amount=100)
    
    for user_id in followers:
        cycle_total = random.uniform(600, 900)
        print(f"\nIniciando ciclo para o usuário {user_id} com intervalo total de {cycle_total:.2f} seg.")
        cycle_start = time.time()
        
        simulate_interval_behavior(cl, user_id, total_interval=cycle_total)
        
        try:
            cl.user_follow(user_id)
            print(f"Seguiu: {user_id}")
        except Exception as e:
            print(f"\nErro ao seguir {user_id}: {e}")
            time.sleep(random.uniform(120, 180))
        
        elapsed = time.time() - cycle_start
        if elapsed < cycle_total:
            wait_time = cycle_total - elapsed
            print(f"Esperando {wait_time:.2f} seg para iniciar o próximo ciclo.\n")
            time.sleep(wait_time)
