from fastapi import  APIRouter


router = APIRouter()


@router.get("something/")
def get_user():
    return {"username": "nababa"}

