from pymongo import MongoClient

# ---- PUT YOUR CONNECTION STRING HERE ----
MONGO_URI = "mongodb+srv://dimply:Dimply2004@lab-cluster.csxjcka.mongodb.net/?retryWrites=true&w=majority&appName=lab-cluster"

try:
    client = MongoClient(MONGO_URI)
    client.admin.command("ping")
    print("🌟 MongoDB connected successfully!")
except Exception as e:
    print("❌ Error:", e)
