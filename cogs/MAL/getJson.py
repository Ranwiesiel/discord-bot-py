import requests

"""Untuk mendapatkan data JSON dari MyAnimeList."""

def jikanJson(uri: str):
        response =requests.get(uri)
        json_data = response.json()
        if response.status_code != 200:
            return f"code: {json_data['status']} {json_data['message']}"
        return json_data