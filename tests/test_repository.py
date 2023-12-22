from repository.repository import AbstractRepository
from model.model import OrderLine
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
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)',
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        'SELECT id FROM batches WHERE reference=:batch_id AND sku="GENERIC-SOFA"',
        dict(batch_id=batch_id),
    )
    return batch_id


def insert_allocation(session, orderline_id, batch_id):
    session.execute(
        "INSERT INTO allocations (orderline_id, batch_id)"
        " VALUES (:orderline_id, :batch_id)",
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares reference
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        OrderLine("order1", "GENERIC-SOFA", 12),
    }

