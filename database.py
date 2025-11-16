import sqlite3
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional

class GraphDatabase:
    def __init__(self, db_path="data/algorithm_results.db", use_docker_api=False, api_url="http://localhost:5000"):
        self.use_docker_api = use_docker_api
        self.api_url = api_url
        self.db_path = db_path
        
        if not self.use_docker_api:
            self.init_database()
        else:
            self._check_api_health()
    
    def _check_api_health(self):
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                print("Подключение к Docker Database API установлено")
            else:
                raise Exception(f"API returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Не удалось подключиться к Docker Database API: {e}")
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
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
    
    def save_algorithm_result(self, graph_name: str, graph_data: dict, 
                            algorithm_name: str, mst_weight: float, 
                            mst_edges: list, execution_time: float = None) -> int:
        if self.use_docker_api:
            response = requests.post(f"{self.api_url}/results", json={
                'graph_name': graph_name,
                'graph_data': graph_data,
                'algorithm_name': algorithm_name,
                'mst_weight': mst_weight,
                'mst_edges': mst_edges,
                'execution_time': execution_time
            })
            
            if response.status_code == 200:
                return response.json()['id']
            else:
                raise Exception(f"API error: {response.json().get('error', 'Unknown error')}")
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO algorithm_results 
                (graph_name, graph_data, algorithm_name, mst_weight, mst_edges, execution_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                graph_name,
                json.dumps(graph_data, ensure_ascii=False),
                algorithm_name,
                mst_weight,
                json.dumps(mst_edges, ensure_ascii=False),
                execution_time
            ))
            
            result_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return result_id
    
    def get_all_results(self) -> List[dict]:
        if self.use_docker_api:
            response = requests.get(f"{self.api_url}/results")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API error: {response.json().get('error', 'Unknown error')}")
        else:
            conn = sqlite3.connect(self.db_path)
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
            return results
    
    def get_result(self, result_id: int) -> Optional[dict]:
        if self.use_docker_api:
            response = requests.get(f"{self.api_url}/results/{result_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise Exception(f"API error: {response.json().get('error', 'Unknown error')}")
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM algorithm_results WHERE id = ?', (result_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'graph_name': row[1],
                    'graph_data': json.loads(row[2]),
                    'algorithm_name': row[3],
                    'mst_weight': row[4],
                    'mst_edges': json.loads(row[5]),
                    'execution_time': row[6],
                    'timestamp': row[7]
                }
            return None
    
    def delete_result(self, result_id: int):
        if self.use_docker_api:
            response = requests.delete(f"{self.api_url}/results/{result_id}")
            if response.status_code != 200:
                raise Exception(f"API error: {response.json().get('error', 'Unknown error')}")
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM algorithm_results WHERE id = ?', (result_id,))
            conn.commit()
            conn.close()
    
    def clear_all_results(self):
        if self.use_docker_api:
            response = requests.delete(f"{self.api_url}/results")
            if response.status_code != 200:
                raise Exception(f"API error: {response.json().get('error', 'Unknown error')}")
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM algorithm_results')
            conn.commit()
            conn.close()
    
    def get_database_info(self) -> dict:
        if self.use_docker_api:
            return {
                'type': 'Docker SQLite API',
                'url': self.api_url,
                'status': 'connected'
            }
        else:
            return {
                'type': 'Local SQLite',
                'path': self.db_path
            }