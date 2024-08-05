# Wait for MySQL to be ready
until mysql -h db -u root -proot_password -e "SELECT 1" &> /dev/null; do
  echo "Waiting for MySQL..."
  sleep 2
done

# Debug: Check MySQL connection
mysql -h db -u root -proot_password -e "SHOW DATABASES;" || { echo "Failed to connect to MySQL"; exit 1; }

# Grant all privileges to root
mysql -h db -u root -proot_password -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;" || { echo "Failed to grant privileges to root"; exit 1; }
echo "Granted all privileges to root"

# Grant CREATE and DROP privileges to the DB_USER
mysql -h db -u root -proot_password -e "GRANT ALL PRIVILEGES ON *.* TO '${DB_USER}'@'%'; FLUSH PRIVILEGES;" || { echo "Failed to grant CREATE, DROP privileges to ${DB_USER}"; exit 1; }
echo "Granted CREATE, DROP privileges to ${DB_USER}"