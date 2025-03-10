from pymongo import MongoClient

# Koneksi ke database MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["face_recognition_db"]
face_collection = db["faces"]

def add_face(name, embedding):
    """Menambahkan wajah ke database"""
    face_data = {"name": name, "embedding": embedding}
    return face_collection.insert_one(face_data).inserted_id

def get_all_faces():
    """Mengambil semua wajah dari database"""
    return list(face_collection.find({}, {"_id": 1, "name": 1}))

def find_face_by_embedding(embedding, threshold=0.5):
    """Mencari wajah berdasarkan kemiripan embedding"""
    from deepface.commons import distance as dst
    faces = face_collection.find()
    for face in faces:
        dist = dst.findCosineDistance(embedding, face["embedding"])
        if dist < threshold:
            return face
    return None

def delete_face(face_id):
    """Menghapus wajah berdasarkan ID"""
    from bson.objectid import ObjectId
    return face_collection.delete_one({"_id": ObjectId(face_id)}).deleted_count
