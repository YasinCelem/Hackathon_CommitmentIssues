from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from .data_storage.visit_tracker import get_top_visits, get_recent_visits, track_visit
from .nav import NAV
from .services import backend_client
from .auth import login_required, is_authenticated, get_current_user

bp = Blueprint("frontend", __name__)

def get_page_info(endpoint):
    for section in NAV:
        if section.get("endpoint") == endpoint:
            return section.get("label"), section.get("icon", "").replace("bi-", "")
        for child in section.get("children", []):
            if child.get("endpoint") == endpoint:
                parent_icon = section.get("icon", "").replace("bi-", "")
                return child.get("label"), parent_icon
    return None, None

def track_page_visit(endpoint):
    if endpoint and endpoint != "frontend.settings":
        title, icon = get_page_info(endpoint)
        if title and icon:
            track_visit(endpoint, title, icon)

def get_category_items(category_name, static_items):
    from datetime import datetime
    
    user_id = session.get("user_id")
    db_name = "Zane_Dima"
    
    backend_docs = backend_client.get_documents(category_name.lower(), user_id, db_name)
    
    static_map = {item["title"]: item for item in static_items}
    
    items = []
    doc_titles = set()
    
    for doc in backend_docs:
        doc_name = doc.get("name", "Document")
        doc_status = doc.get("status", "pending")
        
        deadlines = doc.get("deadlines", [])
        if deadlines and len(deadlines) > 0:
            try:
                deadline_date = deadlines[0][0] if len(deadlines[0]) > 0 else None
                if deadline_date:
                    deadline_obj = datetime.strptime(deadline_date[:10], "%Y-%m-%d")
                    today = datetime.now().date()
                    deadline_date_obj = deadline_obj.date()
                    
                    if deadline_date_obj < today:
                        doc_status = "need_attention"
                    elif deadline_date_obj == today:
                        doc_status = "need_attention"
                    elif (deadline_date_obj - today).days <= 7:
                        doc_status = "need_attention"
                    else:
                        doc_status = doc_status if doc_status in ["pending", "completed"] else "pending"
            except Exception:
                pass
        else:
            if doc_status not in ["pending", "completed", "need_attention"]:
                doc_status = "pending"
        
        static_item = None
        if doc_name in static_map:
            static_item = static_map[doc_name]
        else:
            for static_title, static_item_candidate in static_map.items():
                if static_title in doc_name or doc_name in static_title:
                    static_item = static_item_candidate
                    break
        
        if static_item:
            item = static_item.copy()
            item["status"] = doc_status
            item["doc_id"] = str(doc.get("_id"))
            item["title"] = static_item["title"]
        else:
            short_title = doc_name
            if " - " in doc_name:
                parts = doc_name.split(" - ")
                if len(parts) >= 4:
                    short_title = parts[-1]
                elif len(parts) >= 2:
                    short_title = parts[-1]
            
            item = {
                "title": short_title,
                "description": deadlines[0][1] if deadlines and len(deadlines[0]) > 1 else "Document",
                "endpoint": None,
                "info_url": None,
                "status": doc_status,
                "doc_id": str(doc.get("_id"))
            }
        
        items.append(item)
        doc_titles.add(item["title"])
    
    return items


