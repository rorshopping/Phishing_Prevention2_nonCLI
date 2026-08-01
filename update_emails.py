"""Update all employee email addresses in phishguard_test.db.

Usage examples:
  # Replace @gmail.com with @company.com for all employees
  python update_emails.py --old @gmail.com --new @acmecorp.com

  # Set specific address for a single employee (by name_hash)
  python update_emails.py --name "Alice Smith" --email alice@acmecorp.com
"""
import sqlite3
import argparse

DB = r"C:\Users\Richard\Documents\Projects\Phishing_Prevention2_nonCLI\phishguard_test.db"

def bulk_replace(old: str, new: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, email_hash, name_hash FROM employees WHERE email_hash LIKE ?", (f"%{old}%",))
    found = cur.fetchall()
    if not found:
        print(f"No employees found with '{old}' in email_hash")
        conn.close()
        return
    print(f"Updating {len(found)} employees:")
    for row in found:
        new_email = row[1].replace(old, new)
        cur.execute("UPDATE employees SET email_hash = ?, email = ? WHERE id = ?", (new_email, new_email, row[0]))
        print(f"  {row[2]:20s} {row[1]} -> {new_email}")
    conn.commit()
    conn.close()

def set_one(name: str, email: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, email_hash, name_hash FROM employees WHERE name_hash = ?", (name,))
    row = cur.fetchone()
    if not row:
        print(f"No employee found with name_hash = '{name}'")
        conn.close()
        return
    cur.execute("UPDATE employees SET email_hash = ?, email = ? WHERE id = ?", (email, email, row[0]))
    conn.commit()
    conn.close()
    print(f"Updated {row[2]}: {row[1]} -> {email}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update employee emails in phishguard_test.db")
    parser.add_argument("--old", help="Bulk replace: text to replace (e.g. @gmail.com)")
    parser.add_argument("--new", help="Bulk replace: replacement text")
    parser.add_argument("--name", help="Set one: employee name_hash")
    parser.add_argument("--email", help="Set one: new email address")
    args = parser.parse_args()

    if args.old and args.new:
        bulk_replace(args.old, args.new)
    elif args.name and args.email:
        set_one(args.name, args.email)
    else:
        print("Usage:\n"
              "  python update_emails.py --old @gmail.com --new @acmecorp.com\n"
              "  python update_emails.py --name \"Alice Smith\" --email alice@acmecorp.com")
