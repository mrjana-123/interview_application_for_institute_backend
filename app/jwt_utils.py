import jwt
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime, timedelta


def jwt_encode(data):
    data["exp"] = datetime.utcnow() + timedelta(
        minutes=getattr(settings, "JWT_EXP_MINUTES", 60)
    )
    token = jwt.encode(
        data,
        getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY),
        algorithm=getattr(settings, "JWT_ALGORITHM", "HS256")
    )
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def jwt_decode(token):
    try:
        decoded = jwt.decode(
            token,
            getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY),
            algorithms=[getattr(settings, "JWT_ALGORITHM", "HS256")]
        )
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"message": "Authorization token missing"}, status=401)

        token = auth_header.split("Bearer ")[1]
        decoded = jwt_decode(token)

        if not decoded:
            return JsonResponse({"message": "Invalid or expired token"}, status=401)

        request.decoded_token = decoded   # <-- set this

        return view_func(request, *args, **kwargs)

    return wrapper
