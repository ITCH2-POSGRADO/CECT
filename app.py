from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
import os

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), "data.db")


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_type TEXT,
                data TEXT
            )
            """
        )


@app.before_first_request
def setup():
    init_db()


@app.route("/")
def index():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.execute(
            "SELECT id, order_type, data FROM orders ORDER BY id DESC"
        )
        items = [
            {"id": row[0], "order_type": row[1], "data": json.loads(row[2])}
            for row in cur.fetchall()
        ]
    return render_template("index.html", items=items)


@app.route("/create/<order_type>", methods=["GET", "POST"])
def create(order_type):
    if request.method == "POST":
        data = request.form.to_dict()
        with sqlite3.connect(DATABASE) as conn:
            conn.execute(
                "INSERT INTO orders (order_type, data) VALUES (?, ?)",
                (order_type, json.dumps(data)),
            )
        return redirect(url_for("index"))
    return render_template("form.html", order_type=order_type)


@app.route("/view/<int:order_id>")
def view(order_id):
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.execute(
            "SELECT order_type, data FROM orders WHERE id = ?",
            (order_id,),
        )
        row = cur.fetchone()
        if row:
            data = json.loads(row[1])
            return render_template(
                "view.html",
                order_id=order_id,
                order_type=row[0],
                data=data,
            )
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
