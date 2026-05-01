from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import FLASK_SECRET_KEY, FLASK_HOST, FLASK_PORT
from backend.database import db
from backend.auth import hash_password, verify_password, generate_token, verify_token

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
CORS(app)

@app.before_request
def init_db():
    if not db.connection or not db.connection.is_connected():
        db.connect()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        request.user_id = payload['user_id']
        request.role = payload['role']
        
        return f(*args, **kwargs)
    
    return decorated


def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.role != required_role:
                return jsonify({'message': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password', 'email']):
        return jsonify({'message': 'Missing required fields'}), 400
    
    username = data['username']
    password = data['password']
    email = data['email']
    role = data.get('role', 'customer')  # Default to 'customer' if not specified
    
    # Validate role
    if role not in ['customer', 'manager']:
        return jsonify({'message': 'Invalid role'}), 400
    
    existing_user = db.fetch_one("SELECT id FROM users WHERE username = %s", (username,))
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    hashed_password = hash_password(password)
    query = "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)"
    
    if db.execute_query(query, (username, hashed_password, email, role)):
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'message': 'Registration failed'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'message': 'Missing username or password'}), 400
    
    username = data['username']
    password = data['password']
    
    user = db.fetch_one("SELECT id, password, role FROM users WHERE username = %s", (username,))
    
    if not user or not verify_password(password, user['password']):
        return jsonify({'message': 'Invalid username or password'}), 401
    
    token = generate_token(user['id'], user['role'])
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user_id': user['id'],
        'role': user['role']
    }), 200


@app.route('/api/manager-login', methods=['POST'])
def manager_login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'message': 'Missing username or password'}), 400
    
    username = data['username']
    password = data['password']
    
    user = db.fetch_one("SELECT id, password, role FROM users WHERE username = %s AND role = %s", 
                        (username, 'manager'))
    
    if not user or not verify_password(password, user['password']):
        return jsonify({'message': 'Invalid manager credentials'}), 401
    
    token = generate_token(user['id'], user['role'])
    return jsonify({
        'message': 'Manager login successful',
        'token': token,
        'user_id': user['id'],
        'role': user['role']
    }), 200


@app.route('/api/search', methods=['GET'])
@token_required
def search_books():
    keyword = request.args.get('keyword', '')
    
    if not keyword:
        return jsonify({'message': 'Search keyword is required'}), 400
    
    query = """
        SELECT id, title, author, price_buy, price_rent, available_count 
        FROM books 
        WHERE title LIKE %s OR author LIKE %s
    """
    
    search_term = f"%{keyword}%"
    books = db.fetch_query(query, (search_term, search_term))
    
    if books is None:
        return jsonify({'message': 'Search failed'}), 500
    
    return jsonify({'books': books}), 200


@app.route('/api/books', methods=['GET'])
@token_required
def get_all_books():
    query = """
        SELECT id, title, author, price_buy, price_rent, available_count 
        FROM books
    """
    
    books = db.fetch_query(query)
    if books is None:
        return jsonify({'message': 'Failed to fetch books'}), 500
    
    return jsonify({'books': books}), 200


@app.route('/api/place-order', methods=['POST'])
@token_required
def place_order():
    data = request.get_json()
    
    if not data or 'items' not in data:
        return jsonify({'message': 'Missing order items'}), 400
    
    items = data['items']  # List of {'book_id': x, 'type': 'buy'/'rent', 'quantity': y}
    
    if not items:
        return jsonify({'message': 'Order must contain at least one item'}), 400
    
    try:
        total = 0
        order_items = []
        
        for item in items:
            book_id = item.get('book_id')
            order_type = item.get('type')  # 'buy' or 'rent'
            quantity = item.get('quantity', 1)
            
            book = db.fetch_one("SELECT price_buy, price_rent FROM books WHERE id = %s", (book_id,))
            if not book:
                return jsonify({'message': f'Book {book_id} not found'}), 404
            
            price = book['price_buy'] if order_type == 'buy' else book['price_rent']
            item_total = price * quantity
            total += item_total
            
            order_items.append({
                'book_id': book_id,
                'type': order_type,
                'quantity': quantity,
                'price': price
            })
        
        order_query = """
            INSERT INTO orders (user_id, total_amount, payment_status, order_date)
            VALUES (%s, %s, %s, NOW())
        """
        db.execute_query(order_query, (request.user_id, total, 'Pending'))
        
        order = db.fetch_one("SELECT id FROM orders WHERE user_id = %s ORDER BY order_date DESC LIMIT 1", 
                            (request.user_id,))
        
        item_query = """
            INSERT INTO order_items (order_id, book_id, item_type, quantity, price)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        for item in order_items:
            db.execute_query(item_query, (order['id'], item['book_id'], item['type'], 
                                         item['quantity'], item['price']))
        
        return jsonify({
            'message': 'Order placed successfully',
            'order_id': order['id'],
            'total': total
        }), 201
        
    except Exception as e:
        print(f"Error placing order: {e}")
        return jsonify({'message': 'Failed to place order'}), 500


@app.route('/api/orders', methods=['GET'])
@token_required
def get_orders():
    query = """
        SELECT id, total_amount, payment_status, order_date 
        FROM orders 
        WHERE user_id = %s
        ORDER BY order_date DESC
    """
    
    orders = db.fetch_query(query, (request.user_id,))
    if orders is None:
        return jsonify({'message': 'Failed to fetch orders'}), 500
    
    return jsonify({'orders': orders}), 200


@app.route('/api/order-details/<int:order_id>', methods=['GET'])
@token_required
def get_order_details(order_id):
    order = db.fetch_one("SELECT user_id FROM orders WHERE id = %s", (order_id,))
    
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    
    if request.role == 'customer' and order['user_id'] != request.user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    query = """
        SELECT oi.book_id, b.title, b.author, oi.item_type, oi.quantity, oi.price
        FROM order_items oi
        JOIN books b ON oi.book_id = b.id
        WHERE oi.order_id = %s
    """
    
    items = db.fetch_query(query, (order_id,))
    if items is None:
        return jsonify({'message': 'Failed to fetch order items'}), 500
    
    return jsonify({'items': items}), 200


@app.route('/api/all-orders', methods=['GET'])
@token_required
@role_required('manager')
def get_all_orders():
    query = """
        SELECT o.id, o.user_id, u.username, o.total_amount, o.payment_status, o.order_date
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.order_date DESC
    """
    
    orders = db.fetch_query(query)
    if orders is None:
        return jsonify({'message': 'Failed to fetch orders'}), 500
    
    return jsonify({'orders': orders}), 200


@app.route('/api/update-payment-status', methods=['PUT'])
@token_required
@role_required('manager')
def update_payment_status():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['order_id', 'payment_status']):
        return jsonify({'message': 'Missing required fields'}), 400
    
    order_id = data['order_id']
    payment_status = data['payment_status']
    
    # Validate status
    valid_statuses = ['Pending', 'Paid', 'Failed']
    if payment_status not in valid_statuses:
        return jsonify({'message': 'Invalid payment status'}), 400
    
    query = "UPDATE orders SET payment_status = %s WHERE id = %s"
    
    if db.execute_query(query, (payment_status, order_id)):
        return jsonify({'message': 'Payment status updated successfully'}), 200
    else:
        return jsonify({'message': 'Failed to update payment status'}), 500


@app.route('/api/add-book', methods=['POST'])
@token_required
@role_required('manager')
def add_book():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['title', 'author', 'price_buy', 'price_rent']):
        return jsonify({'message': 'Missing required fields'}), 400
    
    title = data['title']
    author = data['author']
    price_buy = data['price_buy']
    price_rent = data['price_rent']
    available_count = data.get('available_count', 0)
    
    query = """
        INSERT INTO books (title, author, price_buy, price_rent, available_count)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    if db.execute_query(query, (title, author, price_buy, price_rent, available_count)):
        return jsonify({'message': 'Book added successfully'}), 201
    else:
        return jsonify({'message': 'Failed to add book'}), 500


