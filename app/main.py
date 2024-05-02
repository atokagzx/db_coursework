### ! /usr/bin/env python3

# FastAPI imports
from fastapi import FastAPI, Request
from fastapi.responses import (
    RedirectResponse,
    JSONResponse
)

# Custom imports
from routes._authentication_routes import router as auth_router
from routes._courses_routes import router as courses_router
from routes._modules_routes import router as modules_router
from routes._assignment_routes import router as assignment_router
from routes._material_routes import router as material_router
from routes._users_routes import router as users_router
from routes._test_routes import router as test_router

from configure import *

app = FastAPI(
    title="Studyboard API",
    description="API for Studyboard", 
    version="0.0.1",
    openapi_tags=tags_metadata
)

for route in [auth_router,
                courses_router,
                modules_router,
                assignment_router,
                material_router,
                users_router,
                test_router
                ]:
    
    app.include_router(route)


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url='/docs')


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    def check_auth():
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                method, token = auth_header.split(' ')
            except ValueError:
                logger.info(f"got unexpected auth header")
                method = None
                token = None
            if method is None or token is None:
                raise HTTPException(status_code=401, detail="Invalid Authorization header")
            if method.lower() == 'bearer':
                logger.info(f"request: {request.url} by user {get_current_user(token)}")
            else:
                logger.info(f"got unexpected auth method: {method}")
        else:
            logger.info(f"Request: {request.url} by anonymous user")

    try:
        check_auth()
    except HTTPException as e:
        response = JSONResponse(content=e.detail, status_code=e.status_code)
        return response
        
    response = await call_next(request)
    return response
