"""Seed initial product opportunities into Firestore database for Customer to Product Action agent."""

import datetime
from google.cloud import firestore

# Hardcoded project ID as required to prevent Agent Platform project number issue
PROJECT_ID = "qwiklabs-gcp-04-edadb8856cae"
COLLECTION_NAME = "product_opportunities"

SEED_ITEMS = [
    {
        "opportunity_id": "opp-001",
        "title": "3D GPU Render Performance & Export Bottleneck",
        "persona": "Lead Mechanical Engineer / Piping Designer",
        "problem_statement": "Large plant 3D models experience 10+ second frame drops and stuttering during live client reviews.",
        "desired_outcome": "Smooth 60 FPS viewport rendering and instant background export.",
        "product_area": "Smart 3D",
        "priority_tier": "P0 - Investigate Immediately",
        "weighted_score": 86.0,
        "status": "under_review",
        "source_customer": "Acme Industrial Engineering",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "opportunity_id": "opp-002",
        "title": "Cross-System Excel Specification Sync",
        "persona": "Product Manager / Operations Lead",
        "problem_statement": "Engineers manually re-type equipment spec tables between SDx and external Excel sheets, causing data drift.",
        "desired_outcome": "Bi-directional automated background sync between SDx catalog and Excel spreadsheets.",
        "product_area": "SDx",
        "priority_tier": "P1 - Strong Roadmap Candidate",
        "weighted_score": 74.5,
        "status": "under_review",
        "source_customer": "Global Energy Corp",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "opportunity_id": "opp-003",
        "title": "Unified Cross-Product License Usage Dashboard",
        "persona": "IT Administrator / Procurement Manager",
        "problem_statement": "No single pane of glass to audit concurrent license seats across Forte 3D and InConcert.",
        "desired_outcome": "Centralized Platform analytics dashboard showing real-time seat utilization.",
        "product_area": "Platform",
        "priority_tier": "P2 - Validate with More Customers",
        "weighted_score": 58.0,
        "status": "under_review",
        "source_customer": "Apex Process Solutions",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
]


def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    print(f"Seeding Firestore collection '{COLLECTION_NAME}' in project '{PROJECT_ID}'...")
    for item in SEED_ITEMS:
        doc_ref = collection_ref.document(item["opportunity_id"])
        doc_ref.set(item)
        print(f"  ✓ Seeded document: {item['opportunity_id']} - {item['title']}")

    print("Firestore database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
