from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import status
from .jwt_utils import jwt_encode
from .jwt_utils import jwt_required
from .models import *
import secrets








@api_view(['GET'])
@jwt_required  
def dashboard(request):
    token_data = request.decoded_token
    admin_id = token_data["user_id"]
    
    total_keys = Activation_code.objects.filter(admin_id = admin_id ).count()
    active_keys = Activation_code.objects.filter(status="Active" , admin_id = admin_id ).count()
    deactivated_keys = Activation_code.objects.filter(status="Revoked" , admin_id = admin_id  ).count()
    # Count of unique clients/devices who activated keys
    # activated_clients = Activation_code.objects.filter(status="Active").distinct('key_created_by').count()
    activated_clients_list = Activation_code.objects.filter(status="Active" , admin_id = admin_id , using_times__gt= 0  ).distinct('key_created_by')
    activated_clients = len(activated_clients_list)

    # Recent activations (last 5–10)
    recent_activations_qs = Activation_code.objects.filter(using_times__gt=0 , admin_id = admin_id ).order_by('-created_at')[:10]
    recent_activations = [
        {
            "id": str(k.id),
            "keyUsed": k.activation_code,
            "activationDate": k.activation_date.strftime("%Y-%m-%d %H:%M:%S") if k.activation_date else None
        }
        for k in recent_activations_qs
    ]

    data = {
        "totalKeys": total_keys,
        "activeKeys": active_keys,
        "expiredKeys": deactivated_keys,
        "activatedClients": activated_clients,
        "recentActivations": recent_activations
    }

    return Response({"success": True, "data": data}, status=status.HTTP_200_OK)






@api_view(["POST"])
@jwt_required  
def revoke_key(request):
    data = request.data
    key_id = data["key_id"]  # ✅ Get from query params
    
    if not key_id:
        return Response({"error": "key_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    key = Activation_code.objects(id=key_id).first()
    if not key:
        return Response({"error": "Key not found"}, status=status.HTTP_404_NOT_FOUND)

    # Update status
    key.status = "Revoked"
    key.save()

    return Response({"success": True, "message": "Key revoked successfully", "key": str(key.id)}, status=status.HTTP_200_OK)



# ✅ Login API
@api_view(['POST'])
def login(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

    user = Admin.objects.filter(email=email, password=password).first()

    if not user:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    # create JWT payload
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        # "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # token expiry
        # "iat": datetime.datetime.utcnow()
    }

    token = jwt_encode(payload)
    print(token)
    return Response({
        "message": "Login successful",
        "token": token,
        "user": {"id": str(user.id), "name": user.name, "email": user.email}
    }, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def signup(request):


# def signup():
#     email = "seltam@gmail.com"
#     password = "password"

#     if Admin.objects(email=email).first():
#         return Response({"message": "Email already exists"}, status=400)

#     admin = Admin(email=email, password=password)
#     admin.save()

#     return "done"

# print(signup())






# ✅ API 2: Get Keys List
@api_view(['GET'])
@jwt_required 
def get_keys(request):
   
    # Fetch all keys ordered by created_at descending
    token_data = request.decoded_token
    admin_id = token_data['user_id']
    print(admin_id)
    # admin_id = request.query_params.get('id')  # e.g. /api/admin-details/?id=3

    if not admin_id:
        return Response({"error": "id parameter is required"}, status=400)

    keys = Activation_code.objects.filter(admin_id = admin_id ).order_by('-created_at')

    # Separate active and non-active keys
    active_keys = []
    other_keys = []

    for k in keys:
        key_data = {
            "id": str(k.id),
            "key": k.activation_code,
            "createdDate": k.created_at.strftime("%Y-%m-%d"),
            "status": k.status,
            "maxUsage": k.max_using,
            "usedCount": k.using_times,
        }

        if k.status == "Active":
            active_keys.append(key_data)
        else:
            other_keys.append(key_data)

    # Merge lists: active first
    sorted_keys = active_keys + other_keys

    return Response({"success": True, "keys": sorted_keys}, status=200)

    
   
def generate_unique_code(length=8):
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return ''.join(secrets.choice(alphabet) for _ in range(length)) 


@jwt_required  
@api_view(['POST'])
def generate_key(request):
    token_data = request.decoded_token
    email = token_data["email"]
    data = request.data
    created_by = email
    max_usage = int(data.get("maxUsage", 1))
    
    # Generate unique activation code
    activation_code_str = generate_unique_code()


    key = Activation_code(
        admin_id = token_data["user_id"],
        key_created_by=created_by,
        activation_code=activation_code_str,
        max_using=max_usage,
    )
    
    key.save()

    return Response({
        "success": True,
        "key": {
            "id": str(key.id),
            "key": key.activation_code,
            "createdDate": key.created_at.strftime("%Y-%m-%d"),
            "status": key.status,
            "maxUsage": key.max_using,
            "usedCount": key.using_times
        }
    }, status=201)

 
  
  


@api_view(['POST'])
def activation_code(request):
    code = request.data.get("code")
    if not code:
        return Response({"error": "Activation code is required"}, status=status.HTTP_400_BAD_REQUEST)

    result = Activation_code.objects.filter(activation_code=code , status = "Active" ).first()
    if not result:
        return Response({"error": "Invalid activation code"}, status=status.HTTP_400_BAD_REQUEST)

    if result.using_times < result.max_using:
        result.using_times += 1
        result.activation_date = timezone.now()
        result.save()
        return Response({"message": "Activation successful"}, status=status.HTTP_200_OK)
    
    else:
        return Response({"error": "Activation limit reached"}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    


@api_view(['GET'])
@jwt_required
def current_user(request):
    token_data = request.decoded_token
    email = token_data.get('email')
    user = Admin.objects(email=email).first()
    if not user:
        return Response({"error": "User not found"}, status=404)
    
    data = {
        "id": str(user.id),
        "username": user.name,
        "email": user.email,
    }
    return Response({"user": data}, status=200)





@api_view(['POST'])
@jwt_required
def update_profile(request):
    token_data = request.decoded_token
    email = token_data['email']
    user_id = request.user.id  # Assuming you use JWT or session authentication
    user = Admin.objects(email=email).first()
    if not user:
        return Response({"success": False, "error": "User not found"}, status=404)
    
    name = request.data.get("name")
    if name:
        user.name = name
        user.save()
        return Response({"success": True, "message": "Profile updated successfully"})
    
    return Response({"success": False, "error": "No data provided"}, status=400)



