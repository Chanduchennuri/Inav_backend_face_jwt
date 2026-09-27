
from datetime import datetime

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    Request
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.responses import JSONResponse

from .jwt_auth import (
    create_access_token,
    decode_access_token
)

from .auth import (
    validate_email,
    hash_password,
    verify_password
)

from .storage import (
    save_user,
    get_user,
    user_exists
)

from .face_recog import FaceEngine

from .verifier import FaceVerifier


app = FastAPI(
    title="Face Authentication API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://localhost:5173",
        "https://jarvis-inav.vercel.app/"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


face_engine = FaceEngine()

verifier = FaceVerifier(
    threshold=0.45
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "service": "face-authentication"
    }


# ============================================================
# ENROLLMENT
# ============================================================

@app.post("/api/enroll")
async def enroll_user(

    user_id: str = Form(...),

    name: str = Form(...),

    email: str = Form(...),

    password: str = Form(...),

    file: UploadFile = File(...)
):

    # -----------------------------
    # Basic validation
    # -----------------------------

    user_id = user_id.strip()

    name = name.strip()

    email = email.strip().lower()


    if not user_id:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "User ID is required"
            }
        )


    if not name:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Name is required"
            }
        )


    if not validate_email(email):

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Invalid email"
            }
        )


    if len(password) < 8:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message":
                    "Password must contain at least 8 characters"
            }
        )


    # -----------------------------
    # Check existing user
    # -----------------------------

    if user_exists(user_id):

        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "message": "User already exists"
            }
        )


    # -----------------------------
    # Validate image
    # -----------------------------

    if not file.content_type.startswith("image/"):

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Invalid image"
            }
        )


    image_bytes = await file.read()


    # -----------------------------
    # Generate face embedding
    # -----------------------------

    try:

        embedding = (
            face_engine.extract_embedding(
                image_bytes
            )
        )

    except ValueError as error:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": str(error)
            }
        )


    # -----------------------------
    # Create user
    # -----------------------------

    user = {

        "user_id":
            user_id.lower(),

        "name":
            name,

        "email":
            email,

        "password_hash":
            hash_password(password),

        "face_embedding":
            embedding.tolist(),

        "created_at":
            datetime.utcnow().isoformat()
    }


    save_user(user)


    return {

        "success": True,

        "message":
            "User enrolled successfully",

        "user": {

            "user_id":
                user["user_id"],

            "name":
                user["name"],

            "email":
                user["email"]
        }
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/api/login")
async def login_user(

    user_id: str = Form(...),

    password: str = Form(...),

    file: UploadFile = File(...)
):

    user = get_user(user_id)


    # -----------------------------
    # User lookup
    # -----------------------------

    if user is None:

        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": "Invalid credentials"
            }
        )


    # -----------------------------
    # Password verification
    # -----------------------------

    if not verify_password(
        password,
        user["password_hash"]
    ):

        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": "Invalid credentials"
            }
        )


    # -----------------------------
    # Validate image
    # -----------------------------

    if not file.content_type.startswith("image/"):

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Invalid image"
            }
        )


    image_bytes = await file.read()


    # -----------------------------
    # Face embedding
    # -----------------------------

    try:

        captured_embedding = (
            face_engine.extract_embedding(
                image_bytes
            )
        )

    except ValueError as error:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": str(error)
            }
        )


    # -----------------------------
    # Face verification
    # -----------------------------

    result = verifier.verify(

        captured_embedding,

        user["face_embedding"]
    )


    if not result["verified"]:

        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message":
                    "Face verification failed"
            }
        )


    # ========================================================
    # SUCCESSFUL LOGIN
    # ========================================================

    token = create_access_token(
        user_id=user["user_id"],
        name=user["name"]
    )


    response = JSONResponse(

        content={

            "success": True,

            "verified": True,

            "message":
                "Authentication successful",

            "user": {

                "user_id":
                    user["user_id"],

                "name":
                    user["name"],

                "email":
                    user["email"]
            }
        }
    )


    response.set_cookie(

        key="access_token",

        value=token,

        httponly=True,

        max_age=300,

        samesite="lax",

        secure=False
    )


    return response


# ============================================================
# SESSION CHECK
# ============================================================

@app.get("/api/session")
async def check_session(

    request: Request
):

    token = request.cookies.get(
        "access_token"
    )


    # -----------------------------
    # No token
    # -----------------------------

    if not token:

        return JSONResponse(

            status_code=401,

            content={
                "authenticated": False
            }
        )


    # -----------------------------
    # Decode token
    # -----------------------------

    payload = decode_access_token(
        token
    )


    if payload is None:

        return JSONResponse(

            status_code=401,

            content={
                "authenticated": False
            }
        )


    # -----------------------------
    # Get user ID from JWT
    # -----------------------------

    user_id = payload.get(
        "sub"
    )


    user = get_user(
        user_id
    )


    # -----------------------------
    # User no longer exists
    # -----------------------------

    if user is None:

        return JSONResponse(

            status_code=401,

            content={
                "authenticated": False
            }
        )


    # -----------------------------
    # Valid session
    # -----------------------------

    return {

        "authenticated": True,

        "user": {

            "user_id":
                user["user_id"],

            "name":
                user["name"],

            "email":
                user["email"]
        }
    }


# ============================================================
# LOGOUT
# ============================================================

@app.post("/api/logout")
async def logout():

    response = JSONResponse(

        content={

            "success": True,

            "message": "Logged out"
        }
    )


    response.delete_cookie(
        key="access_token"
    )


    return response

