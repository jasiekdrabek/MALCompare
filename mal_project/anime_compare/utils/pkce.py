import string
import secrets

def generate_pkce_pair_plain():

    alphabet = string.ascii_letters + string.digits + "-._~"
    code_verifier = ''.join(secrets.choice(alphabet) for _ in range(64))

    code_challenge = code_verifier

    return code_verifier, code_challenge