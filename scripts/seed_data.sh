#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

escape_sql_literal() {
  local value="${1:-}"
  value=${value//\'/\'\'}
  printf "'%s'" "$value"
}

invoke_sqlite() {
  local db_path="$1"
  local sql="$2"
  sqlite3 "$db_path" "$sql"
}

invoke_sqlite_scalar() {
  local db_path="$1"
  local sql="$2"
  sqlite3 "$db_path" "$sql" | head -n 1 | tr -d '\r'
}

ensure_db_file() {
  local db_path="$1"
  if [[ ! -f "$db_path" ]]; then
    echo "[ERROR] Database file not found: $db_path" >&2
    exit 1
  fi
}

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "[ERROR] sqlite3 command not found in PATH." >&2
  exit 1
fi

declare -A db
db[books]="$WORKSPACE_ROOT/book-service/book_service/db.sqlite3"
db[categories]="$WORKSPACE_ROOT/catalog-service/catalog_service/db.sqlite3"
db[customers]="$WORKSPACE_ROOT/customer-service/customer_service/db.sqlite3"
db[carts]="$WORKSPACE_ROOT/cart-service/cart_service/db.sqlite3"
db[staff]="$WORKSPACE_ROOT/staff-service/staff_service/db.sqlite3"
db[managers]="$WORKSPACE_ROOT/manager-service/manager_service/db.sqlite3"
db[reviews]="$WORKSPACE_ROOT/comment-rate-service/comment_rate_service/db.sqlite3"
db[orders]="$WORKSPACE_ROOT/order-service/order_service/db.sqlite3"
db[payments]="$WORKSPACE_ROOT/pay-service/pay_service/db.sqlite3"
db[shipments]="$WORKSPACE_ROOT/ship-service/ship_service/db.sqlite3"

for key in "${!db[@]}"; do
  ensure_db_file "${db[$key]}"
done

book_has_image_column="$(invoke_sqlite_scalar "${db[books]}" "SELECT 1 FROM pragma_table_info('app_book') WHERE name = 'image' LIMIT 1;")"

echo "Seeding categories ..."
invoke_sqlite "${db[categories]}" "INSERT INTO app_category (name, description, created_at, parent_id) SELECT 'Fiction', 'Fiction books', datetime('now'), NULL WHERE NOT EXISTS (SELECT 1 FROM app_category WHERE name = 'Fiction');"
invoke_sqlite "${db[categories]}" "INSERT INTO app_category (name, description, created_at, parent_id) SELECT 'Self-Help', 'Self-help and self-improvement books', datetime('now'), NULL WHERE NOT EXISTS (SELECT 1 FROM app_category WHERE name = 'Self-Help');"
invoke_sqlite "${db[categories]}" "INSERT INTO app_category (name, description, created_at, parent_id) SELECT 'Sci-Fi', 'Science fiction', datetime('now'), NULL WHERE NOT EXISTS (SELECT 1 FROM app_category WHERE name = 'Sci-Fi');"
invoke_sqlite "${db[categories]}" "INSERT INTO app_category (name, description, created_at, parent_id) SELECT 'Mystery', 'Mystery and thriller books', datetime('now'), NULL WHERE NOT EXISTS (SELECT 1 FROM app_category WHERE name = 'Mystery');"
invoke_sqlite "${db[categories]}" "INSERT INTO app_category (name, description, created_at, parent_id) SELECT 'Non-Fiction', 'Non-fiction books', datetime('now'), NULL WHERE NOT EXISTS (SELECT 1 FROM app_category WHERE name = 'Non-Fiction');"
invoke_sqlite "${db[categories]}" "INSERT INTO app_category (name, description, created_at, parent_id) SELECT 'Biography', 'Biographies and autobiographies', datetime('now'), NULL WHERE NOT EXISTS (SELECT 1 FROM app_category WHERE name = 'Biography');"
invoke_sqlite "${db[categories]}" "INSERT INTO app_category (name, description, created_at, parent_id) SELECT 'Technology', 'Technology and computer science', datetime('now'), NULL WHERE NOT EXISTS (SELECT 1 FROM app_category WHERE name = 'Technology');"
invoke_sqlite "${db[categories]}" "INSERT INTO app_category (name, description, created_at, parent_id) SELECT 'Business', 'Business, finance and investing', datetime('now'), NULL WHERE NOT EXISTS (SELECT 1 FROM app_category WHERE name = 'Business');"
invoke_sqlite "${db[categories]}" "INSERT INTO app_category (name, description, created_at, parent_id) SELECT 'Fantasy', 'Fantasy world books', datetime('now'), NULL WHERE NOT EXISTS (SELECT 1 FROM app_category WHERE name = 'Fantasy');"


 

echo "Seeding books ..."
seed_book() {
  local title="$1" author="$2" price="$3" stock="$4" image="$5" category="$6" format="$7" pages="$8" language="$9" publisher="${10}" publicationDate="${11}" isbn="${12}" description="${13}"
  local t a i c f l p pd is d
  t=$(escape_sql_literal "$title")
  a=$(escape_sql_literal "$author")
  i=$(escape_sql_literal "$image")
  c=$(escape_sql_literal "$category")
  f=$(escape_sql_literal "$format")
  l=$(escape_sql_literal "$language")
  p=$(escape_sql_literal "$publisher")
  pd=$(escape_sql_literal "$publicationDate")
  is=$(escape_sql_literal "$isbn")
  d=$(escape_sql_literal "$description")

  if [[ "$book_has_image_column" == "1" ]]; then
    invoke_sqlite "${db[books]}" "INSERT INTO app_book (title, author, price, stock, image, category, format, pages, language, publisher, publicationDate, isbn, description) SELECT $t, $a, $price, $stock, $i, $c, $f, $pages, $l, $p, $pd, $is, $d WHERE NOT EXISTS (SELECT 1 FROM app_book WHERE title = $t AND author = $a);"
  else
    invoke_sqlite "${db[books]}" "INSERT INTO app_book (title, author, price, stock) SELECT $t, $a, $price, $stock WHERE NOT EXISTS (SELECT 1 FROM app_book WHERE title = $t AND author = $a);"
  fi
}

seed_book "The Midnight Library" "Matt Haig" "24.99" "15" "https://picsum.photos/seed/book1/300/450" "Fiction" "Hardcover" "304" "English" "Viking" "Sept 29, 2020" "978-0525559474" "Between life and death there is a library..."
seed_book "Atomic Habits" "James Clear" "19.99" "42" "https://picsum.photos/seed/book2/300/450" "Self-Help" "Paperback" "320" "English" "Avery" "Oct 16, 2018" "978-0735211292" "No matter your goals, Atomic Habits offers a proven framework..."
seed_book "Project Hail Mary" "Andy Weir" "22.50" "8" "https://picsum.photos/seed/book3/300/450" "Sci-Fi" "Hardcover" "496" "English" "Ballantine Books" "May 4, 2021" "978-0593135204" "Ryland Grace is the sole survivor..."
seed_book "Dune" "Frank Herbert" "21.00" "25" "https://picsum.photos/seed/book4/300/450" "Sci-Fi" "Paperback" "896" "English" "Ace Books" "Oct 1, 1990" "978-0441172719" "Set on the desert planet Arrakis..."
seed_book "The Silent Patient" "Alex Michaelides" "18.50" "12" "https://picsum.photos/seed/book5/300/450" "Mystery" "Paperback" "336" "English" "Celadon Books" "Feb 5, 2019" "978-1250301697" "Alicia Berenson’s life is seemingly perfect..."
seed_book "Sapiens: A Brief History of Humankind" "Yuval Noah Harari" "25.00" "30" "https://picsum.photos/seed/book6/300/450" "Non-Fiction" "Paperback" "464" "English" "Harper" "Feb 10, 2015" "978-0062316097" "From a renowned historian..."
seed_book "Thinking, Fast and Slow" "Daniel Kahneman" "20.00" "18" "https://picsum.photos/seed/book7/300/450" "Non-Fiction" "Paperback" "499" "English" "Farrar, Straus and Giroux" "Apr 2, 2013" "978-0374533557" "The phenomenal New York Times Bestseller..."
seed_book "1984" "George Orwell" "15.99" "50" "https://picsum.photos/seed/book8/300/450" "Fiction" "Paperback" "328" "English" "Signet Classic" "Jan 1, 1950" "978-0451524935" "Among the seminal texts of the 20th century..."
seed_book "The Alchemist" "Paulo Coelho" "16.99" "35" "https://picsum.photos/seed/book9/300/450" "Fiction" "Paperback" "208" "English" "HarperOne" "Apr 15, 2014" "978-0062315007" "Paulo Coelho's enchanting novel..."
seed_book "Becoming" "Michelle Obama" "22.00" "22" "https://picsum.photos/seed/book10/300/450" "Biography" "Hardcover" "448" "English" "Crown" "Nov 13, 2018" "978-1524763138" "In a life filled with meaning and accomplishment..."
seed_book "The Psychology of Money" "Morgan Housel" "18.99" "40" "https://picsum.photos/seed/book11/300/450" "Self-Help" "Paperback" "252" "English" "Harriman House" "Sep 8, 2020" "978-0857197689" "Doing well with money isn't necessarily about what you know..."
seed_book "Educated" "Tara Westover" "17.99" "14" "https://picsum.photos/seed/book12/300/450" "Biography" "Paperback" "352" "English" "Random House" "Feb 20, 2018" "978-0399590504" "An unforgettable memoir about a young girl..."
seed_book "Clean Code" "Robert C. Martin" "34.50" "25" "https://picsum.photos/seed/book13/300/450" "Technology" "Paperback" "464" "English" "Prentice Hall" "Aug 1, 2008" "978-0132350884" "Even bad code can function..." 
seed_book "The Pragmatic Programmer" "David Thomas" "39.99" "15" "https://picsum.photos/seed/book14/300/450" "Technology" "Hardcover" "352" "English" "Addison-Wesley" "Sep 13, 2019" "978-0135957059" "The Pragmatic Programmer is one of those rare tech books..."
seed_book "Fluent Python" "Luciano Ramalho" "45.00" "12" "https://picsum.photos/seed/book15/300/450" "Technology" "Paperback" "984" "English" "O'Reilly Media" "May 20, 2022" "978-1492056355" "Python's simplicity lets you become productive quickly..."
seed_book "Designing Data-Intensive Applications" "Martin Kleppmann" "42.50" "20" "https://picsum.photos/seed/book16/300/450" "Technology" "Paperback" "616" "English" "O'Reilly Media" "Mar 16, 2017" "978-1449373320" "Data is at the center of many challenges..."

book_1="$(invoke_sqlite_scalar "${db[books]}" "SELECT id FROM app_book WHERE title='The Midnight Library' AND author='Matt Haig' LIMIT 1;")"
book_2="$(invoke_sqlite_scalar "${db[books]}" "SELECT id FROM app_book WHERE title='Atomic Habits' AND author='James Clear' LIMIT 1;")"
book_3="$(invoke_sqlite_scalar "${db[books]}" "SELECT id FROM app_book WHERE title='Project Hail Mary' AND author='Andy Weir' LIMIT 1;")"
book_4="$(invoke_sqlite_scalar "${db[books]}" "SELECT id FROM app_book WHERE title='Dune' AND author='Frank Herbert' LIMIT 1;")"
book_cc="$(invoke_sqlite_scalar "${db[books]}" "SELECT id FROM app_book WHERE title='Clean Code' AND author='Robert C. Martin' LIMIT 1;")"
book_pp="$(invoke_sqlite_scalar "${db[books]}" "SELECT id FROM app_book WHERE title='The Pragmatic Programmer' AND author='David Thomas' LIMIT 1;")"
book_fp="$(invoke_sqlite_scalar "${db[books]}" "SELECT id FROM app_book WHERE title='Fluent Python' AND author='Luciano Ramalho' LIMIT 1;")"
book_1984="$(invoke_sqlite_scalar "${db[books]}" "SELECT id FROM app_book WHERE title='1984' AND author='George Orwell' LIMIT 1;")"

for v in "$book_1" "$book_2" "$book_3" "$book_4" "$book_cc" "$book_pp" "$book_fp" "$book_1984"; do
  if [[ -z "$v" ]]; then
    echo "[ERROR] Cannot resolve seeded book IDs." >&2
    exit 1
  fi
done


echo "Seeding customers ..."
invoke_sqlite "${db[customers]}" "INSERT INTO app_customer (name, email) SELECT 'Nguyen Van An', 'nguyenvanan@example.com' WHERE NOT EXISTS (SELECT 1 FROM app_customer WHERE email='nguyenvanan@example.com');"
invoke_sqlite "${db[customers]}" "INSERT INTO app_customer (name, email) SELECT 'Tran Minh Chau', 'tranminhchau@example.com' WHERE NOT EXISTS (SELECT 1 FROM app_customer WHERE email='tranminhchau@example.com');"
invoke_sqlite "${db[customers]}" "INSERT INTO app_customer (name, email) SELECT 'Le Hoang Duc', 'lehoangduc@example.com' WHERE NOT EXISTS (SELECT 1 FROM app_customer WHERE email='lehoangduc@example.com');"

customer_an="$(invoke_sqlite_scalar "${db[customers]}" "SELECT id FROM app_customer WHERE email='nguyenvanan@example.com' LIMIT 1;")"
customer_chau="$(invoke_sqlite_scalar "${db[customers]}" "SELECT id FROM app_customer WHERE email='tranminhchau@example.com' LIMIT 1;")"
customer_duc="$(invoke_sqlite_scalar "${db[customers]}" "SELECT id FROM app_customer WHERE email='lehoangduc@example.com' LIMIT 1;")"

for v in "$customer_an" "$customer_chau" "$customer_duc"; do
  if [[ -z "$v" ]]; then
    echo "[ERROR] Cannot resolve seeded customer IDs." >&2
    exit 1
  fi
done

echo "Seeding carts ..."
invoke_sqlite "${db[carts]}" "INSERT INTO app_cart (customer_id, created_at) SELECT $customer_an, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_cart WHERE customer_id = $customer_an);"
invoke_sqlite "${db[carts]}" "INSERT INTO app_cart (customer_id, created_at) SELECT $customer_chau, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_cart WHERE customer_id = $customer_chau);"
invoke_sqlite "${db[carts]}" "INSERT INTO app_cart (customer_id, created_at) SELECT $customer_duc, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_cart WHERE customer_id = $customer_duc);"

echo "Seeding staff ..."
invoke_sqlite "${db[staff]}" "INSERT INTO app_staff (name, email, role, employee_id, is_active, created_at) SELECT 'Pham Thi Kho', 'warehouse.team@example.com', 'warehouse', 'STF001', 1, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_staff WHERE employee_id='STF001');"
invoke_sqlite "${db[staff]}" "INSERT INTO app_staff (name, email, role, employee_id, is_active, created_at) SELECT 'Vu Bao Sales', 'sales.team@example.com', 'sales', 'STF002', 1, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_staff WHERE employee_id='STF002');"
invoke_sqlite "${db[staff]}" "INSERT INTO app_staff (name, email, role, employee_id, is_active, created_at) SELECT 'Do Support', 'support.team@example.com', 'support', 'STF003', 1, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_staff WHERE employee_id='STF003');"
invoke_sqlite "${db[staff]}" "INSERT INTO app_staff (name, email, role, employee_id, is_active, created_at) SELECT 'Vuong Security', 'security.team@example.com', 'security', 'STF004', 1, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_staff WHERE employee_id='STF004');"


echo "Seeding managers ..."
invoke_sqlite "${db[managers]}" "INSERT INTO app_manager (name, email, department, employee_id, is_active, created_at) SELECT 'Nguyen Operations', 'operations.manager@example.com', 'operations', 'MGR001', 1, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_manager WHERE employee_id='MGR001');"
invoke_sqlite "${db[managers]}" "INSERT INTO app_manager (name, email, department, employee_id, is_active, created_at) SELECT 'Tran Inventory', 'inventory.manager@example.com', 'inventory', 'MGR002', 1, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_manager WHERE employee_id='MGR002');"
invoke_sqlite "${db[managers]}" "INSERT INTO app_manager (name, email, department, employee_id, is_active, created_at) SELECT 'Le Finance', 'finance.manager@example.com', 'finance', 'MGR003', 1, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_manager WHERE employee_id='MGR003');"
invoke_sqlite "${db[managers]}" "INSERT INTO app_manager (name, email, department, employee_id, is_active, created_at) SELECT 'Truong IT', 'it.manager@example.com', 'it', 'MGR004', 1, datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_manager WHERE employee_id='MGR004');"


echo "Seeding reviews ..."
insert_review() {
  local customer_id="$1" book_id="$2" rating="$3" comment="$4"
  local c
  c=$(escape_sql_literal "$comment")
  invoke_sqlite "${db[reviews]}" "INSERT INTO app_review (customer_id, book_id, rating, comment, created_at, updated_at) SELECT $customer_id, $book_id, $rating, $c, datetime('now'), datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_review WHERE customer_id = $customer_id AND book_id = $book_id);"
}

insert_review "$customer_an" "$book_1" 5 "Sách tuyệt vời, rất đáng suy ngẫm về các lựa chọn trong cuộc đời."
insert_review "$customer_an" "$book_2" 5 "Nội dung thực tế, hữu ích để thay đổi thói quen."
insert_review "$customer_chau" "$book_3" 4 "Một chuyến phiêu lưu không gian thú vị."
insert_review "$customer_duc" "$book_4" 5 "Tuyệt tác Sci-Fi không thể bỏ qua."
insert_review "$customer_mai" "$book_cc" 5 "Sách gối đầu giường cho mọi lập trình viên."
insert_review "$customer_mai" "$book_pp" 5 "Kiến thức vô giá cho sự nghiệp IT."
insert_review "$customer_kiet" "$book_fp" 4 "Sách hay cho ai muốn hiểu sâu về Python."
insert_review "$customer_giang" "$book_1984" 5 "Một tác phẩm kinh điển đáng sợ lại rất thực tế."


echo "Seeding orders, payments and shipments ..."

address_1="123 Nguyen Hue, Quan 1, TP.HCM"
method_1="credit_card"
total_1="44.98"
addr1_sql=$(escape_sql_literal "$address_1")
method1_sql=$(escape_sql_literal "$method_1")

invoke_sqlite "${db[orders]}" "INSERT INTO app_order (customer_id, status, total_amount, shipping_address, created_at, updated_at) SELECT $customer_an, 'pending', $total_1, $addr1_sql, datetime('now'), datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_order WHERE customer_id=$customer_an AND shipping_address=$addr1_sql);"
order_1="$(invoke_sqlite_scalar "${db[orders]}" "SELECT id FROM app_order WHERE customer_id=$customer_an AND shipping_address=$addr1_sql ORDER BY id DESC LIMIT 1;")"
invoke_sqlite "${db[orders]}" "INSERT INTO app_orderitem (book_id, quantity, unit_price, order_id) SELECT $book_python_crash_course, 1, 24.99, $order_1 WHERE NOT EXISTS (SELECT 1 FROM app_orderitem WHERE order_id=$order_1 AND book_id=$book_python_crash_course AND quantity=1 AND unit_price=24.99);"
invoke_sqlite "${db[orders]}" "INSERT INTO app_orderitem (book_id, quantity, unit_price, order_id) SELECT $book_clean_code, 1, 19.99, $order_1 WHERE NOT EXISTS (SELECT 1 FROM app_orderitem WHERE order_id=$order_1 AND book_id=$book_clean_code AND quantity=1 AND unit_price=19.99);"
invoke_sqlite "${db[payments]}" "INSERT INTO app_payment (order_id, customer_id, amount, method, status, created_at, updated_at) SELECT $order_1, $customer_an, $total_1, $method1_sql, 'pending', datetime('now'), datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_payment WHERE order_id=$order_1);"
invoke_sqlite "${db[shipments]}" "INSERT INTO app_shipment (order_id, customer_id, address, tracking_number, status, created_at, updated_at) SELECT $order_1, $customer_an, $addr1_sql, 'TRK-' || $order_1, 'pending', datetime('now'), datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_shipment WHERE order_id=$order_1);"

address_2="45 Le Loi, Hai Chau, Da Nang"
method_2="paypal"
total_2="22.50"
addr2_sql=$(escape_sql_literal "$address_2")
method2_sql=$(escape_sql_literal "$method_2")

invoke_sqlite "${db[orders]}" "INSERT INTO app_order (customer_id, status, total_amount, shipping_address, created_at, updated_at) SELECT $customer_chau, 'pending', $total_2, $addr2_sql, datetime('now'), datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_order WHERE customer_id=$customer_chau AND shipping_address=$addr2_sql);"
order_2="$(invoke_sqlite_scalar "${db[orders]}" "SELECT id FROM app_order WHERE customer_id=$customer_chau AND shipping_address=$addr2_sql ORDER BY id DESC LIMIT 1;")"
invoke_sqlite "${db[orders]}" "INSERT INTO app_orderitem (book_id, quantity, unit_price, order_id) SELECT $book_fluent_python, 1, 22.50, $order_2 WHERE NOT EXISTS (SELECT 1 FROM app_orderitem WHERE order_id=$order_2 AND book_id=$book_fluent_python AND quantity=1 AND unit_price=22.50);"
invoke_sqlite "${db[payments]}" "INSERT INTO app_payment (order_id, customer_id, amount, method, status, created_at, updated_at) SELECT $order_2, $customer_chau, $total_2, $method2_sql, 'pending', datetime('now'), datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_payment WHERE order_id=$order_2);"
invoke_sqlite "${db[shipments]}" "INSERT INTO app_shipment (order_id, customer_id, address, tracking_number, status, created_at, updated_at) SELECT $order_2, $customer_chau, $addr2_sql, 'TRK-' || $order_2, 'pending', datetime('now'), datetime('now') WHERE NOT EXISTS (SELECT 1 FROM app_shipment WHERE order_id=$order_2);"

books_count="$(invoke_sqlite_scalar "${db[books]}" "SELECT COUNT(1) FROM app_book;")"
customers_count="$(invoke_sqlite_scalar "${db[customers]}" "SELECT COUNT(1) FROM app_customer;")"
carts_count="$(invoke_sqlite_scalar "${db[carts]}" "SELECT COUNT(1) FROM app_cart;")"
staff_count="$(invoke_sqlite_scalar "${db[staff]}" "SELECT COUNT(1) FROM app_staff;")"
managers_count="$(invoke_sqlite_scalar "${db[managers]}" "SELECT COUNT(1) FROM app_manager;")"
categories_count="$(invoke_sqlite_scalar "${db[categories]}" "SELECT COUNT(1) FROM app_category;")"
orders_count="$(invoke_sqlite_scalar "${db[orders]}" "SELECT COUNT(1) FROM app_order;")"
order_items_count="$(invoke_sqlite_scalar "${db[orders]}" "SELECT COUNT(1) FROM app_orderitem;")"
payments_count="$(invoke_sqlite_scalar "${db[payments]}" "SELECT COUNT(1) FROM app_payment;")"
shipments_count="$(invoke_sqlite_scalar "${db[shipments]}" "SELECT COUNT(1) FROM app_shipment;")"
reviews_count="$(invoke_sqlite_scalar "${db[reviews]}" "SELECT COUNT(1) FROM app_review;")"

echo "Seed complete (direct SQLite)."
echo "books: $books_count"
echo "customers: $customers_count"
echo "carts: $carts_count"
echo "staff: $staff_count"
echo "managers: $managers_count"
echo "categories: $categories_count"
echo "orders: $orders_count"
echo "order_items: $order_items_count"
echo "payments: $payments_count"
echo "shipments: $shipments_count"
echo "reviews: $reviews_count"
