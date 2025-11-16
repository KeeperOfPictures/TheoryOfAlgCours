from flask import Flask, request, jsonify
import sqlite3
import json
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = '/app/data/algorithm_results.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS algorithm_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            graph_name TEXT NOT NULL,
            graph_data TEXT NOT NULL,
            algorithm_name TEXT NOT NULL,
            mst_weight REAL NOT NULL,
            mst_edges TEXT NOT NULL,
            execution_time REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Database API is running'})

@app.route('/results', methods=['POST'])
def save_result():
    try:
        data = request.json
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO algorithm_results 
            (graph_name, graph_data, algorithm_name, mst_weight, mst_edges, execution_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['graph_name'],
            json.dumps(data['graph_data']),
            data['algorithm_name'],
            data['mst_weight'],
            json.dumps(data['mst_edges']),
            data.get('execution_time')
        ))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'id': result_id, 'status': 'success'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['GET'])
def get_all_results():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM algorithm_results ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'graph_name': row[1],
                'graph_data': json.loads(row[2]),
                'algorithm_name': row[3],
                'mst_weight': row[4],
                'mst_edges': json.loads(row[5]),
                'execution_time': row[6],
                'timestamp': row[7]
            })
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<int:result_id>', methods=['GET'])
def get_result(result_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM algorithm_results WHERE id = ?', (result_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                'id': row[0],
                'graph_name': row[1],
                'graph_data': json.loads(row[2]),
                'algorithm_name': row[3],
                'mst_weight': row[4],
                'mst_edges': json.loads(row[5]),
                'execution_time': row[6],
                'timestamp': row[7]
            })
        else:
            return jsonify({'error': 'Result not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM algorithm_results WHERE id = ?', (result_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': f'Result {result_id} deleted'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['DELETE'])
def clear_all_results():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM algorithm_results')
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'All results cleared'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("Database API started on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000)