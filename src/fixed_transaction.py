"""Practice 7: fix definite assignment, dead store and audit resource leak."""


def process_transaction(
    user_id, amount, db_connection, *, audit_path="audit_log.txt"
):
    """Process a positive amount and append the final status to the audit.

    The connection must provide get_balance(user_id) and
    update_balance(user_id, new_balance). Nonpositive amounts stay pending
    and do not access the database. Database and file errors propagate.
    audit_path is optional so tests can use an isolated temporary file.
    """
    status = "pending"
    if amount > 0:
        balance = db_connection.get_balance(user_id)
        new_balance = balance - amount
        db_connection.update_balance(user_id, new_balance)
        status = "approved"
    log_entry = "Transaction finished with status: " + status
    with open(audit_path, "a", encoding="utf-8") as audit_file:
        audit_file.write(log_entry + "\n")
    return status
