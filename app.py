#Working for Sql Db
from flask import Flask, request, jsonify
import pyodbc
import os
from prometheus_client import Counter, generate_latest
from flask import Response

app = Flask(__name__)

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status']
)

PRIMARY_DB = os.getenv("PRIMARYDB")
SECONDARY_DB = os.getenv("SECONDARYDB")
DB_USER = os.getenv("DBUSER")
DB_PASSWORD = os.getenv("DBPASSWORD")
DB_NAME = os.getenv("DBNAME")

def get_connection(server):
    conn_str = f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={server};
        DATABASE={DBNAME};
        UID={DBUSER};
        PWD={DBPASSWORD};
    """
    return pyodbc.connect(conn_str)

# 🔹 Health check
# Added a feature branch done
@app.route("/")
def home():
    return "Flask Active-Active DB App Running! pushed by branch previous was closed added one more user"

# 🔹 Create table (run once)
@app.route("/init")
def init_db():
    try:
        conn = get_connection(PRIMARYDB)
        cursor = conn.cursor()

        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name VARCHAR(100)
            )
        """)

        conn.commit()
        return "Table created successfully!"
    except Exception as e:
        return str(e)

@app.route("/add", methods=["GET", "POST"])
def add_user():
    if request.method == "GET":
        return '''
        <h2>Add User</h2>
        <form method="POST">
            Name: <input type="text" name="name" />
            <input type="submit" value="Add User" />
        </form>
        '''

    # POST (from form)
    name = request.form.get("name")

    try:
        conn = get_connection(PRIMARYDB)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (name) VALUES (?)", name)
        conn.commit()

        return f"User '{name}' added successfully! <br><a href='/add'>Go Back</a>"
    except Exception as e:
        return str(e)

# 🔹 Read (Secondary DB)
@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = get_connection(SECONDARYDB)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        users = [{"id": row[0], "name": row[1]} for row in rows]

        return jsonify(users)
    except Exception as e:
        return str(e)


@app.after_request
def track_requests(response):
    REQUEST_COUNT.labels(
        request.method,
        request.path,
        response.status_code
    ).inc()
    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


#Working for CosmosDb
# from flask import Flask, request, jsonify
# from azure.cosmos import CosmosClient
# import os
# import uuid

# app = Flask(__name__)

# COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
# COSMOS_KEY = os.getenv("COSMOS_KEY")

# DB_NAME = "appdb"
# CONTAINER_NAME = "users"

# client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
# database = client.get_database_client(DB_NAME)
# container = database.get_container_client(CONTAINER_NAME)

# # 🔹 Health check
# @app.route("/")
# def home():
#     return "Cosmos Active-Active App Running!"

# # 🔹 Add user (works from ANY region)
# @app.route("/add", methods=["GET", "POST"])
# def add_user():
#     if request.method == "GET":
#         return '''
#         <h2>Add User</h2>
#         <form method="POST">
#             Name: <input type="text" name="name" />
#             <input type="submit" value="Add User" />
#         </form>
#         '''

#     name = request.form.get("name")

#     item = {
#         "id": str(uuid.uuid4()),
#         "name": name
#     }

#     container.create_item(body=item)

#     return f"User '{name}' added! <br><a href='/add'>Go Back</a>"

# # 🔹 Read users (global read)
# @app.route("/users")
# def get_users():
#     items = list(container.read_all_items())

#     return jsonify(items)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
