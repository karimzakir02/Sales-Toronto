DROP TABLE IF EXISTS products;

CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  original_store TEXT NOT NULL,
  current_price REAL NOT NULL,
  old_price REAL NOT NULL,
  in_stock INTEGER,
  package_size TEXT,
)
