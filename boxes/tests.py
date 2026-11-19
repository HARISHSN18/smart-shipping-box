from django.test import TestCase
from rest_framework.test import APITestCase

from .models import Box, Order, OrderItem, Product
from .services import recommend_box, recommend_for_order


def box(name, l, w, h, mw=10, cost="1.00"):
    return Box(name=name, length=l, width=w, height=h, max_weight=mw, cost=cost)


class AlgorithmTests(TestCase):
    def test_rotation_is_used(self):
        r = recommend_box([(30, 5, 5, 1, 1)], [box("tall", 5, 5, 30)])
        self.assertTrue(r.fits)

    def test_quantity_is_packed_not_just_volume(self):
        boxes = [box("cube", 20, 20, 20)]
        self.assertTrue(recommend_box([(10, 10, 10, 1, 8)], boxes).fits)
        self.assertFalse(recommend_box([(10, 10, 10, 1, 9)], boxes).fits)

    def test_volume_ok_but_shape_wrong(self):
        # 2 sticks 30x10x10 have volume 6000 = box volume 6000, but 30 > 20 in a 20x20x15 box
        r = recommend_box([(30, 10, 10, 1, 2)], [box("flat", 20, 20, 15)])
        self.assertFalse(r.fits)
        self.assertIn("larger than every box", r.reason)

    def test_weight_limit(self):
        r = recommend_box([(5, 5, 5, 6, 2)], [box("b", 20, 20, 20, mw=10)])
        self.assertFalse(r.fits)
        self.assertIn("kg", r.reason)

    def test_smallest_box_then_cheapest(self):
        boxes = [box("big", 40, 40, 40, cost="0.50"), box("small", 12, 12, 12, cost="2.00"),
                 box("small-cheap", 12, 12, 12, cost="1.00")]
        r = recommend_box([(10, 10, 10, 1, 1)], boxes)
        self.assertEqual(r.box.name, "small-cheap")

    def test_no_items_and_no_boxes(self):
        self.assertFalse(recommend_box([], [box("b", 1, 1, 1)]).fits)
        self.assertIn("No shipping boxes", recommend_box([(1, 1, 1, 1, 1)], []).reason)


class ApiTests(APITestCase):
    def test_order_flow(self):
        self.client.post("/api/boxes/", dict(name="M", length=40, width=30, height=20, max_weight=10, cost="1.10"))
        p = self.client.post("/api/products/", dict(name="Mug", length=10, width=10, height=11, weight=0.4)).data
        o = self.client.post("/api/orders/", {"items": [{"product": p["id"], "quantity": 3}]}, format="json")
        self.assertEqual(o.status_code, 201)
        self.assertEqual(o.data["packing_status"], "PENDING")
        r = self.client.post(f"/api/orders/{o.data['id']}/recommend/")
        self.assertEqual(r.data["packing_status"], "PACKED")
        self.assertEqual(r.data["recommended_box"]["name"], "M")
        self.assertEqual(self.client.get(f"/api/orders/{o.data['id']}/").status_code, 200)

    def test_empty_order_rejected(self):
        self.assertEqual(self.client.post("/api/orders/", {"items": []}, format="json").status_code, 400)


class WebTests(TestCase):
    def setUp(self):
        self.box = Box.objects.create(name="S", length=30, width=20, height=15, max_weight=5, cost="0.70")
        self.p = Product.objects.create(name="Shirt", length=28, width=20, height=3, weight=0.2)

    def test_pages_load(self):
        for url in ["/", "/products/", "/boxes/", "/orders/", "/orders/new/", "/products/add/", "/boxes/add/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_create_order_shows_result(self):
        r = self.client.post("/orders/new/", {
            "customer_name": "Ana", "items-TOTAL_FORMS": 1, "items-INITIAL_FORMS": 0,
            "items-0-product": self.p.id, "items-0-quantity": 2}, follow=True)
        self.assertContains(r, "Recommended box")
        self.assertEqual(Order.objects.get().packing_status, "PACKED")

    def test_order_without_items_is_rejected(self):
        r = self.client.post("/orders/new/", {"items-TOTAL_FORMS": 1, "items-INITIAL_FORMS": 0})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    def test_product_in_order_cannot_be_deleted(self):
        o = Order.objects.create()
        OrderItem.objects.create(order=o, product=self.p, quantity=1)
        self.client.post(f"/products/{self.p.id}/delete/")
        self.assertTrue(Product.objects.filter(pk=self.p.pk).exists())


class OrderFormRowsTests(TestCase):
    def test_add_row_template_and_many_rows(self):
        p1 = Product.objects.create(name="A", length=5, width=5, height=5, weight=1)
        p2 = Product.objects.create(name="B", length=6, width=6, height=6, weight=1)
        Box.objects.create(name="M", length=40, width=30, height=20, max_weight=10, cost="1.00")
        self.assertContains(self.client.get("/orders/new/"), 'id="add-row"')
        r = self.client.post("/orders/new/", {
            "items-TOTAL_FORMS": 6, "items-INITIAL_FORMS": 0,
            "items-0-product": p1.id, "items-0-quantity": 1, "items-5-product": p2.id, "items-5-quantity": 2,
            **{f"items-{i}-{k}": v for i in range(1, 5) for k, v in (("product", ""), ("quantity", 1))}}, follow=True)
        self.assertEqual(Order.objects.get().items.count(), 2)
        self.assertContains(r, "Recommended box")
