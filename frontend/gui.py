import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_BASE_URL

current_user = None
current_token = None
user_role = None
cart = []  # List of {book_id, type, quantity, title, author, price}


class BookstoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Bookstore")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self.books_frame = None
        self.cart_display = None
        
        self.show_login_screen()
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display login screen"""
        global current_user, current_token, user_role
        
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)
        
        title = ttk.Label(frame, text="Online Bookstore", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Role selection
        role_frame = ttk.LabelFrame(frame, text="Login As", padding="10")
        role_frame.pack(pady=10, fill="x")
        
        role_var = tk.StringVar(value="customer")
        ttk.Radiobutton(role_frame, text="Customer", variable=role_var, value="customer").pack()
        ttk.Radiobutton(role_frame, text="Manager", variable=role_var, value="manager").pack()
        
        # Username
        ttk.Label(frame, text="Username:").pack()
        username_entry = ttk.Entry(frame, width=30)
        username_entry.pack(pady=5)
        
        # Password
        ttk.Label(frame, text="Password:").pack()
        password_entry = ttk.Entry(frame, width=30, show="*")
        password_entry.pack(pady=5)
        
        def login():
            global current_user, current_token, user_role
            username = username_entry.get()
            password = password_entry.get()
            role = role_var.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter username and password")
                return
            
            try:
                if role == "customer":
                    endpoint = f"{API_BASE_URL}/login"
                else:
                    endpoint = f"{API_BASE_URL}/manager-login"
                
                response = requests.post(endpoint, json={"username": username, "password": password})
                
                if response.status_code == 200:
                    data = response.json()
                    current_user = username
                    current_token = data['token']
                    user_role = data['role']
                    
                    if user_role == 'customer':
                        self.show_customer_dashboard()
                    else:
                        self.show_manager_dashboard()
                else:
                    messagebox.showerror("Login Failed", response.json().get('message', 'Login failed'))
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")
        
        def go_to_register():
            self.show_register_screen()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Login", command=login).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Register", command=go_to_register).pack(side="left", padx=5)
    
    def show_register_screen(self):
        """Display registration screen"""
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)
        
        title = ttk.Label(frame, text="Register New Account", font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        # Role selection
        role_frame = ttk.LabelFrame(frame, text="Account Type", padding="10")
        role_frame.pack(pady=10, fill="x")
        
        role_var = tk.StringVar(value="customer")
        ttk.Radiobutton(role_frame, text="Customer", variable=role_var, value="customer").pack()
        ttk.Radiobutton(role_frame, text="Manager", variable=role_var, value="manager").pack()
        
        ttk.Label(frame, text="Username:").pack()
        username_entry = ttk.Entry(frame, width=30)
        username_entry.pack(pady=5)
        
        ttk.Label(frame, text="Email:").pack()
        email_entry = ttk.Entry(frame, width=30)
        email_entry.pack(pady=5)
        
        ttk.Label(frame, text="Password:").pack()
        password_entry = ttk.Entry(frame, width=30, show="*")
        password_entry.pack(pady=5)
        
        ttk.Label(frame, text="Confirm Password:").pack()
        confirm_entry = ttk.Entry(frame, width=30, show="*")
        confirm_entry.pack(pady=5)
        
        def register():
            username = username_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            confirm = confirm_entry.get()
            role = role_var.get()
            
            if not all([username, email, password, confirm]):
                messagebox.showerror("Error", "All fields are required")
                return
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            try:
                response = requests.post(f"{API_BASE_URL}/register", 
                                        json={"username": username, "email": email, "password": password, "role": role})
                
                if response.status_code == 201:
                    messagebox.showinfo("Success", "Account created! Please log in.")
                    self.show_login_screen()
                else:
                    messagebox.showerror("Registration Failed", response.json().get('message', 'Registration failed'))
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Register", command=register).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Back to Login", command=self.show_login_screen).pack(side="left", padx=5)
    
    def show_customer_dashboard(self):
        """Display customer dashboard"""
        self.clear_window()
        
        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(top_frame, text=f"Welcome, {current_user}!", font=("Arial", 14, "bold")).pack(side="left")
        ttk.Button(top_frame, text="Logout", command=self.logout).pack(side="right")
        
        # Main content
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Search and Books
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="both", expand=True)
        
        ttk.Label(left_panel, text="Search Books", font=("Arial", 12, "bold")).pack()
        
        search_frame = ttk.Frame(left_panel)
        search_frame.pack(fill="x", pady=5)
        
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side="left", fill="x", expand=True)
        
        def search():
            keyword = search_entry.get()
            if not keyword:
                messagebox.showwarning("Warning", "Please enter a search keyword")
                return
            
            self.search_and_display_books(keyword, left_panel, search_frame.winfo_children())
        
        ttk.Button(search_frame, text="Search", command=search).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Show All", command=lambda: self.load_all_books(left_panel)).pack(side="left", padx=5)
        
        # Books display area
        self.books_frame = ttk.Frame(left_panel)
        self.books_frame.pack(fill="both", expand=True, pady=10)
        
        # Right panel - Cart
        right_panel = ttk.LabelFrame(main_frame, text="Shopping Cart", padding="10")
        right_panel.pack(side="right", fill="both", padx=10, pady=10)
        
        self.cart_display = scrolledtext.ScrolledText(right_panel, width=30, height=20)
        self.cart_display.pack(fill="both", expand=True)
        self.cart_display.config(state="disabled")
        
        # Cart buttons
        cart_button_frame = ttk.Frame(right_panel)
        cart_button_frame.pack(fill="x", pady=5)
        
        ttk.Button(cart_button_frame, text="Place Order", command=self.place_order).pack(fill="x", pady=2)
        ttk.Button(cart_button_frame, text="Clear Cart", command=self.clear_cart).pack(fill="x", pady=2)
        ttk.Button(cart_button_frame, text="View Orders", command=self.view_customer_orders).pack(fill="x", pady=2)
        
        # Load initial books
        self.load_all_books(left_panel)
    
    def search_and_display_books(self, keyword, parent, search_widgets):
        """Search for books and display results"""
        try:
            headers = {"Authorization": f"Bearer {current_token}"}
            response = requests.get(f"{API_BASE_URL}/search?keyword={keyword}", headers=headers)
            
            if response.status_code == 200:
                books = response.json()['books']
                self.display_books(books, parent)
            else:
                messagebox.showerror("Error", response.json().get('message', 'Search failed'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def load_all_books(self, parent):
        """Load and display all books"""
        try:
            headers = {"Authorization": f"Bearer {current_token}"}
            response = requests.get(f"{API_BASE_URL}/books", headers=headers)
            
            if response.status_code == 200:
                books = response.json()['books']
                self.display_books(books, parent)
            else:
                messagebox.showerror("Error", response.json().get('message', 'Failed to load books'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def display_books(self, books, parent):
        """Display books in the books frame"""
        if not self.books_frame:
            return
        # Clear previous books
        for widget in self.books_frame.winfo_children():
            widget.destroy()
        
        # Create scrolled frame for books
        canvas = tk.Canvas(self.books_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.books_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for book in books:
            self.create_book_card(scrollable_frame, book)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_book_card(self, parent, book):
        card = ttk.LabelFrame(parent, text=book['title'], padding="10")
        card.pack(fill="x", pady=5)
        
        ttk.Label(card, text=f"Author: {book['author']}", font=("Arial", 9)).pack(anchor="w")
        ttk.Label(card, text=f"Buy Price: ${float(book['price_buy']):.2f}", font=("Arial", 9)).pack(anchor="w")
        ttk.Label(card, text=f"Rent Price: ${float(book['price_rent']):.2f}", font=("Arial", 9)).pack(anchor="w")
        ttk.Label(card, text=f"Available: {int(book['available_count'])}", font=("Arial", 9)).pack(anchor="w")
        
        button_frame = ttk.Frame(card)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(button_frame, text="Buy", command=lambda: self.add_to_cart(book, 'buy')).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Rent", command=lambda: self.add_to_cart(book, 'rent')).pack(side="left", padx=5)
    
    def add_to_cart(self, book, order_type):
        try:
            global cart
            
            for item in cart:
                if item['book_id'] == book['id'] and item['type'] == order_type:
                    item['quantity'] += 1
                    self.update_cart_display()
                    messagebox.showinfo("Updated", f"Quantity increased for {book['title']}!")
                    return
            
            price = float(book['price_buy']) if order_type == 'buy' else float(book['price_rent'])
            cart.append({
                'book_id': book['id'],
                'type': order_type,
                'quantity': 1,
                'title': book['title'],
                'author': book['author'],
                'price': price
            })
            
            self.update_cart_display()
            messagebox.showinfo("Added", f"{book['title']} ({order_type}) added to cart!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to cart: {str(e)}")
    
    def update_cart_display(self):
        global cart
        
        if not self.cart_display:
            return
        
        self.cart_display.config(state="normal")
        self.cart_display.delete(1.0, tk.END)
        
        if not cart:
            self.cart_display.insert(tk.END, "Cart is empty")
            self.cart_display.config(state="disabled")
            return
        
        total = 0
        for item in cart:
            subtotal = float(item['price']) * int(item['quantity'])
            total += subtotal
            
            text = f"{item['title']}\n"
            text += f"  Type: {item['type']}\n"
            text += f"  Qty: {item['quantity']} @ ${float(item['price']):.2f}\n"
            text += f"  Subtotal: ${subtotal:.2f}\n\n"
            
            self.cart_display.insert(tk.END, text)
        
        self.cart_display.insert(tk.END, f"\n{'='*25}\n")
        self.cart_display.insert(tk.END, f"Total: ${total:.2f}\n")
        self.cart_display.config(state="disabled")
    
    def place_order(self):
        """Place order with items in cart"""
        global cart
        
        if not cart:
            messagebox.showwarning("Warning", "Cart is empty")
            return
        
        try:
            headers = {"Authorization": f"Bearer {current_token}"}
            order_items = [{'book_id': item['book_id'], 'type': item['type'], 'quantity': item['quantity']} 
                          for item in cart]
            
            response = requests.post(f"{API_BASE_URL}/place-order", 
                                    json={'items': order_items},
                                    headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                messagebox.showinfo("Success", f"Order {data['order_id']} placed!\nTotal: ${float(data['total']):.2f}\n\nGenerating bill...")
                
                # Generate bill
                self.generate_bill(data['order_id'])
                
                # Clear cart
                cart = []
                self.update_cart_display()
            else:
                messagebox.showerror("Error", response.json().get('message', 'Failed to place order'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def clear_cart(self):
        """Clear shopping cart"""
        global cart
        
        if messagebox.askyesno("Confirm", "Clear cart?"):
            cart = []
            self.update_cart_display()
    
    def generate_bill(self, order_id):
        """Generate bill for order"""
        try:
            headers = {"Authorization": f"Bearer {current_token}"}
            response = requests.get(f"{API_BASE_URL}/generate-bill/{order_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                messagebox.showinfo("Bill Generated", f"Bill saved to: {data['filename']}")
            else:
                messagebox.showerror("Error", response.json().get('message', 'Failed to generate bill'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def view_customer_orders(self):
        """Display customer's orders"""
        try:
            headers = {"Authorization": f"Bearer {current_token}"}
            response = requests.get(f"{API_BASE_URL}/orders", headers=headers)
            
            if response.status_code == 200:
                orders = response.json()['orders']
                self.show_orders_window(orders)
            else:
                messagebox.showerror("Error", response.json().get('message', 'Failed to fetch orders'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def show_orders_window(self, orders):
        """Display orders in a new window"""
        order_window = tk.Toplevel(self.root)
        order_window.title("My Orders")
        order_window.geometry("600x400")
        
        if not orders:
            ttk.Label(order_window, text="No orders yet", font=("Arial", 12)).pack(pady=20)
            return
        
        tree = ttk.Treeview(order_window, columns=("ID", "Date", "Total", "Status"), height=15)
        tree.column("#0", width=0, stretch="no")
        tree.column("ID", anchor=tk.W, width=50)
        tree.column("Date", anchor=tk.W, width=150)
        tree.column("Total", anchor=tk.W, width=100)
        tree.column("Status", anchor=tk.W, width=100)
        
        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("ID", text="Order ID", anchor=tk.W)
        tree.heading("Date", text="Date", anchor=tk.W)
        tree.heading("Total", text="Total", anchor=tk.W)
        tree.heading("Status", text="Status", anchor=tk.W)
        
        for order in orders:
            tree.insert("", "end", values=(order['id'], order['order_date'], f"${float(order['total_amount']):.2f}", order['payment_status']))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        def view_details():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an order")
                return
            
            item = tree.item(selected[0])
            order_id = item['values'][0]
            self.show_order_details(order_id)
        
        ttk.Button(order_window, text="View Details", command=view_details).pack(pady=5)
    
    def show_order_details(self, order_id):
        """Display details of a specific order"""
        try:
            headers = {"Authorization": f"Bearer {current_token}"}
            response = requests.get(f"{API_BASE_URL}/order-details/{order_id}", headers=headers)
            
            if response.status_code == 200:
                items = response.json()['items']
                
                detail_window = tk.Toplevel(self.root)
                detail_window.title(f"Order {order_id} Details")
                detail_window.geometry("600x400")
                
                tree = ttk.Treeview(detail_window, columns=("Title", "Author", "Type", "Qty", "Price"), height=15)
                tree.column("#0", width=0, stretch="no")
                tree.column("Title", anchor=tk.W, width=150)
                tree.column("Author", anchor=tk.W, width=120)
                tree.column("Type", anchor=tk.W, width=80)
                tree.column("Qty", anchor=tk.W, width=50)
                tree.column("Price", anchor=tk.W, width=80)
                
                tree.heading("#0", text="", anchor=tk.W)
                tree.heading("Title", text="Title", anchor=tk.W)
                tree.heading("Author", text="Author", anchor=tk.W)
                tree.heading("Type", text="Type", anchor=tk.W)
                tree.heading("Qty", text="Qty", anchor=tk.W)
                tree.heading("Price", text="Price", anchor=tk.W)
                
                for item in items:
                   tree.insert("", "end", values=(item['title'], item['author'], item['item_type'].capitalize(), item['quantity'], f"${float(item['price']):.2f}"))
                tree.pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def show_manager_dashboard(self):
        """Display manager dashboard"""
        self.clear_window()
        
        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(top_frame, text=f"Manager Dashboard - {current_user}", font=("Arial", 14, "bold")).pack(side="left")
        ttk.Button(top_frame, text="Logout", command=self.logout).pack(side="right")
        
        # Main menu
        menu_frame = ttk.LabelFrame(self.root, text="Manager Menu", padding="20")
        menu_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Button(menu_frame, text="View All Orders", command=self.view_all_orders, width=30).pack(pady=10)
        ttk.Button(menu_frame, text="Manage Books", command=self.manage_books_menu, width=30).pack(pady=10)
    
    def view_all_orders(self):
        """View all orders as manager"""
        try:
            headers = {"Authorization": f"Bearer {current_token}"}
            response = requests.get(f"{API_BASE_URL}/all-orders", headers=headers)
            
            if response.status_code == 200:
                orders = response.json()['orders']
                self.show_all_orders_window(orders)
            else:
                messagebox.showerror("Error", response.json().get('message', 'Failed to fetch orders'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def show_all_orders_window(self, orders):
        """Display all orders in a new window"""
        order_window = tk.Toplevel(self.root)
        order_window.title("All Orders")
        order_window.geometry("800x400")
        
        if not orders:
            ttk.Label(order_window, text="No orders", font=("Arial", 12)).pack(pady=20)
            return
        
        tree = ttk.Treeview(order_window, columns=("ID", "Customer", "Date", "Total", "Status"), height=15)
        tree.column("#0", width=0, stretch="no")
        tree.column("ID", anchor=tk.W, width=50)
        tree.column("Customer", anchor=tk.W, width=150)
        tree.column("Date", anchor=tk.W, width=150)
        tree.column("Total", anchor=tk.W, width=100)
        tree.column("Status", anchor=tk.W, width=100)
        
        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("ID", text="ID", anchor=tk.W)
        tree.heading("Customer", text="Customer", anchor=tk.W)
        tree.heading("Date", text="Date", anchor=tk.W)
        tree.heading("Total", text="Total", anchor=tk.W)
        tree.heading("Status", text="Status", anchor=tk.W)
        
        for order in orders:
            tree.insert("", "end", values=(order['id'], order['username'], order['order_date'], f"${float(order['total_amount']):.2f}", order['payment_status']))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        button_frame = ttk.Frame(order_window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def update_status():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an order")
                return
            
            item = tree.item(selected[0])
            order_id = item['values'][0]
            self.update_order_status(order_id)
        
        ttk.Button(button_frame, text="Update Payment Status", command=update_status).pack(side="left", padx=5)
    
    def update_order_status(self, order_id):
        """Update payment status of an order"""
        status_window = tk.Toplevel(self.root)
        status_window.title(f"Update Order {order_id} Status")
        status_window.geometry("300x150")
        
        ttk.Label(status_window, text="Select Payment Status:").pack(pady=10)
        
        status_var = tk.StringVar(value="Pending")
        ttk.Radiobutton(status_window, text="Pending", variable=status_var, value="Pending").pack()
        ttk.Radiobutton(status_window, text="Paid", variable=status_var, value="Paid").pack()
        ttk.Radiobutton(status_window, text="Failed", variable=status_var, value="Failed").pack()
        
        def update():
            status = status_var.get()
            try:
                headers = {"Authorization": f"Bearer {current_token}"}
                response = requests.put(f"{API_BASE_URL}/update-payment-status",
                                       json={'order_id': order_id, 'payment_status': status},
                                       headers=headers)
                
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Payment status updated")
                    status_window.destroy()
                else:
                    messagebox.showerror("Error", response.json().get('message', 'Failed to update'))
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")
        
        ttk.Button(status_window, text="Update", command=update).pack(pady=10)
    
    def manage_books_menu(self):
        """Manager books management menu"""
        books_window = tk.Toplevel(self.root)
        books_window.title("Book Management")
        books_window.geometry("400x300")
        
        ttk.Button(books_window, text="Add New Book", 
                  command=self.add_book_window, width=40).pack(pady=10)
        ttk.Button(books_window, text="Update Book Information", 
                  command=self.update_book_window, width=40).pack(pady=10)
    
    def add_book_window(self):
        """Window to add a new book"""
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Book")
        add_window.geometry("400x350")
        
        ttk.Label(add_window, text="Title:").pack()
        title_entry = ttk.Entry(add_window, width=40)
        title_entry.pack(pady=5)
        
        ttk.Label(add_window, text="Author:").pack()
        author_entry = ttk.Entry(add_window, width=40)
        author_entry.pack(pady=5)
        
        ttk.Label(add_window, text="Buy Price:").pack()
        buy_price_entry = ttk.Entry(add_window, width=40)
        buy_price_entry.pack(pady=5)
        
        ttk.Label(add_window, text="Rent Price:").pack()
        rent_price_entry = ttk.Entry(add_window, width=40)
        rent_price_entry.pack(pady=5)
        
        ttk.Label(add_window, text="Available Count:").pack()
        count_entry = ttk.Entry(add_window, width=40)
        count_entry.pack(pady=5)
        
        def add():
            try:
                title = title_entry.get()
                author = author_entry.get()
                price_buy = float(buy_price_entry.get())
                price_rent = float(rent_price_entry.get())
                available_count = int(count_entry.get())
                
                if not all([title, author]):
                    messagebox.showerror("Error", "Title and Author are required")
                    return
                
                headers = {"Authorization": f"Bearer {current_token}"}
                response = requests.post(f"{API_BASE_URL}/add-book",
                                        json={
                                            'title': title,
                                            'author': author,
                                            'price_buy': price_buy,
                                            'price_rent': price_rent,
                                            'available_count': available_count
                                        },
                                        headers=headers)
                
                if response.status_code == 201:
                    messagebox.showinfo("Success", "Book added successfully")
                    add_window.destroy()
                else:
                    messagebox.showerror("Error", response.json().get('message', 'Failed to add book'))
            except ValueError:
                messagebox.showerror("Error", "Invalid price or count values")
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")
        
        ttk.Button(add_window, text="Add Book", command=add).pack(pady=20)
    
    def update_book_window(self):
        """Window to update book information"""
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Book")
        update_window.geometry("400x400")
        
        ttk.Label(update_window, text="Book ID:").pack()
        book_id_entry = ttk.Entry(update_window, width=40)
        book_id_entry.pack(pady=5)
        
        ttk.Label(update_window, text="New Title (leave empty to skip):").pack()
        title_entry = ttk.Entry(update_window, width=40)
        title_entry.pack(pady=5)
        
        ttk.Label(update_window, text="New Author (leave empty to skip):").pack()
        author_entry = ttk.Entry(update_window, width=40)
        author_entry.pack(pady=5)
        
        ttk.Label(update_window, text="New Buy Price (leave empty to skip):").pack()
        buy_price_entry = ttk.Entry(update_window, width=40)
        buy_price_entry.pack(pady=5)
        
        ttk.Label(update_window, text="New Available Count (leave empty to skip):").pack()
        count_entry = ttk.Entry(update_window, width=40)
        count_entry.pack(pady=5)
        
        def update():
            try:
                book_id = int(book_id_entry.get())
                update_data = {}
                
                if title_entry.get():
                    update_data['title'] = title_entry.get()
                if author_entry.get():
                    update_data['author'] = author_entry.get()
                if buy_price_entry.get():
                    update_data['price_buy'] = float(buy_price_entry.get())
                if count_entry.get():
                    update_data['available_count'] = int(count_entry.get())
                
                if not update_data:
                    messagebox.showwarning("Warning", "No fields to update")
                    return
                
                headers = {"Authorization": f"Bearer {current_token}"}
                response = requests.put(f"{API_BASE_URL}/update-book/{book_id}",
                                       json=update_data,
                                       headers=headers)
                
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Book updated successfully")
                    update_window.destroy()
                else:
                    messagebox.showerror("Error", response.json().get('message', 'Failed to update book'))
            except ValueError:
                messagebox.showerror("Error", "Invalid input values")
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")
        
        ttk.Button(update_window, text="Update Book", command=update).pack(pady=20)
    
    def logout(self):
        global current_user, current_token, user_role, cart
        current_user = None
        current_token = None
        user_role = None
        cart = []
        self.show_login_screen()


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = BookstoreApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
