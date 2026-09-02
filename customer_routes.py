from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Customer, Sale, Payment, SaleItem

customer_bp = Blueprint('customers', __name__, url_prefix='/api/customers')

@customer_bp.route('', methods=['GET'])
def get_customers():
    search = request.args.get('search')
    has_due = request.args.get('has_due')

    query = Customer.query
    if search:
        query = query.filter(
            (Customer.name.ilike(f'%{search}%')) |
            (Customer.phone.ilike(f'%{search}%'))
        )
    if has_due and has_due.lower() == 'true':
        query = query.filter(Customer.remaining_balance > 0)

    customers = query.order_by(Customer.id.desc()).all()
    return jsonify([c.to_dict() for c in customers])

@customer_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = customer.to_dict()
    # attach sales & payments
    sales = Sale.query.filter_by(customer_id=customer_id).order_by(Sale.id.desc()).all()
    payments = Payment.query.filter_by(customer_id=customer_id).order_by(Payment.id.desc()).all()
    data['sales'] = [s.to_dict() for s in sales]
    data['payments'] = [p.to_dict() for p in payments]
    return jsonify(data)

@customer_bp.route('', methods=['POST'])
def create_customer():
    data = request.get_json() or {}
    name = data.get('name')
    phone = data.get('phone')
    opening_balance = float(data.get('opening_balance', 0.0))
    item_description = data.get('item_description', 'Opening Balance Due')

    if not name or not phone:
        return jsonify({'error': 'Name and phone number are required'}), 400

    customer = Customer(
        name=name,
        phone=phone,
        address=data.get('address', ''),
        total_purchase_amount=opening_balance,
        total_amount_paid=0.0,
        remaining_balance=opening_balance,
        notes=data.get('notes', '')
    )
    db.session.add(customer)
    db.session.flush()

    if opening_balance > 0:
        sale = Sale(
            invoice_number=f"OPN-{customer.id}-{int(customer.created_at.timestamp()) % 100000}",
            customer_id=customer.id,
            customer_name=customer.name,
            customer_phone=customer.phone,
            subtotal=opening_balance,
            discount=0.0,
            total_amount=opening_balance,
            amount_paid=0.0,
            remaining_balance=opening_balance,
            payment_method='Opening Due',
            notes=item_description
        )
        db.session.add(sale)
        db.session.flush()

        sale_item = SaleItem(
            sale_id=sale.id,
            product_name=item_description,
            size='-',
            color='-',
            quantity=1,
            unit_price=opening_balance,
            total_price=opening_balance
        )
        db.session.add(sale_item)

    db.session.commit()
    return jsonify(customer.to_dict()), 201

@customer_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json() or {}

    customer.name = data.get('name', customer.name)
    customer.phone = data.get('phone', customer.phone)
    customer.address = data.get('address', customer.address)
    customer.notes = data.get('notes', customer.notes)

    db.session.commit()
    return jsonify(customer.to_dict())

@customer_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'})
