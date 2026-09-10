"""Clause taxonomy and heuristic risk rules.

The taxonomy is injected into every Nemotron analysis prompt so output is
consistent. The heuristic rules double as (a) the offline mock engine and
(b) an eval baseline to compare the models against.

DISCLAIMER: ClauseGuard is an educational assistant, NOT legal advice.
"""
from __future__ import annotations

# category key -> (human label, plain-language meaning)
CATEGORIES: dict[str, tuple[str, str]] = {
    "ip_assignment": (
        "IP / ownership of work",
        "Who owns what is created, and whether you keep rights to your background tools and methods.",
    ),
    "payment_terms": (
        "Payment terms",
        "When and how you get paid, late-payment interest, invoicing rules and fees for work in progress.",
    ),
    "term_termination": (
        "Term & termination",
        "How long the contract lasts and the grounds / notice on which either side can end it.",
    ),
    "auto_renewal": (
        "Auto-renewal / price changes",
        "Whether the contract renews silently and whether prices can be changed without clear consent.",
    ),
    "liability_cap": (
        "Limitation of liability",
        "The maximum you (or the other party) must pay if something goes wrong, and which damages are excluded.",
    ),
    "indemnity": (
        "Indemnity (you pay their losses)",
        "A promise to cover the other party's legal costs and damages, e.g. if a third party sues them.",
    ),
    "confidentiality": (
        "Confidentiality / NDA",
        "What you must keep secret, for how long, and what happens if you breach it.",
    ),
    "non_compete": (
        "Non-compete",
        "Restrictions on working for others or running a competing business, during or after the contract.",
    ),
    "non_solicit": (
        "Non-solicitation",
        "Restrictions on hiring or dealing with the other party's staff or customers afterwards.",
    ),
    "disputes": (
        "Governing law & disputes",
        "Which law applies, where courts/arbitration sit, and who pays costs.",
    ),
    "warranties": (
        "Warranties / 'as is'",
        "What quality or fitness is promised, and which responsibilities are disclaimed.",
    ),
    "data_protection": (
        "Data protection",
        "How personal data is handled (relevant to India's Digital Personal Data Protection Act, 2023).",
    ),
    "amendments": (
        "Amendments / changes",
        "How the contract can be changed and whether one side can change it unilaterally.",
    ),
    "assignment": (
        "Assignment / subcontracting",
        "Whether the contract can be transferred to another company without your consent.",
    ),
    "lock_in": (
        "Lock-in / exit fees",
        "Minimum commitment periods and penalties for leaving early.",
    ),
    "rental_deposit": (
        "Security deposit (rental)",
        "Amount, holding, deductions, and return timing of a tenant's deposit.",
    ),
    "force_majeure": (
        "Force majeure",
        "Relief when performance is impossible due to unforeseeable events beyond a party's control.",
    ),
    "boilerplate": (
        "General boilerplate",
        "Standard clauses (entire agreement, notices, severability) — usually low risk, worth understanding.",
    ),
    "other": ("Other", "Clause type not in the standard checklist."),
}

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}

