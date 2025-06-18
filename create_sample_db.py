"""
Create a sample Northwind-like database for testing.
"""

import sqlite3
import os

def create_northwind_sample():
    """Create a sample Northwind-like database with sample data."""
    
    # Remove existing file if it exists
    if os.path.exists("northwind.db"):
        os.remove("northwind.db")
    
    # Create connection
    conn = sqlite3.connect("northwind.db")
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE Categories (
            CategoryID INTEGER PRIMARY KEY,
            CategoryName TEXT NOT NULL,
            Description TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Products (
            ProductID INTEGER PRIMARY KEY,
            ProductName TEXT NOT NULL,
            CategoryID INTEGER,
            UnitPrice REAL,
            UnitsInStock INTEGER,
            Discontinued INTEGER,
            FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Customers (
            CustomerID TEXT PRIMARY KEY,
            CompanyName TEXT NOT NULL,
            ContactName TEXT,
            City TEXT,
            Country TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Employees (
            EmployeeID INTEGER PRIMARY KEY,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            Title TEXT,
            City TEXT,
            Country TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Orders (
            OrderID INTEGER PRIMARY KEY,
            CustomerID TEXT,
            EmployeeID INTEGER,
            OrderDate TEXT,
            ShipCity TEXT,
            ShipCountry TEXT,
            FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
            FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE OrderDetails (
            OrderID INTEGER,
            ProductID INTEGER,
            UnitPrice REAL,
            Quantity INTEGER,
            Discount REAL,
            PRIMARY KEY (OrderID, ProductID),
            FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        )
    """)
    
    # Insert sample data
    
    # Categories
    categories = [
        (1, "Beverages", "Soft drinks, coffees, teas, beers, and ales"),
        (2, "Condiments", "Sweet and savory sauces, relishes, spreads, and seasonings"),
        (3, "Dairy Products", "Cheeses"),
        (4, "Grains/Cereals", "Breads, crackers, pasta, and cereal"),
        (5, "Meat/Poultry", "Prepared meats"),
        (6, "Produce", "Dried fruit and bean curd"),
        (7, "Seafood", "Seaweed and fish")
    ]
    cursor.executemany("INSERT INTO Categories VALUES (?, ?, ?)", categories)
    
    # Products
    products = [
        (1, "Chai", 1, 18.00, 39, 0),
        (2, "Chang", 1, 19.00, 17, 0),
        (3, "Aniseed Syrup", 2, 10.00, 13, 0),
        (4, "Chef Anton's Cajun Seasoning", 2, 22.00, 53, 0),
        (5, "Chef Anton's Gumbo Mix", 2, 21.35, 0, 1),
        (6, "Grandma's Boysenberry Spread", 2, 25.00, 120, 0),
        (7, "Uncle Bob's Organic Dried Pears", 7, 30.00, 15, 0),
        (8, "Northwoods Cranberry Sauce", 2, 40.00, 6, 0),
        (9, "Mishi Kobe Niku", 6, 97.00, 29, 0),
        (10, "Ikura", 8, 31.00, 31, 0),
        (11, "Queso Cabrales", 4, 21.00, 22, 0),
        (12, "Queso Manchego La Pastora", 4, 38.00, 86, 0),
        (13, "Konbu", 8, 6.00, 24, 0),
        (14, "Tofu", 7, 23.25, 35, 0),
        (15, "Genen Shouyu", 2, 15.50, 39, 0)
    ]
    cursor.executemany("INSERT INTO Products VALUES (?, ?, ?, ?, ?, ?)", products)
    
    # Customers
    customers = [
        ("ALFKI", "Alfreds Futterkiste", "Maria Anders", "Berlin", "Germany"),
        ("ANATR", "Ana Trujillo Emparedados y helados", "Ana Trujillo", "México D.F.", "Mexico"),
        ("ANTON", "Antonio Moreno Taquería", "Antonio Moreno", "México D.F.", "Mexico"),
        ("AROUT", "Around the Horn", "Thomas Hardy", "London", "UK"),
        ("BERGS", "Berglunds snabbköp", "Christina Berglund", "Luleå", "Sweden"),
        ("BLAUS", "Blauer See Delikatessen", "Hanna Moos", "Mannheim", "Germany"),
        ("BLONP", "Blondesddsl père et fils", "Frédérique Citeaux", "Strasbourg", "France"),
        ("BOLID", "Bólido Comidas preparadas", "Martín Sommer", "Madrid", "Spain"),
        ("BONAP", "Bon app'", "Laurence Lebihan", "Marseille", "France"),
        ("BOTTM", "Bottom-Dollar Markets", "Elizabeth Lincoln", "Tsawassen", "Canada")
    ]
    cursor.executemany("INSERT INTO Customers VALUES (?, ?, ?, ?, ?)", customers)
    
    # Employees
    employees = [
        (1, "Nancy", "Davolio", "Sales Representative", "Seattle", "USA"),
        (2, "Andrew", "Fuller", "Vice President, Sales", "Tacoma", "USA"),
        (3, "Janet", "Leverling", "Sales Representative", "Kirkland", "USA"),
        (4, "Margaret", "Peacock", "Sales Representative", "Redmond", "USA"),
        (5, "Steven", "Buchanan", "Sales Manager", "London", "UK"),
        (6, "Michael", "Suyama", "Sales Representative", "London", "UK"),
        (7, "Robert", "King", "Sales Representative", "London", "UK"),
        (8, "Laura", "Callahan", "Inside Sales Coordinator", "Seattle", "USA"),
        (9, "Anne", "Dodsworth", "Sales Representative", "London", "UK")
    ]
    cursor.executemany("INSERT INTO Employees VALUES (?, ?, ?, ?, ?, ?)", employees)
    
    # Orders
    orders = [
        (10248, "ALFKI", 5, "1996-07-04", "Reims", "France"),
        (10249, "TOMSP", 6, "1996-07-05", "Münster", "Germany"),
        (10250, "HANAR", 4, "1996-07-08", "Rio de Janeiro", "Brazil"),
        (10251, "VICTE", 3, "1996-07-08", "Lyon", "France"),
        (10252, "SUPRD", 4, "1996-07-09", "Charleroi", "Belgium"),
        (10253, "HANAR", 3, "1996-07-10", "Rio de Janeiro", "Brazil"),
        (10254, "CHOPS", 5, "1996-07-11", "Bern", "Switzerland"),
        (10255, "RICSU", 9, "1996-07-12", "Genève", "Switzerland"),
        (10256, "WELLI", 3, "1996-07-15", "Resende", "Brazil"),
        (10257, "HILAA", 4, "1996-07-16", "San Cristóbal", "Venezuela")
    ]
    cursor.executemany("INSERT INTO Orders VALUES (?, ?, ?, ?, ?, ?)", orders)
    
    # Order Details
    order_details = [
        (10248, 11, 14.00, 12, 0.0),
        (10248, 42, 9.80, 10, 0.0),
        (10248, 72, 34.80, 5, 0.0),
        (10249, 14, 18.60, 9, 0.0),
        (10249, 51, 42.40, 40, 0.0),
        (10250, 41, 7.70, 10, 0.0),
        (10250, 51, 42.40, 35, 0.15),
        (10250, 65, 16.80, 15, 0.15),
        (10251, 22, 16.80, 6, 0.05),
        (10251, 57, 15.60, 15, 0.05),
        (10252, 20, 64.80, 40, 0.05),
        (10252, 33, 2.00, 25, 0.05),
        (10252, 60, 27.20, 40, 0.0),
        (10253, 31, 10.00, 20, 0.0),
        (10253, 39, 14.40, 42, 0.0),
        (10253, 49, 16.00, 40, 0.0)
    ]
    cursor.executemany("INSERT INTO OrderDetails VALUES (?, ?, ?, ?, ?)", order_details)
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("✅ Northwind sample database created successfully!")
    
    # Verify the database
    conn = sqlite3.connect("northwind.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Created {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()
    return "northwind.db"

if __name__ == "__main__":
    create_northwind_sample() 