import time
import os
import random
import logging
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

# Configuração do log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USERNAME = "papelnoplural"        
PASSWORD = "CorreOed12"        
TARGET_USER = "instagram"         

def challenge_handler(username, choice):
    """
    Handler para desafios de verificação (2FA).
    Solicita o código de verificação ao usuário.
    """
    return input(f"Digite o código de verificação enviado por {choice} para {username}: ")

def login_user():
    """
    Tenta logar usando sessão salva ou credenciais.
    Se o login inicial falhar por conta de 2FA, solicita o código e tenta novamente.
    """
    cl = Client()
    cl.delay_range = [1, 3]
    cl.challenge_code_handler = challenge_handler

    # Tenta carregar a sessão, se existir
    if os.path.exists("session.json"):
        try:
            session = cl.load_settings("session.json")
            logger.info("Sessão carregada do arquivo.")
            cl.set_settings(session)
        except Exception as e:
            logger.info("Erro ao carregar a sessão: %s", e)

    # Tenta fazer o login sem código (para disparar o 2FA se necessário)
    try:
        cl.login(USERNAME, PASSWORD)
    except Exception as e:
        error_str = str(e)
        logger.info("Erro no login: %s", error_str)
        if "Two-factor authentication required" in error_str:
            # Solicita o código 2FA interativamente
            code = challenge_handler(USERNAME, "2FA")
            try:
                cl.login(USERNAME, PASSWORD, verification_code=code)
                logger.info("Login efetuado com 2FA.")
            except Exception as e2:
                logger.info("Falha no login com 2FA: %s", e2)
                raise e2
        else:
            raise e

    # Verifica a sessão chamando uma requisição
    try:
        cl.get_timeline_feed()
    except LoginRequired:
        logger.info("Sessão inválida; realizando login novamente.")
        cl.login(USERNAME, PASSWORD)
    cl.dump_settings("session.json")
    return cl

def get_followers(cl, username, amount=100):
    user_id = cl.user_id_from_username(username)
    followers = cl.user_followers(user_id, amount=amount)
    return list(followers.keys())

def simulate_profile_visit(cl, user_id, delay_range=(20, 40)):
    logger.info(f"Acessando o perfil do usuário {user_id}...")
    try:
        user_info = cl.user_info(user_id)
        logger.info(f"Perfil: {user_info.username} | Seguidores: {user_info.follower_count}")
    except Exception as e:
        logger.info(f"Erro ao acessar perfil do usuário {user_id}: {e}")
    duration = random.uniform(*delay_range)
    logger.info(f"Simulando visita ao perfil por {duration:.2f} seg...")
    time.sleep(duration)
    return duration

def simulate_feed_scrolling(delay_range=(30, 60)):
    logger.info("Visualizando o feed central...")
    try:
        feed = cl.feed_timeline()
        if feed and "items" in feed:
            logger.info(f"Feed central possui {len(feed['items'])} itens.")
        else:
            logger.info("Feed central vazio ou não encontrado.")
    except Exception as e:
        logger.info(f"Erro ao acessar o feed central: {e}")
    duration = random.uniform(*delay_range)
    logger.info(f"Aguardando {duration:.2f} seg para simular a rolagem do feed...")
    time.sleep(duration)
    return duration

def simulate_view_stories(cl, user_id, delay_range=(20, 40)):
    logger.info(f"Visualizando stories do usuário {user_id}...")
    try:
        stories = cl.user_stories(user_id)
        if stories:
            logger.info(f"Encontrados {len(stories)} stories para o usuário {user_id}.")
        else:
            logger.info("Nenhum story encontrado para esse usuário.")
    except Exception as e:
        logger.info(f"Erro ao obter stories do usuário {user_id}: {e}")
    duration = random.uniform(*delay_range)
    logger.info(f"Aguardando {duration:.2f} seg para simular a visualização dos stories do perfil...")
    time.sleep(duration)
    return duration

def view_feed_stories_actual(cl, delay_range=(30, 60)):
    logger.info("Visualizando stories do feed (ação real)...")
    try:
        tray = cl.story_pk_from_url("feed")  # This gets all available stories
        
        if tray:
            for story_id in tray:
                try:
                    cl.story_seen([story_id])
                    logger.info(f"Story {story_id} marcado como visto")
                    time.sleep(random.uniform(1, 3))  # Small delay between each story
                except Exception as e:
                    logger.error(f"Erro ao marcar story {story_id} como visto: {str(e)}")
                    continue
                    
            logger.info(f"Total de {len(tray)} stories marcados como vistos")
        else:
            logger.info("Nenhum story encontrado no feed")
            
    except Exception as e:
        logger.error(f"Erro ao processar stories do feed: {str(e)}")
        
    duration = random.uniform(*delay_range)
    logger.info(f"Aguardando {duration:.2f} seg após visualização dos stories...")
    time.sleep(duration)
    return duration

