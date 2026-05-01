# Online Bookstore Application

A complete desktop application for managing books (buy and rent) with a Python Flask backend and Tkinter GUI frontend.

## Project Structure

```
Project/
├── backend/
│   ├── __init__.py
│   ├── app.py              # Flask API application
│   ├── auth.py             # Authentication utilities
│   └── database.py         # Database connection and queries
├── frontend/
│   ├── __init__.py
│   └── gui.py              # Tkinter GUI application
├── bills/                  # Directory for generated bills (HTML)
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── schema.sql              # Database schema and sample data
└── README.md               # This file
```

## Prerequisites

- Python 3.8 or higher
- MySQL Server running on localhost
- MySQL database named "Project"

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create MySQL Database and Tables

1. Open MySQL Command Line or MySQL Workbench
2. Create database (if not exists):
   ```sql
   CREATE DATABASE Project;
   ```
3. Execute all commands from `schema.sql`:
   ```sql
   USE Project;
   -- Copy and paste contents of schema.sql here
   ```

### 3. Update Database Configuration

Edit `config.py` and update the database credentials if needed:
```python
DB_CONFIG = {
    'user': '[username]',
    'password': '[password]',  # Your MySQL password
    'host': '[hostname]',
    'database': '[database]'
}
```

## Running the Application

### 1. Start the Backend Server

Open a terminal/PowerShell in the project root directory:

```bash
python -m backend.app
```

The Flask server will start on `http://localhost:5000`

### 2. Start the Frontend Application

Open another terminal/PowerShell in the project root directory:

```bash
python frontend/gui.py
```

The Tkinter GUI window will open.

## Features

### Customer Features
- **Registration & Login**: Create account and securely log in
- **Book Search**: Search books by title or author
- **Browse Catalog**: View all available books with prices
- **Shopping Cart**: Add books to buy or rent
- **Place Orders**: Complete purchases and rentals
- **View Orders**: See order history and details
- **Bill Generation**: Automatically generate HTML bills

### Manager Features
- **Manager Login**: Secure manager authentication
- **View All Orders**: See all customer orders
- **Update Payment Status**: Mark orders as Pending, Paid, or Failed
- **Manage Books**: Add new books and update existing book information

## API Endpoints

### Authentication
- `POST /api/register` - Register new customer account
- `POST /api/login` - Customer login
- `POST /api/manager-login` - Manager login

### Books & Search
- `GET /api/books` - Get all books
- `GET /api/search?keyword=<keyword>` - Search books

### Orders
- `POST /api/place-order` - Place new order
- `GET /api/orders` - Get user's orders
- `GET /api/order-details/<order_id>` - Get order details
- `GET /api/all-orders` - Get all orders (manager only)
- `PUT /api/update-payment-status` - Update payment status (manager only)

### Books Management
- `POST /api/add-book` - Add new book (manager only)
- `PUT /api/update-book/<book_id>` - Update book info (manager only)

### Billing
- `GET /api/generate-bill/<order_id>` - Generate bill in HTML format

## Database Schema

### Users Table
- `id` - User ID (primary key)
- `username` - Username (unique)
- `password` - Hashed password (bcrypt)
- `email` - Email address
- `role` - 'customer' or 'manager'
- `created_at` - Account creation timestamp

### Books Table
- `id` - Book ID (primary key)
- `title` - Book title
- `author` - Author name
- `price_buy` - Purchase price
- `price_rent` - Rental price
- `available_count` - Copies available

### Orders Table
- `id` - Order ID (primary key)
- `user_id` - Foreign key to users
- `total_amount` - Total order amount
- `payment_status` - 'Pending', 'Paid', or 'Failed'
- `order_date` - Order timestamp

### Order Items Table
- `id` - Item ID (primary key)
- `order_id` - Foreign key to orders
- `book_id` - Foreign key to books
- `item_type` - 'buy' or 'rent'
- `quantity` - Number of copies
- `price` - Unit price at time of order

## Security Features

- **Password Hashing**: Passwords are hashed using bcrypt
- **JWT Tokens**: Stateless authentication using JWT tokens
- **Role-Based Access**: Separate permissions for customers and managers
- **Authorization Checks**: Customers can only access their own data
- **Protected Endpoints**: All user-specific endpoints require valid tokens

## Sample Login Credentials

Use the following credentials to test the application (after running schema.sql):

**Customer Account:**
- Username: `john_customer`
- Password: (Use bcrypt to verify - sample hash is for testing)

**Manager Account:**
- Username: `manager1`
- Password: (Use bcrypt to verify - sample hash is for testing)

Note: The sample credentials have hash placeholders. To create actual test accounts, use the registration feature or manually hash passwords using bcrypt.

## Testing Recommendations

1. **Test Registration**: Create new customer accounts
2. **Test Search**: Search for books by title and author
3. **Test Ordering**: Add books to cart and place orders
4. **Test Manager Features**: Log in as manager and update payment statuses
5. **Test Bill Generation**: Generate bills for orders and verify HTML output

## File Locations

- **Generated Bills**: Located in the `bills/` directory as HTML files
- **Log Output**: Check terminal for Flask server logs

## Troubleshooting

### Connection Refused Error
- Ensure MySQL server is running
- Check database credentials in `config.py`
- Verify database name is "Project"

### Module Not Found Error
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're running from the project root directory

### Port Already in Use
- The Flask server defaults to port 5000
- If port is in use, modify `FLASK_PORT` in `config.py`

## Notes

- The application uses JWT tokens for authentication (24-hour expiration)
- Bills are saved as HTML files for easy printing and distribution
- All prices are stored as DECIMAL(10, 2)
- The system assumes a local MySQL setup (no remote database yet)

## Extra Credit Features (Can be implemented)

- User profiles with order history
- Book reviews and ratings
- Inventory management for physical books
- Advanced search filters (by genre, publication year)
- Book return system for rentals
