def process_transaction(user_id, amount, db_connection):
    status = "pending"
    if amount > 0:
        balance = db_connection.get_balance(user_id)
        new_balance = balance - amount
        db_connection.update_balance(user_id, new_balance)
        status = "approved"
    log_entry = "Transaction finished with status: " + status
    with open("audit_log.txt", "a", encoding="utf-8") as file:
        file.write(log_entry + "\n")
    return status
