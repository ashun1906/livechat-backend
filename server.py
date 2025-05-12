from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import json
import uvicorn

app = FastAPI()

# Cho phép truy cập từ web client (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://livechat-frontend-self.vercel.app"],  # KHÔNG có dấu /
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đọc user từ file json
def load_users():
    with open("users.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Lưu user vào file json
def save_users(users):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# Dữ liệu demo (bạn sẽ lấy từ app thật)
PLATFORMS = [
    {"platform": "69VN", "chatting": 43},
    {"platform": "NH88", "chatting": 21},
    {"platform": "66ZZ", "chatting": 16},
    {"platform": "U34", "chatting": 12},
    {"platform": "16bet", "chatting": 2},
    {"platform": "116,BET", "chatting": 1},
    {"platform": "UM,BET", "chatting": 1},
    {"platform": "SW777", "chatting": 1},
    {"platform": "NN55", "chatting": 1},
    {"platform": "FB,BET", "chatting": 1},
    {"platform": "ZZ66bet", "chatting": 1},
    {"platform": "BKB,BET", "chatting": 1},
    {"platform": "776,BET", "chatting": 0},
    {"platform": "VX777BET", "chatting": 0},
    {"platform": "WINVIP", "chatting": 0},
    {"platform": "TTTT777", "chatting": 0},
    {"platform": "W78", "chatting": "-"},
    {"platform": "661bet", "chatting": "-"},
    {"platform": "HH789", "chatting": "-"}
]

# Đăng nhập
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users = load_users()
    for user in users:
        if user["username"] == form_data.username and user["password"] == form_data.password:
            # Trả về token đơn giản (ở đây là username, thực tế nên dùng JWT)
            return {"access_token": user["username"], "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")

# Lấy dữ liệu (yêu cầu token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/data")
def get_data(token: str = Depends(oauth2_scheme)):
    # Kiểm tra token (ở đây là username)
    users = load_users()
    if not any(u["username"] == token for u in users):
        raise HTTPException(status_code=401, detail="Token không hợp lệ")
    # Đọc dữ liệu thực tế từ file platforms.json
    try:
        with open("platforms.json", "r", encoding="utf-8") as f:
            platforms = json.load(f)
    except Exception:
        platforms = []
    return {"data": platforms}

# Thêm user (chỉ admin mới được phép, ví dụ hardcode)
class UserCreate(BaseModel):
    username: str
    password: str

@app.post("/add_user")
def add_user(user: UserCreate, token: str = Depends(oauth2_scheme)):
    if token != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin được phép thêm user")
    users = load_users()
    if any(u["username"] == user.username for u in users):
        raise HTTPException(status_code=400, detail="User đã tồn tại")
    users.append({"username": user.username, "password": user.password})
    save_users(users)
    return {"msg": "Thêm user thành công"}

class ChangePasswordRequest(BaseModel):
    new_password: str

@app.post("/change-password")
def change_password(req: ChangePasswordRequest, token: str = Depends(oauth2_scheme)):
    if not req.new_password or len(req.new_password) < 4:
        raise HTTPException(status_code=400, detail="Mật khẩu quá ngắn")
    users = load_users()
    found = False
    for u in users:
        if u["username"] == token:
            u["password"] = req.new_password
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")
    save_users(users)
    return {"success": True}

@app.post("/update-platforms")
async def update_platforms(request: Request, token: str = Depends(oauth2_scheme)):
    if token != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền")
    data = await request.json()
    with open("platforms.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"success": True}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True) 
    