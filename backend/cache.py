import json
import time
import logging

logger = logging.getLogger(__name__)

redis_client = None

def _get_redis(): 
    global redis_client
    if redis_client is not None: 
        return redis_client
    try: 
        import redis
        from backend.config import settings
        redis_client = redis.from_url(settings.REDIS_URL , decode_responses = True)
        redis_client.ping()
        logger.info("Reddis Connected")
    except Exception as e : 
        logger.warning(f"Redis Unavailable ({e}) - using in-memory fallback")
        redis_client = None
    return redis_client

mem_cache : dict[str , dict] = {}

def get_cached(key : str):
    """ return cached value or none if expired or missing"""
    r = _get_redis()
    if r : 
        try: 
            val = r.get(key)
            return json.loads(val) if val else None
        except Exception : 
            pass

    entry = mem_cache.get(key)
    if entry and (entry["expires_at"] is None or time.time() < entry["expires_at"]): 
        return entry["value"]
    return None

def set_cached(key : str , value , ttl : int = 3600):
    """ store value with TTL """
    r = _get_redis()
    if r : 
        try: 
            r.set(key , json.dumps(value , default=str) , ex= ttl)
            return
        except Exception : 
            pass
    mem_cache[key] = {
        "value" : value , 
        "expires_at" : time.time() + ttl if ttl else None
    }

def invalidate(key : str): 
    """ delete cached entry"""
    r = _get_redis()
    if r : 
        try: 
            r.delete(key)
        except Exception : 
            pass
    mem_cache.pop(key  , None)
    