from fastapi import APIRouter, Request, Depends
from typing import Optional
from src.services.financial_statement.controller import FinancialStatementController
from src.services.home.serializer import ConsentInBound
from src.lib.authorisation import AuthorisationService
router = APIRouter()


@router.get("/quaterly-reports")
async def index(request: Request, mid: Optional[str] = None, date: Optional[str] = None, _ = Depends(AuthorisationService.authorize_user)):
    return await FinancialStatementController.get_quaterly_report(request, mid, date)

@router.get("/semiannual-reports")
async def semiannual_report(request: Request, mid: Optional[str] = None, date: Optional[str] = None, _ = Depends(AuthorisationService.authorize_user)):
    return await FinancialStatementController.get_semi_annual_reports(request, mid, date)

@router.get("/annual-reports")
async def annual_report(request: Request, mid: Optional[str] = None, date: Optional[str] = None, _ = Depends(AuthorisationService.authorize_user)):
    return await FinancialStatementController.get_quaterly_report(request, mid, date)



