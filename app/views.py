from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import status
from .jwt_utils import jwt_encode
from .jwt_utils import jwt_required
from .models import *
import secrets
from datetime import datetime , timedelta
import string





@api_view(["POST"])
def delete_key(request):
    key_id = request.data.get("key_id")
    print(key_id)
    try:
        key = Sender_Activation_code.objects.get(id=key_id)
        key.status = "InActive"
        key.save()
        return Response({"success": True, "message": "Key deleted"})
    except Sender_Activation_code.DoesNotExist:
        return Response({"success": False, "message": "Key not found"}, status=404)



def generate_unique_key():
    while True:
        code = ''.join(
            secrets.choice(string.ascii_uppercase + string.digits)
            for _ in range(10)
        )
        if not Activation_code.objects(activation_code=code).first():
            return code




# @api_view(["POST"])
# def super_admin_generate_key(request):
#     data = request.data

#     admin_id = data.get("admin_id")
#     key_count = int(data.get("key_count", 1))
#     max_usage = int(data.get("max_usage", 1))
#     expiry_date_str = data.get("expiry_date")

#     if not all([admin_id, expiry_date_str]):
#         return Response(
#             {"error": "admin_id and expiry_date required"},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     if key_count < 1 or key_count > 1000:
#         return Response(
#             {"error": "key_count must be between 1 and 1000"},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     try:
#         expiry_date = datetime.datetime.fromisoformat(
#             expiry_date_str.replace("Z", "+00:00")
#         )
#     except Exception:
#         return Response(
#             {"error": "Invalid expiry_date format"},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     created_keys = []

#     for _ in range(key_count):
#         key = Sender_Activation_code(
#             admin_id=admin_id,
#             activation_code=generate_unique_key(),
#             max_using=max_usage,
#             using_times=0,
#             expiry_date=expiry_date,
#             status="Active"
#         )
#         key.save()

#         created_keys.append({
#             "id": str(key.id),
#             "key": key.activation_code,
#             "status": key.status,
#             "maxUsage": key.max_using,
#             "usedCount": key.using_times,
#             "expiryDate": expiry_date.date().isoformat(),
#         })

#     return Response({
#         "success": True,
#         "message": f"{len(created_keys)} keys generated",
#         "keys": created_keys
#     }, status=status.HTTP_201_CREATED)




