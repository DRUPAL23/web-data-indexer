from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import router

app = FastAPI(title='Web Data Indexer API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(',')], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(router)

@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'api'}
