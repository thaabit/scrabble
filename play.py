import urllib3
import json
import time

def get_path(path='', method="GET", fields=None, json=None, headers=None):
    if not headers: headers = {}
    if "Content-Type" not in headers: headers["Content-Type"] = 'application/json'

    url = 'http://127.0.0.1:6000/' + path

    resp = http.request(method, url, json=json, fields=fields, headers=headers)
    data = resp.data.decode('utf-8')

    json_ = resp.json()
    if resp.status != 200:
        raise Exception(f"cannot {method} {url}: {resp.status} {data}")
    return dict(json_)

http = urllib3.PoolManager()
get_path("")

# setup users
user1 = 'player_a_' + str(int(time.time()))
pw1 = 'testa'
print(f"creating {user1}")
print(get_path("user", "POST", json={'username': user1, 'password': pw1}))

user2 = 'player_b_' + str(int(time.time()))
pw2 = 'testb'
print(f"creating {user2}")
print(get_path("user", "POST", json={'username': user2, 'password': pw2}))

print(f"login {user1}")
r = get_path("login", "POST", json={'username': user1, 'password': pw1})
print(r)
header1 = {
    "Authorization": f"Bearer {r['access_token']}"
}
print(f"login {user2}")
r = get_path("login", "POST", json={'username': user2, 'password': pw2})
header2 = {
    "Authorization": f"Bearer {r['access_token']}"
}

print(f"creating game")
r = get_path(f"game?opponent={user2}", "POST", headers=header1)
game_id = r["id"]

# make moves until letters run out
row = 7
user_headers = header1
r = get_path(f"tray/{game_id}", headers=user_headers)
switch = False
while not r["game_over"]:
    tray, data = r["tray"], []
    for col, letter in enumerate(tray):
        if letter == '?': letter = '?A'
        col = col + 7
        data.append(f"{letter}:{row}:{col}")
    print(get_path("move", "POST", json={"game_id": game_id, "data":"::".join(data)}, headers=user_headers))

    user_headers = header2 if user_headers == header1 else header1
    r = get_path(f"tray/{game_id}", headers=user_headers)
    if row == 14:
        row = 7
        switch = True
    row = row + 1 if not switch else row - 1
