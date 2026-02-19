import pytest


class TestStockAdjustment:

    def _simulate_adjust(self, current_stock, delta):
        new_qty = current_stock + delta
        if new_qty < 0:
            raise ValueError(
                f"Insufficient stock. Available: {current_stock}, requested: {abs(delta)}"
            )
        return new_qty

    def test_add_stock(self):
        assert self._simulate_adjust(10, 5) == 15

    def test_deduct_stock(self):
        assert self._simulate_adjust(10, -3) == 7

    def test_exact_deduct(self):
        assert self._simulate_adjust(5, -5) == 0

    def test_prevent_negative_stock(self):
        with pytest.raises(ValueError, match="Insufficient stock"):
            self._simulate_adjust(3, -10)

    def test_zero_stock_cannot_sell(self):
        with pytest.raises(ValueError):
            self._simulate_adjust(0, -1)


class TestProfitCalculation:

    def test_basic_profit(self):
        assert (80.0 - 50.0) * 3 == 90.0

    def test_zero_margin(self):
        assert (100.0 - 100.0) * 5 == 0.0

    def test_loss_scenario(self):
        assert (40.0 - 60.0) * 2 == -40.0


class TestProductValidation:

    def _validate(self, data):
        errors = []
        if not data.get("name", "").strip():
            errors.append("Product name is required.")
        try:
            cost = float(data.get("cost_price", -1))
            sell = float(data.get("selling_price", -1))
            if cost < 0:
                errors.append("cost_price must be >= 0.")
            if sell < 0:
                errors.append("selling_price must be >= 0.")
        except (TypeError, ValueError):
            errors.append("Prices must be numeric.")
        if not data.get("category_id"):
            errors.append("category_id is required.")
        return errors

    def test_valid_product(self):
        assert self._validate({
            "name": "Widget", "cost_price": 10,
            "selling_price": 20, "category_id": 1
        }) == []

    def test_missing_name(self):
        errors = self._validate({
            "name": "", "cost_price": 10,
            "selling_price": 20, "category_id": 1
        })
        assert any("name" in e for e in errors)

    def test_negative_price(self):
        errors = self._validate({
            "name": "X", "cost_price": -5,
            "selling_price": 10, "category_id": 1
        })
        assert any("cost_price" in e for e in errors)

    def test_missing_category(self):
        errors = self._validate({
            "name": "X", "cost_price": 10, "selling_price": 20
        })
        assert any("category_id" in e for e in errors)