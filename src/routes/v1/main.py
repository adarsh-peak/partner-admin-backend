from fastapi import APIRouter
from src.routes.v1 import home, financial_statements

api_router = APIRouter()

api_router.include_router(home.router, prefix='/v1/home', tags=["Home"])
api_router.include_router(financial_statements.router, prefix='/v1/financial-statement', tags=["Financial Statements"])