@app.route('/api/update-book/<int:book_id>', methods=['PUT'])
@token_required
@role_required('manager')
def update_book(book_id):
    data = request.get_json()
    
    book = db.fetch_one("SELECT id FROM books WHERE id = %s", (book_id,))
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    
    update_fields = []
    params = []
    
    for field in ['title', 'author', 'price_buy', 'price_rent', 'available_count']:
        if field in data:
            update_fields.append(f"{field} = %s")
            params.append(data[field])
    
    if not update_fields:
        return jsonify({'message': 'No fields to update'}), 400
    
    params.append(book_id)
    query = f"UPDATE books SET {', '.join(update_fields)} WHERE id = %s"
    
    if db.execute_query(query, params):
        return jsonify({'message': 'Book updated successfully'}), 200
    else:
        return jsonify({'message': 'Failed to update book'}), 500


@app.route('/api/generate-bill/<int:order_id>', methods=['GET'])
@token_required
def generate_bill(order_id):
    """Generate bill in HTML format"""
    order = db.fetch_one("SELECT user_id, total_amount, payment_status, order_date FROM orders WHERE id = %s", 
                        (order_id,))
    
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    
    if request.role == 'customer' and order['user_id'] != request.user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    items_query = """
        SELECT oi.book_id, b.title, b.author, oi.item_type, oi.quantity, oi.price
        FROM order_items oi
        JOIN books b ON oi.book_id = b.id
        WHERE oi.order_id = %s
    """
    items = db.fetch_query(items_query, (order_id,))
    
    # Get user info
    user = db.fetch_one("SELECT username, email FROM users WHERE id = %s", (order['user_id'],))
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bill - Order #{order_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            .total {{ font-weight: bold; font-size: 16px; }}
            .footer {{ text-align: center; margin-top: 40px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Online Bookstore Bill</h1>
            <p>Order ID: {order_id}</p>
        </div>
        
        <div>
            <p><strong>Customer:</strong> {user['username']}</p>
            <p><strong>Email:</strong> {user['email']}</p>
            <p><strong>Order Date:</strong> {order['order_date']}</p>
            <p><strong>Payment Status:</strong> {order['payment_status']}</p>
        </div>
        
        <table>
            <tr>
                <th>Book Title</th>
                <th>Author</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Subtotal</th>
            </tr>
    """
    
    for item in items:
        subtotal = item['price'] * item['quantity']
        html_content += f"""
            <tr>
                <td>{item['title']}</td>
                <td>{item['author']}</td>
                <td>{item['item_type'].capitalize()}</td>
                <td>{item['quantity']}</td>
                <td>${item['price']:.2f}</td>
                <td>${subtotal:.2f}</td>
            </tr>
        """
    
    html_content += f"""
        </table>
        
        <div style="text-align: right; margin-right: 20px;">
            <p class="total">Total Amount: ${order['total_amount']:.2f}</p>
        </div>
        
        <div class="footer">
            <p>Thank you for your purchase!</p>
            <p>This is a system-generated bill.</p>
        </div>
    </body>
    </html>
    """
    
    os.makedirs('./bills', exist_ok=True)
    bill_filename = f"./bills/bill_order_{order_id}.html"
    
    with open(bill_filename, 'w') as f:
        f.write(html_content)
    
    return jsonify({
        'message': 'Bill generated successfully',
        'filename': bill_filename,
        'bill_html': html_content
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'message': 'API is running'}), 200


if __name__ == '__main__':
    db.connect()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