def simulate_like_feed_post(cl, delay_range=(10, 20)):
    logger.info("Curtindo uma foto do feed central...")
    try:
        # Get the timeline feed with a proper amount parameter
        feed = cl.feed_timeline(amount=10)  # Get 10 posts to have a good sample
        media_items = []
        
        # Extract valid media items
        if isinstance(feed, dict) and "items" in feed:
            media_items = [item for item in feed["items"] if "id" in item]
        elif isinstance(feed, list):
            media_items = [item for item in feed if "id" in item]
            
        if media_items:
            media = random.choice(media_items)
            media_id = media.get("id") or media.get("pk")
            
            # Check if media is already liked
            if not cl.media_info(media_id).liked:
                cl.media_like(media_id)
                logger.info(f"Curti a mídia {media_id} do feed.")
            else:
                logger.info("Post já está curtido, pulando...")
                
        else:
            logger.info("Nenhum post válido encontrado no feed.")
            
        duration = random.uniform(*delay_range)
        logger.info(f"Esperando {duration:.2f} seg...")
        time.sleep(duration)
        return duration
        
    except Exception as e:
        logger.error(f"Erro ao curtir post do feed: {str(e)}")
        duration = random.uniform(*delay_range)
        time.sleep(duration)
        return duration

def simulate_interval_behavior(cl, user_id, total_interval):
    """
    Distribui ações com pesos diferentes e maior controle de erros
    """
    actions = [
        ("visita", lambda: simulate_profile_visit(cl, user_id), 1),  # weight 1
        ("rolagem do feed", lambda: simulate_feed_scrolling(), 1),    # weight 1
        ("stories (perfil)", lambda: simulate_view_stories(cl, user_id), 2),  # weight 2
        ("stories (feed)", lambda: view_feed_stories_actual(cl), 2),   # weight 2
        ("curtir feed", lambda: simulate_like_feed_post(cl), 1)        # weight 1
    ]
    
    start = time.time()
    action_count = 0
    max_consecutive_errors = 3
    consecutive_errors = 0
    
    while True:
        elapsed = time.time() - start
        remaining = total_interval - elapsed
        
        if remaining <= 0 or consecutive_errors >= max_consecutive_errors:
            break
            
        # Calculate wait time with more variation
        wait_time = random.uniform(60, min(240, remaining))
        logger.info(f"Aguardando {wait_time:.2f} seg antes da próxima ação...")
        time.sleep(wait_time)
        
        # Select action based on weights
        weighted_actions = []
        for name, func, weight in actions:
            weighted_actions.extend([(name, func)] * weight)
            
        action_name, action_func = random.choice(weighted_actions)
        logger.info(f"Executando ação: {action_name}")
        
        try:
            action_func()
            consecutive_errors = 0
            action_count += 1
        except Exception as e:
            logger.error(f"Erro na ação {action_name}: {str(e)}")
            consecutive_errors += 1
            time.sleep(random.uniform(180, 300))  # Longer delay after error

if __name__ == "__main__":
    cl = login_user()
    followers = get_followers(cl, TARGET_USER, amount=100)
    
    # Para cada usuário, define um ciclo total aleatório entre 10 e 15 minutos (600-900 seg)
    for user_id in followers:
        cycle_total = random.uniform(600, 900)
        logger.info(f"\nIniciando ciclo para o usuário {user_id} com intervalo total de {cycle_total:.2f} seg.")
        cycle_start = time.time()
        
        # Durante o ciclo, distribui as ações reais ao longo do tempo
        simulate_interval_behavior(cl, user_id, total_interval=cycle_total)
        
        # Ao final do ciclo, realiza o follow
        try:
            cl.user_follow(user_id)
            logger.info(f"Seguiu: {user_id}")
        except Exception as e:
            logger.info(f"\nErro ao seguir {user_id}: {e}")
            time.sleep(random.uniform(120, 180))
        
        elapsed = time.time() - cycle_start
        if elapsed < cycle_total:
            wait_time = cycle_total - elapsed
            logger.info(f"Esperando {wait_time:.2f} seg para iniciar o próximo ciclo.\n")
            time.sleep(wait_time)
