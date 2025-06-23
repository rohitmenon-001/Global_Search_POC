from flask import Flask, request, jsonify
from layer1.db_connection import get_db_connection
from utils.embedding_generator import generate_embedding
from chroma_module.multitenant_chroma import upsert_tenant_embedding, get_tenant_collection
#from auth_middleware import tenant_auth_required
from auth.tenant_auth import tenant_auth_required


import datetime

app = Flask(__name__)

@app.route("/api/tenant/<tenant_id>/orders", methods=["POST"])
@tenant_auth_required
def insert_order(tenant_id):
    data = request.json
    order_id = data.get("order_id")
    customer_id = data.get("customer_id")
    order_date = data.get("order_date", str(datetime.date.today()))
    amount = float(data.get("amount", 0))
    status = data.get("status", "PENDING")

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO orders (order_id, customer_id, order_date, amount, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, customer_id, order_date, amount, status)
        )
        cur.execute(
            "INSERT INTO change_log (record_id, tenant_id) VALUES (?, ?)",
            (order_id, tenant_id)
        )
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"message": f"Order {order_id} inserted for tenant {tenant_id}"}), 200


@app.route("/api/tenant/<tenant_id>/refresh", methods=["POST"])
@tenant_auth_required
def refresh_tenant(tenant_id):
    from delta_refresh.tenant_pipeline import run_tenant_pipeline
    try:
        run_tenant_pipeline()
        return jsonify({"message": f"Refreshed embeddings for tenant {tenant_id}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tenant/<tenant_id>/search", methods=["POST"])
@tenant_auth_required
def semantic_search(tenant_id):
    query = request.json.get("query", "")
    embedding = generate_embedding(query)
    collection = get_tenant_collection(tenant_id)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=3,
        include=["documents", "distances"]
    )

    response = []
    for i in range(len(results["ids"][0])):
        response.append({
            "record_id": results["ids"][0][i],
            "sentence": results["documents"][0][i],
            "score": results["distances"][0][i]
        })

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(debug=True)
