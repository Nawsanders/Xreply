from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import urllib.parse


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

replied_tweets = set()
tweets_sent = 0
BOT_USERNAME = "le nom de ton bot"  # Username du bot

# Connexion à Twitter
def login_twitter(username, password):
    print("Tentative de connexion à Twitter...")
    driver.get("https://x.com/login")
    time.sleep(5)
    try:
        username_field = driver.find_element(By.NAME, "text")
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)
        time.sleep(3)
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)
        print("Connexion réussie.")
    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
        driver.quit()
        exit()

# Répondre à un tweet via l’URL intent
def reply_to_tweet(tweet_id, author_username):
    global tweets_sent
    if tweet_id in replied_tweets or author_username == BOT_USERNAME:
        print(f"Tweet {tweet_id} ignoré (déjà répondu ou tweet du bot).")
        return False

    # Construire l’URL de réponse avec le texte
    reply_text = urllib.parse.quote("ce que tu veux répondre")
    intent_url = f"https://twitter.com/intent/tweet?in_reply_to={tweet_id}&text={reply_text}"
    print(f"Traitement du tweet {tweet_id} via {intent_url}...")
    driver.get(intent_url)
    time.sleep(5)  =t

    try:
        # Trouver le bouton "Post" dans la fenêtre d’intent
        print("Recherche du bouton 'Post'...")
        post_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="tweetButton"]'))
        )
        print("Bouton trouvé, tentative de clic...")
        driver.execute_script("arguments[0].click();", post_button)
        time.sleep(3)

        tweets_sent += 1
        replied_tweets.add(tweet_id)
        print(f"Réponse envoyée au tweet {tweet_id} (Total: {tweets_sent})")
        return True

    except TimeoutException as e:
        print(f"Erreur : Bouton 'Post' introuvable pour {intent_url} - {e}")
        return False
    except Exception as e:
        print(f"Erreur inattendue pour {intent_url} : {e}")
        return False

# Recherche des tweets récents via URL
def search_and_reply():
    search_terms = 'recherche le mot que tu souhaites spam'
    encoded_search = urllib.parse.quote(search_terms)
    search_url = f"https://x.com/search?q={encoded_search}&src=typed_query&f=live"
    print(f"Navigation vers la recherche : {search_url}")
    driver.get(search_url)
    time.sleep(15)

    print("Recherche du tweet le plus récent...")
    tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

    if not tweets:
        print("Aucun tweet trouvé !")
        return
    
    print(f"{len(tweets)} tweets trouvés.")
    for tweet in tweets:
        try:
            # Récupérer l'URL du tweet
            tweet_link = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
            tweet_url = tweet_link.get_attribute("href")
            tweet_id = tweet_url.split("/")[-1]

            # Récupérer le pseudo de l'auteur
            author_element = tweet.find_element(By.XPATH, './/a[contains(@href, "/")]')
            author_username = author_element.get_attribute("href").split("/")[-1]

            if reply_to_tweet(tweet_id, author_username):
                print(f"Tweet {tweet_id} traité avec succès.")
                break  

        except Exception as e:
            print(f"Erreur lors de l'analyse d'un tweet : {e}")

# Boucle principale
def start():
    global tweets_sent
    while True:
        try:
            search_and_reply()
            print(f"Total de tweets envoyés : {tweets_sent}")
        except Exception as e:
            print(f"Erreur générale : {e}")
        time.sleep(30)

if __name__ == "__main__":
    username = "Your username"
    password = "Your password"
    login_twitter(username, password)
    start()
