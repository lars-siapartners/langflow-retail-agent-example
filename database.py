from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List
import pandas as pd
from sqlalchemy.engine import Engine


class Product(SQLModel, table=True):
    __tablename__ = "product"
    __table_args__ = {"extend_existing": True}
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str | None = None
    price: float
    supplier: str = Field(foreign_key="supplier.id")


class CustomerOrder(SQLModel, table=True):
    __tablename__ = "customer_order"
    __table_args__ = {"extend_existing": True}
    id: int = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    total_price: float


class StockLevels(SQLModel, table=True):
    __tablename__ = "stock_levels"
    __table_args__ = {"extend_existing": True}
    id: int = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    stock_quantity: int


class Supplier(SQLModel, table=True):
    __tablename__ = "supplier"
    __table_args__ = {"extend_existing": True}
    id: int = Field(default=None, primary_key=True)
    name: str
    contact_info: str | None = None


class RestockRules(SQLModel, table=True):
    __tablename__ = "restock_rules"
    __table_args__ = {"extend_existing": True}
    id: int = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    order_quantity: int
    minimum_stock: int


def create_db() -> Engine:
    engine = create_engine("sqlite:///retail_inventory.db")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    if len(get_products(engine)) == 0:
        generate_sample_data(engine)
    return engine

def load_db() -> Engine:
    engine = create_engine("sqlite:///retail_inventory.db")
    SQLModel.metadata.create_all(engine)

    return engine


def generate_sample_data(engine: Engine):
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Sample Suppliers
        supplier1 = Supplier(
            name="Lars's Supplies Co.", contact_info="lars.vansomeren@sia-partners.com"
        )

        session.add(supplier1)
        session.commit()

        # Sample Products
        product1 = Product(
            name="Laptop",
            description="A high-performance laptop",
            price=1200.00,
            supplier=supplier1.id,
        )
        product2 = Product(
            name="Smartphone",
            description="A latest model smartphone",
            price=800.00,
            supplier=supplier1.id,
        )

        session.add_all([product1, product2])
        session.commit()

        # Sample Stock Levels
        stock1 = StockLevels(product_id=product1.id, stock_quantity=50)
        stock2 = StockLevels(product_id=product2.id, stock_quantity=100)

        # Sample Restock Rules
        restock_rule1 = RestockRules(
            product_id=product1.id, order_quantity=20, minimum_stock=50
        )
        restock_rule2 = RestockRules(
            product_id=product2.id, order_quantity=30, minimum_stock=50
        )

        session.add_all([stock1, stock2, restock_rule1, restock_rule2])
        session.commit()


def process_order(order: CustomerOrder, engine: Engine):
    with Session(engine) as session:
        product = session.get(Product, order.product_id)
        if not product:
            raise ValueError("Product not found")

        stock = session.exec(
            SQLModel.select(StockLevels).where(StockLevels.product_id == product.id)
        ).first()

        if not stock or stock.stock_quantity < order.quantity:
            raise ValueError("Insufficient stock")

        order.total_price = product.price * order.quantity
        stock.stock_quantity -= order.quantity

        session.add(order)
        session.add(stock)
        session.commit()


def get_products(engine: Engine) -> List[Product]:
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
    return products


def get_product_data(engine: Engine) -> pd.DataFrame:
    with Session(engine) as session:
        data = session.exec(
            select(Product, StockLevels, RestockRules, Supplier)
            .join(StockLevels)
            .join(RestockRules)
            .join(Supplier)
        ).all()

    df = pd.DataFrame(
        [
            {
                "Name": p.name,
                "Stock Quantity": sl.stock_quantity,
                "Minimum Stock": rr.minimum_stock,
                "Order Quantity": rr.order_quantity,
                "Supplier Email": s.contact_info,
            }
            for p, sl, rr, s in data
        ]
    )
    return df
