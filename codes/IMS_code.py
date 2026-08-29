import mysql.connector as c
import sys
import csv
from datetime import datetime

# =========================================================
# INVENTORY MANAGEMENT SYSTEM
# Features:
# - Role Based Login
# - Product Catalog Display
# - Product Search
# - Purchase History Tracking Using CSV
# - New Product Addition
# - Product Information Management
# - Product Purchase Processing
# - Inventory Restocking
# - Product Removal
# =========================================================

# ================= DATABASE CONNECTION =================

try:
    con = c.connect(host='localhost',user='root',password='password')
    if con.is_connected():
        print("Database Connected Successfully")
except c.Error as e:
    print("Database Connection Failed", e.msg)
    sys.exit()

# ================= CREATE DATABASE =================

cursor = con.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_system")
cursor.execute("USE inventory_system")

# ================= CREATE PRODUCTS TABLE =================

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    Product_ID INT AUTO_INCREMENT PRIMARY KEY,
    Product_Name VARCHAR(100) UNIQUE NOT NULL,
    Category VARCHAR(50),
    Quantity INT NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    Supplier VARCHAR(100)
)
""")

# ================= INITIALIZE PURCHASE CSV =================

try:

    with open("purchase_history.csv", "r"):
        pass
except FileNotFoundError:
    with open('purchase_history.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Purchase_ID',
            'Product_ID',
            'Product_Name',
            'Quantity_Purchased',
            'Total_Price',
            'Purchased_By',
            'Purchase_Date'
        ])

# ================= CREATE USERS TABLE =================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    User_ID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) UNIQUE,
    Password VARCHAR(50),
    Role ENUM('admin','staff','viewer')
)
""")

# ================= INSERT DEFAULT USERS =================

cursor.execute("SELECT * FROM users")
data = cursor.fetchall()
if not data:
    users = [
        ('admin', 'admin123', 'admin'),
        ('staff1', 'staff123', 'staff'),
        ('viewer1', 'viewer123', 'viewer')
    ]
    query = """
    INSERT INTO users(Username, Password, Role)
    VALUES(%s, %s, %s)
    """
    cursor.executemany(query, users)
    con.commit()

# ================= HELPER FUNCTIONS =================

def execute_query(query, values=None):
    try:
        cursor.execute(query, values)
        con.commit()
        return True
    except c.Error:
        con.rollback()
        print("Database Error")
        return False
def fetch_one(query, values=None):
    cursor.execute(query, values)
    return cursor.fetchone()
def fetch_all(query, values=None):
    cursor.execute(query, values)
    return cursor.fetchall()

# ================= VALIDATION FUNCTIONS =================

def validate_text(value):
    return value.strip() != ""
def validate_positive_number(value):
    return value > 0

# ================= LOGIN FUNCTION =================

def login():
    print("\n========== LOGIN ==========")
    username = input("Enter Username: ")
    password = input("Enter Password: ")
    query = """
    SELECT Username, Role
    FROM users
    WHERE Username=%s AND Password=%s
    """
    data = fetch_one(query, (username, password))
    if data:
        print(f"\nLogin Successful | Role: {data[1]}")
        return data[0], data[1]
    else:
        print("\nInvalid Username or Password")
        return None

# ================= LOW STOCK ALERT =================

def low_stock_alert():
    query = """
    SELECT Product_ID, Product_Name, Quantity
    FROM products
    WHERE Quantity < 5
    """
    records = fetch_all(query)
    if records:
        print("\n========== LOW STOCK ALERT ==========\n")
        for i in records:
            print(
                f"Product ID : {i[0]} | "
                f"Product Name : {i[1]} | "
                f"Remaining Stock : {i[2]}"
            )

# ================= ADD PRODUCT =================

def add_product():
    try:
        pname = input("Enter Product Name: ")
        if not validate_text(pname):
            print("Invalid Product Name")
            return
        category = input("Enter Product Category: ")
        qty = int(input("Enter Quantity: "))
        price = float(input("Enter Price: "))
        supplier = input("Enter Supplier Name: ")
        if not validate_positive_number(qty):
            print("Quantity Must Be Greater Than Zero")
            return
        if not validate_positive_number(price):
            print("Price Must Be Greater Than Zero")
            return
        check_query = """
        SELECT * FROM products
        WHERE Product_Name=%s
        """
        data = fetch_one(check_query, (pname,))
        if data:
            print("Product Already Exists")
            return
        query = """
        INSERT INTO products
        (Product_Name, Category, Quantity, Price, Supplier)
        VALUES(%s, %s, %s, %s, %s)
        """
        values = (pname, category, qty, price, supplier)
        execute_query(query, values)
        print("Product Added Successfully")
    except ValueError:
        print("Invalid Input")

