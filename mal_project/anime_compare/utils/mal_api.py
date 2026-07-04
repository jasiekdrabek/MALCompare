import requests
import os

BASE_URL = os.getenv("BASE_API_URL")
MAL_CLIENT_ID = os.getenv("MAL_CLIENT_ID") 

def mal_get(request, url, params=None):
    token = request.session.get("mal_token")
    if not token:
        raise Exception("Brak tokena — użytkownik musi się zalogować przez MAL.")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

def mal_fetch_anime_list(username):

    all_anime = []
    
    # pierwszy URL
    url = (
        f"{BASE_URL}users/{username}/animelist"
        "?fields=list_status,genres,num_episodes,main_picture,title"
        "&limit=1000"
    )

    headers = {
        "X-MAL-CLIENT-ID": MAL_CLIENT_ID
    }

    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Dodajemy batch
        if "data" in data:
            all_anime.extend(data["data"])

        # Czy jest kolejna strona?
        url = data.get("paging", {}).get("next")

    return all_anime
