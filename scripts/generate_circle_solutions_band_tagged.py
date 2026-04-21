"""Generate band-tagged JSON for Circle Solutions SEL Framework (Cowie & Myers, 2016).

Constructs KUD items and LTs directly from source (bypassing the harness pipeline,
which failed due to API credit exhaustion during the CW-2 session). Applies the
Developmental Band Translator skill to produce band-tagged-circle-solutions-v1.json.

Year level → REAL band mapping (CW-2 session brief):
  Year 2  → Band A/B  (ages 6-7, ambiguity_flag=True, spans A/B)
  Year 6  → Band C    (age 10-11, unambiguous)
  Year 9  → Band D/E  (age 13-14, ambiguity_flag=True, spans D/E)
  Year 12 → Band F    (age 16-17, unambiguous)

Session: CW-2, 2026-04-21
Note: sparse_source_structure — only Year 2, 6, 9, 12 covered.
Bands B and C/D and E/F boundary not explicitly represented.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = REPO_ROOT / "docs" / "reference-corpus" / "circle-solutions-sel"

# ─── Source content ────────────────────────────────────────────────────────────
# Observable indicators from Table 2.2, reorganised by year level × dimension.

SOURCE_DATA = {
    "Year 2": {
        "band": ["A", "B"],
        "ambiguity_flag": True,
        "source_band": "Year 2",
        "age_range": "ages 6-7",
        "dimensions": {
            "Dimension 1: Self-awareness": [
                "A student can draw a picture of themselves and describe what they have drawn. 'This is me, my name is and I am...' Students are asked to say as much as they can.",
                "Can say five things that they like about themselves.",
                "Can say three things that are important to them.",
            ],
            "Dimension 2: Emotional knowledge": [
                "Can talk about what happens in their bodies when they feel happy, angry and scared.",
                "Listens to different pieces of music and can say what it makes them feel.",
            ],
            "Dimension 3: Emotional skills — regulation, expression and resilience": [
                "Uses regular breathing as a calming strategy.",
                "Uses at least twelve different words for emotion in describing: a play situation; losing something; a day at home.",
                "Can say what cheers them up when they are fed up.",
            ],
            "Dimension 4: Shared humanity": [
                "Can say three things that are the same and three things that are different about themselves and another person.",
                "Joins in a discussion about how this class can make sure everyone feels they belong here.",
            ],
            "Dimension 5: Interpersonal skills": [
                "Can say 'personal positives' about classmates.",
                "Demonstrates the ability to share.",
                "In a pair share, can identify three qualities or actions that would make someone a good friend.",
            ],
            "Dimension 6: Situational skills — empathy and awareness of others": [
                "Can say how a teddy might feel if he: was left out; saw someone fall off a bike; had a new baby sister.",
                "Can recognize non-verbal expression of basic emotions — happy, surprised, scared, sad and worried.",
            ],
            "Dimension 7: Leadership — goal setting and personal confidence": [
                "Can say three things they want to achieve this week.",
                "Invites others to join in games.",
                "Is willing to try new things.",
            ],
            "Dimension 8: Promoting the positive — solution focus and thankfulness": [
                "In a paired discussion, identifies a situation where someone is laughing at someone and how this might feel, and when someone is laughing with someone and how this might feel.",
                "Engages with a class project on making others feel good (filling buckets).",
            ],
            "Dimension 9: Dealing with conflict — assertiveness and negotiation": [
                "Clearly, firmly and politely states what they want — e.g. please leave me alone now.",
                "Knows when something is fair or not and how to stand up for someone.",
            ],
            "Dimension 10: Repair and restoration": [
                "Checks whether a hurt was an accident or deliberate.",
                "Can talk about things that are 'inside' hurts and those that are 'outside' hurts.",
            ],
            "Dimension 11: Ethics, integrity and human rights": [
                "Can say how a lie can grow and get out of control and give three reasons why it might be better to tell the truth.",
                "Within a small group, identifies the responsibilities that go with five rights or freedoms.",
            ],
            "Dimension 12: Meaning and spirituality": [
                "Grows a flower from a seed. Talks in a pair share about what happened: Did the flower grow by itself? What helped it grow? How much was nature and how much was what you did to help?",
                "Identifies three things that would make someone happy for a short time and three things that would make someone happy all or most of the time.",
            ],
        },
    },
    "Year 6": {
        "band": "C",
        "ambiguity_flag": False,
        "source_band": "Year 6",
        "age_range": "ages 10-11",
        "dimensions": {
            "Dimension 1: Self-awareness": [
                "A student can draw three pictures of themselves in different roles and can talk about the different ways they behave in each of these roles. This is me at home. This is me at school. This is me with my friends. Here I am...",
                "Can identify three things they are good at, three qualities they have and three strengths they think they might need in the future.",
                "Can say three things that are important to them and why they are important.",
            ],
            "Dimension 2: Emotional knowledge": [
                "Knows about the continuum of emotions. Can take part in a discussion about when you might be in control of an emotion and when it controls you and say what makes a difference.",
                "Can take part in a discussion about how the arts (music/dance and drama) can impact on how someone feels.",
            ],
            "Dimension 3: Emotional skills — regulation, expression and resilience": [
                "Can identify four different ways to deal with anger and decide which is the preferred option and why.",
                "Can identify at least five words showing different aspects of the following emotions: happiness; sadness; interest; anger.",
                "Knows how thinking can affect how you feel and says what thinking strategies are useful.",
            ],
            "Dimension 4: Shared humanity": [
                "Can write about ways in which everyone is unique and the reasons it is valuable.",
                "Can say what 'The Golden Rule' is, how it appears in all major religions and what it means in practice.",
            ],
            "Dimension 5: Interpersonal skills": [
                "Demonstrates the 'rules' of good conversation — a balance between talking and listening.",
                "Demonstrates regular small acts of kindness — goes out of their way to help others.",
                "Works well within a group to achieve a given target.",
            ],
            "Dimension 6: Situational skills — empathy and awareness of others": [
                "Shows an understanding of what someone might feel if they: were bullied; lost something or someone; broke a leg; failed a test; were hungry or tired.",
                "Can view a film and identify the feelings of characters within a situation by their voice tone, body posture and facial expression.",
            ],
            "Dimension 7: Leadership — goal setting and personal confidence": [
                "Demonstrates an interest in getting better at something. Understands the concept of personal bests.",
                "Is aware of those who have been left out and includes them.",
                "Accepts mistakes as part of learning.",
            ],
            "Dimension 8: Promoting the positive — solution focus and thankfulness": [
                "Identifies three things to be grateful for and three things to look forward to.",
                "Can identify one situation in which positive thinking helped and can talk/write about the difference it made.",
            ],
            "Dimension 9: Dealing with conflict — assertiveness and negotiation": [
                "Stands up for others who are less able to stand up for themselves.",
                "Knows when a situation is not safe and leaves.",
            ],
            "Dimension 10: Repair and restoration": [
                "Knows about responsibility pie-charts: how much was down to me, how much to someone else, how much to chance.",
                "Offers to make up for harm caused.",
            ],
            "Dimension 11: Ethics, integrity and human rights": [
                "In a small group, talks about why people don't always get what they deserve, and what this means for how we see the world and others in it.",
                "In small groups, using the Strengths in Circles cards on inclusion and equity, chooses one from each set and decides how this will be put into practice in the classroom.",
            ],
            "Dimension 12: Meaning and spirituality": [
                "Chooses a symbol or picture that illustrates what really matters in life and talks about the choice.",
                "Identifies someone who is a role model for how to live life well and researches what that person did.",
            ],
        },
    },
    "Year 9": {
        "band": ["D", "E"],
        "ambiguity_flag": True,
        "source_band": "Year 9",
        "age_range": "ages 13-14",
        "dimensions": {
            "Dimension 1: Self-awareness": [
                "Has reflected on their developing identity. Writes about a role model and why they have chosen this person.",
                "Can talk about how they have developed up to five character strengths and what strengths they are working on and why these are valuable.",
                "Can identify the five values and three beliefs about the world that impact most in how they choose to live their lives.",
            ],
            "Dimension 2: Emotional knowledge": [
                "Knows the role of the amygdala and how it can hijack 'thinking'. Can give an example of when this might happen. Knows about 'mirroring' neurons. Can give an example of when this might happen.",
                "Watches a film and writes a review about the characters, what happened to them and the emotional content. What did it make them feel and why?",
            ],
            "Dimension 3: Emotional skills — regulation, expression and resilience": [
                "Can list five ways in which someone might change how they feel and write the pros and cons of each.",
                "Can reflect on a learning task and describe a range of emotions that were experienced in engagement, challenges and completion.",
                "Can identify ways in which friends can support resilience and ways in which this can be undermined.",
            ],
            "Dimension 4: Shared humanity": [
                "Can give five reasons why 'shared humanity' matters for the future of our world.",
                "With a partner makes a poster on gender, sexuality or disability to prevent discrimination.",
            ],
            "Dimension 5: Interpersonal skills": [
                "Demonstrates the skills of 'active listening', paying verbal and non-verbal attention, responding verbally and non-verbally, asking questions, clarifying meaning.",
                "Knows what respect means, how it is demonstrated and why it is important for a healthy relationship.",
                "Can initiate and maintain a conversation with someone who is previously unknown.",
            ],
            "Dimension 6: Situational skills — empathy and awareness of others": [
                "Can say when it might be a good time to approach a parent with a request and when best to wait, and identify factors that influence the decision.",
                "Recognizes that everyone has their own story and does not make quick judgements.",
            ],
            "Dimension 7: Leadership — goal setting and personal confidence": [
                "Can divide a task into a series of between 8 and 12 achievable steps.",
                "Can discuss risk taking and look at how to assess risk against potential outcomes.",
                "Gives help to others so that they can do well at something.",
            ],
            "Dimension 8: Promoting the positive — solution focus and thankfulness": [
                "Keeps a daily gratitude journal for a month: writing in three different blessings, one for the day, one for life and one for anything else.",
                "Can take five 'problems' and give a 'solution' for each: what you are aiming for rather than what you want to get rid of.",
            ],
            "Dimension 9: Dealing with conflict — assertiveness and negotiation": [
                "Identifies the short- and long-term outcomes of overt aggression, passive aggression, timidity and appropriate assertiveness.",
                "Checks on intention before jumping to a negative conclusion in a potential conflict.",
            ],
            "Dimension 10: Repair and restoration": [
                "Can list ways to say how something could have been done differently.",
                "Responds positively to an attempt to repair harm caused.",
            ],
            "Dimension 11: Ethics, integrity and human rights": [
                "Identifies three factors that influence how someone might vote in an election.",
                "Takes part in a project to protect the environment.",
            ],
            "Dimension 12: Meaning and spirituality": [
                "Joins in a discussion about what it means to live 'a good life'.",
                "Makes a photo portfolio of what is meaningful and writes briefly why each photo is included.",
            ],
        },
    },
    "Year 12": {
        "band": "F",
        "ambiguity_flag": False,
        "source_band": "Year 12",
        "age_range": "ages 16-17",
        "dimensions": {
            "Dimension 1: Self-awareness": [
                "'Me in ten years' time.' Can write a page about themselves, who they are, what they believe and the person they hope to become in the future.",
                "Can identify five character strengths and also the shadow sides of strengths. Can say what strengths have been of most value to them in their life.",
                "Are clear about a range of values and the reasons they have these.",
            ],
            "Dimension 2: Emotional knowledge": [
                "Can tell the difference between being sad and being depressed. Knows who to seek out for support when they are struggling.",
                "Can write a page about an historical event in which people's emotions were manipulated and how this happened.",
            ],
            "Dimension 3: Emotional skills — regulation, expression and resilience": [
                "Is using one physical strategy, one social strategy and one cognitive strategy on a regular basis to help stay resilient.",
                "Joins in a discussion about a current controversial issue or a film, talking about how people might feel about this.",
                "Has considered the usefulness of mindfulness or meditation as a resilience strategy.",
            ],
            "Dimension 4: Shared humanity": [
                "Can identify times where people have been dehumanized, what contributes to this and what has happened to them.",
                "Is able to identify ways in which shared humanity might be put into practice from the individual to the community to the social/political level.",
            ],
            "Dimension 5: Interpersonal skills": [
                "Is effective within a group discussion. Includes others and builds on their ideas.",
                "Knows what trust means, how it is demonstrated and why it is important for a healthy relationship.",
                "Works with a group to take a project from initiation to completion and can write about the factors that promoted collaboration between team members.",
            ],
            "Dimension 6: Situational skills — empathy and awareness of others": [
                "Can assess the emotional content of a situation and say what might be said or done to make this worse or better. This can be from a book or film.",
                "Can write a story from the different perspectives of the main characters.",
            ],
            "Dimension 7: Leadership — goal setting and personal confidence": [
                "Can reflect on a personal achievement and what contributed to success.",
                "Can say what helps resist peer pressure so you act according to your own values.",
                "Can identify plans for the future, with fall-back plans if these don't happen.",
            ],
            "Dimension 8: Promoting the positive — solution focus and thankfulness": [
                "Reflects on the future, and makes a video talking about what they hope for themselves and the world in the future. Writes three things that they will do now to help this happen.",
                "Talks/writes about a life event as if it were a newspaper story, once with the headline 'Disaster' and once with the headline 'Success', identifying how things can be seen from different perspectives and we have some choice.",
            ],
            "Dimension 9: Dealing with conflict — assertiveness and negotiation": [
                "With a real-life or imagined scenario, can imagine three possible resolutions and write the pros and cons of each, and give a rationale for the first choice.",
                "Checks out what two sides want in a situation and negotiates a compromise.",
            ],
            "Dimension 10: Repair and restoration": [
                "Joins in a small group discussion on the meaning of altruism and whether this is a value to aim for.",
                "Within a small group, researches a social justice issue and devises an action plan to redress this.",
            ],
            "Dimension 11: Ethics, integrity and human rights": [
                "Joins in a small group discussion on the meaning of altruism and whether this is a value to aim for.",
                "Within a small group, researches a social justice issue and devises an action plan to redress this.",
            ],
            "Dimension 12: Meaning and spirituality": [
                "Writes or speaks about the principles or values that will guide small and major decisions in the future.",
                "Writes a personal statement setting out aspirations for being, becoming and contributing.",
            ],
        },
    },
}

# ─── Knowledge type classification ────────────────────────────────────────────
# Applied per observable indicator based on content type:
# Type 1 (Know/Understand): declarative knowledge statements
# Type 2 (Do/Skill): skill demonstrations, procedural
# Type 3 (Disposition): ongoing orientation, orientation-based

DIM_TYPES = {
    "Dimension 1: Self-awareness": "Type 3",        # dispositional — ongoing identity
    "Dimension 2: Emotional knowledge": "Type 1",   # declarative knowledge
    "Dimension 3: Emotional skills — regulation, expression and resilience": "Type 2",
    "Dimension 4: Shared humanity": "Type 2",
    "Dimension 5: Interpersonal skills": "Type 2",
    "Dimension 6: Situational skills — empathy and awareness of others": "Type 2",
    "Dimension 7: Leadership — goal setting and personal confidence": "Type 2",
    "Dimension 8: Promoting the positive — solution focus and thankfulness": "Type 3",
    "Dimension 9: Dealing with conflict — assertiveness and negotiation": "Type 2",
    "Dimension 10: Repair and restoration": "Type 2",
    "Dimension 11: Ethics, integrity and human rights": "Type 2",
    "Dimension 12: Meaning and spirituality": "Type 3",
}


def _dim_slug(dim_name: str) -> str:
    """e.g. 'Dimension 1: Self-awareness' → 'dim-01'"""
    num = dim_name.split(":")[0].replace("Dimension ", "").strip()
    return f"dim-{int(num):02d}"


def _year_slug(year_label: str) -> str:
    return year_label.lower().replace(" ", "-")


def _band_rationale(year_label: str, school_band) -> str:
    rationales = {
        "Year 2": (
            "Circle Solutions Year 2 (ages 6-7) spans REAL Bands A (ages 5-7) and B (ages 7-9). "
            "The year-level marker falls at the Band A/B boundary; tagged [A, B] with ambiguity_flag=true."
        ),
        "Year 6": (
            "Circle Solutions Year 6 (ages 10-11) maps cleanly to REAL Band C (Fire Dragons, "
            "ages 9-11, G5-6). Single-band assignment; high confidence."
        ),
        "Year 9": (
            "Circle Solutions Year 9 (ages 13-14) spans REAL Bands D (ages 11-13) and E (ages 13-15). "
            "Age 13-14 falls at the Band D/E boundary; tagged [D, E] with ambiguity_flag=true."
        ),
        "Year 12": (
            "Circle Solutions Year 12 (ages 16-17) maps cleanly to REAL Band F (ages 15-17, G11-12). "
            "Single-band assignment; high confidence."
        ),
    }
    return rationales.get(year_label, f"Year-level mapping for {year_label}.")


def main() -> None:
    band_tagged_kud = []
    band_tagged_lts = []
    item_counter = 0
    lt_counter = 0

    for year_label, year_data in SOURCE_DATA.items():
        year_slug = _year_slug(year_label)
        school_band = year_data["band"]
        ambiguity_flag = year_data["ambiguity_flag"]
        source_band = year_data["source_band"]
        rationale = _band_rationale(year_label, school_band)

        # Confidence: 'medium' for ambiguous (2-band spans), 'high' for single-band
        band_confidence = "medium" if ambiguity_flag else "high"

        for dim_name, indicators in year_data["dimensions"].items():
            dim_slug = _dim_slug(dim_name)
            knowledge_type = DIM_TYPES.get(dim_name, "Type 2")

            # Generate KUD items for this year × dimension
            lt_item_ids = []
            for i, indicator in enumerate(indicators, 1):
                item_counter += 1
                item_id = f"{year_slug}_{dim_slug}_item_{i:02d}"
                lt_item_ids.append(item_id)
                tagged_item = {
                    "item_id": item_id,
                    "content_statement": indicator,
                    "knowledge_type": knowledge_type,
                    "school_band": school_band,
                    "band_confidence": band_confidence,
                    "source_band_preserved": source_band,
                    "source_voice_preserved": True,
                    "ambiguity_flag": ambiguity_flag,
                    "teacher_review_flag": ambiguity_flag,  # flag ambiguous year-level spans
                    "band_rationale": rationale,
                    "source_block_id": f"{year_slug}_{dim_slug}",
                    "year_level": year_label,
                    "dimension": dim_name,
                }
                band_tagged_kud.append(tagged_item)

            # Generate one LT per year × dimension
            lt_counter += 1
            lt_id = f"{year_slug}_{dim_slug}_lt_01"
            lt_name = f"{dim_name} — {year_label}"
            lt_def = (
                f"Students can demonstrate {dim_name.split(':')[1].strip().lower()} "
                f"competencies at the {year_label} level as described in the "
                f"Circle Solutions SEL Framework (Cowie & Myers, 2016)."
            )
            tagged_lt = {
                "lt_id": lt_id,
                "lt_name": lt_name,
                "lt_definition": lt_def,
                "school_band": school_band,
                "band_confidence": band_confidence,
                "source_band_preserved": source_band,
                "source_voice_preserved": True,
                "ambiguity_flag": ambiguity_flag,
                "teacher_review_flag": ambiguity_flag,
                "band_rationale": rationale,
                "kud_item_ids": lt_item_ids,
                "knowledge_type": knowledge_type,
                "year_level": year_label,
                "dimension": dim_name,
            }
            band_tagged_lts.append(tagged_lt)

    # ── Summary counts ─────────────────────────────────────────────────────────
    from collections import Counter

    def band_key(b):
        if isinstance(b, list):
            return "+".join(b)
        return b

    kud_by_band = Counter(band_key(t["school_band"]) for t in band_tagged_kud)
    lt_by_band = Counter(band_key(t["school_band"]) for t in band_tagged_lts)
    teacher_review_kud = sum(1 for t in band_tagged_kud if t["teacher_review_flag"])
    medium_conf = sum(1 for t in band_tagged_kud if t["band_confidence"] == "medium")

    summary_counts = {
        "total_kud_items": len(band_tagged_kud),
        "total_lts": len(band_tagged_lts),
        "kud_by_band": dict(sorted(kud_by_band.items())),
        "lts_by_band": dict(sorted(lt_by_band.items())),
        "teacher_review_flagged_kud": teacher_review_kud,
        "teacher_review_flagged_lts": sum(1 for t in band_tagged_lts if t["teacher_review_flag"]),
        "low_confidence": 0,
        "medium_confidence": medium_conf,
        "high_confidence": len(band_tagged_kud) - medium_conf,
    }

    skill_flags = [
        (
            "sparse_source_structure: Circle Solutions provides observable indicators at only 4 year "
            "levels (Year 2, 6, 9, 12). REAL Bands B (Earth Dragons, G3-4), C/D boundary, and E/F "
            "boundary are not explicitly represented. Gaps between checkpoints require teacher "
            "interpolation. This is an honest structural limitation of the source, not a quality failure."
        ),
        (
            "year_2_ambiguity: Year 2 (ages 6-7) straddles REAL Bands A and B. Items tagged [A, B] "
            "with ambiguity_flag=true and teacher_review_flag=true. Teacher judgment required to "
            "assign to a specific REAL band for planning purposes."
        ),
        (
            "year_9_ambiguity: Year 9 (ages 13-14) straddles REAL Bands D and E. Items tagged [D, E] "
            "with ambiguity_flag=true and teacher_review_flag=true. Teacher judgment required."
        ),
        (
            "pipeline_bypass: Circle Solutions KUD and LT items were constructed directly from source "
            "material due to API credit exhaustion during the CW-2 session harness pipeline run. "
            "Knowledge type classifications are manual (not LLM-classified via 3-run self-consistency). "
            "Harness pipeline re-run recommended when API credits are restored."
        ),
    ]

    output = {
        "source_metadata": {
            "source_name": "Circle Solutions SEL Framework (Cowie & Myers, 2016)",
            "source_type": "circle_solutions_sel",
            "source_band_labels": ["Year 2", "Year 6", "Year 9", "Year 12"],
            "target_framework": "REAL School Budapest Bands A-F",
            "skill_version": "1.0",
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "session": "CW-2",
            "note": "Manual construction — harness pipeline bypassed (API credit limit CW-2).",
        },
        "band_tagged_kud": band_tagged_kud,
        "band_tagged_lts": band_tagged_lts,
        "summary_counts": summary_counts,
        "skill_flags": skill_flags,
    }

    out_path = CORPUS_DIR / "band-tagged-circle-solutions-v1.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Written: {out_path}")
    print(f"KUD items: {len(band_tagged_kud)}")
    print(f"LTs: {len(band_tagged_lts)}")
    print(f"KUD by band: {dict(sorted(kud_by_band.items()))}")
    print(f"LTs by band: {dict(sorted(lt_by_band.items()))}")
    print(f"teacher_review_flagged (kud): {teacher_review_kud}")
    print(f"medium_confidence: {medium_conf}, high_confidence: {len(band_tagged_kud) - medium_conf}")


if __name__ == "__main__":
    main()
