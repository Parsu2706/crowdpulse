from backend.services.digest import generate_digest
import logging 
from fastapi import APIRouter
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/digest")
def get_digest():
    try : 
        result = generate_digest(force=False)
        return {"status" : "success" , "data" : result}
    except Exception as e : 
        logger.exception("Digest GET Failed")
        return {"status" : "error" , "message" : str(e) , "data" : None}

@router.post("/digest/force")
def force_digest():
    try:
        result = generate_digest(force=True)
        return {"status" : "success" , "data" : result}
    except Exception as e:
        logger.exception("Digest force-refresh failed")
        return {"status" : "error" , "message" :str(e) , "data" : None}
    