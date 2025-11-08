NAV = [
    {
        "label": "Assistant", "icon": "bi-robot", "endpoint": "frontend.assistant", "children": [
            {"label": "Chat", "endpoint": "frontend.assistant_chat"},
            {"label": "Recommendations", "endpoint": "frontend.assistant_recommendations"},
        ]
    },
    {
        "label": "Taxes", "icon": "bi-receipt", "endpoint": "frontend.taxes", "children": [
            {"label": "Overview", "endpoint": "frontend.taxes"},
            {"label": "VAT Return & Payment", "endpoint": "frontend.vat_return_payment"},
            {"label": "VAT ICP Report", "endpoint": "frontend.vat_icp_report"},
            {"label": "VAT OSS (One-Stop Shop)", "endpoint": "frontend.vat_oss"},
            {"label": "VAT KOR", "endpoint": "frontend.vat_kor"},
            {"label": "VAT Article 23 (Import)", "endpoint": "frontend.vat_article_23"},
            {"label": "VAT Rates & Exemptions", "endpoint": "frontend.vat_rates_exemptions"},
            {"label": "VAT / OB Numbers", "endpoint": "frontend.vat_ob_numbers"},
            {"label": "VAT Supplement", "endpoint": "frontend.vat_supplement"},
            {"label": "Payroll Tax", "endpoint": "frontend.payroll_tax"},
            {"label": "Income Tax (IB)", "endpoint": "frontend.income_tax"},
            {"label": "Corporate Tax (VPB)", "endpoint": "frontend.corporate_tax"},
        ]
    },
    {
        "label": "KvK", "icon": "bi-building", "endpoint": "frontend.kvk", "children": [
            {"label": "Overview", "endpoint": "frontend.kvk"},
            {"label": "UBO Register", "endpoint": "frontend.ubo_register"},
            {"label": "UBO Extract", "endpoint": "frontend.ubo_extract"},
            {"label": "Annual Report Filing (SBR)", "endpoint": "frontend.annual_report_sbr"},
            {"label": "Self-File Annual Report", "endpoint": "frontend.self_file_annual_report"},
        ]
    },
    {
        "label": "Contracts", "icon": "bi-file-earmark-text", "endpoint": "frontend.contracts", "children": [
            {"label": "Overview", "endpoint": "frontend.contracts"},
            {"label": "Repository", "endpoint": "frontend.contracts_repository"},
            {"label": "Drafts", "endpoint": "frontend.contracts_drafts"},
            {"label": "Negotiations", "endpoint": "frontend.contracts_negotiations"},
            {"label": "Approvals", "endpoint": "frontend.contracts_approvals"},
            {"label": "Signatures", "endpoint": "frontend.contracts_signatures"},
            {"label": "Obligations & Renewals", "endpoint": "frontend.contracts_obligations_renewals"},
        ]
    },
    {
        "label": "Finances", "icon": "bi-cash-coin", "endpoint": "frontend.finances", "children": [
            {"label": "Overview", "endpoint": "frontend.finances"},
            {"label": "Bank Connections", "endpoint": "frontend.bank_connections"},
            {"label": "Transactions", "endpoint": "frontend.transactions"},
            {"label": "Sales (Invoices)", "endpoint": "frontend.sales"},
            {"label": "Purchases (Bills)", "endpoint": "frontend.bills"},
        ]
    },
    {
        "label": "Documents", "icon": "bi-folder2", "endpoint": "frontend.documents", "children": [
            {"label": "Overview", "endpoint": "frontend.documents"},
            {"label": "Uploads", "endpoint": "frontend.documents_uploads"},
            {"label": "Recent", "endpoint": "frontend.documents_recent"},
            {"label": "Versions", "endpoint": "frontend.documents_versions"},
            {"label": "Templates", "endpoint": "frontend.documents_templates"},
            {"label": "Search", "endpoint": "frontend.documents_search"},
        ]
    },
    {
        "label": "Settings", "icon": "bi-gear", "endpoint": "frontend.settings", "children": []
    },
]
