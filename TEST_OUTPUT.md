# Test Run Output

> **Honest note:** the output below was produced by the AI assistant in its own sandbox (Python 3.12.3, Django 6.1.3,
> DRF 3.18.3), NOT on my computer. **[FILL IN]** Before submitting, run the command below on your own machine and
> replace this block with your own terminal output (or use the GitHub Actions link instead).

## Command
```
python manage.py test -v 2
```

## Output (assistant sandbox)
```
Found 13 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
    Running deferred SQL...
Running migrations:
System check identified no issues (0 silenced).
test_no_items_and_no_boxes (boxes.tests.AlgorithmTests.test_no_items_and_no_boxes) ... ok
test_quantity_is_packed_not_just_volume (boxes.tests.AlgorithmTests.test_quantity_is_packed_not_just_volume) ... ok
test_rotation_is_used (boxes.tests.AlgorithmTests.test_rotation_is_used) ... ok
test_smallest_box_then_cheapest (boxes.tests.AlgorithmTests.test_smallest_box_then_cheapest) ... ok
test_volume_ok_but_shape_wrong (boxes.tests.AlgorithmTests.test_volume_ok_but_shape_wrong) ... ok
test_weight_limit (boxes.tests.AlgorithmTests.test_weight_limit) ... ok
test_empty_order_rejected (boxes.tests.ApiTests.test_empty_order_rejected) ... ok
test_order_flow (boxes.tests.ApiTests.test_order_flow) ... ok
test_add_row_template_and_many_rows (boxes.tests.OrderFormRowsTests.test_add_row_template_and_many_rows) ... ok
test_create_order_shows_result (boxes.tests.WebTests.test_create_order_shows_result) ... ok
test_order_without_items_is_rejected (boxes.tests.WebTests.test_order_without_items_is_rejected) ... ok
test_pages_load (boxes.tests.WebTests.test_pages_load) ... ok
test_product_in_order_cannot_be_deleted (boxes.tests.WebTests.test_product_in_order_cannot_be_deleted) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.103s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

## GitHub Actions
Workflow file: `.github/workflows/tests.yml` (runs `manage.py check` and the tests on every push).
**[FILL IN]** link to your successful run: `https://github.com/<user>/<repo>/actions`
