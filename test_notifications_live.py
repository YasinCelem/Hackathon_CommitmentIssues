#!/usr/bin/env python
"""Live test script for notifications - sends test notifications"""
import sys
from pathlib import Path
import time

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("LIVE NOTIFICATION TEST")
print("=" * 60)
print()

# Test 1: Import notification helper
print("[1] Importing notification helper...")
try:
    from src.FrontEnd.notification_helper import (
        create_compare_notification,
        create_form_notification,
        create_transaction_notification,
        create_generic_notification,
        set_notification_queue
    )
    print("  [OK] Notification helper imported")
except Exception as e:
    print(f"  [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize notification queue
print("\n[2] Initializing notification queue...")
try:
    from src.FrontEnd.routes import notification_queue
    set_notification_queue(notification_queue)
    print("  [OK] Notification queue initialized")
    print(f"  [INFO] Queue size: {notification_queue.qsize()}")
except Exception as e:
    print(f"  [FAIL] Queue initialization failed: {e}")
    sys.exit(1)

# Test 3: Send test notifications
print("\n[3] Sending test notifications...")
print()

# Test Compare Notification
print("  [TEST] Sending compare notification...")
create_compare_notification(
    "Test comparison: Changes detected in rental contract. Key differences include:\n"
    "- Updated rent amount from €800 to €850\n"
    "- New clause added about pet policy\n"
    "- Modified maintenance responsibility terms",
    "doc123"
)
time.sleep(0.5)
print(f"  [OK] Compare notification sent (queue size: {notification_queue.qsize()})")

# Test Form Notification
print("\n  [TEST] Sending form notification...")
create_form_notification(
    "Form filled successfully. All fields have been completed using your database information.",
    "form456",
    "filled_output.pdf"
)
time.sleep(0.5)
print(f"  [OK] Form notification sent (queue size: {notification_queue.qsize()})")

# Test Transaction Notification
print("\n  [TEST] Sending transaction notification...")
create_transaction_notification(
    "Transaction is pending. Please review and confirm to process.\n"
    "Amount: €1,250.00\n"
    "Date: 2025-11-09\n"
    "Status: Pending approval",
    "trans789"
)
time.sleep(0.5)
print(f"  [OK] Transaction notification sent (queue size: {notification_queue.qsize()})")

# Test Generic Notification
print("\n  [TEST] Sending generic notification...")
create_generic_notification(
    "System Test",
    "This is a generic test notification to verify the notification system is working correctly.",
    "info",
    {"test": True, "timestamp": time.time()}
)
time.sleep(0.5)
print(f"  [OK] Generic notification sent (queue size: {notification_queue.qsize()})")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"Total notifications in queue: {notification_queue.qsize()}")
print()
print("Next steps:")
print("1. Start the frontend server:")
print("   python -m flask --app src.FrontEnd.front_end_main run --debug --port 5000")
print()
print("2. Open your browser to: http://localhost:5000")
print()
print("3. The notifications should appear automatically via Server-Sent Events")
print("   Or click the notification bell icon to view them")
print()
print("4. You can also test via the test endpoint:")
print("   http://localhost:5000/test/notifications")
print("   http://localhost:5000/test/notifications?type=compare")
print("   http://localhost:5000/test/notifications?type=form")
print("   http://localhost:5000/test/notifications?type=transaction")
print()
print("=" * 60)

