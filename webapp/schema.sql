DROP TABLE IF EXISTS products;

CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  original_store TEXT NOT NULL,
  current_price REAL NOT NULL,
  old_price REAL NOT NULL,
  link TEXT,
  package_size TEXT,
  date_started TEXT,
  date_ended TEXT,
);
