"""Conservative comparisons between different published versions of one application.

This is a *textual/structural* delta, not a legal claim-scope opinion.
Claim number renumbering is not a 1:1 identity alignment.
"""
from __future__ import annotations


def compare_publication_versions(first, second, *, relationship_source=None):
    p1=first.get("publication_number")
    p2=second.get("publication_number")
    if not p1 or not p2 or p1 == p2:
        raise ValueError("Requires two different identified publication versions")
    if first.get("quality",{}).get("private_text_included") or second.get("quality",{}).get("private_text_included"):
        raise ValueError("Version comparison must use hash-only derived documents; keep raw text private")
    c1=first.get("claims") or []
    c2=second.get("claims") or []
    a={c["number"]:c for c in c1}
    b={c["number"]:c for c in c2}
    n1,n2=set(a),set(b)
    common=sorted(n1 & n2)
    changed=[n for n in common if a[n]["sha256_utf8_normalized_text"]!=b[n]["sha256_utf8_normalized_text"]]
    e1={(e["from_claim_number"],e["referenced_claim_number"]) for e in first.get("claim_dependency_edges",[])}
    e2={(e["from_claim_number"],e["referenced_claim_number"]) for e in second.get("claim_dependency_edges",[])}
    meta1=first.get("application_number_as_provider_meta")
    meta2=second.get("application_number_as_provider_meta")
    return {
       "first_publication":p1,
       "second_publication":p2,
       "first_date_as_provider_meta":first.get("publication_date_as_provider_meta"),
       "second_date_as_provider_meta":second.get("publication_date_as_provider_meta"),
       "first_kind_code":first.get("kind_code_as_provider_meta"),
       "second_kind_code":second.get("kind_code_as_provider_meta"),
       "first_application_as_provider_meta":meta1,
       "second_application_as_provider_meta":meta2,
       "exact_provider_application_meta_match": bool(meta1 and meta2 and meta1==meta2),
       "version_relationship_source":relationship_source or "researcher_supplied_not_officially_verified",
       "claim_counts":{
           "first":len(c1),"second":len(c2),
           "difference_second_minus_first":len(c2)-len(c1),
       },
       "same_number_positions":len(common),
       "changed_normalized_claim_text_hash_by_same_number":changed,
       "changed_count_same_number":len(changed),
       "unmatched_first_numbered_positions":sorted(n1-n2),
       "unmatched_second_numbered_positions":sorted(n2-n1),
       "first_claim_reference_edges":len(e1),
       "second_claim_reference_edges":len(e2),
       "observed_claim_reference_edges_changed_count":len(e1.symmetric_difference(e2)),
       "first_description_paragraphs":len(first.get("description_paragraphs",[])),
       "second_description_paragraphs":len(second.get("description_paragraphs",[])),
       "same_number_identifies_same_legal_claim_across_versions":False,
       "legal_protection_scope_narrowed_or_expanded_verified":False,
       "review_required_for_claim_merger_and_renumbering":True,
       "version_original_patent_office_text_independently_verified":False,
       "limitations":[
           "The same number in two versions is only a positional match, not proof of identical claim identity.",
           "Changed text hashes alone do not prove narrowing, amendment reasons, validity or infringement.",
           "Different observed count may reflect claim merger, deletion, rewriting or renumbering; manually compare original files.",
           "A and B/C version application association must be independently grounded; publisher metadata may vary by kind.",
           "All figures come from Google Patents HTML as observed, not authenticated original patent-office grant copies.",
       ],
    }

