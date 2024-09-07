-- este archivo prepara la base de datos que se puede usar con este programa
-- recomendado ejecutarlo una sola vez
-- creado por Hapurobokka

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT
);

CREATE TABLE IF NOT EXISTS shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shift_name TEXT
);

CREATE TABLE IF NOT EXISTS dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    price INTEGER
);

CREATE TABLE IF NOT EXISTS registers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    date_id INTEGER,
    shift_id INTEGER,

    CONSTRAINT fk_employee FOREIGN KEY(employee_id) REFERENCES employees(id),
    CONSTRAINT fk_date FOREIGN KEY(date_id) REFERENCES dates(id),
    CONSTRAINT fk_shift FOREIGN KEY(shift_id) REFERENCES shifts(id)
);

CREATE TABLE IF NOT EXISTS machine_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    register_id INTEGER,
    machine_name TEXT,
    amount INTEGER,
    CONSTRAINT fk_register FOREIGN KEY(register_id) REFERENCES registers(id)
);

CREATE TABLE IF NOT EXISTS machine_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    register_id INTEGER,
    machine_name TEXT,
    amount INTEGER,
    CONSTRAINT fk_register FOREIGN KEY(register_id) REFERENCES registers(id)
);

CREATE TABLE IF NOT EXISTS replenishments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    register_id INTEGER,
    machine_name TEXT,
    amount INTEGER,
    CONSTRAINT fk_register FOREIGN KEY(register_id) REFERENCES registers(id)
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    register_id INTEGER,
    concept TEXT,
    amount INTEGER,
    CONSTRAINT fk_register FOREIGN KEY(register_id) REFERENCES registers(id)
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    register_id INTEGER,
    concept TEXT,
    amount INTEGER,
    CONSTRAINT fk_register FOREIGN KEY(register_id) REFERENCES registers(id)
);

CREATE TABLE IF NOT EXISTS products_sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    register_id INTEGER,
    product_id INTEGER,
    in_product INTEGER,
    out_product INTEGER,
    profits INTEGER,

    CONSTRAINT fk_register FOREIGN KEY(register_id) REFERENCES registers(id),
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    register_id INTEGER,
    final_profits INTEGER,
    final_expenses INTEGER,
    total_funds INTEGER,
    initial_funds INTEGER,
    extra_funds INTEGER,
    reported_funds INTEGER,
    difference INTEGER,

    CONSTRAINT fk_register FOREIGN KEY (register_id) REFERENCES registers(id)
)
