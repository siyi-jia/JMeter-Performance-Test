from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/posts', methods=['POST', 'GET'])
def mock_posts():
    if request.method == 'POST':
        data = request.json
        return jsonify({"id": 123, "message": "Created successfully", "received_data": data}), 201
    return jsonify({"status": "success"}), 200

# 新增：支持 /posts/123 这样的 GET 查询
@app.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    return jsonify({"id": post_id, "status": "success", "title": "Mock Data"}), 200

if __name__ == '__main__':
    # 关键：加入 threaded=True 开启多线程处理并发
    app.run(host='127.0.0.1', port=8080, threaded=True)