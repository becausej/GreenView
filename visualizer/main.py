from fastapi import FastAPI
from starlette.responses import FileResponse 

app = FastAPI()


@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/main.js")
def read_main():
    return FileResponse("main.js")

@app.get("/style.css")
def read_main():
    return FileResponse("style.css")

@app.get("/geojson.json")
def read_geojson():
    return FileResponse("../output/geojson.json")

