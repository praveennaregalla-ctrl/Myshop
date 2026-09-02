from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Product, ProductVariant, Category, InventoryTransaction

product_bp = Blueprint('products', __name__, url_prefix='/api/products')

@product_bp.route('', methods=['GET'])
def get_products():
    category_id = request.args.get('category_id', type=int)
    gender = request.args.get('gender')
    search = request.args.get('search')
    is_new_arrival = request.args.get('new_arrival')

    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if gender and gender != 'All':
        query = query.filter_by(gender=gender)
    if is_new_arrival is not None:
        val = is_new_arrival.lower() in ['true', '1']
        query = query.filter_by(is_new_arrival=val)
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) |
            (Product.brand.ilike(f'%{search}%')) |
            (Product.description.ilike(f'%{search}%'))
        )

    products = query.order_by(Product.id.desc()).all()
    return jsonify([p.to_dict() for p in products])

@product_bp.route('/new-arrivals', methods=['GET'])
def get_new_arrivals():
    products = Product.query.filter_by(is_new_arrival=True).order_by(Product.id.desc()).all()
    return jsonify([p.to_dict() for p in products])

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@product_bp.route('', methods=['POST'])
def create_product():
    data = request.get_json() or {}
    name = data.get('name')
    selling_price = data.get('selling_price')

    if not name or selling_price is None:
        return jsonify({'error': 'Product name and selling price are required'}), 400

    product = Product(
        name=name,
        description=data.get('description', ''),
        category_id=data.get('category_id'),
        brand=data.get('brand', ''),
        gender=data.get('gender', 'Unisex'),
        purchase_price=float(data.get('purchase_price', 0.0)),
        selling_price=float(selling_price),
        quantity=int(data.get('quantity', 0)),
        minimum_stock=int(data.get('minimum_stock', 5)),
        supplier_name=data.get('supplier_name', ''),
        supplier_contact=data.get('supplier_contact', ''),
        image_url=data.get('image_url', ''),
        is_new_arrival=bool(data.get('is_new_arrival', False))
    )
    db.session.add(product)
    db.session.flush()

    # Add variants
    variants = data.get('variants', [])
    for v in variants:
        variant = ProductVariant(
            product_id=product.id,
            size=v.get('size', 'Free Size'),
            color=v.get('color', 'Standard'),
            quantity=int(v.get('quantity', 0))
        )
        db.session.add(variant)

    if product.quantity > 0:
        tx = InventoryTransaction(
            product_id=product.id,
            transaction_type='STOCK_ADDED',
            quantity=product.quantity,
            reason='Initial Stock Entry'
        )
        db.session.add(tx)

    db.session.commit()
    return jsonify(product.to_dict()), 201

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.category_id = data.get('category_id', product.category_id)
    product.brand = data.get('brand', product.brand)
    product.gender = data.get('gender', product.gender)
    product.purchase_price = float(data.get('purchase_price', product.purchase_price))
    product.selling_price = float(data.get('selling_price', product.selling_price))
    product.minimum_stock = int(data.get('minimum_stock', product.minimum_stock))
    product.supplier_name = data.get('supplier_name', product.supplier_name)
    product.supplier_contact = data.get('supplier_contact', product.supplier_contact)
    product.image_url = data.get('image_url', product.image_url)
    if 'is_new_arrival' in data:
        product.is_new_arrival = bool(data['is_new_arrival'])

    # Update Stock if adjusted
    if 'quantity' in data:
        new_qty = int(data['quantity'])
        diff = new_qty - product.quantity
        if diff != 0:
            tx = InventoryTransaction(
                product_id=product.id,
                transaction_type='ADJUSTMENT' if diff > 0 else 'STOCK_REDUCED',
                quantity=abs(diff),
                reason=data.get('adjustment_reason', 'Manual Stock Adjustment')
            )
            db.session.add(tx)
            product.quantity = max(0, new_qty)

    db.session.commit()
    return jsonify(product.to_dict())

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})