@bp.route("/")
def index():
    if not is_authenticated():
        return redirect(url_for('frontend.login'))
    
    recent_visits = get_recent_visits(3)
    frequent = []
    
    seen_endpoints = set()
    for visit in recent_visits:
        endpoint = visit.get("endpoint")
        if endpoint and endpoint not in seen_endpoints:
            frequent.append({
                "title": visit.get("title"),
                "endpoint": endpoint,
                "icon": visit.get("icon")
            })
            seen_endpoints.add(endpoint)
    
    if len(frequent) < 3:
        default_sections = [
            {"title": "Taxes", "endpoint": "frontend.taxes", "icon": "receipt"},
            {"title": "KvK", "endpoint": "frontend.kvk", "icon": "building"},
            {"title": "Contracts", "endpoint": "frontend.contracts", "icon": "file-earmark-text"},
        ]
        for default in default_sections:
            if default["endpoint"] not in seen_endpoints:
                frequent.append(default)
                seen_endpoints.add(default["endpoint"])
                if len(frequent) >= 3:
                    break
    
    user_id = session.get("user_id")
    db_name = "Zane_Dima"
    
    backend_docs = backend_client.get_documents(user_id=user_id, db_name=db_name)
    
    approvals = []
    from datetime import datetime
    
    if backend_docs:
        for i, doc in enumerate(backend_docs, 1):
            deadlines = doc.get("deadlines", [])
            if deadlines:
                for deadline in deadlines:
                    if len(deadline) >= 2:
                        deadline_date = deadline[0]
                        deadline_desc = deadline[1] if len(deadline) > 1 else "Pending review"
                        
                        deadline_display = deadline_date
                        if deadline_date:
                            try:
                                if isinstance(deadline_date, str) and len(deadline_date) >= 10:
                                    date_obj = datetime.strptime(deadline_date[:10], "%Y-%m-%d")
                                    deadline_display = date_obj.strftime("%d-%m-%Y")
                            except Exception:
                                deadline_display = deadline_date
                        
                        approvals.append({
                            "id": doc.get("_id", i),
                            "doc_id": doc.get("_id"),
                            "title": doc.get("name", "Document"),
                            "description": deadline_desc,
                            "deadline_date": deadline_date,
                            "deadline_display": deadline_display,
                            "category": doc.get("category", "")
                        })
    
    if not approvals:
        from datetime import timedelta
        today = datetime.now()
        approvals = [
            {"id": 1, "title": "Q4 Tax Return Review", "description": "Pending review from finance team", "deadline_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"), "deadline_display": (today + timedelta(days=5)).strftime("%d-%m-%Y"), "doc_id": None},
            {"id": 2, "title": "Asset Purchase Approval", "description": "New equipment request", "deadline_date": (today + timedelta(days=12)).strftime("%Y-%m-%d"), "deadline_display": (today + timedelta(days=12)).strftime("%d-%m-%Y"), "doc_id": None},
            {"id": 3, "title": "Contract Renewal", "description": "Service agreement extension", "deadline_date": (today + timedelta(days=20)).strftime("%Y-%m-%d"), "deadline_display": (today + timedelta(days=20)).strftime("%d-%m-%Y"), "doc_id": None},
        ]
    
    approvals.sort(key=lambda x: x.get("deadline_date", "9999-12-31"))
    approvals = approvals[:5]
    
    return render_template("index.html", frequent=frequent, approvals=approvals)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if is_authenticated():
        return redirect(url_for('frontend.index'))
    
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form.to_dict()
        username_or_email = data.get("username_or_email")
        password = data.get("password")
        
        if not username_or_email or not password:
            if request.is_json:
                return jsonify({"error": "Username/email and password are required"}), 400
            return render_template("login.html", error="Username/email and password are required")
        
        result = backend_client.login_user(username_or_email, password)
        
        if not result:
            error_msg = "Unable to connect to backend. Please check if the backend is running."
            if request.is_json:
                return jsonify({"error": error_msg}), 503
            return render_template("login.html", error=error_msg)
        
        if result.get("user"):
            user = result["user"]
            session["user_id"] = user.get("id")
            session["username"] = user.get("username")
            session["database_name"] = "Zane_Dima"
            
            if request.is_json:
                next_url = request.args.get("next", url_for("frontend.index"))
                return jsonify({"message": "Login successful", "redirect": next_url}), 200
            else:
                next_url = request.args.get("next", url_for("frontend.index"))
                return redirect(next_url)
        else:
            error_msg = "Invalid username or password"
            if request.is_json:
                return jsonify({"error": error_msg}), 401
            return render_template("login.html", error=error_msg)
    
    return render_template("login.html")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if is_authenticated():
        return redirect(url_for('frontend.index'))
    
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form.to_dict()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        
        if not username or not email or not password:
            if request.is_json:
                return jsonify({"error": "Username, email, and password are required"}), 400
            return render_template("register.html", error="All fields are required")
        
        result = backend_client.register_user({
            "username": username,
            "email": email,
            "password": password
        })
        
        if result:
            if request.is_json:
                return jsonify({"message": "Registration successful"}), 201
            return render_template("register.html", success="Registration successful! Please login.")
        else:
            error_msg = "Registration failed. Username or email may already exist."
            if request.is_json:
                return jsonify({"error": error_msg}), 400
            return render_template("register.html", error=error_msg)
    
    return render_template("register.html")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('frontend.login'))

