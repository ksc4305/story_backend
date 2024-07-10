from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.routers import story
import os

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # 모든 출처를 허용하려면 ["*"]로 설정, 특정 출처를 허용하려면 ["http://localhost:3000"] 등으로 설정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 경로 설정
build_path = os.path.join(os.path.dirname(__file__), "../../story-app/build")
if not os.path.exists(build_path):
    raise RuntimeError(f"Build directory '{build_path}' does not exist")

app.mount(
    "/static", StaticFiles(directory=os.path.join(build_path, "static")), name="static"
)


# React index.html 경로 설정
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    file_path = os.path.join(build_path, "index.html")
    if not os.path.exists(file_path):
        raise RuntimeError(f"Index file '{file_path}' does not exist")
    return FileResponse(file_path)


# 기타 경로에 대한 설정
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_static_files(full_path: str):
    file_path = os.path.join(build_path, full_path)
    if not os.path.exists(file_path):
        file_path = os.path.join(build_path, "index.html")
    return FileResponse(file_path)


app.include_router(story.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
