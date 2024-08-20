import os, sys, random

import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from baize.asgi import FileResponse
from starlette.routing import Route

current_path = ""
current_file = ""
showfile = ""
# files = []

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
for ext in list(ALLOWED_EXTENSIONS):
    ALLOWED_EXTENSIONS.add(ext.upper())

NEWEST_N_FILES = 5

def get_file_response(filename):
    path = os.path.join(current_path, filename)
    try:
        return FileResponse(path)
    except:
        return HTMLResponse(f"File not found: {filename}")

def get_current_path():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app path into sys._MEIPASS.
        return os.path.dirname(sys.executable)
    else:
        # If the application is run as a script, use the current file path.
        return os.path.dirname(os.path.realpath(__file__))

async def homepage(request):
    try:
        with open('index.html', 'r') as f:
            return HTMLResponse(f.read())
    except:
        return HTMLResponse("index.html not found")


async def img(request):
    global current_file
    global showfile

    files = os.listdir(current_path)

    # Filter for allowed extensions
    files = [f for f in files if f.split(".")[-1] in ALLOWED_EXTENSIONS]

    # Sort by date
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    if len(files) == 0:
        return HTMLResponse("No images found")
    
    if current_file == "":
        current_file = files[0]
        return get_file_response(current_file)
        return HTMLResponse("<br>".join(files) + f"<br>current: {current_file}")
    elif files[0] != current_file:
        index = files.index(current_file)
        current_file = files[index-1]
        return get_file_response(current_file)
        return HTMLResponse("<br>".join(files) + f"<br>current: {current_file}")
    

    # Random Fallback
    # Only the newest N files
    files = files[:NEWEST_N_FILES]
    nextfile = showfile
    while nextfile == showfile:
        nextfile = random.choice(files)
    
    showfile = nextfile

    return get_file_response(showfile)
    return HTMLResponse("<br>".join(files) + f"<br>fallback: {showfile}")

app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/img', img),
])


if __name__ == "__main__":

    current_path = get_current_path()

    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=5000,
        log_level="info",
        workers=1)

    server = uvicorn.Server(config)
    server.run()
