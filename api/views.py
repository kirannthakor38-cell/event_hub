from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User , TempUser

import random
from django.core.mail import send_mail

import re


from bson import ObjectId

def doc(obj):
    d = obj.to_mongo().to_dict()
    d["id"] = str(d.get("_id"))
    d.pop("_id", None)
    return d


# SIMPLE TEST API
def hello(request):
    return JsonResponse({"message": "Hello from Django!"})


# SIGNUP API
@api_view(["POST"])
def signup(request):
    data = request.data

    username = data.get("username")
    rollno = data.get("rollno")
    email = data.get("email")
    mobile = data.get("mobile")
    password = data.get("password")

    # Validate required fields
    if not all([username, rollno, email, mobile, password]):
        return Response({"error": "All fields are required"}, status=400)

    # Validate roll number format
    try:
        if not re.match(r"^\d{2}(BCA|IT)\d{3}$", rollno.upper()):
            return Response({"error": "Roll no must be like 23BCA119 or 23IT131"}, status=400)
    except Exception:
        return Response({"error": "Invalid rollno format"}, status=400)

    # Prevent duplicates
    if User.objects(rollno=rollno.upper()).first():
        return Response({"error": "Roll number already exists"}, status=400)
    if User.objects(email=email).first():
        return Response({"error": "Email already exists"}, status=400)
    if User.objects(mobile=mobile).first():
        return Response({"error": "Mobile number already exists"}, status=400)

    # Remove old temp entry
    TempUser.objects(email=email).delete()

    # Generate OTP
    otp = random.randint(100000, 999999)

    # Try sending email safely
    try:
        send_mail(
            subject="TechNova Fest – OTP Verification (IT Club • DNiCA)",
            message=(
                f"Hello,\n\n"
                f"Thank you for registering for TechNova Fest organized by the IT Club.\n\n"
                f"Your OTP is: {otp}\nValid for 5 minutes.\n\nDo not share it.\n"
            ),
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        return Response({"error": f"Email sending failed: {str(e)}"}, status=500)

    # Save new Temp User
    TempUser.objects.create(
        username=username,
        rollno=rollno.upper(),
        email=email,
        mobile=mobile,
        password=password,
        otp=otp
    )

    return Response({"msg": "OTP sent to your email"})


@api_view(["POST"])
def verify_otp(request):
    email = request.data.get("email")
    otp = request.data.get("otp")

    temp = TempUser.objects(email=email).first()
    if not temp:
        return Response({"error": "Signup session expired. Please signup again."}, status=400)

    if str(temp.otp) != str(otp):
        return Response({"error": "Invalid OTP"}, status=400)

    # Create final user
    user = User(
        username=temp.username,
        rollno=temp.rollno,
        email=temp.email,
        mobile=temp.mobile,
        password=temp.password
    )
    user.save()

    # Remove temporary data
    temp.delete()

    return Response({
    "msg": "Verified! Account created",
    "username": user.username,
    "rollno": user.rollno,
    "mobile": user.mobile,
    "email": user.email
})



    

@api_view(["POST"])
def login(request):
    data = request.data

    rollno = data.get("rollno")
    password = data.get("password")

    # Rollno must exist
    if not rollno or not password:
        return Response({"error": "Roll no and password are required"}, status=400)

    # Convert rollno to uppercase for matching
    rollno = rollno.upper()

    # Find user (plain password match)
    user = User.objects(rollno=rollno, password=password).first()

    if not user:
        return Response({"error": "Invalid roll number or password"}, status=400)

    # Success response (FOR REACT)
    return Response({
        "msg": "Login successful",
        "username": user.username,
        "rollno": user.rollno,
        "mobile": user.mobile
    })






from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Event, Registration


# Get all events
@api_view(["GET"])
def get_events(request):
    events = Event.objects()

    data = [
        {
            "event_id": e.event_id,
            "title": e.title,
            "description": e.description,
            "image": e.image,
            "date": e.date
        }
        for e in events
    ]

    return Response(data)


# Register Event
@api_view(["POST"])
def register_event(request):
    event_id = request.data.get("event_id")
    rollno = request.data.get("rollno")
    username = request.data.get("username")
    score = request.data.get("score", 0)  # ⭐ default score = 0

    # prevent duplicate
    if Registration.objects(event_id=event_id, rollno=rollno).first():
        return Response({"error": "Already registered"}, status=400)

    reg = Registration(
        event_id=event_id,
        rollno=rollno,
        username=username,
        score=score     # ⭐ store score
    )
    reg.save()

    return Response({"msg": "Registered Successfully"})



# Get user registrations
@api_view(["GET"])
def my_registrations(request):
    rollno = request.GET.get("rollno")

    regs = Registration.objects(rollno=rollno)

    event_ids = [r.event_id for r in regs]

    return Response({"registered": event_ids})




@api_view(["GET"])
def my_activity(request):
    rollno = request.GET.get("rollno")

    regs = Registration.objects(rollno=rollno)

    output = []

    for r in regs:
        ev = Event.objects(event_id=r.event_id).first()
        if ev:
            output.append({
                "event_id": ev.event_id,
                "title": ev.title,
                "description": ev.description,
                "image": ev.image,
                "date": ev.date,
                "score": r.score
            })

    return Response({"events": output})





from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Winner

@api_view(["GET"])
def get_winners(request):
    winners = Winner.objects()
    data = []

    for w in winners:
        data.append({
            "event_id": w.event_id,
            "event_title": w.event_title,
            "event_date": w.event_date,
            "winners": [
                {
                    "rollno": item.rollno,
                    "name": item.name,
                    "image": item.image
                }
                for item in w.winners
            ]
        })

    return Response({"winners": data})



from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Examiner

@csrf_exempt
@api_view(["POST"])
def examiner_login(request):
    data = request.data

    username = data.get("username")
    password = data.get("password")

    ex = Examiner.objects(username=username, password=password).first()

    if not ex:
        return Response({"error": "Invalid username or password"}, status=400)

    return Response({
        "msg": "success",
        "username": ex.username,
        "event_id": ex.event_id
    })


def examiner_event(request):
    event_id = request.GET.get("event_id")

    try:
        ev = Event.objects(event_id=event_id).first()
        if not ev:
            return JsonResponse({"error": "Event not found"})
    except:
        return JsonResponse({"error": "Event not found"})

    return JsonResponse({
        "event_id": ev.event_id,
        "title": ev.title,
        "description": ev.description,
        "date": ev.date
    })




def examiner_participants(request):
    event_id = request.GET.get("event_id")
    regs = Registration.objects(event_id=event_id)

    data = []
    for r in regs:
        data.append({
            "rollno": r.rollno,
            "username": r.username,
            "score": r.score
        })

    return JsonResponse({"participants": data})




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def examiner_submit_score(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    event_id = data.get("event_id")
    rollno = data.get("rollno")
    score = data.get("score")

    reg = Registration.objects(event_id=event_id, rollno=rollno).first()
    if not reg:
        return JsonResponse({"error": "User not registered"}, status=404)

    reg.score = score
    reg.save()

    return JsonResponse({"success": True, "message": "Score updated"})









# api/views.py
import json
import jwt
import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import AdminRadhe

def generate_jwt(payload: dict) -> str:
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=getattr(settings, "JWT_EXP_DELTA_SECONDS", 3600))
    payload.update({"exp": exp})
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

@csrf_exempt
@require_http_methods(["POST"])
def admin_login_jwt(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
    except Exception:
        return JsonResponse({"success": False, "msg": "Invalid request"}, status=400)

    admin = AdminRadhe.objects(username=username).first()
    if not admin:
        return JsonResponse({"success": False, "msg": "Invalid credentials"}, status=401)

    # Plain text password check
    if password != admin.password:
        return JsonResponse({"success": False, "msg": "Invalid credentials"}, status=401)

    token = generate_jwt({"username": username})
    return JsonResponse({"success": True, "token": token, "username": username})

@require_http_methods(["GET"])
def admin_check_jwt(request):
    auth = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION")
    if not auth or not auth.startswith("Bearer "):
        return JsonResponse({"logged_in": False, "username": ""}, status=401)
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return JsonResponse({"logged_in": True, "username": payload.get("username")})
    except jwt.ExpiredSignatureError:
        return JsonResponse({"logged_in": False, "username": "", "msg": "Token expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"logged_in": False, "username": ""}, status=401)
    










 


# -------------------------------------------------------------------
# USERS CRUD
# -------------------------------------------------------------------
@csrf_exempt
def users_list_create(request):
    if request.method == "GET":
        users = User.objects.all()
        return JsonResponse([doc(u) for u in users], safe=False)

    if request.method == "POST":
        data = json.loads(request.body.decode())
        try:
            user = User(
                username=data["username"],
                rollno=data["rollno"],
                mobile=data["mobile"],
                password=data["password"]
            )
            user.save()
            return JsonResponse({"message": "User created"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def user_detail(request, rollno):
    try:
        user = User.objects.get(rollno=rollno)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(doc(user))

    if request.method == "PUT":
        data = json.loads(request.body.decode())
        user.username = data.get("username", user.username)
        user.mobile = data.get("mobile", user.mobile)
        user.password = data.get("password", user.password)
        user.save()
        return JsonResponse({"message": "User updated"})

    # Support PATCH for partial updates (e.g., admin updating password)
    if request.method == "PATCH":
        try:
            data = json.loads(request.body.decode())
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Only update provided fields
        if "username" in data:
            user.username = data.get("username")
        if "mobile" in data:
            user.mobile = data.get("mobile")
        if "password" in data:
            user.password = data.get("password")

        user.save()
        return JsonResponse({"message": "User patched"})

    if request.method == "DELETE":
        user.delete()
        return JsonResponse({"message": "User deleted"})


# -------------------------------------------------------------------
# EVENTS CRUD
# -------------------------------------------------------------------
@csrf_exempt
def events_list_create(request):
    if request.method == "GET":
        events = Event.objects.all()
        return JsonResponse([doc(e) for e in events], safe=False)

    if request.method == "POST":
        data = json.loads(request.body.decode())
        try:
            ev = Event(
                event_id=data["event_id"],
                title=data["title"],
                description=data.get("description", ""),
                image=data.get("image", ""),
                date=data.get("date", "")
            )
            ev.save()
            return JsonResponse({"message": "Event created"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def event_detail(request, event_id):
    try:
        ev = Event.objects.get(event_id=event_id)
    except DoesNotExist:
        return JsonResponse({"error": "Event not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(doc(ev))

    if request.method == "PUT":
        data = json.loads(request.body.decode())
        ev.title = data.get("title", ev.title)
        ev.description = data.get("description", ev.description)
        ev.image = data.get("image", ev.image)
        ev.date = data.get("date", ev.date)
        ev.save()
        return JsonResponse({"message": "Event updated"})

    if request.method == "DELETE":
        ev.delete()
        return JsonResponse({"message": "Event deleted"})


# -------------------------------------------------------------------
# REGISTRATIONS CRUD
# -------------------------------------------------------------------
@csrf_exempt
def registrations_list_create(request):
    if request.method == "GET":
        regs = Registration.objects.all()
        return JsonResponse([doc(r) for r in regs], safe=False)

    if request.method == "POST":
        data = json.loads(request.body.decode())
        try:
            reg = Registration(
                event_id=data["event_id"],
                rollno=data["rollno"],
                username=data["username"],
                score=data.get("score", 0)
            )
            reg.save()
            return JsonResponse({"message": "Registration added"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def registration_detail(request, reg_id):
    try:
        reg = Registration.objects.get(id=reg_id)
    except DoesNotExist:
        return JsonResponse({"error": "Registration not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(doc(reg))

    if request.method == "PUT":
        data = json.loads(request.body.decode())
        reg.event_id = data.get("event_id", reg.event_id)
        reg.rollno = data.get("rollno", reg.rollno)
        reg.username = data.get("username", reg.username)
        reg.score = data.get("score", reg.score)
        reg.save()
        return JsonResponse({"message": "Registration updated"})

    if request.method == "DELETE":
        reg.delete()
        return JsonResponse({"message": "Registration deleted"})


# -------------------------------------------------------------------
# EXAMINERS CRUD
# -------------------------------------------------------------------
@csrf_exempt
def examiners_list_create(request):
    if request.method == "GET":
        ex = Examiner.objects.all()
        return JsonResponse([doc(e) for e in ex], safe=False)

    if request.method == "POST":
        data = json.loads(request.body.decode())
        try:
            x = Examiner(
                username=data["username"],
                password=data["password"],
                event_id=data["event_id"]
            )
            x.save()
            return JsonResponse({"message": "Examiner added"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def examiner_detail(request, examiner_id):
    try:
        ex = Examiner.objects.get(id=examiner_id)
    except DoesNotExist:
        return JsonResponse({"error": "Examiner not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(doc(ex))

    if request.method == "PUT":
        data = json.loads(request.body.decode())
        ex.username = data.get("username", ex.username)
        ex.password = data.get("password", ex.password)
        ex.event_id = data.get("event_id", ex.event_id)
        ex.save()
        return JsonResponse({"message": "Examiner updated"})

    if request.method == "DELETE":
        ex.delete()
        return JsonResponse({"message": "Examiner deleted"})


# -------------------------------------------------------------------
# WINNERS CRUD
# -------------------------------------------------------------------
@csrf_exempt
def winners_list_create(request):
    if request.method == "GET":
        win = Winner.objects.all()
        return JsonResponse([doc(w) for w in win], safe=False)

    if request.method == "POST":
        data = json.loads(request.body.decode())
        try:
            w = Winner(
                event_id=data["event_id"],
                event_title=data["event_title"],
                event_date=data["event_date"],
                winners=data.get("winners", [])
            )
            w.save()
            return JsonResponse({"message": "Winner list created"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def winner_detail(request, winner_id):
    try:
        w = Winner.objects.get(id=winner_id)
    except DoesNotExist:
        return JsonResponse({"error": "Winner not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(doc(w))

    if request.method == "PUT":
        data = json.loads(request.body.decode())
        w.event_title = data.get("event_title", w.event_title)
        w.event_date = data.get("event_date", w.event_date)

        if "winners" in data:
            w.winners = data["winners"]

        w.save()
        return JsonResponse({"message": "Winner updated"})

    if request.method == "DELETE":
        w.delete()
        return JsonResponse({"message": "Winner deleted"})


# -------------------------------------------------------------------
# ADMIN CRUD
# -------------------------------------------------------------------
@csrf_exempt
def admins_list_create(request):
    if request.method == "GET":
        admins = AdminRadhe.objects.all()
        return JsonResponse([doc(a) for a in admins], safe=False)

    if request.method == "POST":
        data = json.loads(request.body.decode())
        try:
            a = AdminRadhe(
                username=data["username"],
                password=data["password"],
            )
            a.save()
            return JsonResponse({"message": "Admin created"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def admin_detail(request, username):
    try:
        a = AdminRadhe.objects.get(username=username)
    except DoesNotExist:
        return JsonResponse({"error": "Admin not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(doc(a))

    if request.method == "PUT":
        data = json.loads(request.body.decode())
        a.password = data.get("password", a.password)
        a.save()
        return JsonResponse({"message": "Admin updated"})

    if request.method == "DELETE":
        a.delete()
        return JsonResponse({"message": "Admin deleted"})

