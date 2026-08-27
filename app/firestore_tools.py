"""Firestore database integration tools for Customer to Product Action agent."""

import datetime
from typing import Optional
from google.cloud import firestore

# Hardcoded project ID as explicitly required for Agent Platform compatibility
PROJECT_ID = "qwiklabs-gcp-04-edadb8856cae"
COLLECTION_NAME = "product_opportunities"


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded GCP project ID."""
    return firestore.Client(project=PROJECT_ID)


def add_product_opportunity(
    title: str,
    persona: str,
    problem_statement: str,
    desired_outcome: str,
    product_area: str,
    priority_tier: str,
    weighted_score: float,
    source_customer: str = "Internal / Unspecified",
) -> str:
    """Saves a new product opportunity to the Firestore database.

    Args:
        title: Short title of the product opportunity.
        persona: Target user persona (e.g. Mechanical Engineer, IT Admin).
        problem_statement: Clear description of the underlying problem.
        desired_outcome: Target state / outcome requested.
        product_area: Product taxonomy area (e.g. Smart 3D, SDx, Platform, Cross-product).
        priority_tier: Priority tier (e.g. P0 - Investigate Immediately, P1).
        weighted_score: Calculated opportunity priority score (0-100).
        source_customer: Customer or company source of the feedback.

    Returns:
        Confirmation message with the generated opportunity ID.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document()
    opportunity_id = doc_ref.id

    data = {
        "opportunity_id": opportunity_id,
        "title": title,
        "persona": persona,
        "problem_statement": problem_statement,
        "desired_outcome": desired_outcome,
        "product_area": product_area,
        "priority_tier": priority_tier,
        "weighted_score": float(weighted_score),
        "status": "under_review",
        "source_customer": source_customer,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    doc_ref.set(data)
    return f"Successfully saved opportunity '{title}' (ID: {opportunity_id}) to Firestore."


def list_product_opportunities(product_area: str = "") -> str:
    """Lists product opportunities stored in Firestore, optionally filtered by product area.

    Args:
        product_area: Optional product area to filter by (e.g. 'Smart 3D', 'SDx', 'Platform').

    Returns:
        A formatted list of product opportunities found in Firestore.
    """
    db = get_firestore_client()
    query = db.collection(COLLECTION_NAME)

    if product_area and product_area.strip():
        query = query.where("product_area", "==", product_area.strip())

    docs = list(query.stream())
    if not docs:
        filter_str = f" for product area '{product_area}'" if product_area else ""
        return f"No product opportunities found in Firestore{filter_str}."

    results = []
    for doc in docs:
        d = doc.to_dict()
        results.append(
            f"• [{d.get('opportunity_id')}] {d.get('title')} ({d.get('product_area')})\n"
            f"  Priority: {d.get('priority_tier')} | Score: {d.get('weighted_score')}/100 | Status: {d.get('status')}\n"
            f"  Persona: {d.get('persona')}\n"
            f"  Problem: {d.get('problem_statement')}"
        )

    return f"Found {len(results)} opportunity(ies) in Firestore:\n\n" + "\n\n".join(results)


def get_product_opportunity(opportunity_id: str) -> str:
    """Retrieves full details for a single product opportunity from Firestore.

    Args:
        opportunity_id: The ID of the opportunity (e.g. 'opp-001').

    Returns:
        Full details of the requested opportunity or an error message if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(opportunity_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Opportunity ID '{opportunity_id}' not found in Firestore."

    d = doc.to_dict()
    return (
        f"Opportunity Details [{d.get('opportunity_id')}]:\n"
        f"Title: {d.get('title')}\n"
        f"Product Area: {d.get('product_area')}\n"
        f"Priority Tier: {d.get('priority_tier')} (Score: {d.get('weighted_score')}/100)\n"
        f"Status: {d.get('status')}\n"
        f"Persona: {d.get('persona')}\n"
        f"Problem Statement: {d.get('problem_statement')}\n"
        f"Desired Outcome: {d.get('desired_outcome')}\n"
        f"Source Customer: {d.get('source_customer')}\n"
        f"Created At: {d.get('created_at')}"
    )
