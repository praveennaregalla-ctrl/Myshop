import time
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Sale, SaleItem, Customer, Product, Payment, InventoryTransaction

sales_bp = Blueprint('sales', __name__, url_prefix='/api/sales')

@sales_bp.route('', methods=['GET'])
def get_sales():
    customer_id = request.args.get('customer_id', type=int)
    query = Sale.query
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    sales = query.order_by(Sale.id.desc()).all()
    return jsonify([s.to_dict() for s in sales])

@sales_bp.route('/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    return jsonify(sale.to_dict())

@sales_bp.route('', methods=['POST'])
def create_sale():
    data = request.get_json() or {}
    items_data = data.get('items', [])
    if not items_data:
        return jsonify({'error': 'Sale items cannot be empty'}), 400

    customer_id = data.get('customer_id')
    customer_name = data.get('customer_name', 'Walk-in Customer')
    customer_phone = data.get('customer_phone', '')
    subtotal = float(data.get('subtotal', 0.0))
    discount = float(data.get('discount', 0.0))
    total_amount = float(data.get('total_amount', max(0.0, subtotal - discount)))
    amount_paid = float(data.get('amount_paid', total_amount))
    remaining_balance = max(0.0, total_amount - amount_paid)
    payment_method = data.get('payment_method', 'Cash')
    notes = data.get('notes', '')

    invoice_no = f"INV-{datetime.now().year}-{int(time.time()) % 1000000:06d}"

    try:
        # 1. Create Sale Record
        sale = Sale(
            invoice_number=invoice_no,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            subtotal=subtotal,
            discount=discount,
            total_amount=total_amount,
            amount_paid=amount_paid,
            remaining_balance=remaining_balance,
            payment_method=payment_method,
            notes=notes
        )
        db.session.add(sale)
        db.session.flush()

        item_names = []
        # 2. Create Sale Items and Reduce Stock
        for item in items_data:
            p_id = item.get('product_id')
            p_name = item.get('product_name', 'Cloth Item')
            p_size = item.get('size', '-')
            p_color = item.get('color', '-')
            p_qty = int(item.get('quantity', 1))
            p_price = float(item.get('unit_price', 0.0))
            p_total = float(item.get('total_price', p_price * p_qty))

            item_names.append(f"{p_qty}x {p_name}")

            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=p_id,
                product_name=p_name,
                size=p_size,
                color=p_color,
                quantity=p_qty,
                unit_price=p_price,
                total_price=p_total
            )
            db.session.add(sale_item)

            # Reduce Inventory
            if p_id:
                product = Product.query.get(p_id)
                if product:
                    product.quantity = max(0, product.quantity - p_qty)
                    tx = InventoryTransaction(
                        product_id=product.id,
                        transaction_type='SALE',
                        quantity=p_qty,
                        reason=f'Sold in Invoice #{invoice_no}'
                    )
                    db.session.add(tx)

        # 3. Create Payment Record if amount_paid > 0
        if amount_paid > 0:
            payment = Payment(
                customer_id=customer_id,
                customer_name=customer_name,
                sale_id=sale.id,
                item_description=', '.join(item_names[:2]),
                total_amount=total_amount,
                amount_paid=amount_paid,
                remaining_balance=remaining_balance,
                payment_method=payment_method,
                payment_notes=f"Initial Payment for Invoice #{invoice_no}"
            )
            db.session.add(payment)

        # 4. Update Customer Balances
        if customer_id:
            customer = Customer.query.get(customer_id)
            if customer:
                customer.total_purchase_amount += total_amount
                customer.total_amount_paid += amount_paid
                customer.remaining_balance += remaining_balance

        db.session.commit()
        return jsonify(sale.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
