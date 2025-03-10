from flask import Flask, request, jsonify
# from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from database import add_face, get_all_faces, find_face_by_embedding, delete_face
from face_recognition import detect_face, extract_features

app = Flask(__name__)
# CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/api/face", methods=["GET"])
def get_faces():
    """Mengambil semua wajah yang telah terdaftar"""
    faces = get_all_faces()
    return jsonify({"faces": faces})

@app.route("/api/face/register", methods=["POST"])
def register_face():
    """Mendaftarkan wajah baru"""
    if "image" not in request.files:
        return jsonify({"error": "Tidak ada gambar yang diunggah"}), 400

    file = request.files["image"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    detected_face = detect_face(filepath)
    if detected_face is None:
        return jsonify({"error": "Wajah tidak terdeteksi"}), 400

    features = extract_features(filepath)
    if features is None:
        return jsonify({"error": "Gagal mengekstrak fitur"}), 500

    face_id = add_face(filename, features)
    return jsonify({"message": "Wajah berhasil didaftarkan", "face_id": str(face_id)}), 201

@app.route("/api/face/recognize", methods=["POST"])
def recognize_face():
    """Mengenali wajah dari gambar yang diunggah"""
    if "image" not in request.files:
        return jsonify({"error": "Tidak ada gambar yang diunggah"}), 400

    file = request.files["image"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    features = extract_features(filepath)
    if features is None:
        return jsonify({"error": "Gagal mengekstrak fitur"}), 500

    matched_face = find_face_by_embedding(features)
    if matched_face:
        return jsonify({"message": "Wajah dikenali", "name": matched_face["name"]}), 200
    else:
        return jsonify({"message": "Wajah tidak ditemukan"}), 404

@app.route("/api/face/<face_id>", methods=["DELETE"])
def delete_face_route(face_id):
    """Menghapus wajah berdasarkan ID"""
    deleted_count = delete_face(face_id)
    if deleted_count:
        return jsonify({"message": "Wajah berhasil dihapus"}), 200
    return jsonify({"error": "Wajah tidak ditemukan"}), 404

if __name__ == "__main__":
    app.run(debug=True)
