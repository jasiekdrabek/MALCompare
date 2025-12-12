import requests

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
