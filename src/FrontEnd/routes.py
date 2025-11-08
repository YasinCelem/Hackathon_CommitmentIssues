from flask import Blueprint, render_template
from .data_storage.visit_tracker import get_top_visits, get_recent_visits, track_visit
from .nav import NAV

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


@bp.route("/")
def index():
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
    
    approvals = [
        {"id": 1, "title": "Q4 Tax Return Review", "description": "Pending review from finance team"},
        {"id": 2, "title": "Asset Purchase Approval", "description": "New equipment request"},
        {"id": 3, "title": "Contract Renewal", "description": "Service agreement extension"},
    ]
    
    return render_template("index.html", frequent=frequent, approvals=approvals)


@bp.route("/taxes")
def taxes():
    track_visit("frontend.taxes", "Taxes", "receipt")
    items = [
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
    return render_template("section.html", title="Taxes", items=items)


@bp.route("/taxes/vat-return-payment")
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
def kvk():
    track_visit("frontend.kvk", "KvK", "building")
    items = [
        {"title": "UBO Register", "description": "Ultimate beneficial owner registration", "endpoint": "frontend.ubo_register", "info_url": "https://www.kvk.nl/ubo/over-het-ubo-register/", "status": "pending"},
        {"title": "UBO Extract", "description": "View UBO extract information", "endpoint": "frontend.ubo_extract", "info_url": "https://www.kvk.nl/ubo/over-het-ubo-register/", "status": "completed"},
        {"title": "Annual Report Filing (SBR)", "description": "File annual reports via SBR", "endpoint": "frontend.annual_report_sbr", "info_url": "https://www.kvk.nl/deponeren/jaarrekening-deponeren/", "status": "need_attention"},
        {"title": "Self-File Annual Report", "description": "Self-file your annual report", "endpoint": "frontend.self_file_annual_report", "info_url": "https://www.kvk.nl/deponeren/jaarrekening-deponeren/", "status": "pending"},
    ]
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
def contracts():
    track_visit("frontend.contracts", "Contracts", "file-earmark-text")
    items = [
        {"title": "Repository", "description": "View all contracts", "endpoint": "frontend.contracts_repository", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "completed"},
        {"title": "Drafts", "description": "Manage contract drafts", "endpoint": "frontend.contracts_drafts", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "pending"},
        {"title": "Negotiations", "description": "Track contract negotiations", "endpoint": "frontend.contracts_negotiations", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "need_attention"},
        {"title": "Approvals", "description": "Pending contract approvals", "endpoint": "frontend.contracts_approvals", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "pending"},
        {"title": "Signatures", "description": "Manage contract signatures", "endpoint": "frontend.contracts_signatures", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "pending"},
        {"title": "Obligations & Renewals", "description": "Track contract obligations and renewals", "endpoint": "frontend.contracts_obligations_renewals", "info_url": "https://www.rijksoverheid.nl/onderwerpen/contractenrecht", "status": "completed"},
    ]
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
def finances():
    track_visit("frontend.finances", "Finances", "cash-coin")
    items = [
        {"title": "Bank Connections", "description": "Manage bank account connections", "endpoint": "frontend.bank_connections", "info_url": "https://www.afm.nl/", "status": "completed"},
        {"title": "Transactions", "description": "View all financial transactions", "endpoint": "frontend.transactions", "info_url": "https://www.afm.nl/", "status": "pending"},
        {"title": "Sales (Invoices)", "description": "Manage sales and invoices", "endpoint": "frontend.sales", "info_url": "https://www.rijksoverheid.nl/onderwerpen/facturen", "status": "need_attention"},
        {"title": "Purchases (Bills)", "description": "Manage purchases and bills", "endpoint": "frontend.bills", "info_url": "https://www.rijksoverheid.nl/onderwerpen/facturen", "status": "pending"},
    ]
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
def documents():
    track_visit("frontend.documents", "Documents", "folder2")
    items = [
        {"title": "Uploads", "description": "Upload new documents", "endpoint": "frontend.documents_uploads", "info_url": "https://www.rijksoverheid.nl/onderwerpen/archief", "status": "completed"},
        {"title": "Recent", "description": "Recently accessed documents", "endpoint": "frontend.documents_recent", "info_url": "https://www.rijksoverheid.nl/onderwerpen/archief", "status": "pending"},
        {"title": "Versions", "description": "Document version history", "endpoint": "frontend.documents_versions", "info_url": "https://www.rijksoverheid.nl/onderwerpen/archief", "status": "completed"},
        {"title": "Templates", "description": "Document templates", "endpoint": "frontend.documents_templates", "info_url": "https://www.rijksoverheid.nl/onderwerpen/archief", "status": "pending"},
        {"title": "Search", "description": "Search documents", "endpoint": "frontend.documents_search", "info_url": "https://www.rijksoverheid.nl/onderwerpen/archief", "status": "completed"},
    ]
    return render_template("section.html", title="Documents", items=items)


@bp.route("/documents/uploads")
def documents_uploads():
    track_page_visit("frontend.documents_uploads")
    return render_template("pages/documents/uploads.html")


@bp.route("/documents/recent")
def documents_recent():
    track_page_visit("frontend.documents_recent")
    return render_template("pages/documents/recent.html")


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
def settings():
    track_visit("frontend.settings", "Settings", "gear")
    return render_template("settings.html")


@bp.route("/login")
def login():
    return render_template("page.html", title="Login", content="Login functionality.")
