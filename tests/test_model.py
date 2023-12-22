import pytest
from model.model import Batch
from model.model import OrderLine
from model.model import OutOfStock
from model.model import allocate
from datetime import date
from datetime import timedelta

today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=5)

# Tests based on ALLOCATION.md

def make_batch_and_line(sku, batch_qty, order_line_qty):
    return (
            Batch("BATCH001", sku, batch_qty, eta=date.today()),
            OrderLine("ORDER001", sku, order_line_qty),
            )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    order_line = OrderLine("ORDER001", "RED-CHAIR", 2)
    batch = Batch("BATCH001", "RED-CHAIR", 3, date.today())
    batch.allocate(order_line)
    assert batch.available_quantity == 1

def test_can_allocate_if_available_greater_than_required():
    large_batch, small_order_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_order_line)

def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_order_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_order_line) is False

def test_can_allocate_if_available_equal_to_required():
    batch, order_line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(order_line)

def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("BATCH001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_order_line = OrderLine("ORDER001", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_order_line) is False

def test_can_only_deallocate_allocated_order_lines():
   batch, unallocated_order_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
   batch.deallocate(unallocated_order_line)
   assert batch.available_quantity == 20

def test_allocation_is_idempotent():
    batch, order_line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(order_line)
    batch.allocate(order_line)
    assert batch.available_quantity == 18

def test_prefers_warehouse_batches_to_shipment():
    in_stock_batch = Batch("BATCH001", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("BATCH002", "RETRO-CLOCK", 100, eta=tomorrow) 
    order_line = OrderLine("ORDER001", "RETRO-CLOCK", 10)
    allocate(order_line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

    
def test_prefers_earlier_batches():
    earliest = Batch("BATCH001", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("BATCH002", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("BATCH003", "MINIMALIST-SPOON", 100, eta=later)
    order_line = OrderLine("ORDER001", "MINIMALIST-SPOON", 10)

    allocate(order_line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100

def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("BATCH001", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("BATCH002", "HIGHBROW-POSTER", 100, eta=tomorrow)

    order_line = OrderLine("ORDER001", "HIGHBROW-POSTER", 10)
    allocation = allocate(order_line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference

def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("BATCH001", "SMALL-FORK", 10, eta=today)
    order_line = OrderLine("ORDER001", "SMALL-FORK", 10)
    allocate(order_line, [batch])

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        allocate(OrderLine("ORDER002", "SMALL-FORK", 1), [batch])

