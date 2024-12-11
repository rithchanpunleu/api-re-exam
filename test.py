from flask import Flask, jsonify, g
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = "database.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, check_same_thread=False)
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.get("/videos/<course_id>")
def get_video_playlist(course_id):
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Validate that course_id is numeric
        if not course_id.isdigit():
            return jsonify({"error": "Invalid course_id provided"}), 400
        
        # Cast course_id to an integer
        course_id = int(course_id)
        
        # Fetch course details
        course_result = cursor.execute(
            "SELECT title, created_by, video_count FROM courses WHERE id = ?",
            (course_id,)
        )
        course = course_result.fetchone()
        
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        # Fetch video details for the given course
        videos_result = cursor.execute(
            "SELECT title, duration FROM videos WHERE course_id = ?",
            (course_id,)
        )
        videos = videos_result.fetchall()
        
        # Construct the response
        response = {
            "courseTitle": course[0],
            "createdBy": course[1],
            "videoCount": course[2],
            "videos": [{"title": video[0], "duration": video[1]} for video in videos]
        }
        
        return jsonify(response)
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.commit()



if __name__ == '__main__':
    app.run(debug=True, port=5050)
