# from flask import Flask, request, jsonify, session
# from flask_cors import CORS
# import pandas as pd
# import json
# import os
# from functools import wraps
# from datetime import timedelta

# app = Flask(__name__)
# app.secret_key = 'your-secret-key-here'  # Change this in production

# # Configure session
# app.config.update(
#     SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
#     SESSION_COOKIE_HTTPONLY=True,
#     SESSION_COOKIE_SAMESITE='Lax',
#     PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
# )

# # Configure CORS with specific settings for credentials
# CORS(app, 
#      supports_credentials=True,
#      origins=['http://localhost:*', 'http://127.0.0.1:*', 'file://*'],  # Allow local development
#      allow_headers=['Content-Type', 'Authorization'],
#      expose_headers=['Content-Type', 'Authorization'])

# # Load Iris dataset
# try:
#     df = pd.read_csv('iris.csv')
# except:
#     # If no CSV file, create sample data
#     from sklearn.datasets import load_iris
#     iris = load_iris()
#     df = pd.DataFrame(data=iris.data, columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
#     df['species'] = iris.target
#     df['species'] = df['species'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})
#     df.to_csv('iris.csv', index=False)

# # Simple user database (in production, use proper authentication)
# USERS = {
#     'setosa@example.com': {
#         'password': 'password123',
#         'access': 'setosa'
#     },
#     'virginica@example.com': {
#         'password': 'password123',
#         'access': 'virginica'
#     }
# }

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user' not in session:
#             return jsonify({'error': 'Not authenticated'}), 401
#         return f(*args, **kwargs)
#     return decorated_function

# @app.route('/api/login', methods=['POST', 'OPTIONS'])
# def login():
#     if request.method == 'OPTIONS':
#         # Preflight request
#         return '', 200
    
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({'success': False, 'error': 'No data provided'}), 400
            
#         email = data.get('email')
#         password = data.get('password')
        
#         if not email or not password:
#             return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
#         if email in USERS and USERS[email]['password'] == password:
#             session['user'] = email
#             session['access'] = USERS[email]['access']
#             session.permanent = True  # Make session persistent
            
#             return jsonify({
#                 'success': True,
#                 'user': email,
#                 'access': USERS[email]['access']
#             })
        
#         return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
#     except Exception as e:
#         app.logger.error(f"Login error: {str(e)}")
#         return jsonify({'success': False, 'error': 'Server error'}), 500

# @app.route('/api/logout', methods=['POST', 'OPTIONS'])
# def logout():
#     if request.method == 'OPTIONS':
#         return '', 200
        
#     session.clear()
#     return jsonify({'success': True})

# @app.route('/api/data', methods=['GET', 'OPTIONS'])
# @login_required
# def get_data():
#     if request.method == 'OPTIONS':
#         return '', 200
        
#     try:
#         user_access = session.get('access', 'setosa')
        
#         # Filter data based on user access
#         filtered_df = df[df['species'] == user_access]
        
#         # Prepare data for frontend
#         data = {
#             'sepal_length': filtered_df['sepal_length'].tolist(),
#             'sepal_width': filtered_df['sepal_width'].tolist(),
#             'petal_length': filtered_df['petal_length'].tolist(),
#             'petal_width': filtered_df['petal_width'].tolist(),
#             'species': user_access
#         }
        
#         return jsonify(data)
        
#     except Exception as e:
#         app.logger.error(f"Data fetch error: {str(e)}")
#         return jsonify({'error': 'Server error'}), 500

# @app.route('/api/check-auth', methods=['GET', 'OPTIONS'])
# def check_auth():
#     if request.method == 'OPTIONS':
#         return '', 200
        
#     if 'user' in session:
#         return jsonify({
#             'authenticated': True,
#             'user': session['user'],
#             'access': session.get('access')
#         })
#     return jsonify({'authenticated': False})

# # Add a test route to verify the server is running
# @app.route('/api/test', methods=['GET'])
# def test():
#     return jsonify({'status': 'Server is running'})

# if __name__ == '__main__':
#     app.run(debug=True, port=5000, host='0.0.0.0')