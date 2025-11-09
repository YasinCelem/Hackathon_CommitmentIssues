from src.FrontEnd.routes import notification_queue


def create_compare_notification(doc_id, title="Document Comparison"):
    """Creates a compare notification"""
    notification = {
        'type': 'compare',
        'title': title,
        'message': 'Document differences have been detected.',
        'data': {'docId': doc_id}
    }
    notification_queue.put(notification)
    return notification


def create_form_notification(form_id, title="Form Ready"):
    """Creates a form notification"""
    notification = {
        'type': 'form',
        'title': title,
        'message': 'A form has been filled and is ready for review.',
        'data': {'formId': form_id}
    }
    notification_queue.put(notification)
    return notification


def create_transaction_notification(transaction_id, title="Transaction Pending"):
    """Creates a transaction notification"""
    notification = {
        'type': 'transaction',
        'title': title,
        'message': 'A transaction requires your confirmation.',
        'data': {'transactionId': transaction_id}
    }
    notification_queue.put(notification)
    return notification
