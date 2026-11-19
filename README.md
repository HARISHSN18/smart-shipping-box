# Smart Shipping Box Recommendation System

Django + Django REST Framework + SQLite + Bootstrap 5.

## Run on Windows (VS Code terminal)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data          # optional sample boxes and products
python manage.py createsuperuser    # optional, for /admin/
python manage.py runserver
```
Open http://127.0.0.1:8000/ . Run the tests with `python manage.py test`.

## Pages
`/` home · `/products/` · `/boxes/` · `/orders/new/` · `/orders/<id>/` (result page with 3D preview)

## REST API (`/api/`)
| Method | URL | Purpose |
|---|---|---|
| GET, POST | `/api/products/`, `/api/boxes/` | list / create |
| GET, PUT, PATCH, DELETE | `/api/products/<id>/`, `/api/boxes/<id>/` | detail / update / delete |
| POST | `/api/orders/` | create order `{"customer_name":"", "items":[{"product":1,"quantity":2}]}` |
| GET | `/api/orders/`, `/api/orders/<id>/` | order details + recommendation |
| POST | `/api/orders/<id>/recommend/` | calculate / recalculate the best box |

## Project layout
- `models.py` Product, Box, Order, OrderItem
- `services.py` packing algorithm + recommendation (no logic in views)
- `serializers.py`, `views.py` (API viewsets + web views), `urls.py` (pages), `api_urls.py` (API)
- `forms.py`, `admin.py`, `tests.py`, `templates/boxes/`, `static/boxes/`

## Algorithm and limitations
See the docstring at the top of `boxes/services.py`. In short: a first-fit 3D heuristic that tries
all 6 rotations at corner positions. It never wrongly says "fits", but may miss tight arrangements,
ignores padding/fragility, and does not split orders into several parcels.

## Test cases (`boxes/tests.py`, 13 tests)
| Test | What it checks |
|---|---|
| `test_rotation_is_used` | A 30x5x5 item fits a 5x5x30 box only by rotating it |
| `test_quantity_is_packed_not_just_volume` | 8 cubes fit a 20 cm cube, the 9th does not |
| `test_volume_ok_but_shape_wrong` | Equal volume is not enough: shape must fit |
| `test_weight_limit` | Order heavier than box capacity is rejected with a message |
| `test_smallest_box_then_cheapest` | Smallest box wins; equal size -> cheapest |
| `test_no_items_and_no_boxes` | Meaningful messages for an empty order / no boxes |
| `test_order_flow` | API: create order, recommend, retrieve |
| `test_empty_order_rejected` | API returns 400 for an order without items |
| `test_pages_load` | All dashboard pages return 200 |
| `test_create_order_shows_result` | Web order creation shows the recommendation |
| `test_order_without_items_is_rejected` | Web form rejects an empty order |
| `test_product_in_order_cannot_be_deleted` | Protected product stays in the database |
| `test_add_row_template_and_many_rows` | "Add row" form with many rows saves correctly |

Run them with `python manage.py test -v 2`. Output: `TEST_OUTPUT.md`. CI: `.github/workflows/tests.yml`.

## Submission files
- `README.md` this file
- `AI_USAGE.md` how AI was used, mistakes found, verification
- `docs/` exported chat transcript
- `TEST_OUTPUT.md` test run output
