import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

import sqlite3
def get_user(username):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = '" + username + "'")
    return cursor.fetchall()

app = Flask(__name__)
CORS(app)

def get_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )

@app.route('/api/notes', methods=['GET'])
def get_notes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM notes ORDER BY id DESC')
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(notes)

@app.route('/api/notes', methods=['POST'])
def add_note():
    content = request.json.get('content')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notes (content) VALUES (%s)', (content,))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({'id': new_id, 'content': content})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = %s', (note_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'deleted': note_id})

@app.route('/health', methods=['GET'])
def health():
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)  # NOSONAR
