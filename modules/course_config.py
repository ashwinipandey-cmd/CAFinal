"""
course_config.py — StudyTracker
All course definitions: levels, subjects, default topics.
Users can fully customise subjects & topics; these are only defaults/presets.
"""

from __future__ import annotations

# ══════════════════════════════════════════════════════════════════════════════
# COURSE REGISTRY
# Each course has:
#   label       : display name
#   short       : abbreviation
#   icon        : emoji
#   levels      : ordered list of level dicts
#   category    : grouping for UI
#
# Each level has:
#   key         : unique string  e.g. "ca_foundation"
#   label       : display name
#   short       : short label
#   subjects    : list of subject dicts (defaults — user can modify)
#
# Each subject has:
#   key         : short code e.g. "FR"
#   label       : full name
#   target_hrs  : default target hours
#   color       : hex color for charts
#   topics      : list of topic strings (defaults)
# ══════════════════════════════════════════════════════════════════════════════

COURSES: dict[str, dict] = {

    # ── CA ────────────────────────────────────────────────────────────────────
    "ca": {
        "label": "Chartered Accountancy (CA)",
        "short": "CA",
        "icon": "📊",
        "category": "Professional",
        "levels": [
            {
                "key": "ca_foundation",
                "label": "CA Foundation",
                "short": "Foundation",
                "clear_condition": "both_groups",  # N/A for foundation (single exam)
                "subjects": [
                    {"key": "ACCOUNTS", "label": "Principles & Practice of Accounting",
                     "target_hrs": 120, "color": "#7DD3FC",
                     "topics": [
                         "Accounting Fundamentals & Principles",
                         "Journal Ledger & Trial Balance",
                         "Bank Reconciliation Statement",
                         "Depreciation Provisions & Reserves",
                         "Bills of Exchange & Consignment",
                         "Partnership Accounts",
                         "Company Accounts – Introduction",
                         "Financial Statements – Sole Trader",
                     ]},
                    {"key": "MATHS", "label": "Business Mathematics & LR & Statistics",
                     "target_hrs": 100, "color": "#34D399",
                     "topics": [
                         "Ratio Proportion & Indices",
                         "Equations – Linear & Quadratic",
                         "Logarithms",
                         "Mathematics of Finance",
                         "Permutations & Combinations",
                         "Sets Functions & Relations",
                         "Basic Statistics – Measures of Central Tendency",
                         "Dispersion & Skewness",
                         "Probability",
                         "Theoretical Distributions",
                         "Correlation & Regression",
                         "Index Numbers & Time Series",
                     ]},
                    {"key": "MECON", "label": "Business Economics & Business & Commercial Knowledge",
                     "target_hrs": 90, "color": "#FBBF24",
                     "topics": [
                         "Nature & Scope of Business Economics",
                         "Theory of Demand & Supply",
                         "Theory of Production & Cost",
                         "Price Determination – Market Forms",
                         "Business Cycles",
                         "Money & Banking",
                         "Introduction to Business",
                         "Forms of Business Organisation",
                         "Government Policies for Business Growth",
                         "Business Organisations in India",
                     ]},
                    {"key": "BLAW", "label": "Business Laws & Business Correspondence",
                     "target_hrs": 90, "color": "#F87171",
                     "topics": [
                         "Indian Contract Act 1872 – Essentials",
                         "Contract – Offer Acceptance & Consideration",
                         "Void Agreements & Quasi Contracts",
                         "Sale of Goods Act 1930",
                         "Indian Partnership Act 1932",
                         "LLP Act 2008",
                         "Companies Act 2013 – Introduction",
                         "Business Correspondence & Communication",
                     ]},
                ],
            },
            {
                "key": "ca_inter",
                "label": "CA Intermediate",
                "short": "Inter",
                "clear_condition": "both_groups",
                "subjects": [
                    # Group 1
                    {"key": "ADVACCOUNTS", "label": "Advanced Accounting",
                     "target_hrs": 150, "color": "#7DD3FC",
                     "topics": [
                         "Framework for Preparation of FS",
                         "Accounting Standards – Overview",
                         "Company Accounts",
                         "Reorganisation & Liquidation",
                         "Partnership – Advanced",
                         "Branch Accounts",
                         "Hire Purchase & Installment",
                         "Investment Accounts",
                         "Insurance Claims",
                         "Accounting for Employee Stock Options",
                     ]},
                    {"key": "CORPLAW", "label": "Corporate & Other Laws",
                     "target_hrs": 120, "color": "#34D399",
                     "topics": [
                         "Companies Act – Incorporation",
                         "Companies Act – Share Capital",
                         "Companies Act – Meetings & Resolutions",
                         "Companies Act – Directors",
                         "Companies Act – Audit & Accounts",
                         "LLP Act",
                         "Negotiable Instruments Act",
                         "General Clauses Act",
                     ]},
                    {"key": "COSTING", "label": "Cost & Management Accounting",
                     "target_hrs": 130, "color": "#FBBF24",
                     "topics": [
                         "Introduction to Cost Accounting",
                         "Material Cost",
                         "Labour Cost",
                         "Overheads",
                         "Cost Sheet",
                         "Activity Based Costing",
                         "Job & Batch Costing",
                         "Process Costing",
                         "Joint & By Products",
                         "Standard Costing",
                         "Marginal Costing",
                         "Budgets & Budgetary Control",
                     ]},
                    {"key": "TAXATION_I", "label": "Taxation – Direct Tax",
                     "target_hrs": 130, "color": "#F87171",
                     "topics": [
                         "Basic Concepts",
                         "Residential Status",
                         "Income from Salaries",
                         "Income from House Property",
                         "PGBP",
                         "Capital Gains",
                         "Income from Other Sources",
                         "Clubbing & Set-off",
                         "Deductions Chapter VI-A",
                         "Assessment of Individuals",
                         "TDS & Advance Tax",
                     ]},
                    # Group 2
                    {"key": "AUDIT_I", "label": "Auditing & Assurance",
                     "target_hrs": 110, "color": "#60A5FA",
                     "topics": [
                         "Nature & Objectives of Audit",
                         "Audit Strategy Planning & Programming",
                         "Risk Assessment",
                         "Audit Evidence",
                         "Internal Control",
                         "Company Audit",
                         "Audit Report",
                         "Special Audits",
                     ]},
                    {"key": "FM_ECO", "label": "Financial Management & Economics for Finance",
                     "target_hrs": 130, "color": "#A78BFA",
                     "topics": [
                         "Financial Management Overview",
                         "Capital Budgeting",
                         "Cost of Capital",
                         "Leverages",
                         "Capital Structure",
                         "Dividend Policy",
                         "Working Capital",
                         "Indian Financial System",
                         "Determination of National Income",
                         "Money Market",
                         "International Trade",
                     ]},
                    {"key": "EIS_SM", "label": "Enterprise Information Systems & Strategic Management",
                     "target_hrs": 100, "color": "#FB923C",
                     "topics": [
                         "Introduction to EIS",
                         "IT Infrastructure",
                         "Information Systems & Controls",
                         "E-Commerce",
                         "Introduction to Strategic Management",
                         "Strategic Analysis",
                         "Strategy Formulation",
                         "Strategy Implementation",
                     ]},
                    {"key": "TAXATION_II", "label": "Taxation – Indirect Tax (GST)",
                     "target_hrs": 120, "color": "#34D399",
                     "topics": [
                         "GST – Constitutional Background",
                         "GST – Levy & Exemptions",
                         "Time, Place & Value of Supply",
                         "Input Tax Credit",
                         "Registration",
                         "Tax Invoice & Returns",
                         "Payment & Refund",
                         "Assessment & Audit",
                         "Customs – Basics",
                     ]},
                ],
            },
            {
                "key": "ca_final",
                "label": "CA Final",
                "short": "Final",
                "clear_condition": "both_groups",
                "subjects": [
                    {"key": "FR",  "label": "Financial Reporting",      "target_hrs": 200, "color": "#7DD3FC",
                     "topics": [
                         "Ind AS 1 – Presentation of FS","Ind AS 2 – Inventories",
                         "Ind AS 7 – Cash Flow Statements","Ind AS 8 – Accounting Policies",
                         "Ind AS 10 – Events after Reporting Period","Ind AS 12 – Deferred Tax",
                         "Ind AS 16 – Property Plant & Equipment","Ind AS 19 – Employee Benefits",
                         "Ind AS 20 – Government Grants","Ind AS 21 – Foreign Currency",
                         "Ind AS 23 – Borrowing Costs","Ind AS 24 – Related Party Disclosures",
                         "Ind AS 32 – Financial Instruments: Presentation",
                         "Ind AS 33 – Earnings per Share","Ind AS 36 – Impairment of Assets",
                         "Ind AS 37 – Provisions & Contingencies","Ind AS 38 – Intangible Assets",
                         "Ind AS 40 – Investment Property","Ind AS 101 – First-time Adoption",
                         "Ind AS 103 – Business Combinations","Ind AS 109 – Financial Instruments",
                         "Ind AS 110 – Consolidated FS","Ind AS 115 – Revenue from Contracts",
                         "Ind AS 116 – Leases","Analysis & Interpretation of FS",
                     ]},
                    {"key": "AFM", "label": "Adv. FM & Economics",       "target_hrs": 160, "color": "#34D399",
                     "topics": [
                         "Financial Policy & Corporate Strategy","Risk Management – Overview",
                         "Capital Budgeting under Risk","Dividend Policy",
                         "Indian Capital Market & SEBI","Security Analysis",
                         "Portfolio Management & CAPM","Mutual Funds",
                         "Derivatives – Futures & Forwards","Derivatives – Options",
                         "Derivatives – Swaps","Foreign Exchange Risk Management",
                         "International Financial Management","Mergers & Acquisitions",
                         "Startup Finance & Venture Capital","Bond Valuation",
                     ]},
                    {"key": "AA",  "label": "Advanced Auditing",         "target_hrs": 150, "color": "#FBBF24",
                     "topics": [
                         "Ethics & Independence (SA 200-299)","Audit Planning & Risk",
                         "Internal Control & Internal Audit","Audit Evidence – SA 500 series",
                         "Sampling & CAAT","Company Audit – Specific Areas",
                         "Audit Report & Modified Opinions","Special Audits – Banks Insurance NBFCs",
                         "Cost Audit","Forensic Accounting & Fraud Investigation",
                         "Peer Review & Quality Control","Audit under IT Environment",
                     ]},
                    {"key": "DT",  "label": "Direct Tax & Int'l Tax",    "target_hrs": 200, "color": "#F87171",
                     "topics": [
                         "Basic Concepts & Residential Status","Incomes Exempt from Tax",
                         "Income from Salaries","Income from House Property",
                         "PGBP","Capital Gains","Income from Other Sources",
                         "Clubbing Set-off & Carry Forward","Deductions under Chapter VIA",
                         "Assessment – Individuals HUF Firms","Assessment – Companies",
                         "MAT & AMT","TDS & TCS Provisions","Advance Tax & Interest",
                         "Return Filing & Assessment Procedure","Appeals & Revision",
                         "International Taxation – Transfer Pricing","DTAA & OECD/UN Model",
                         "GAAR POEM & BEPS",
                     ]},
                    {"key": "IDT", "label": "Indirect Tax",              "target_hrs": 180, "color": "#60A5FA",
                     "topics": [
                         "GST – Constitutional Background","GST – Levy & Exemptions",
                         "GST – Time Place & Value of Supply","GST – Input Tax Credit",
                         "GST – Registration","GST – Tax Invoice Credit & Debit Notes",
                         "GST – Returns","GST – Payment & Refund",
                         "GST – Import & Export (Zero-rated)","GST – Assessment & Audit",
                         "GST – Appeals & Revision","GST – Offences & Penalties",
                         "Customs – Levy & Exemptions","Customs – Import/Export Procedure",
                         "Customs – Valuation & Baggage Rules","FTP – Overview",
                     ]},
                ],
            },
        ],
    },

    # ── JEE ───────────────────────────────────────────────────────────────────
    "jee": {
        "label": "Joint Entrance Examination (JEE)",
        "short": "JEE",
        "icon": "⚙️",
        "category": "Engineering",
        "levels": [
            {
                "key": "jee_main",
                "label": "JEE Main",
                "short": "Main",
                "clear_condition": "qualify_cutoff",
                "subjects": [
                    {"key": "JEE_PHY", "label": "Physics", "target_hrs": 200, "color": "#7DD3FC",
                     "topics": [
                         "Units & Measurements","Kinematics","Laws of Motion",
                         "Work Energy & Power","Rotational Motion","Gravitation",
                         "Properties of Matter","Thermodynamics","Kinetic Theory",
                         "Oscillations","Waves","Electrostatics","Current Electricity",
                         "Magnetic Effects of Current","EMI & AC","Optics – Ray",
                         "Optics – Wave","Dual Nature of Matter","Atoms & Nuclei",
                         "Electronic Devices",
                     ]},
                    {"key": "JEE_CHEM", "label": "Chemistry", "target_hrs": 200, "color": "#34D399",
                     "topics": [
                         "Basic Concepts of Chemistry","Structure of Atom",
                         "Classification of Elements","Chemical Bonding",
                         "States of Matter","Thermodynamics (Chem)",
                         "Equilibrium","Redox Reactions","Hydrogen",
                         "s-Block Elements","p-Block Elements",
                         "d & f Block Elements","Coordination Compounds",
                         "Organic Chemistry – Basic Principles","Hydrocarbons",
                         "Haloalkanes & Haloarenes","Alcohols Phenols Ethers",
                         "Aldehydes Ketones & Carboxylic Acids","Amines",
                         "Biomolecules","Polymers","Chemistry in Everyday Life",
                         "Electrochemistry","Chemical Kinetics","Surface Chemistry",
                         "Solid State","Solutions",
                     ]},
                    {"key": "JEE_MATH", "label": "Mathematics", "target_hrs": 200, "color": "#FBBF24",
                     "topics": [
                         "Sets Relations & Functions","Complex Numbers",
                         "Matrices & Determinants","Permutations & Combinations",
                         "Mathematical Induction","Binomial Theorem",
                         "Sequences & Series","Limits Continuity & Differentiability",
                         "Integral Calculus","Differential Equations",
                         "Coordinate Geometry – Straight Lines","Circles",
                         "Conic Sections","3D Geometry","Vector Algebra",
                         "Statistics & Probability","Trigonometry",
                         "Mathematical Reasoning",
                     ]},
                ],
            },
            {
                "key": "jee_advanced",
                "label": "JEE Advanced",
                "short": "Advanced",
                "clear_condition": "qualify_cutoff",
                "subjects": [
                    {"key": "ADV_PHY", "label": "Physics (Advanced)", "target_hrs": 220, "color": "#7DD3FC",
                     "topics": [
                         "Mechanics – Rigid Body Dynamics","Mechanics – Fluid Dynamics",
                         "Waves & Sound – Advanced","Optics – Advanced",
                         "Electrostatics – Advanced","Magnetism – Advanced",
                         "Modern Physics – Photoelectric & X-rays",
                         "Nuclear Physics & Radioactivity",
                         "Semiconductors – Advanced","Experimental Physics",
                     ]},
                    {"key": "ADV_CHEM", "label": "Chemistry (Advanced)", "target_hrs": 220, "color": "#34D399",
                     "topics": [
                         "Physical Chemistry – Deep Dive",
                         "Inorganic Chemistry – Advanced",
                         "Organic Chemistry – Mechanisms",
                         "Named Reactions","Stereochemistry",
                         "Spectroscopy Basics","Electrochemistry – Advanced",
                         "Thermodynamics & Equilibrium – Advanced",
                     ]},
                    {"key": "ADV_MATH", "label": "Mathematics (Advanced)", "target_hrs": 220, "color": "#FBBF24",
                     "topics": [
                         "Algebra – Advanced","Complex Numbers – Advanced",
                         "Calculus – Advanced Techniques","Differential Equations – Advanced",
                         "Coordinate Geometry – Advanced","3D & Vectors – Advanced",
                         "Probability – Advanced","Number Theory",
                         "Functional Equations",
                     ]},
                ],
            },
        ],
    },

    # ── NEET ─────────────────────────────────────────────────────────────────
    "neet": {
        "label": "National Eligibility cum Entrance Test (NEET)",
        "short": "NEET",
        "icon": "🏥",
        "category": "Medical",
        "levels": [
            {
                "key": "neet_ug",
                "label": "NEET UG",
                "short": "UG",
                "clear_condition": "qualify_cutoff",
                "subjects": [
                    {"key": "NEET_PHY", "label": "Physics", "target_hrs": 180, "color": "#7DD3FC",
                     "topics": [
                         "Physical World & Measurement","Kinematics",
                         "Laws of Motion","Work Energy & Power",
                         "Motion of System of Particles","Gravitation",
                         "Properties of Bulk Matter","Thermodynamics",
                         "Behaviour of Perfect Gas & KTG",
                         "Oscillations & Waves","Electrostatics",
                         "Current Electricity","Magnetic Effects & Magnetism",
                         "EMI & AC Currents","Electromagnetic Waves",
                         "Optics","Dual Nature of Matter",
                         "Atoms & Nuclei","Electronic Devices",
                     ]},
                    {"key": "NEET_CHEM", "label": "Chemistry", "target_hrs": 180, "color": "#34D399",
                     "topics": [
                         "Some Basic Concepts","Structure of Atom",
                         "Classification of Elements","Chemical Bonding & Molecular Structure",
                         "States of Matter","Thermodynamics",
                         "Equilibrium","Redox Reactions",
                         "Hydrogen & s-Block","p-Block Elements",
                         "Organic Chemistry – Basics","Hydrocarbons",
                         "Environmental Chemistry","Solid State","Solutions",
                         "Electrochemistry","Chemical Kinetics",
                         "Surface Chemistry","d & f Block","Coordination Compounds",
                         "Haloalkanes & Haloarenes","Alcohols Phenols Ethers",
                         "Aldehydes Ketones Carboxylic Acids","Amines",
                         "Biomolecules & Polymers","Chemistry in Everyday Life",
                     ]},
                    {"key": "NEET_BIO", "label": "Biology", "target_hrs": 220, "color": "#F87171",
                     "topics": [
                         "Diversity in Living World","Structural Organisation",
                         "Cell Structure & Function","Plant Physiology",
                         "Human Physiology","Reproduction",
                         "Genetics & Evolution","Biology & Human Welfare",
                         "Biotechnology","Ecology & Environment",
                     ]},
                ],
            },
            {
                "key": "neet_pg",
                "label": "NEET PG",
                "short": "PG",
                "clear_condition": "qualify_cutoff",
                "subjects": [
                    {"key": "PRECLINICAL", "label": "Pre-Clinical Subjects", "target_hrs": 200, "color": "#7DD3FC",
                     "topics": [
                         "Anatomy","Physiology","Biochemistry",
                     ]},
                    {"key": "PARACLINICAL", "label": "Para-Clinical Subjects", "target_hrs": 200, "color": "#34D399",
                     "topics": [
                         "Pathology","Microbiology","Pharmacology",
                         "Forensic Medicine","Community Medicine",
                     ]},
                    {"key": "CLINICAL", "label": "Clinical Subjects", "target_hrs": 250, "color": "#FBBF24",
                     "topics": [
                         "General Medicine","Surgery","Obstetrics & Gynaecology",
                         "Paediatrics","Psychiatry","Dermatology",
                         "Ophthalmology","ENT","Radiology","Anaesthesia",
                         "Orthopaedics",
                     ]},
                ],
            },
        ],
    },

    # ── CS ────────────────────────────────────────────────────────────────────
    "cs": {
        "label": "Company Secretary (CS)",
        "short": "CS",
        "icon": "⚖️",
        "category": "Professional",
        "levels": [
            {
                "key": "cs_foundation",
                "label": "CS Foundation",
                "short": "Foundation",
                "clear_condition": "single_exam",
                "subjects": [
                    {"key": "BLAW_CS", "label": "Business Environment & Law", "target_hrs": 100, "color": "#7DD3FC", "topics": [
                        "Business Environment","Forms of Business Organisation",
                        "Indian Contract Act","Sale of Goods Act","Negotiable Instruments Act",
                        "Companies Act – Introduction",
                    ]},
                    {"key": "MGMT_CS", "label": "Business Management Ethics & Entrepreneurship", "target_hrs": 90, "color": "#34D399", "topics": [
                        "Principles of Management","Business Ethics",
                        "Entrepreneurship","Corporate Governance Basics",
                    ]},
                    {"key": "ECON_CS", "label": "Business Economics", "target_hrs": 90, "color": "#FBBF24", "topics": [
                        "Basic Concepts","Demand & Supply","Market Forms","National Income",
                        "Money & Banking","Indian Economy",
                    ]},
                    {"key": "ACC_CS", "label": "Fundamentals of Accounting & Auditing", "target_hrs": 100, "color": "#F87171", "topics": [
                        "Basics of Accounting","Journal & Ledger","Financial Statements",
                        "Auditing Basics",
                    ]},
                ],
            },
            {
                "key": "cs_executive",
                "label": "CS Executive",
                "short": "Executive",
                "clear_condition": "both_modules",
                "subjects": [
                    {"key": "JGLS", "label": "Jurisprudence Interpretation & General Laws", "target_hrs": 110, "color": "#7DD3FC", "topics": ["Jurisprudence","Interpretation of Statutes","General Laws","Administrative Law"]},
                    {"key": "CORPLAW_CS", "label": "Company Law", "target_hrs": 130, "color": "#34D399", "topics": ["Incorporation","Share Capital","Meetings","Directors","Accounts & Audit","Winding Up"]},
                    {"key": "SET_CS", "label": "Setting Up of Business Entities & Closure", "target_hrs": 100, "color": "#FBBF24", "topics": ["Types of Entities","Registration & Licences","Closure Procedures"]},
                    {"key": "TAX_CS", "label": "Tax Laws", "target_hrs": 120, "color": "#F87171", "topics": ["Income Tax Basics","GST Basics","Customs Basics"]},
                    {"key": "ECL", "label": "Economic Business & Commercial Laws", "target_hrs": 110, "color": "#60A5FA", "topics": ["Competition Law","Consumer Protection","FEMA","IP Laws"]},
                    {"key": "SCM_CS", "label": "Securities Laws & Capital Markets", "target_hrs": 100, "color": "#A78BFA", "topics": ["SEBI Regulations","Stock Exchanges","Issue of Securities","Takeover Code"]},
                    {"key": "FM_CS", "label": "Financial & Strategic Management", "target_hrs": 120, "color": "#FB923C", "topics": ["Financial Management","Strategic Management","Investment Decisions"]},
                ],
            },
            {
                "key": "cs_professional",
                "label": "CS Professional",
                "short": "Professional",
                "clear_condition": "all_modules",
                "subjects": [
                    {"key": "GCC", "label": "Governance Risk & Compliance", "target_hrs": 130, "color": "#7DD3FC", "topics": ["Corporate Governance","Risk Management","Compliance","Ethics"]},
                    {"key": "ADV_TAX_CS", "label": "Advanced Tax Laws", "target_hrs": 150, "color": "#34D399", "topics": ["Direct Tax – Advanced","GST – Advanced","International Taxation"]},
                    {"key": "DIFC", "label": "Drafting Appearances & Pleadings", "target_hrs": 120, "color": "#FBBF24", "topics": ["Drafting Skills","Court Appearances","NCLT/NCLAT Procedures"]},
                    {"key": "SCL", "label": "Secretarial Audit Compliance Management", "target_hrs": 110, "color": "#F87171", "topics": ["Secretarial Audit","Compliance Management","Due Diligence"]},
                    {"key": "CGL_CS", "label": "Corporate Restructuring Insolvency & Liquidation", "target_hrs": 120, "color": "#60A5FA", "topics": ["Mergers & Acquisitions","IBC – Insolvency","Liquidation"]},
                    {"key": "RESO", "label": "Resolution of Corporate Disputes", "target_hrs": 100, "color": "#A78BFA", "topics": ["Dispute Resolution Mechanisms","NCLT Proceedings","Mediation & Arbitration"]},
                ],
            },
        ],
    },

    # ── CMA ───────────────────────────────────────────────────────────────────
    "cma": {
        "label": "Cost & Management Accountant (CMA)",
        "short": "CMA",
        "icon": "💹",
        "category": "Professional",
        "levels": [
            {
                "key": "cma_foundation",
                "label": "CMA Foundation",
                "short": "Foundation",
                "clear_condition": "single_exam",
                "subjects": [
                    {"key": "FAC_CMA", "label": "Fundamentals of Accounting", "target_hrs": 100, "color": "#7DD3FC", "topics": ["Accounting Basics","Journal Ledger","Financial Statements","Depreciation","Partnership"]},
                    {"key": "FBE_CMA", "label": "Fundamentals of Business Economics", "target_hrs": 90, "color": "#34D399", "topics": ["Demand & Supply","Production","Market Forms","National Income","Money"]},
                    {"key": "FBM_CMA", "label": "Fundamentals of Business Mathematics & Statistics", "target_hrs": 90, "color": "#FBBF24", "topics": ["Arithmetic","Algebra","Calculus Basics","Statistics","Probability"]},
                    {"key": "FBL_CMA", "label": "Fundamentals of Business Laws & Ethics", "target_hrs": 90, "color": "#F87171", "topics": ["Indian Contract Act","Sale of Goods","Companies Act Basics","Ethics"]},
                ],
            },
            {
                "key": "cma_inter",
                "label": "CMA Intermediate",
                "short": "Inter",
                "clear_condition": "both_groups",
                "subjects": [
                    {"key": "COSTACC", "label": "Cost Accounting", "target_hrs": 130, "color": "#7DD3FC", "topics": ["Material Cost","Labour","Overheads","Job Costing","Process Costing","Standard Costing","Marginal Costing"]},
                    {"key": "FINACC", "label": "Financial Accounting", "target_hrs": 120, "color": "#34D399", "topics": ["Accounting Standards","Company Accounts","Partnership","Branch Accounts","Insurance Claims"]},
                    {"key": "DLAWGOV", "label": "Direct Taxation & Laws & Governance", "target_hrs": 130, "color": "#FBBF24", "topics": ["Income Tax – Basics","Deductions","GST – Basics","Company Law","Ethics & Governance"]},
                    {"key": "OPSTRAT", "label": "Operations Management & Strategic Management", "target_hrs": 110, "color": "#F87171", "topics": ["Operations Research","Supply Chain","Strategic Analysis","Strategy Formulation"]},
                    {"key": "FINMGMT", "label": "Financial Management", "target_hrs": 120, "color": "#60A5FA", "topics": ["Capital Structure","Capital Budgeting","Working Capital","Leasing","Risk Management"]},
                    {"key": "INDIR_CMA", "label": "Indirect Taxation", "target_hrs": 110, "color": "#A78BFA", "topics": ["GST – Advanced","Customs","FTP"]},
                ],
            },
            {
                "key": "cma_final",
                "label": "CMA Final",
                "short": "Final",
                "clear_condition": "both_groups",
                "subjects": [
                    {"key": "CORP_ETHIC", "label": "Corporate Laws & Compliance", "target_hrs": 130, "color": "#7DD3FC", "topics": ["Companies Act – Advanced","IBC","Competition Law","FEMA","Ethics"]},
                    {"key": "SFM_CMA", "label": "Strategic Financial Management", "target_hrs": 150, "color": "#34D399", "topics": ["Portfolio Management","Derivatives","Mergers & Acquisitions","Foreign Exchange","Project Finance"]},
                    {"key": "SCM_CMA", "label": "Strategic Cost Management & Performance Evaluation", "target_hrs": 140, "color": "#FBBF24", "topics": ["Activity Based Costing","Target Costing","Throughput Accounting","Transfer Pricing","Balanced Scorecard"]},
                    {"key": "DIRINDTAX", "label": "Direct Tax Laws & International Taxation", "target_hrs": 150, "color": "#F87171", "topics": ["Assessment of Various Entities","TDS","Transfer Pricing","DTAA","GAAR"]},
                    {"key": "INDIR_FIN", "label": "Indirect Tax Laws & Practice", "target_hrs": 130, "color": "#60A5FA", "topics": ["GST – Comprehensive","Customs – Comprehensive","FTP"]},
                    {"key": "MGMT_AUDIT", "label": "Cost & Management Audit", "target_hrs": 120, "color": "#A78BFA", "topics": ["Cost Audit","Management Audit","Forensic Audit","Internal Audit – Advanced"]},
                ],
            },
        ],
    },

    # ── UPSC ─────────────────────────────────────────────────────────────────
    "upsc": {
        "label": "UPSC Civil Services",
        "short": "UPSC",
        "icon": "🏛️",
        "category": "Government",
        "levels": [
            {
                "key": "upsc_prelims",
                "label": "Prelims",
                "short": "Prelims",
                "clear_condition": "qualify_cutoff",
                "subjects": [
                    {"key": "GS_PRE", "label": "General Studies (Paper 1)", "target_hrs": 300, "color": "#7DD3FC",
                     "topics": ["History – Ancient","History – Medieval","History – Modern","Geography – Physical","Geography – India","Polity","Economy","Environment & Ecology","Science & Technology","Current Affairs"]},
                    {"key": "CSAT", "label": "CSAT (Paper 2)", "target_hrs": 100, "color": "#34D399",
                     "topics": ["Reading Comprehension","Logical Reasoning","Data Interpretation","Basic Numeracy","Decision Making"]},
                ],
            },
            {
                "key": "upsc_mains",
                "label": "Mains",
                "short": "Mains",
                "clear_condition": "qualify_marks",
                "subjects": [
                    {"key": "ESSAY", "label": "Essay", "target_hrs": 80, "color": "#7DD3FC", "topics": ["Essay Writing Practice","Current Affairs Essays","Philosophical Essays"]},
                    {"key": "GS1", "label": "GS Paper 1", "target_hrs": 150, "color": "#34D399", "topics": ["Indian Culture","History – World & Society","Geography"]},
                    {"key": "GS2", "label": "GS Paper 2 – Polity & IR", "target_hrs": 150, "color": "#FBBF24", "topics": ["Indian Constitution","Governance","Social Justice","International Relations"]},
                    {"key": "GS3", "label": "GS Paper 3 – Economy & Security", "target_hrs": 150, "color": "#F87171", "topics": ["Economy","Agriculture","Science & Tech","Environment","Disaster Management","Security"]},
                    {"key": "GS4", "label": "GS Paper 4 – Ethics", "target_hrs": 120, "color": "#60A5FA", "topics": ["Ethics – Theory","Ethics in Public Administration","Case Studies"]},
                    {"key": "OPTIONAL", "label": "Optional Subject", "target_hrs": 250, "color": "#A78BFA", "topics": ["Optional Paper 1","Optional Paper 2"]},
                ],
            },
            {
                "key": "upsc_interview",
                "label": "Interview / Personality Test",
                "short": "Interview",
                "clear_condition": "qualify_marks",
                "subjects": [
                    {"key": "INTV", "label": "Personality Test Preparation", "target_hrs": 80, "color": "#7DD3FC", "topics": ["Mock Interviews","Current Affairs Revision","DAF Review","Hobby & Optional Depth"]},
                ],
            },
        ],
    },

    # ── CLAT ─────────────────────────────────────────────────────────────────
    "clat": {
        "label": "CLAT – Law Entrance",
        "short": "CLAT",
        "icon": "⚖️",
        "category": "Law",
        "levels": [
            {
                "key": "clat_ug",
                "label": "CLAT UG",
                "short": "UG",
                "clear_condition": "qualify_cutoff",
                "subjects": [
                    {"key": "CLAT_ENG", "label": "English", "target_hrs": 100, "color": "#7DD3FC", "topics": ["Reading Comprehension","Vocabulary","Grammar","Critical Reasoning"]},
                    {"key": "CLAT_CA", "label": "Current Affairs & GK", "target_hrs": 120, "color": "#34D399", "topics": ["National Events","International Events","Legal Current Affairs","Static GK"]},
                    {"key": "CLAT_LEGAL", "label": "Legal Reasoning", "target_hrs": 150, "color": "#FBBF24", "topics": ["Principles Based Questions","Legal Knowledge","Torts","Contract","Constitution Basics"]},
                    {"key": "CLAT_LOGIC", "label": "Logical Reasoning", "target_hrs": 100, "color": "#F87171", "topics": ["Analytical Reasoning","Critical Thinking","Syllogisms"]},
                    {"key": "CLAT_QUANT", "label": "Quantitative Techniques", "target_hrs": 80, "color": "#60A5FA", "topics": ["Data Interpretation","Basic Mathematics"]},
                ],
            },
            {
                "key": "clat_pg",
                "label": "CLAT PG",
                "short": "PG",
                "clear_condition": "qualify_cutoff",
                "subjects": [
                    {"key": "CONST_LAW", "label": "Constitutional Law", "target_hrs": 120, "color": "#7DD3FC", "topics": ["Fundamental Rights","Directive Principles","Federalism","Separation of Powers"]},
                    {"key": "JURIS", "label": "Jurisprudence", "target_hrs": 100, "color": "#34D399", "topics": ["Theories of Law","Schools of Jurisprudence","Legal Concepts"]},
                    {"key": "CONTRACT_ADV", "label": "Contract Law", "target_hrs": 100, "color": "#FBBF24", "topics": ["Essentials","Breach & Remedies","Specific Relief","Special Contracts"]},
                    {"key": "CRIM", "label": "Criminal Law", "target_hrs": 100, "color": "#F87171", "topics": ["IPC","CrPC","Evidence Act"]},
                    {"key": "INT_LAW", "label": "International Law", "target_hrs": 100, "color": "#60A5FA", "topics": ["Public International Law","Treaties","UN System","Human Rights"]},
                ],
            },
        ],
    },
}