# ================= DISPLAY PRODUCTS =================

def display_products():
    records = fetch_all(
        "SELECT * FROM products ORDER BY Product_Name"
    )
    if not records:
        print("No Products Available")
        return
    print("\n================ PRODUCT DETAILS ================\n")
    print(
        f"{'ID':<5}"
        f"{'NAME':<20}"
        f"{'CATEGORY':<15}"
        f"{'QTY':<10}"
        f"{'PRICE':<12}"
        f"{'SUPPLIER'}"
    )
    print("-" * 80)
    for i in records:
        print(
            f"{i[0]:<5}"
            f"{i[1]:<20}"
            f"{i[2]:<15}"
            f"{i[3]:<10}"
            f"{i[4]:<12}"
            f"{i[5]}"
        )

# ================= SEARCH PRODUCT =================

def search_product():
    print("\n========== SEARCH PRODUCT ==========")
    print("1. Search By ID")
    print("2. Search By Name")
    print("3. Search By Category")
    try:
        ch = int(input("Enter Choice: "))
        if ch == 1:
            pid = int(input("Enter Product ID: "))
            query = "SELECT * FROM products WHERE Product_ID=%s"
            records = fetch_all(query, (pid,))
        elif ch == 2:
            name = input("Enter Product Name: ")
            query = """
            SELECT * FROM products
            WHERE Product_Name LIKE %s
            """
            records = fetch_all(query, ('%' + name + '%',))
        elif ch == 3:
            category = input("Enter Category: ")
            query = """
            SELECT * FROM products
            WHERE Category LIKE %s
            """
            records = fetch_all(query, ('%' + category + '%',))
        else:
            print("Invalid Choice")
            return
        if records:
            print("\n========== PRODUCTS FOUND ==========\n")
            for i in records:
                print(
                    f"{i[0]:<5}"
                    f"{i[1]:<20}"
                    f"{i[2]:<15}"
                    f"{i[3]:<10}"
                    f"{i[4]:<12}"
                    f"{i[5]}"
                )
        else:
            print("No Products Found")
    except ValueError:
        print("Invalid Input")

# ================= UPDATE PRODUCT =================

def update_product():
    try:
        pid = int(input("Enter Product ID: "))
        data = fetch_one(
            "SELECT * FROM products WHERE Product_ID=%s",
            (pid,)
        )
        if not data:
            print("Product Not Found")
            return
        new_qty = int(input("Enter New Quantity: "))
        new_price = float(input("Enter New Price: "))
        if new_qty < 0:
            print("Quantity Cannot Be Negative")
            return
        if not validate_positive_number(new_price):
            print("Quantity Must Be Greater Than Zero")
            return
        query = """
        UPDATE products
        SET Quantity=%s, Price=%s
        WHERE Product_ID=%s
        """
        execute_query(query, (new_qty, new_price, pid))
        print("Product Updated Successfully")
    except ValueError:
        print("Invalid Input")

# ================= DELETE PRODUCT =================

def delete_product():
    try:
        pid = int(input("Enter Product ID to Delete: "))
        data = fetch_one(
            "SELECT * FROM products WHERE Product_ID=%s",
            (pid,)
        )
        if not data:
            print("Product Not Found")
            return
        query = "DELETE FROM products WHERE Product_ID=%s"
        execute_query(query, (pid,))
        print("Product Deleted Successfully")
    except ValueError:
        print("Invalid Input")

# ================= PURCHASE PRODUCT =================

def purchase_product(role, username):
    try:
        pid = int(input("Enter Product ID: "))
        qty_purchased = int(input("Enter Quantity To Purchase: "))
        if not validate_positive_number(qty_purchased):
            print("Quantity Must Be Greater Than Zero")
            return
        # Get product information from MySQL
        query = """
        SELECT Product_Name, Quantity, Price
        FROM products
        WHERE Product_ID=%s
        """
        data = fetch_one(query, (pid,))
        if not data:
            print("Product Not Found")
            return
        pname = data[0]
        stock = data[1]
        price = float(data[2])
        if qty_purchased > stock:
            print("Insufficient Stock")
            return
        # Calculate new stock and total price
        new_stock = stock - qty_purchased
        total_price = qty_purchased * price
        # Update inventory in MySQL
        update_query = """
        UPDATE products
        SET Quantity=%s
        WHERE Product_ID=%s
        """
        purchase_success=execute_query(update_query, (new_stock, pid))
        if not purchase_success:
            print("Purchase Failed")
            return

        # ================= SAVE PURCHASE TO CSV =================

        count = 0
        with open('purchase_history.csv','r',newline='') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                count+=1
            purchase_id=count+1
        purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('purchase_history.csv','a',newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                purchase_id,
                pid,
                pname,
                qty_purchased,
                total_price,
                username,
                purchase_date
            ])

        # ================= PURCHASE BILL =================

        print("\n========== PURCHASE BILL ==========")
        print(f"Purchase ID        : {purchase_id}")
        print(f"Product Name       : {pname}")
        print(f"Quantity Purchased : {qty_purchased}")
        print(f"Price Per Item     : Rs.{price}")
        print(f"Total Amount       : Rs.{total_price}")
        print(f"Purchased By       : {username}")
        print(f"Purchase Date      : {purchase_date}")
        print("===================================")

        if role in ['admin', 'staff']:
            low_stock_alert()
    except ValueError:
        print("Invalid Input")
    except Exception as e:
        print("Error Saving Purchase:", e)

