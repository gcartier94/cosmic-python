from repository.repository import AbstractRepository
from model.model import Batch


def test_repository_can_save_a_batch(session):
    batch = Batch("BATCH001", "RUSTY-SOAPDISH", 100, eta=None)

    repo =  SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execute(
            'SELECT reference, sku, _purchased_quantity, eta from "batches"'
            )
    assert list(rows) == [("BATCH001", "RUSTY-SIAPDISH", 100, None)]

def insert_order_line(session):
    session.execute(
            "INSERT INTO order_lines (orderid, sku, qty)"
            ' VALUES ("ORDER001", "GENERIC-SOFA", 12)'
            )
    [[order_line_id]] = session.execute(
            "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
            dict(orderid="ORDER001", sku="GENERIC-SOFA"),
            )
    return order_line_id

def insert_batch(session, batch_id):
    pass

def insert_allocation(session):
    pass

def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "BATCH001")
    insert_batch(session, "BATCH002")
    pass 