# ── CATEGORY GROUPING FOR UI ─────────────────────────────────────────────────
CATEGORY_ORDER = ["Professional", "Engineering", "Medical", "Government", "Law", "Other"]

def get_course(course_id: str) -> dict | None:
    return COURSES.get(course_id)

def get_level(course_id: str, level_key: str) -> dict | None:
    course = get_course(course_id)
    if not course:
        return None
    for lv in course["levels"]:
        if lv["key"] == level_key:
            return lv
    return None

def get_default_subjects(course_id: str, level_key: str) -> list[dict]:
    lv = get_level(course_id, level_key)
    return lv["subjects"] if lv else []

def get_level_index(course_id: str, level_key: str) -> int:
    course = get_course(course_id)
    if not course:
        return -1
    for i, lv in enumerate(course["levels"]):
        if lv["key"] == level_key:
            return i
    return -1

def get_next_level(course_id: str, current_level_key: str) -> dict | None:
    course = get_course(course_id)
    if not course:
        return None
    levels = course["levels"]
    for i, lv in enumerate(levels):
        if lv["key"] == current_level_key and i + 1 < len(levels):
            return levels[i + 1]
    return None  # No next level — course complete

def list_courses_by_category() -> dict[str, list[tuple[str, dict]]]:
    """Returns {category: [(course_id, course_dict), ...]}"""
    result: dict[str, list] = {cat: [] for cat in CATEGORY_ORDER}
    for cid, cdata in COURSES.items():
        cat = cdata.get("category", "Other")
        if cat not in result:
            result[cat] = []
        result[cat].append((cid, cdata))
    return {k: v for k, v in result.items() if v}

# Legacy mapping — existing CA Final users auto-migrate to this level
LEGACY_CA_FINAL_LEVEL = "ca_final"
LEGACY_COURSE_ID      = "ca"
