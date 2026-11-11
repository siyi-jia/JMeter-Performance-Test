from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)
# 使用集合存储所有有效的 Token，解决高并发下 Token 被覆盖的问题
valid_tokens = set()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')

    if not username:
        return jsonify({"msg": "用户名不能为空"}), 400

    # 生成唯一 Token 并存入集合
    token = str(uuid.uuid4())
    valid_tokens.add(token)

    return jsonify({"token": token}), 200


@app.route('/cart/checkout', methods=['POST'])
def checkout():
    # 1. 鉴权拦截：验证请求头
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"msg": "未授权"}), 401

    token = auth_header.split(" ")[1]
    if token not in valid_tokens:
        return jsonify({"msg": "Token无效"}), 401

    # 2. 数据解析防弹衣（防止高并发下空数据导致 400 崩溃）
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"msg": "请求体格式错误"}), 400

    try:
        total_amount = float(data.get('total_amount', 0))
    except (ValueError, TypeError):
        return jsonify({"msg": "金额必须为数字"}), 400

    if total_amount <= 0:
        return jsonify({"msg": "金额必须大于0"}), 400

    # 3. 双十一核心业务逻辑
    final_price = total_amount
    if total_amount >= 300:
        final_price -= 50
    if data.get('user_level') == 'VIP':
        final_price *= 0.9
    if data.get('has_coupon'):
        final_price -= 20
    if final_price < 0:
        final_price = 0

    return jsonify({
        "msg": "下单成功",
        "original_amount": total_amount,
        "final_price": round(final_price, 2)
    }), 200


if __name__ == '__main__':
    print("🚀 双十一高并发生产级靶场已启动！")
    from waitress import serve
    # waitress 是生产级的 WSGI 服务器，抗并发能力极强！
    serve(app, host='127.0.0.1', port=8080, threads=50)