@api_view(["POST"])
def activated_key_for_sender(request):
    activation_code = request.data.get("activation_code")

    if not activation_code:
        return Response(
            {"error": "Activation code is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        key_obj = Sender_Activation_code.objects.get(
            activation_code=activation_code
        )
    except Sender_Activation_code.DoesNotExist:
        return Response(
            {"error": "Invalid activation key"},
            status=status.HTTP_404_NOT_FOUND
        )

    today = datetime.now()

    # ❌ Key revoked
    if key_obj.status != "Active":
        return Response(
            {"error": "Key is revoked or inactive"},
            status=status.HTTP_403_FORBIDDEN
        )

    # ❌ Not yet active
    if today < key_obj.start_date:
        return Response(
            {
                "error": "Key not active yet",
               
                "activation_date": (
                key_obj.activation_date.strftime("%Y-%m-%d")
                if key_obj.activation_date else None
            )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # ❌ Expired
    if today > key_obj.expiry_date:
        key_obj.status = "Expired"
        key_obj.save(update_fields=["status"])

        return Response(
            {"error": "Key expired"},
            status=status.HTTP_400_BAD_REQUEST
        )

   
        

    # ✅ Activate key
    key_obj.using_times += 1

    # # Auto mark as used if limit reached
    # if key_obj.using_times >= key_obj.max_using:
    #     key_obj.status = "Used"

    key_obj.save()

    return Response(
        {
            "success": True,
            "message": "Key activated successfully",
            "data": {
                "key": key_obj.activation_code,
                "used_count": key_obj.using_times,
                "max_usage": key_obj.max_using,
                 "expiry_date": (
                key_obj.expiry_date.strftime("%Y-%m-%d")
                if key_obj.expiry_date else None
            )
            }
        },
        status=status.HTTP_200_OK
    )
    
    
          
           

@api_view(["POST"])
def activated_key_for_receiver(request):
    activation_code = request.data.get("activation_code")

    if not activation_code:
        return Response(
            {"error": "Activation code is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        key_obj = Activation_code.objects.get(
            activation_code=activation_code
        )
    except Sender_Activation_code.DoesNotExist:
        return Response(
            {"error": "Invalid activation key"},
            status=status.HTTP_404_NOT_FOUND
        )

    today = datetime.now()

    # ❌ Key revoked
    if key_obj.status != "Active":
        return Response(
            {"error": "Key is revoked or inactive"},
            status=status.HTTP_403_FORBIDDEN
        )

    # # ❌ Not yet active
    # if today < key_obj.start_date:
    #     return Response(
    #         {
    #             "error": "Key not active yet",
    #             "activation_date": key_obj.activation_date.strftime("%Y-%m-%d")
    #         },
    #         status=status.HTTP_403_FORBIDDEN0
        

    # ❌ Expired
    if today > key_obj.expiry_date:
        key_obj.status = "Expired"
        key_obj.save(update_fields=["status"])

        return Response(
            {"error": "Key expired"},
            status=status.HTTP_400_BAD_REQUEST
        )


    # ✅ Activate key
    key_obj.using_times += 1

    # Auto mark as used if limit reached
 
    key_obj.save()

    return Response(
        {
            "success": True,
            "message": "Key activated successfully",
            "data": {
                "key": key_obj.activation_code,
                "used_count": key_obj.using_times,
                "max_usage": key_obj.max_using,
                  "expiry_date": (
                key_obj.expiry_date.strftime("%Y-%m-%d")
                if key_obj.expiry_date else None)
            }
        },
        status=status.HTTP_200_OK
    )

    

@api_view(["POST"])
def super_admin_generate_key(request):
    data = request.data

    admin_id = data.get("admin_id")
    key_count = int(data.get("key_count", 1))
    max_usage = int(data.get("max_usage", 1))
    start_date = data.get("start_date")
    expiry_date = data.get("expiry_date")

    if not all([admin_id, start_date, expiry_date]):
        return Response(
            {"error": "admin_id, start_date, expiry_date required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")

    if expiry_date <= start_date:
        return Response(
            {"error": "Expiry date must be after start date"},
            status=status.HTTP_400_BAD_REQUEST
        )

    created_keys = []

    for _ in range(key_count):
        key = Sender_Activation_code(
            admin_id=admin_id,
            activation_code=uuid.uuid4().hex.upper()[:10],
            max_using=1,
            using_times=0,
            start_date=start_date,
            expiry_date=expiry_date,
            status="Active"
        )
        key.save()

        created_keys.append({
            "id": str(key.id),
            "key": key.activation_code,
            "startDate": start_date.strftime("%Y-%m-%d"),
            "expiryDate": expiry_date.strftime("%Y-%m-%d"),
        })

    return Response({
        "success": True,
        "keys": created_keys
    }, status=status.HTTP_201_CREATED)
    
    
    
@api_view(["GET"])
def get_admin_keys(request):
    admin_id = request.GET.get("admin_id")

    if not admin_id:
        return Response(
            {"error": "admin_id required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    keys = Sender_Activation_code.objects(admin_id=admin_id ).order_by('-created_at')

    data = []
    for k in keys:
        if k.status == "InActive":
            continue
            
        data.append({
            "id": str(k.id),
            "key": k.activation_code,
            "status": k.status,
            "usedCount": k.using_times,
            "createdDate": k.created_at.strftime("%Y-%m-%d"),
            "expiryDate": k.expiry_date.strftime("%Y-%m-%d"),
            "startDate": k.start_date.strftime("%Y-%m-%d"),
        })

    return Response({
        "success": True,
        "keys": data
    })



@api_view(['PUT'])
def update_admin(request):
    data = request.data
    admin_id = data.get("id")

    if not admin_id:
        return Response(
            {"error": "Admin ID required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    admin = Admin.objects(id=admin_id).first()
    if not admin:
        return Response(
            {"error": "Admin not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    admin.name = data.get("name", admin.name)
    admin.email = data.get("email", admin.email)
    admin.status = data.get("status", admin.status)

    # password update (optional)
    if data.get("password"):
        admin.password = data.get("password")

    admin.save()

    return Response(
        {"message": "Admin updated successfully"},
        status=status.HTTP_200_OK
    )
    
    
    
@api_view(['DELETE'])
def delete_admin(request):
    admin_id = request.data.get("admin_id")

    if not admin_id:
        return Response(
            {"error": "Admin ID required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    admin = Admin.objects(id=admin_id).first()
    if not admin:
        return Response(
            {"error": "Admin not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    admin.delete()

    return Response(
        {"message": "Admin deleted successfully"},
        status=status.HTTP_200_OK
    )



from django.http import JsonResponse



@api_view(['GET'])
def get_admins(request):
    admins = Admin.objects.order_by("-created_at")

    today = datetime.now()
    expiring_limit = today + timedelta(days=7)  # expiring soon = next 7 days

    admin_list = []

    for admin in admins:
        keys = Sender_Activation_code.objects.filter(admin_id=str(admin.id))
        keys_count = Sender_Activation_code.objects.filter(admin_id=str(admin.id) ,  status = "Active" ).count()
        
        recent_activations_qs = Sender_Activation_code.objects.filter(using_times__gt=0 , admin_id = str(admin.id) ).count()
        
        
        total_keys = keys.count()
        expired_keys = keys.filter(expiry_date__lt=today).count()
        expiring_soon = keys.filter(
            expiry_date__gte=today,
            expiry_date__lte=expiring_limit
        ).count()
        
        # admin_data.append({
         
        #     "customer": a.name,
        #     "email": a.email,
        #     "service": a.custom_key_count,
        #     "usedKey": recent_activations_qs,
        #     "reminingkey": int(a.total_keys - recent_activations_qs),
        #     "status": a.status,
        #     "date": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else None,
        # })

        admin_list.append({
            "id": str(admin.id),
            "customer": admin.name,
            "email": admin.email,
            "status": admin.status,
            
            "service": keys_count,
            "usedKey": recent_activations_qs,
            "reminingkey": int(keys_count - recent_activations_qs),

            # 🔥 Key stats
            "total_keys": total_keys,
            "expired_keys": expired_keys,
            "expiring_soon": expiring_soon,
            "date": admin.created_at.strftime("%Y-%m-%d %H:%M:%S") if admin.created_at else None,
            # "created_at": admin.created_at.strftime("%Y-%m-%d"),
        })

    return JsonResponse({"success": True, "data": admin_list}, status=200)




   
@api_view(['GET'])
def get_admin_details(request):
    admin_id = request.query_params.get('id')  # e.g. /api/admin-details/?id=3

    if not admin_id:
        return Response({"error": "id parameter is required"}, status=400)

    try:
        admin_user = Admin.objects.get(id=admin_id)
    except User.DoesNotExist:
        return Response({"error": "Admin not found"}, status=404)
    
    

    total_keys = Activation_code.objects.filter(   admin_id = admin_id ).count()
    active_keys = Activation_code.objects.filter(status="Active" , admin_id = admin_id ).count()
    deactivated_keys = Activation_code.objects.filter(status="Revoked" , admin_id = admin_id  ).count()
    # Count of unique clients/devices who activated keys
    # activated_clients = Activation_code.objects.filter(status="Active").distinct('key_created_by').count()
    activated_clients_list = Activation_code.objects.filter(status="Active" , admin_id = admin_id ).distinct('key_created_by')
    activated_clients = len(activated_clients_list)

    # Recent activations (last 5–10)
    recent_activations_qs = Activation_code.objects.filter(using_times__gt=0 , admin_id = admin_id ).order_by('-created_at')[:10]
    # recent_activations_qs = Activation_code.objects.filter( admin_id = admin_id ).order_by('-created_at')[:10]
    recent_activations = [
        {
            "id": str(k.id),
            "keyUsed": k.activation_code,
            "activationDate": k.activation_date.strftime("%Y-%m-%d %H:%M:%S") if k.activation_date else None
        }
        for k in recent_activations_qs
    ]
    
    
     # Fetch all keys ordered by created_at descending
    keys = Activation_code.objects.filter(admin_id = admin_id).order_by('-created_at')

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


    data = {
        "totalKeys": total_keys,
        "activeKeys": active_keys,
        "expiredKeys": deactivated_keys,
        "activatedClients": activated_clients,
        "recentActivations": recent_activations,
        "totalAdminkeys": sorted_keys,
        
    }

    return Response({"success": True, "data": data}, status=status.HTTP_200_OK)
     



@api_view(['POST'])
def add_admin(request):
    data = request.data

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    status_value = data.get("status", "Active")

    if not all([name, email, password]):
        return Response(
            {"error": "Name, email, and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check duplicate email
    if Admin.objects(email=email).first():
        return Response(
            {"error": "Admin with this email already exists"},
            status=status.HTTP_409_CONFLICT
        )

    admin = Admin(
        name=name,
        email=email,
        password=password,   # (you can hash later)
        status=status_value,
        key_option="Unlimited",
        total_keys=0,
        used_keys=0,
    )
    admin.save()

    return Response(
        {
            "message": "Admin added successfully",
            "admin": {
                "id": str(admin.id),
                "name": admin.name,
                "email": admin.email,
                "status": admin.status,
            }
        },
        status=status.HTTP_201_CREATED
    )
    
    
    

# @api_view(["POST"])
# def super_admin_generate_key(request):
#     data = request.data

  
#     # ---- Admin data ----
#     email = data.get("email")
#     password = data.get("password")
#     admin_status = data.get("status", "Active")

#     # ---- Key data ----
#     max_usage = int(data.get("max_usage", 1))
#     duration = int(data.get("duration", 30))  # days

#     if not email or not password:
#         return Response(
#             {"success": False, "message": "Email and password required"},
#             status=400,
#         )

#     if Admin.objects(email=email).first():
#         return Response(
#             {"success": False, "message": "Admin already exists"},
#             status=400,
#         )

#     # ---- Create Admin ----
#     admin = Admin(
#         email=email,
#         password=password,
#         status=admin_status,
#         total_keys=1,
#     )
#     admin.save()

#     # ---- Create Activation Key ----
#     activation_key = Sender_Activation_code(
#         admin_id=str(admin.id),
#         activation_code=str(uuid.uuid4()),
#         max_using=max_usage,
#         expiry_date=timezone.now() + timezone.timedelta(days=duration),
#     )
#     activation_key.save()

#     return Response({
#         "success": True,
#         "admin": {
#             "id": str(admin.id),
#             "email": admin.email,
#             "status": admin.status,
#         },
#         "key": {
#             "id": str(activation_key.id),
#             "activation_code": activation_key.activation_code,
#             "expiry_date": activation_key.expiry_date,
#         },
#     }, status=status.HTTP_201_CREATED)

@api_view(["GET"])
def super_admin_dashboard_cards(request):

    today = timezone.now().date()
    soon_date = today + timedelta(days=7)

    # 1️⃣ Active Admins
    active_admins = Admin.objects.filter(status="Active").count()

    # 2️⃣ Expired Keys
    expired_by_status = Sender_Activation_code.objects.filter(status="Expired").count()
    expired_by_date = Sender_Activation_code.objects.filter(expiry_date__lt=today).count()

    expired_keys = expired_by_status + expired_by_date

    # 3️⃣ Expiring Soon Keys
    expiring_soon_keys = Activation_code.objects.filter(
        status="Active",
        expiry_date__gte=today,
        expiry_date__lte=soon_date
    ).count()

    return Response({
        "success": True,
        "data": {
            "active_admins": active_admins,
            "expired_keys": expired_keys,
            "expiring_soon_keys": expiring_soon_keys,
        }
    }, status=status.HTTP_200_OK)

    
        
        
        

@api_view(["GET"])
@jwt_required 
def super_admin_dashboarded(request):
    try:
        # ---- Admin stats ----
        total_admins = Admin.objects.count()
        active_admins = Admin.objects(status="Active").count()
        inactive_admins = Admin.objects(status="Inactive").count()

        # ---- Activation code stats ----
        total_activation_codes = Activation_code.objects.count()
        active_activation_codes = Activation_code.objects(status="Active").count()
        expired_activation_codes = Activation_code.objects(status="Expired").count()

        # ---- Key usage stats ----
        total_keys_generated = sum(
            admin.total_keys for admin in Admin.objects.only("total_keys")
        )

        total_keys_used = sum(
            admin.used_keys for admin in Admin.objects.only("used_keys")
        )

        # ---- Recent admins ----
        recent_admins = Admin.objects.order_by("-created_at").limit(5)
        recent_admins_data = [
            {
                "id": str(admin.id),
                "name": admin.name,
                "email": admin.email,
                "status": admin.status,
                "created_at": admin.created_at,
            }
            for admin in recent_admins
        ]

        return Response({
            "success": True,
            "dashboard": {
                "admins": {
                    "total": total_admins,
                    "active": active_admins,
                    "inactive": inactive_admins,
                },
                "activation_codes": {
                    "total": total_activation_codes,
                    "active": active_activation_codes,
                    "expired": expired_activation_codes,
                },
                "keys": {
                    "total_generated": total_keys_generated,
                    "total_used": total_keys_used,
                },
                "recent_admins": recent_admins_data,
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "success": False,
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        






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
def sender_revoke_key(request):
    data = request.data
    key_id = data["key_id"]  # ✅ Get from query params
    
    if not key_id:
        return Response({"error": "key_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    key = Sender_Activation_code.objects(id=key_id).first()
    if not key:
        return Response({"error": "Key not found"}, status=status.HTTP_404_NOT_FOUND)

    # Update status
    key.status = "Revoked"
    key.save()

    return Response({"success": True, "message": "Key revoked successfully", "key": str(key.id)}, status=status.HTTP_200_OK)




@api_view(["POST"])
@jwt_required  
def revoke_key(request):
    data = request.data
    key_id = data["key_id"]  # ✅ Get from query params
    
    if not key_id:
        return Response({"error": "key_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    key = Sender_Activation_code.objects(id=key_id).first()
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
   
    return Response({
        "message": "Login successful",
        "token": token,
        "user": {"id": str(user.id), "name": user.name, "email": user.email}
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
def super_admin_login(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

    user = SuperAdmin.objects.filter(email=email, password=password).first()

    if not user:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    # create JWT payload
    payload = {
        "user_id": str(user.id),
        "email": user.email,
    
    }

    token = jwt_encode(payload)
   
    return Response({
        "message": "Login successful",
        "token": token,
        "user": {"id": str(user.id), "email": user.email}
    }, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def signup(request):


def signup():
    email = "seltam@gmail.com"
    password = "password"

    if SuperAdmin.objects(email=email).first():
        return Response({"message": "Email already exists"}, status=400)

    admin = Admin(email=email, password=password)
    admin.save()

    return "done"

print(signup())






# ✅ API 2: Get Keys List


@api_view(['GET'])
@jwt_required 
def get_keys(request):
   
    token_data = request.decoded_token
    admin_id = token_data["user_id"]

    today = timezone.now().date()
    print("Today:", today)

    # 1️⃣ Mark expired keys
    expired_keys = Sender_Activation_code.objects(
        expiry_date__lt=today,
        admin_id=admin_id,
        status="Active"
    ).all()

    if expired_keys:
        for expired_key in expired_keys:
            expired_key.status="Expired"
            expired_key.save()
            

    # 2️⃣ Check if payment / subscription is valid
    valid_key = Sender_Activation_code.objects(
        expiry_date__gte=today,
        admin_id=admin_id,
        status="Active"
    )


    pay_status = True
    
    if len(valid_key) == 0:
        
        pay_status = False
        print("Payment status:", pay_status)

        
        
    

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
            "key_cheks": pay_status,
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


from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view

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

    today = timezone.now().date()

    # Check if sender activation code is expired
    key_expiry_check = Sender_Activation_code.objects.filter(
        expiry_date__gte=today,
        admin_id=token_data["user_id"],
        status="Active"
    )
    

    if len(key_expiry_check) == 0:
        return Response(
            {
                "success": False,
                "message": "Key expired. Please make payment to generate a new key."
            },
            status=403
        )

    # Create activation key
    key = Activation_code.objects.create(
        admin_id=token_data["user_id"],
        key_created_by=created_by,
        activation_code=activation_code_str,
        max_using=max_usage,
    )

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

# @jwt_required  
# @api_view(['POST'])
# def generate_key(request):
#     token_data = request.decoded_token
#     email = token_data["email"]
#     data = request.data
#     created_by = email
#     max_usage = int(data.get("maxUsage", 1))
    
#     # Generate unique activation code
#     activation_code_str = generate_unique_code()
    
#     today = 
#     key_expriy_check = Sender_Activation_code.objects.filter( expiry_date = today)
    
#     if not key_expriy_check:
#         return "key expriyed make payment you can generate" 
   
#     key = Activation_code(
#         admin_id = token_data["user_id"],
#         key_created_by=created_by,
#         activation_code=activation_code_str,
#         max_using=max_usage,
#     )
    
#     key.save()

#     return Response({
#         "success": True,
#         "key": {
#             "id": str(key.id),
#             "key": key.activation_code,
#             "createdDate": key.created_at.strftime("%Y-%m-%d"),
#             "status": key.status,
#             "maxUsage": key.max_using,
#             "usedCount": key.using_times
#         }
#     }, status=201)

 
  
  


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








@api_view(['POST'])
def create_admin(request):
    name = request.data.get("name")
    email = request.data.get("email")
    password = request.data.get("password")
    key_option = request.data.get("key_option", "Default")
    custom_key_count = int(request.data.get("custom_key_count", 0))
    status_value = request.data.get("status", "Active")

    # Validation
    if not all([name, email, password]):
        return Response({"error": "Name, Email, and Password are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Check duplicate email
    if Admin.objects(email=email).first():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    # Create Admin
    admin = Admin(
        name=name,
        email=email,
        password=password,
        custom_key_count=custom_key_count,
        total_keys=custom_key_count,
        status=status_value
    )
    admin.save()

    # Auto-generate activation keys
    created_keys = []
    for _ in range(custom_key_count):
        key = generate_key()
        Activation_code(
            key_created_by = "Super Admin" ,
            activation_code=key,
            
            admin_id=str(admin.id),
            
            status="Active"
            
        ).save()
        created_keys.append(key)

    return Response({
        "message": "Admin created successfully",
        "admin": {
            "id": str(admin.id),
            "name": admin.name,
            "email": admin.email,
            "custom_key_count": admin.custom_key_count,
            "status": admin.status
        },
        "generated_keys": created_keys
    }, status=status.HTTP_201_CREATED)





@api_view(['GET'])
@jwt_required  
def admin_list(request):
    

    token_data = request.decoded_token
    admin_id = token_data["user_id"]

    admins = Admin.objects.order_by("-created_at")  # newest first
    
    admin_data = []

    for a in admins:
        recent_activations_qs = Activation_code.objects.filter(using_times__gt=0 , admin_id = str(a.id) ).count()
        # activated_clients_list = Activation_code.objects.filter(status="Active" , admin_id = str(a.id) )
        # activated_clients = len(activated_clients_list)
        admin_data.append({
            "id": str(a.id),
            "customer": a.name,
            "email": a.email,
            "service": a.custom_key_count,
            "usedKey": recent_activations_qs,
            "reminingkey": int(a.total_keys - recent_activations_qs),
            "status": a.status,
            "date": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else None,
        })

    return JsonResponse({"success": True, "data": admin_data}, status=200)






@api_view(['POST'])
def change_admin_status(request):
    new_status = request.data["status"]
    admin_id = request.data["id"]

    if new_status not in ["Active", "Blocked"]:
        return JsonResponse({"success": False, "error": "Invalid status"}, status=400)

    admin = Admin.objects(id=admin_id).first()
    if not admin:
        return JsonResponse({"success": False, "error": "Admin not found"}, status=404)

    admin.status = new_status
    admin.save()

    return JsonResponse({"success": True, "message": f"Admin status changed to {new_status}"}, status=200)
 

   
   
   
   