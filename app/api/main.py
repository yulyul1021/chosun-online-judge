from fastapi import APIRouter

from app.api.routes import courses, login, problems, users, submissions, admin

api_router = APIRouter()
api_router.include_router(admin.router, prefix="/management", tags=["admin"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(problems.router, prefix="/problems", tags=["problems"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
api_router.include_router(users.router, prefix="/users", tags=["users"])