@bp.route("/api/login", methods=["POST"])
def api_login():
    return login()

@bp.route("/api/register", methods=["POST"])
def api_register():
    return register()

@bp.route("/taxes")
@login_required
def taxes():
    track_visit("frontend.taxes", "Taxes", "receipt")
    static_items = [
        {"title": "VAT Return & Payment", "description": "File and pay your VAT returns", "endpoint": "frontend.vat_return_payment", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/", "status": "pending"},
        {"title": "VAT ICP Report", "description": "Intra-Community transactions reporting", "endpoint": "frontend.vat_icp_report", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/", "status": "completed"},
        {"title": "VAT OSS (One-Stop Shop)", "description": "One-stop shop for EU VAT", "endpoint": "frontend.vat_oss", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/", "status": "need_attention"},
        {"title": "VAT KOR", "description": "Small businesses scheme", "endpoint": "frontend.vat_kor", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/", "status": "pending"},
        {"title": "VAT Article 23 (Import)", "description": "Import VAT reverse charge", "endpoint": "frontend.vat_article_23", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/", "status": "completed"},
        {"title": "VAT Rates & Exemptions", "description": "View VAT rates and exemptions", "endpoint": "frontend.vat_rates_exemptions", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/", "status": "pending"},
        {"title": "VAT / OB Numbers", "description": "Manage your VAT and OB numbers", "endpoint": "frontend.vat_ob_numbers", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/", "status": "completed"},
        {"title": "VAT Supplement", "description": "Submit VAT supplements", "endpoint": "frontend.vat_supplement", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/", "status": "need_attention"},
        {"title": "Payroll Tax", "description": "Payroll tax declarations", "endpoint": "frontend.payroll_tax", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/personeel-en-loon/content/loonaangifte-aangifte-loonheffingen/", "status": "pending"},
        {"title": "Income Tax (IB)", "description": "Income tax filing", "endpoint": "frontend.income_tax", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/inkomstenbelasting/", "status": "completed"},
        {"title": "Corporate Tax (VPB)", "description": "Corporate tax filing", "endpoint": "frontend.corporate_tax", "info_url": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/vennootschapsbelasting/", "status": "pending"},
    ]
    items = get_category_items("taxes", static_items)
    return render_template("section.html", title="Taxes", items=items)


@bp.route("/taxes/vat-return-payment")
@login_required
def vat_return_payment():
    track_page_visit("frontend.vat_return_payment")
    return render_template("pages/taxes/vat_return_payment.html")


@bp.route("/taxes/vat-icp-report")
def vat_icp_report():
    track_page_visit("frontend.vat_icp_report")
    return render_template("pages/taxes/vat_icp_report.html")


@bp.route("/taxes/vat-oss")
def vat_oss():
    track_page_visit("frontend.vat_oss")
    return render_template("pages/taxes/vat_oss.html")


@bp.route("/taxes/vat-kor")
def vat_kor():
    track_page_visit("frontend.vat_kor")
    return render_template("pages/taxes/vat_kor.html")


@bp.route("/taxes/vat-article-23")
def vat_article_23():
    track_page_visit("frontend.vat_article_23")
    return render_template("pages/taxes/vat_article_23.html")


@bp.route("/taxes/vat-rates-exemptions")
def vat_rates_exemptions():
    track_page_visit("frontend.vat_rates_exemptions")
    return render_template("pages/taxes/vat_rates_exemptions.html")


@bp.route("/taxes/vat-ob-numbers")
def vat_ob_numbers():
    track_page_visit("frontend.vat_ob_numbers")
    return render_template("pages/taxes/vat_ob_numbers.html")


@bp.route("/taxes/vat-supplement")
def vat_supplement():
    track_page_visit("frontend.vat_supplement")
    return render_template("pages/taxes/vat_supplement.html")


@bp.route("/taxes/payroll-tax")
def payroll_tax():
    track_page_visit("frontend.payroll_tax")
    return render_template("pages/taxes/payroll_tax.html")


@bp.route("/taxes/income-tax")
def income_tax():
    track_page_visit("frontend.income_tax")
    return render_template("pages/taxes/income_tax.html")


@bp.route("/taxes/corporate-tax")
def corporate_tax():
    track_page_visit("frontend.corporate_tax")
    return render_template("pages/taxes/corporate_tax.html")


@bp.route("/kvk")
@login_required
def kvk():
    track_visit("frontend.kvk", "KvK", "building")
    static_items = [
        {"title": "UBO Register", "description": "Ultimate beneficial owner registration", "endpoint": "frontend.ubo_register", "info_url": "https://www.kvk.nl/ubo/over-het-ubo-register/", "status": "pending"},
        {"title": "UBO Extract", "description": "View UBO extract information", "endpoint": "frontend.ubo_extract", "info_url": "https://www.kvk.nl/ubo/over-het-ubo-register/", "status": "completed"},
        {"title": "Annual Report Filing (SBR)", "description": "File annual reports via SBR", "endpoint": "frontend.annual_report_sbr", "info_url": "https://www.kvk.nl/deponeren/jaarrekening-deponeren/", "status": "need_attention"},
        {"title": "Self-File Annual Report", "description": "Self-file your annual report", "endpoint": "frontend.self_file_annual_report", "info_url": "https://www.kvk.nl/deponeren/jaarrekening-deponeren/", "status": "pending"},
    ]
    items = get_category_items("kvk", static_items)
    return render_template("section.html", title="KvK", items=items)


@bp.route("/kvk/ubo-register")
def ubo_register():
    track_page_visit("frontend.ubo_register")
    return render_template("pages/kvk/ubo_register.html")


@bp.route("/kvk/ubo-extract")
def ubo_extract():
    track_page_visit("frontend.ubo_extract")
    return render_template("pages/kvk/ubo_extract.html")


@bp.route("/kvk/annual-report-sbr")
def annual_report_sbr():
    track_page_visit("frontend.annual_report_sbr")
    return render_template("pages/kvk/annual_report_sbr.html")


@bp.route("/kvk/self-file-annual-report")
def self_file_annual_report():
    track_page_visit("frontend.self_file_annual_report")
    return render_template("pages/kvk/self_file_annual_report.html")


@bp.route("/contracts")
@login_required
def contracts():
    track_visit("frontend.contracts", "Contracts", "file-earmark-text")
    static_items = [
        {"title": "Repository", "description": "View all contracts", "endpoint": "frontend.contracts_repository", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "completed"},
        {"title": "Drafts", "description": "Manage contract drafts", "endpoint": "frontend.contracts_drafts", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "pending"},
        {"title": "Negotiations", "description": "Track contract negotiations", "endpoint": "frontend.contracts_negotiations", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "need_attention"},
        {"title": "Approvals", "description": "Pending contract approvals", "endpoint": "frontend.contracts_approvals", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "pending"},
        {"title": "Signatures", "description": "Manage contract signatures", "endpoint": "frontend.contracts_signatures", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "pending"},
        {"title": "Obligations & Renewals", "description": "Track contract obligations and renewals", "endpoint": "frontend.contracts_obligations_renewals", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "completed"},
    ]
    items = get_category_items("contracts", static_items)
    return render_template("section.html", title="Contracts", items=items)


@bp.route("/contracts/repository")
def contracts_repository():
    track_page_visit("frontend.contracts_repository")
    return render_template("pages/contracts/repository.html")


@bp.route("/contracts/drafts")
def contracts_drafts():
    track_page_visit("frontend.contracts_drafts")
    return render_template("pages/contracts/drafts.html")


@bp.route("/contracts/negotiations")
def contracts_negotiations():
    track_page_visit("frontend.contracts_negotiations")
    return render_template("pages/contracts/negotiations.html")


@bp.route("/contracts/approvals")
def contracts_approvals():
    track_page_visit("frontend.contracts_approvals")
    return render_template("pages/contracts/approvals.html")


@bp.route("/contracts/signatures")
def contracts_signatures():
    track_page_visit("frontend.contracts_signatures")
    return render_template("pages/contracts/signatures.html")


@bp.route("/contracts/obligations-renewals")
def contracts_obligations_renewals():
    track_page_visit("frontend.contracts_obligations_renewals")
    return render_template("pages/contracts/obligations_renewals.html")


@bp.route("/finances")
@login_required
def finances():
    track_visit("frontend.finances", "Finances", "cash-coin")
    static_items = [
        {"title": "Bank Connections", "description": "Manage bank account connections", "endpoint": "frontend.bank_connections", "info_url": "https://www.afm.nl/", "status": "completed"},
        {"title": "Transactions", "description": "View all financial transactions", "endpoint": "frontend.transactions", "info_url": "https://www.afm.nl/", "status": "pending"},
        {"title": "Sales (Invoices)", "description": "Manage sales and invoices", "endpoint": "frontend.sales", "info_url": "https://www.rijksoverheid.nl/onderwerpen/facturen", "status": "need_attention"},
        {"title": "Purchases (Bills)", "description": "Manage purchases and bills", "endpoint": "frontend.bills", "info_url": "https://www.rijksoverheid.nl/onderwerpen/facturen", "status": "pending"},
    ]
    items = get_category_items("finances", static_items)
    return render_template("section.html", title="Finances", items=items)


@bp.route("/finances/bank-connections")
def bank_connections():
    track_page_visit("frontend.bank_connections")
    return render_template("pages/finances/bank_connections.html")


@bp.route("/finances/transactions")
def transactions():
    track_page_visit("frontend.transactions")
    return render_template("pages/finances/transactions.html")


@bp.route("/finances/sales")
def sales():
    track_page_visit("frontend.sales")
    return render_template("pages/finances/sales.html")


@bp.route("/finances/bills")
def bills():
    track_page_visit("frontend.bills")
    return render_template("pages/finances/bills.html")


@bp.route("/documents")
@login_required
def documents():
    track_visit("frontend.documents", "Documents", "folder2")
    static_items = [
        {"title": "Uploads", "description": "Upload new documents", "endpoint": "frontend.documents_uploads", "info_url": "https://www.rijksoverheid.nl/onderwerpen/archief", "status": "completed"},
        {"title": "Recent", "description": "Recently accessed documents", "endpoint": "frontend.documents_recent", "info_url": "https://www.rijksoverheid.nl/onderwerpen/archief", "status": "pending"},
        {"title": "Versions", "description": "Document version history", "endpoint": "frontend.documents_versions", "info_url": "https://www.rijksoverheid.nl/onderwerpen/archief", "status": "completed"},
        {"title": "Templates", "description": "Document templates", "endpoint": "frontend.documents_templates", "info_url": "https://www.rijksoverheid.nl/onderwerpen/archief", "status": "pending"},
        {"title": "Search", "description": "Search documents", "endpoint": "frontend.documents_search", "info_url": "https://www.rijksoverheid.nl/onderwerpen/archief", "status": "completed"},
    ]
    user_id = session.get("user_id")
    db_name = session.get("database_name")
    backend_docs = backend_client.get_documents(user_id=user_id, db_name=db_name)
    items = get_category_items("documents", static_items)
    return render_template("section.html", title="Documents", items=items, documents=backend_docs)


@bp.route("/documents/uploads")
def documents_uploads():
    track_page_visit("frontend.documents_uploads")
    return render_template("pages/documents/uploads.html")


@bp.route("/documents/recent")
@login_required
def documents_recent():
    track_page_visit("frontend.documents_recent")
    doc_id = request.args.get("doc_id")
    user_id = session.get("user_id")
    db_name = session.get("database_name")
    backend_docs = backend_client.get_documents(user_id=user_id, db_name=db_name)
    selected_doc = None
    if doc_id:
        selected_doc = next((doc for doc in backend_docs if str(doc.get("_id")) == doc_id), None)
    return render_template("pages/documents/recent.html", documents=backend_docs, selected_doc=selected_doc, selected_doc_id=doc_id)


@bp.route("/documents/versions")
def documents_versions():
    track_page_visit("frontend.documents_versions")
    return render_template("pages/documents/versions.html")


@bp.route("/documents/templates")
def documents_templates():
    track_page_visit("frontend.documents_templates")
    return render_template("pages/documents/templates.html")


@bp.route("/documents/search")
def documents_search():
    track_page_visit("frontend.documents_search")
    return render_template("pages/documents/search.html")


@bp.route("/assistant")
@login_required
def assistant():
    track_visit("frontend.assistant", "Assistant", "robot")
    items = [
        {"title": "Chat", "description": "Chat with AI assistant", "endpoint": "frontend.assistant_chat", "info_url": "https://www.rijksoverheid.nl/"},
        {"title": "Recommendations", "description": "AI-powered recommendations", "endpoint": "frontend.assistant_recommendations", "info_url": "https://www.rijksoverheid.nl/"},
    ]
    return render_template("assistant.html", title="Assistant", items=items)


@bp.route("/assistant/chat")
def assistant_chat():
    track_page_visit("frontend.assistant_chat")
    return render_template("pages/assistant/chat.html")


@bp.route("/assistant/recommendations")
def assistant_recommendations():
    track_page_visit("frontend.assistant_recommendations")
    return render_template("pages/assistant/recommendations.html")


@bp.route("/settings")
@login_required
def settings():
    track_visit("frontend.settings", "Settings", "gear")
    return render_template("settings.html")



@bp.route("/api/documents")
@login_required
def api_documents():
    category = request.args.get("category")
    user_id = session.get("user_id")
    db_name = "Zane_Dima"
    docs = backend_client.get_documents(category, user_id, db_name)
    return jsonify(docs)

@bp.route("/api/documents", methods=["POST"])
@login_required
def api_create_document():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    user_id = session.get("user_id")
    db_name = "Zane_Dima"
    if user_id:
        data["user_id"] = user_id
    result = backend_client.create_document(data, db_name=db_name)
    if result:
        return jsonify(result), 201
    return jsonify({"error": "Failed to create document"}), 500

@bp.route("/api/documents/<doc_id>", methods=["PUT"])
@login_required
def api_update_document(doc_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    db_name = "Zane_Dima"
    result = backend_client.update_document(doc_id, data, db_name=db_name)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Failed to update document"}), 500

@bp.route("/api/documents/<doc_id>", methods=["DELETE"])
@login_required
def api_delete_document(doc_id):
    db_name = "Zane_Dima"
    result = backend_client.delete_document(doc_id, db_name=db_name)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Failed to delete document"}), 500

@bp.route("/api/data")
@login_required
def api_data():
    db_name = "Zane_Dima"
    data = backend_client.get_data(db_name=db_name)
    return jsonify(data)

@bp.route("/api/data", methods=["POST"])
@login_required
def api_create_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    db_name = "Zane_Dima"
    result = backend_client.create_data(data, db_name=db_name)
    if result:
        return jsonify(result), 201
    return jsonify({"error": "Failed to create data"}), 500
