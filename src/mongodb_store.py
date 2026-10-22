"""Optional MongoDB storage. The project works without a MongoDB server."""
import os

def get_collection():
    uri=os.getenv("MONGODB_URI","").strip()
    if not uri:
        return None, "MONGODB_URI is not set"
    try:
        from pymongo import MongoClient, ASCENDING, DESCENDING
        client=MongoClient(uri, serverSelectionTimeoutMS=2500)
        client.admin.command("ping")
        collection=client["api_log_intelligence"]["api_logs"]
        # Indexes speed up common filters and chronological queries.
        collection.create_index([("endpoint",ASCENDING)])
        collection.create_index([("status_code",ASCENDING)])
        collection.create_index([("timestamp",DESCENDING)])
        collection.create_index([("endpoint",ASCENDING),("timestamp",DESCENDING)])
        return collection, None
    except Exception as exc:
        return None, str(exc)

def insert_logs(records):
    collection, error=get_collection()
    if collection is None:
        return {"ok":False,"message":f"MongoDB unavailable: {error}"}
    if records:
        collection.insert_many(records, ordered=False)
    return {"ok":True,"inserted":len(records)}

def endpoint_failure_pipeline():
    """MongoDB aggregation pipeline: endpoint-level requests, failures and error rate."""
    return [
        {"$group":{
            "_id":"$endpoint",
            "requests":{"$sum":1},
            "failures":{"$sum":{"$cond":[{"$gte":["$status_code",400]},1,0]}},
            "avg_latency_ms":{"$avg":"$response_time_ms"}
        }},
        {"$project":{
            "_id":0,"endpoint":"$_id","requests":1,"failures":1,
            "error_rate_pct":{"$multiply":[{"$divide":["$failures","$requests"]},100]},
            "avg_latency_ms":{"$round":["$avg_latency_ms",2]}
        }},
        {"$sort":{"failures":-1}}
    ]

def run_endpoint_aggregation():
    collection, error=get_collection()
    if collection is None:
        return None, error
    return list(collection.aggregate(endpoint_failure_pipeline())), None
