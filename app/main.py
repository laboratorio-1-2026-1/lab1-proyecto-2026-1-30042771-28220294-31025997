from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return "Una nueva API, equipo!"
