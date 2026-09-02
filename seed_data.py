from app.extensions import db
from app.models import User, Category, Product, ProductVariant, Customer, Sale, SaleItem, Payment

def seed_database():
    if User.query.first():
        return

    print("🌱 Seeding ClothBook database with sample data...")

    # 1. Admin User
    admin = User(name="Store Admin", email="admin@clothbook.com", role="admin")
    admin.set_password("admin123")
    db.session.add(admin)

    # 2. Categories
    cat_mens = Category(name="Men's Wear", description="Shirts, Trousers, Suits, Jeans")
    cat_womens = Category(name="Women's Ethnic & Western", description="Sarees, Kurtas, Tops, Dresses")
    cat_kids = Category(name="Kids Collection", description="Kids festive and casual wear")
    db.session.add_all([cat_mens, cat_womens, cat_kids])
    db.session.flush()

    # 3. Products
    products_data = [
        ("Pure Kanchipuram Silk Saree", "Rich zari woven traditional wedding saree with unstitched blouse", cat_womens.id, "Virasat Silk", "Women", 2800.0, 4500.0, 15, 3, "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500&q=80", True),
        ("Italian Navy Slim Fit Suit", "Premium wool blend two-piece formal blazer with matching trousers", cat_mens.id, "Raymond", "Men", 3200.0, 5999.0, 8, 2, "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=500&q=80", True),
        ("Anarkali Embroidered Kurti", "Georgette flared long kurta with delicate mirror work and dupatta", cat_womens.id, "Biba", "Women", 950.0, 1899.0, 24, 5, "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=500&q=80", False),
        ("Classic 511 Slim Denim Jeans", "Comfort stretch denim with 5-pocket styling and rinse wash finish", cat_mens.id, "Levi's", "Men", 1100.0, 2299.0, 30, 6, "https://images.unsplash.com/photo-1542272604-780c96856592?w=500&q=80", False),
        ("Kids Festive Kurta Pyjama Set", "Art silk ethnic festive set with printed Nehru jacket", cat_kids.id, "Manyavar Kids", "Kids", 650.0, 1299.0, 18, 4, "https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=500&q=80", True),
        ("Oxford Crisp Cotton Formal Shirt", "100% Egyptian cotton breathable business shirt", cat_mens.id, "Van Heusen", "Men", 700.0, 1499.0, 35, 8, "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&q=80", False),
        ("Floral Print Chiffon Maxi Dress", "Lightweight summer floral evening gown with waist tie-up", cat_womens.id, "Zara", "Women", 1200.0, 2499.0, 12, 3, "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=500&q=80", True),
        ("Casual Graphic Crew Neck T-Shirt", "Bio-washed combed cotton everyday graphic tee", cat_mens.id, "Puma", "Men", 350.0, 799.0, 45, 10, "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&q=80", False),
        ("Banarasi Bridal Georgette Saree", "Golden brocade zari woven handloom festival saree", cat_womens.id, "Heritage Weaves", "Women", 3400.0, 6200.0, 6, 2, "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=500&q=80", True),
        ("Girls Embroidered Party Frock", "Layered tulle net princess birthday frock", cat_kids.id, "Hopscotch", "Kids", 550.0, 1150.0, 14, 4, "https://images.unsplash.com/photo-1518831959646-742c3a14ebf7?w=500&q=80", False),
    ]

    for name, desc, cat_id, brand, gender, p_price, s_price, qty, min_stock, img, is_new in products_data:
        p = Product(
            name=name, description=desc, category_id=cat_id, brand=brand, gender=gender,
            purchase_price=p_price, selling_price=s_price, quantity=qty, minimum_stock=min_stock,
            image_url=img, is_new_arrival=is_new
        )
        db.session.add(p)
        db.session.flush()

        # Add variants
        for size in ["M", "L", "XL"]:
            for color in ["Default", "Navy", "Maroon"]:
                db.session.add(ProductVariant(product_id=p.id, size=size, color=color, quantity=qty // 6))

    # 4. Customers
    cust1 = Customer(name="Ramesh Kumar", phone="+91 98450 12345", address="Market Road, Shop #12", total_purchase_amount=5999.0, total_amount_paid=4000.0, remaining_balance=1999.0, notes="Regular buyer")
    cust2 = Customer(name="Priya Sharma", phone="+91 97412 67890", address="MG Road, Appt 4B", total_purchase_amount=4500.0, total_amount_paid=4500.0, remaining_balance=0.0, notes="Paid in full")
    cust3 = Customer(name="Anil Patel", phone="+91 98860 33445", address="Gandhi Nagar", total_purchase_amount=8298.0, total_amount_paid=5000.0, remaining_balance=3298.0, notes="Wedding shopping due")
    cust4 = Customer(name="Sunita Devi", phone="+91 99001 55667", address="Station Road", total_purchase_amount=2499.0, total_amount_paid=1000.0, remaining_balance=1499.0, notes="Promised payment next Monday")
    cust5 = Customer(name="Vikram Singh", phone="+91 94480 99881", address="Civil Lines", total_purchase_amount=3798.0, total_amount_paid=3798.0, remaining_balance=0.0, notes="VIP Customer")

    db.session.add_all([cust1, cust2, cust3, cust4, cust5])
    db.session.flush()

    # 5. Sample Sales & Payments
    sale1 = Sale(invoice_number="INV-2026-000101", customer_id=cust1.id, customer_name=cust1.name, customer_phone=cust1.phone, subtotal=5999.0, discount=0.0, total_amount=5999.0, amount_paid=4000.0, remaining_balance=1999.0, payment_method="UPI")
    db.session.add(sale1)
    db.session.flush()
    db.session.add(SaleItem(sale_id=sale1.id, product_name="Italian Navy Slim Fit Suit", size="L", color="Navy", quantity=1, unit_price=5999.0, total_price=5999.0))
    db.session.add(Payment(customer_id=cust1.id, customer_name=cust1.name, sale_id=sale1.id, item_description="Italian Navy Slim Fit Suit", total_amount=5999.0, amount_paid=4000.0, remaining_balance=1999.0, payment_method="UPI"))

    sale2 = Sale(invoice_number="INV-2026-000102", customer_id=cust3.id, customer_name=cust3.name, customer_phone=cust3.phone, subtotal=8298.0, discount=0.0, total_amount=8298.0, amount_paid=5000.0, remaining_balance=3298.0, payment_method="Cash")
    db.session.add(sale2)
    db.session.flush()
    db.session.add(SaleItem(sale_id=sale2.id, product_name="Pure Kanchipuram Silk Saree", size="Free", color="Red", quantity=1, unit_price=4500.0, total_price=4500.0))
    db.session.add(SaleItem(sale_id=sale2.id, product_name="Classic 511 Slim Denim Jeans", size="32", color="Blue", quantity=1, unit_price=2299.0, total_price=2299.0))
    db.session.add(Payment(customer_id=cust3.id, customer_name=cust3.name, sale_id=sale2.id, item_description="Pure Silk Saree & Jeans", total_amount=8298.0, amount_paid=5000.0, remaining_balance=3298.0, payment_method="Cash"))

    db.session.commit()
    print("✅ Seed data populated successfully!")
