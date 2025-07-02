import redis
from config_no_docker import get_redis_url

def clear_redis_data():
    """Clear all Redis data - USE ONLY IN DEVELOPMENT"""
    try:
        r = redis.Redis.from_url(get_redis_url(), decode_responses=True)
        r.flushdb()
        print("✅ Redis data cleared successfully")
        return True
    except Exception as e:
        print(f"❌ Error clearing Redis data: {e}")
        return False

def list_redis_keys():
    """List all Redis keys for debugging"""
    try:
        r = redis.Redis.from_url(get_redis_url(), decode_responses=True)
        keys = r.keys('*')
        print(f"📋 Found {len(keys)} Redis keys:")
        for key in keys:
            print(f"  - {key}")
        return keys
    except Exception as e:
        print(f"❌ Error listing Redis keys: {e}")
        return []

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "clear":
            clear_redis_data()
        elif sys.argv[1] == "list":
            list_redis_keys()
        else:
            print("Usage: python dev_utils.py [clear|list]")
    else:
        print("Usage: python dev_utils.py [clear|list]")
        print("  clear - Clear all Redis data")
        print("  list  - List all Redis keys")