# ================= RESTOCK PRODUCT =================

def restock_product():
    try:
        pid = int(input("Enter Product ID: "))
        data = fetch_one(
            "SELECT Quantity FROM products WHERE Product_ID=%s",
            (pid,)
        )
        if not data:
            print("Product Not Found")
            return
        add_qty = int(input("Enter Quantity To Add: "))
        if not validate_positive_number(add_qty):
            print("Quantity Must Be Greater Than Zero")
            return
        new_qty = data[0] + add_qty
        query = """
        UPDATE products
        SET Quantity=%s
        WHERE Product_ID=%s
        """
        execute_query(query, (new_qty, pid))
        print("Stock Updated Successfully")
    except ValueError:
        print("Invalid Input")

# ================= PURCHASE HISTORY =================

def purchase_history(role, username):
    records = []
    with open('purchase_history.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            # Admin and staff can see all purchases
            if role in ['admin', 'staff']:
                records.append(row)
            # Viewer can only see their own purchases
            elif row[5] == username:
                records.append(row)
    if not records:
        print("No Purchase Records Found")
        return

    print("\n================ PURCHASE HISTORY ================\n")
    print(
        f"{'ID':<5}"
        f"{'PRODUCT':<20}"
        f"{'QTY':<8}"
        f"{'TOTAL':<12}"
        f"{'USER':<12}"
        f"{'DATE'}"
    )
    print("-" * 85)
    for record in records:
        print(
            f"{record[0]:<5}"
            f"{record[2]:<20}"
            f"{record[3]:<8}"
            f"Rs.{float(record[4]):<9.2f}"
            f"{record[5]:<12}"
            f"{record[6]}"
        )

# ================= MAIN MENU =================

def main():
    while True:
        login_data = login()
        if login_data:
            username = login_data[0]
            role = login_data[1]
            while True:
                print("\n========== INVENTORY MANAGEMENT SYSTEM ==========")
                menu = {
1:"Display Products",
2:"Search Product",
3:"Purchase History"}
                # Admin and Staff options
                if role in ['admin', 'staff']:

                    menu[len(menu) + 1] = "Add Product"
                    menu[len(menu) + 1] = "Update Product"
                #Common purchase option

                menu[len(menu) + 1] = "Purchase Product"
                #Admin and Staff can restock
                if role in ['admin', 'staff']:

                    menu[len(menu) + 1] = "Restock Product"
                #Admin can delete

                if role == 'admin':

                    menu[len(menu) + 1] = "Delete Product"
                # Logout and Exit
                menu[len(menu) + 1] = "Logout"
                menu[len(menu) + 1] = "Exit"
                #Display menu
                for option in range(1,len(menu)+1):
                    print(str(option)+".",menu[option])
                try:
                    ch = int(input("Enter Your Choice: "))
                    if ch not in menu:

                        print("Invalid Choice")

                        continue
                    description=menu[ch]
                    if description == "Display Products":
                        display_products()
                    elif description == "Search Product":
                        search_product()
                    elif description == "Purchase History":
                        purchase_history(role, username)
                    elif description == "Add Product":
                        add_product()
                    elif description == "Update Product":
                        update_product()
                    elif description == "Purchase Product":
                        purchase_product(role, username)
                    elif description == "Restock Product":
                        restock_product()
                    elif description == "Delete Product":
                        delete_product()
                    elif description == "Logout":
                        print("Logged Out")
                        break
                    elif description == "Exit":
                        print("Program Ended")
                        return
                except ValueError:
                    print("Please Enter Numbers Only")

# ================= RUN PROGRAM =================

try:
    main()
finally:
    cursor.close()
    con.close()
    print("Database Connection Closed")
