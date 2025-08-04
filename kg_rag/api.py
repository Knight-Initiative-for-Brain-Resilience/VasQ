from flask import Flask, request, jsonify
import os, subprocess

app = Flask(__name__)

@app.route("/query", methods=["POST"])
def query_kg_rag():
    user_input = request.json.get("query", "")

    base_dir = "/app"
    script_path = "kg_rag.generation.text_generation"

    command = [
        "conda", "run", "-n", "kg_env",
        "python", "-m", script_path,
        "-g", "gpt-4",
        "--query", user_input
    ]

    try:
        result = subprocess.check_output(
            command,
            cwd=base_dir,
            stderr=subprocess.STDOUT
        )
        return jsonify({"result": result.decode("utf-8")})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.output.decode("utf-8")}), 500