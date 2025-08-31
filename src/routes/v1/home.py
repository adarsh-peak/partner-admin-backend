from fastapi import APIRouter, Request, Depends
from src.services.home.controller import HomeController
from src.services.home.serializer import ConsentInBound
from src.lib.authorisation import AuthorisationService
router = APIRouter()


@router.get("/")
async def index(request: Request, _ = Depends(AuthorisationService.authorize_user)):
    return await HomeController.index(request)


@router.get("/consentview")
async def consent_view(request: Request):
    return await HomeController.consent_view(request)


@router.post("/processk1consent")
async def process_k1_consent(request: Request, payload: ConsentInBound):
    return await HomeController.process_k1_consent(request, payload)
