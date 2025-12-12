import string
import secrets

def generate_pkce_pair_plain():
    """
    MAL wspiera tylko PKCE 'plain'.
    code_challenge = code_verifier
    """
    # 64 losowe znaki — MAL akceptuje (specyfikacja PKCE pozwala 43–128)
    alphabet = string.ascii_letters + string.digits + "-._~"
    code_verifier = ''.join(secrets.choice(alphabet) for _ in range(64))

    # plain = identyczny
    code_challenge = code_verifier

    return code_verifier, code_challenge