"""Conservative comparison of TWO official EPO EP XML publication versions.

Uses only document metadata, paragraph counts and normalized segment hashes.
It does not resolve opposition decisions, legal protection scope, or the
correspondence of differently numbered claims.
"""


def compare_ep_publication_versions(first, second):
    if first.get("source_format") != "EPO_EP_PATENT_DOCUMENT_ST36_FAMILY":
        raise ValueError("First source must be EPO EP document XML")
    if second.get("source_format") != "EPO_EP_PATENT_DOCUMENT_ST36_FAMILY":
        raise ValueError("Second source must be EPO EP document XML")
    p=first.get("document_publication") or ""
    q=second.get("document_publication") or ""
    k1=first.get("document_kind") or ""
    k2=second.get("document_kind") or ""
    if not (p.startswith("EP") and q.startswith("EP") and k1 and k2 and
            p[:-len(k1)] == q[:-len(k2)] and p != q):
        raise ValueError("Need two different publications with same EP number")
    a=first.get("claim_groups",{}).get(first.get("primary_claim_language"),[])
    b=second.get("claim_groups",{}).get(second.get("primary_claim_language"),[])
    by_no=lambda seq:{int(x["number"]):x for x in seq}
    d1,d2=by_no(a),by_no(b)
    common=sorted(set(d1)&set(d2))
    changed=[k for k in common if
             d1[k]["sha256_normalized_utf8_text"] !=
             d2[k]["sha256_normalized_utf8_text"]]
    meanings={
        "B1":"European granted patent specification",
        "B2":"New European patent specification after opposition procedure",
        "B3":"European patent specification after limitation procedure",
        "A1":"Published patent application with search report",
    }
    return {
        "first_publication":p,
        "second_publication":q,
        "first_publication_date":first.get("publication_date"),
        "second_publication_date":second.get("publication_date"),
        "first_DTD_as_declared":first.get("schema_or_dtd_version_as_declared"),
        "second_DTD_as_declared":second.get("schema_or_dtd_version_as_declared"),
        "first_kind_semantics_from_EPO":meanings.get(k1,"verify EPO kind code"),
        "second_kind_semantics_from_EPO":meanings.get(k2,"verify EPO kind code"),
        "kind_code_source":"https://register.epo.org/help?topic=kindcodes",
        "first_primary_claims":len(a) if first.get("claims_present_in_this_XML") else None,
        "second_primary_claims":len(b) if second.get("claims_present_in_this_XML") else None,
        "first_all_language_claim_nodes":first.get("claim_nodes_all_languages"),
        "second_all_language_claim_nodes":second.get("claim_nodes_all_languages"),
        "first_description_paragraphs":len(first.get("description_paragraphs",[])),
        "second_description_paragraphs":len(second.get("description_paragraphs",[])),
        "same_number_claim_positions_examined":len(common),
        "hash_changed_at_same_number_positions":changed,
        "same_number_change_count":len(changed),
        "first_unmatched_claim_positions":sorted(set(d1)-set(d2)),
        "second_unmatched_claim_positions":sorted(set(d2)-set(d1)),
        "both_from_EPO_official_publication_XML":True,
        "legal_scope_change_magnitude_inferred":False,
        "claim_renumbering_and_consolidation_independently_reviewed":False,
        "opposition_file_and_reasoning_independently_reviewed":False,
        "historical_claim_evidence_next":"Review published B1/B2 claims and the actual EPO opposition decision and file wrapper.",
        "cautions":[
            "EPO B2 identifies a post-opposition amended specification, but claim-count subtraction is not protection-scope arithmetic.",
            "Position-matched text hashes only indicate textual differences, not legal identity across versions.",
            "A source containing no XML claim nodes is not evidence that the original application publication had no claims.",
            "Languages in the XML are translations, not distinct patent inventions or extra legal claim units.",
        ],
    }
