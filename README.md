inventory_system/
├── app.py                  # App factory + blueprint registration
├── config.py               # Environment-based configuration
├── database/
│   ├── db.py               # Connection pool + context manager
│   └── schema.sql          # Full schema with indexes + seed data
├── models/
│   ├── product.py          # Product DB operations + adjust_stock()
│   ├── sale.py             # Sale creation with atomic stock deduction
│   ├── purchase.py         # Purchase creation with stock increase
│   ├── category.py
│   └── supplier.py
├── routes/
│   ├── auth_routes.py      # Login, logout, register
│   ├── product_routes.py   # Product CRUD + low-stock + export
│   ├── sale_routes.py      # Sale creation + export
│   ├── purchase_routes.py  # Purchase creation + export
│   ├── analytics_routes.py # Dashboard, profit report, reorder
│   └── catalog_routes.py   # Categories + Suppliers
├── services/
│   ├── analytics.py        # All reporting SQL (GROUP BY, SUM)
│   ├── auth.py             # Login logic + decorators
│   └── export.py           # CSV builder
└── tests/
    └── test_core.py        # Unit tests for business logic