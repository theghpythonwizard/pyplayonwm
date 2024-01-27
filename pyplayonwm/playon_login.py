from .tools._playon_recorder import PlayOnLogin


def login():
    login = PlayOnLogin()
    token = login.login_token()
    return token
