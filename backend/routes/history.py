import logging
from fastapi import APIRouter , Path as FPath , Query
from backend.services.snapshot import load_snapshot , load_snapshots

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/timeline")
def get_timeline(days : int = Query(default=30 , ge=1 , le=90)):
    try: 
        snapshots = load_snapshots(days=days)
        return {
            "status" : "success" , 
            "data" : {
                "snapshots" : snapshots  , 
                "count" : len(snapshots)
            }
        }

    except Exception as e:
        logger.exception("Timeline route failed")
        return {"status" : "error" , "message" : str(e) , "data" : None}
    

@router.get("/snapshot/{date_key}")
def get_snapshot(date_key : str = FPath(..., description="YYYY-MM-DD")):
    try:
        snap = load_snapshot(date_key)
        if not snap:
            return {"status" : "error" , "message" : f"No snapshot found for {date_key}" , "data" : None}

        return {"status" : "success" , "data" : snap}
    except Exception as e : 
        logger.exception("Snapshots route failed")
        return {"status" : "error" , "message" : str(e) , "data" : None}