# Heuristic rules. "match" keywords must ALL appear (case-insensitive).
# Ordered loosely; the highest-severity match wins per clause.
RISK_RULES: list[dict] = [
    {
        "match": ["perpetual", "irrevocable"],
        "category": "ip_assignment",
        "severity": "critical",
        "title": "Perpetual, irrevocable transfer of rights",
        "risk": "You may lose ownership of your work, reusable tools and methods forever, worldwide, with no way to withdraw consent even if you are never paid.",
        "redline": "Assign only the specific final deliverables identified in a Statement of Work, and only after full payment. License (do not assign) background IP, tools and generics back to you; exclude pre-existing works and moral-rights waivers.",
        "law": "Under the Indian Copyright Act, 1957, assignment of copyright (including future works) must be in writing and is construed narrowly; assignment of future works is limited to works identified in the agreement.",
    },
    {
        "match": ["moral", "rights"],
        "category": "ip_assignment",
        "severity": "high",
        "title": "Waiver of moral rights / attribution",
        "risk": "You could be barred from being named as the creator or from objecting to distortion of your work.",
        "redline": "Delete the moral-rights waiver, or limit it to modifications you approve in writing.",
        "law": "Moral rights (Section 57, Copyright Act 1957) cannot ordinarily be assigned away, even if 'waived' in a contract — but litigating this is costly.",
    },
    {
        "match": ["indemnif", "unlimited"],
        "category": "indemnity",
        "severity": "critical",
        "title": "Uncapped indemnity",
        "risk": "You must cover potentially unlimited third-party claims and legal costs — one claim could bankrupt a freelancer.",
        "redline": "Cap aggregate indemnity at fees paid/received in the preceding 12 months; exclude indirect/consequential loss; require prompt notice, control of defence, and carve-outs for the other party's negligence or materials.",
        "law": "Indemnities are enforceable under the Indian Contract Act, 1872, but courts read uncapped, one-sided indemnities strictly; negotiate symmetry and caps.",
    },
    {
        "match": ["indemnif"],
        "category": "indemnity",
        "severity": "high",
        "title": "Broad indemnity obligation",
        "risk": "A wide promise to cover claims (including IP infringement caused by materials the other party supplied).",
        "redline": "Limit indemnity to third-party claims arising directly from breach of your express warranties; add mutuality so the client indemnifies you for its materials and instructions.",
        "law": "Indian Contract Act 1872, ss. 124–125 govern indemnity; scope depends on the precise wording.",
    },
    {
        "match": ["consequential", "damages"],
        "category": "liability_cap",
        "severity": "high",
        "title": "Exposure to indirect / consequential damages",
        "risk": "You could owe far beyond the contract value (e.g. their claimed lost profits).",
        "redline": "Mutual waiver of indirect, incidental, consequential and punitive damages; mutual aggregate liability cap (commonly 3–12 months of fees).",
        "law": "Indian courts (e.g. the Hadley v. Baxendale line followed in India) allow consequential damages only if losses were within the parties' contemplation; an exclusion clause is the cleanest protection.",
    },
    {
        "match": ["sole discretion"],
        "category": "term_termination",
        "severity": "high",
        "title": "One-sided 'sole discretion' decisions",
        "risk": "The other party can reject work, withhold approval, change scope or terminate for any reason — including to avoid paying.",
        "redline": "Replace 'sole discretion' with 'reasonable discretion', objective acceptance criteria, a cure period, and payment for work performed up to termination.",
        "law": "Unconscionable and arbitrary terms may be tested under unreasonableness/good-faith principles, but prevention is far cheaper than litigation.",
    },
    {
        "match": ["terminate", "without cause"],
        "category": "term_termination",
        "severity": "high",
        "title": "Termination for convenience without payment protection",
        "risk": "Contract can end at will while work in progress goes unpaid and resources stay booked.",
        "redline": "Require 30 days' written notice, payment for all work performed and non-cancellable committed costs, plus a kill fee for convenience termination.",
        "law": "The Indian Contract Act allows parties to fix termination terms; quantum meruit may help recover value of work done but is slow and uncertain.",
    },
    {
        "match": ["no payment"],
        "category": "payment_terms",
        "severity": "high",
        "title": "Work performed with no payment protection",
        "risk": "Completed or in-progress work can be forfeited on termination or dispute.",
        "redline": "Payment due for all accepted work and work-in-progress at termination, regardless of reason; milestone-based invoicing.",
        "law": "Quantum meruit and quasi-contract obligations (Indian Contract Act, ss. 68–72) can aid recovery but require evidence and litigation.",
    },
    {
        "match": ["automatic", "renew"],
        "category": "auto_renewal",
        "severity": "medium",
        "title": "Silent auto-renewal",
        "risk": "The contract (and payment obligations) renew automatically unless you remember a narrow cancellation window.",
        "redline": "Require advance email reminder 30 days before renewal; renewal only with written confirmation; pro-rata refund for prepaid unused periods.",
        "law": "Auto-renewal clauses are generally valid in B2B contracts in India but must be clear; consumer contracts face heightened unfair-term scrutiny (Consumer Protection Act 2019).",
    },
    {
        "match": ["non-compete"],
        "category": "non_compete",
        "severity": "high",
        "title": "Non-compete restriction",
        "risk": "Barred from serving other clients or your trade for a long period or wide territory.",
        "redline": "Delete post-term non-compete. If unavoidable, limit it to the contract term, narrow it to directly competing work for named clients, and add compensation for the restricted period.",
        "law": "Section 27 of the Indian Contract Act, 1872 voids agreements in restraint of trade, except narrow cases (e.g. sale of goodwill); broad post-employment/ post-contract bans are typically unenforceable in India.",
    },
    {
        "match": ["shall not engage"],
        "category": "non_compete",
        "severity": "high",
        "title": "Restriction on practising your profession",
        "risk": "Could prevent you taking other work during/after the engagement.",
        "redline": "Limit exclusivity to the term, to named direct competitors, and ensure it does not block your core profession.",
        "law": "Restraint of trade is void under Section 27, Indian Contract Act 1872, beyond what is reasonably necessary.",
    },
    {
        "match": ["non-solicit"],
        "category": "non_solicit",
        "severity": "medium",
        "title": "Non-solicitation restriction",
        "risk": "Restrictions on contacting the other party's customers or hiring its staff after the contract.",
        "redline": "Limit to 6–12 months post-term and to contacts you actually worked with; mutualise the obligation.",
        "law": "Post-term non-solicits are tested under Section 27; narrowly tailored, reasonable restrictions are more likely to be upheld.",
    },
    {
        "match": ["perpetual", "confidential"],
        "category": "confidentiality",
        "severity": "medium",
        "title": "Perpetual confidentiality",
        "risk": "Obligations that never expire, covering even trivial or public information.",
        "redline": "3–5 year term for confidential information; carve-outs for public info, independently developed info, and legally required disclosure; perpetual protection only for genuine trade secrets.",
        "law": "Trade secrets may be protected indefinitely, but a blanket perpetual duty over all shared information is unreasonably broad.",
    },
    {
        "match": ["exclusive", "jurisdiction"],
        "category": "disputes",
        "severity": "medium",
        "title": "Distant / inconvenient exclusive jurisdiction",
        "risk": "You must travel to a far city (or fund arbitration there) to enforce even small claims.",
        "redline": "Choose courts/arbitration seat in your city, or a neutral seat; specify cost-bearing and small-claims carve-outs.",
        "law": "Parties may choose jurisdiction under the Code of Civil Procedure if it has a reasonable nexus; one-sided distant seats raise cost barriers that deter valid claims.",
    },
    {
        "match": ["security deposit"],
        "category": "rental_deposit",
        "severity": "medium",
        "title": "Security deposit terms",
        "risk": "Large deposit with no rules on deductions, interest, or return timing.",
        "redline": "State the amount (and any cap), that it cannot be adjusted for rent without consent, itemised deductions only, and refund within 15–30 days of vacating with bank details.",
        "law": "Security deposits are governed by the contract and applicable state rent laws; some states cap deposits (e.g. model tenancy framework suggests 1–2 months' rent for residential).",
    },
    {
        "match": ["modify", "at any time"],
        "category": "amendments",
        "severity": "medium",
        "title": "Unilateral right to change terms",
        "risk": "The other party can change scope, rates or rules without your agreement.",
        "redline": "Amendments only by written instrument signed by both parties; price changes apply only to future statements of work with notice.",
        "law": "A unilateral variation clause is generally enforceable only if clearly worded and exercised reasonably; surprises are fertile ground for disputes.",
    },
    {
        "match": ["assign", "without consent"],
        "category": "assignment",
        "severity": "medium",
        "title": "Free assignment / subcontracting",
        "risk": "The contract (and your obligations, data, or deliverables) can be transferred to an unknown third party.",
        "redline": "Assignment/subcontracting requires prior written consent, not unreasonably withheld; affiliates and M&A excepted with notice and assumed obligations.",
        "law": "Assignment of contracts is governed by their terms and the Indian Contract Act; personal-service contracts cannot ordinarily be delegated without consent.",
    },
    {
        "match": ["as is"],
        "category": "warranties",
        "severity": "medium",
        "title": "Broad 'as is' disclaimer / warranty stripping",
        "risk": "If you are the buyer, all quality and fitness promises are disclaimed; if you are the provider, warranties may be impossibly broad.",
        "redline": "For buyers: keep fitness-for-purpose and conformance warranties plus a remediation period. For providers: warrant only conformance to agreed specs and remediate within a warranty window.",
        "law": "The Sale of Goods Act / consumer law imply certain quality terms; disclaimers cannot exclude liability for negligence causing harm or statutory consumer rights.",
    },
    {
        "match": ["lock-in"],
        "category": "lock_in",
        "severity": "medium",
        "title": "Lock-in / early-termination fee",
        "risk": "Trapped paying for a minimum term even if service fails.",
        "redline": "Add service-level exit rights (material breach, persistent downtime) without penalty; cap early-exit fees at proven unamortised costs.",
        "law": "Penalties disproportionate to legitimate loss are open to reduction under the principle that liquidated damages must represent genuine pre-estimate (Section 74, Indian Contract Act).",
    },
    {
        "match": ["net 60"],
        "category": "payment_terms",
        "severity": "medium",
        "title": "Very slow payment cycle",
        "risk": "60+ day terms create cash-flow pressure and normalize delayed payment.",
        "redline": "Net 15–30 for freelancers/small vendors; late-payment interest (e.g. 1–1.5%/month); right to pause work after overdue notice.",
        "law": "Late-payment protections exist for MSMEs under the MSMED Act, 2006 (including compound interest) — registration strengthens a small supplier's hand.",
    },
    {
        "match": ["personal data"],
        "category": "data_protection",
        "severity": "low",
        "title": "Personal data handling clause",
        "risk": "Unclear responsibilities for personal data can create compliance exposure.",
        "redline": "Define roles (Data Principal/Trustee/Processor analogues), purpose limitation, breach notice timeline (aim 72h), sub-processor controls, deletion/return on exit.",
        "law": "India's Digital Personal Data Protection Act, 2023 sets consent, notice and breach obligations; rules are still being operationalised — keep clauses aligned to its principles.",
    },
    {
        "match": ["late payment"],
        "category": "payment_terms",
        "severity": "low",
        "title": "Late-payment provision",
        "risk": "Check symmetry: is interest charged to the paying party when they delay?",
        "redline": "Mutual, clearly stated late-payment interest and an overdue-notice + suspension right.",
        "law": "Reasonable interest clauses are enforceable; MSME-registered suppliers have statutory late-payment backing (MSMED Act 2006).",
    },
    {
        "match": ["force majeure"],
        "category": "force_majeure",
        "severity": "low",
        "title": "Force majeure",
        "risk": "Standard relief clause — check it is mutual and includes notice/mitigation duties.",
        "redline": "Make it mutual, list sample events, require prompt notice and mitigation, and excuse only affected obligations for the disruption period.",
        "law": "Force majeure clauses are read under the Indian Contract Act (ss. 32, 56); vague, one-sided clauses are interpreted narrowly.",
    },
    {
        "match": ["entire agreement"],
        "category": "boilerplate",
        "severity": "low",
        "title": "Entire agreement clause",
        "risk": "Promises made in emails or sales calls may no longer count.",
        "redline": "Ensure everything agreed is captured in the contract/SOW; keep carve-outs for fraud and pre-existing rights.",
        "law": "Entire-agreement clauses are generally upheld in India but do not exclude liability for fraud or misrepresentation.",
    },
]
