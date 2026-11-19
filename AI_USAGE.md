# AI Usage Report



## 1. Tools used
- **Claude** (Anthropic), via the claude.ai web chat. Model during this work: Claude Sonnet 5.5 (check the model shown in your chat).
- The assistant ran code in its own sandbox (Django `manage.py test`, `manage.py check`, `node --check`) and produced the project zip.


## 2. Prompts (in order; full text is in the chat transcript)
1. "i want create a project called ai assistant box selection for e-commerce so create the project by using python django restapi"
2. "add css to this and make webpage looks good"
3. Pasted a PowerShell error: `ModuleNotFoundError: No module named 'django'` when running `python manage.py migrate`
4. "i want to see the 3d effect of the box to recommend for the product"
5. The full assignment prompt ("Act as a Senior Python Django Developer, Software Architect, and Mentor... Smart Shipping Box Recommendation System")
6. "add that and also add css to that project to look professional" (the "Add row" button and a more professional theme)

## 3. What I accepted
- Project layout: `models.py`, `serializers.py`, `views.py`, `urls.py`, `services.py`, `admin.py`, `tests.py`.
- The packing heuristic in `services.py` (largest item first, corner positions, all 6 rotations).
- Selection rule: smallest suitable box by volume, lowest cost as tie-break.
- Bootstrap 5 server-rendered pages, REST API with DRF, order formset with an "Add row" button.
- The CSS-only 3D box preview.

## 4. What was rejected or replaced
- The first version (API plus a custom page) was **replaced** after the full assignment arrived. Removed: product SKU, fragile padding, `SelectionLog`, and the separate `packing.py` (logic moved into `services.py` as required).
- The first version ranked boxes by **cost first**. The assignment says smallest box first, then cost, so the ranking was changed to `(volume, cost)`.


## 5. Mistakes found
| Mistake | How it was found | Fix |
|---|---|---|
| Called the project "AI" but the algorithm is rule-based, not machine learning | Re-reading the code | Stated clearly in README; no ML is claimed |
| `{% load static %}` placed before `{% extends %}` in `order_detail.html` | Automated tests failed with `TemplateSyntaxError` | Moved the load tag after extends |
| A test posted formset rows without all fields, so the order was not created | A new test failed | Fixed the test data (the app code was correct) |
| Model redesign made the old `db.sqlite3` incompatible | Reasoning about migrations | Told to delete the old database and re-run `migrate` |
| `ModuleNotFoundError: django` on my machine | My own terminal output | Installed dependencies in the active venv with `pip install -r requirements.txt` |
| DRF `UserWarning: min_value should be an integer or Decimal` from a float validator on the cost field | Noticed in verbose test output | Used a `Decimal` validator and regenerated the initial migration |
| Ranking order (cost before volume) did not match the assignment | Comparing code to the assignment text | Changed to smallest volume, then cost |

## 6. Verification steps
Automated (run by the assistant, 13 tests passing):
- Packing: rotation is used; quantities are really packed (8 cubes fit in a 20 cm cube, 9 do not); volume-equal but wrong-shape case is rejected; weight limit; smallest box then cheapest; empty order and no boxes.
- API: create order, recommend, retrieve; empty order rejected.
- Web: all pages return 200; creating an order shows the result; empty order rejected; a product used in an order cannot be deleted; many rows in the order form.
- `python manage.py check`: no issues. JavaScript syntax checked with `node --check`.

## 7. Known limitations
- The packing algorithm is a heuristic: it may say "no fit" when a tight arrangement exists, but it should not say "fits" wrongly.
- Only 90-degree rotations; no padding, fragile rules or weight distribution; one box per order (no splitting).
- The assistant did not view the pages in a real browser, so visual layout and the 3D preview were not visually verified by the assistant.

## 8. Chat transcript
Exported by me, without AI, and saved in `docs/` (**[FILL IN: conversations.json and 19/11/2026]**).
