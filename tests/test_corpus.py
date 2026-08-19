"""Regression tests for corpus construction.

Every test here holds either a fault that actually occurred in this corpus or a
rule a reported number depends on. The two normalisation faults below were found
only when full-text retrieval downloaded the same article twice, after the
corpus had been frozen and published, and they moved the distinct-work count
from 108 to 99. That is the case for keeping them as tests rather than as a note.
"""

import pandas as pd
import pytest

from build_corpus import (
    assign_duplicate_groups,
    assign_work_venue_class,
    classify_openalex,
    clean_title,
    norm_title,
)
from fetch_fulltext import ordered_records, work_key


def records(*rows: dict) -> pd.DataFrame:
    """A corpus frame with the columns the grouping functions read."""
    return pd.DataFrame(
        [{"doi": "", "title": "", "venue_class": "journal_article", **row} for row in rows]
    )


def groups(frame: pd.DataFrame) -> list[int]:
    return list(assign_duplicate_groups(frame)["dup_group"])


class TestTitleNormalisation:
    def test_version_markers_are_dropped(self):
        """Preprint servers suffix the title of the article's own preprint."""
        assert norm_title("Personality Types of Medical Students (Preprint)") == norm_title(
            "Personality Types of Medical Students"
        )

    def test_html_entities_are_resolved(self):
        """OpenAlex stores &amp; literally; two corpus titles carried one."""
        assert norm_title("Personality Type &amp; Fruit") == norm_title("Personality Type & Fruit")

    @pytest.mark.parametrize(
        "title",
        [
            "ПСИХОЛОГІЧНІ ТИПИ ЯК ІНСТРУМЕНТ",
            "16Personalitiesからみるファッションの傾向",
            "Ψυχολογικοί τύποι",
        ],
    )
    def test_non_latin_titles_survive(self, title):
        """A [^a-z0-9] normaliser emptied these, and an empty key matches nothing.

        About a quarter of this corpus is not in English, so those works could
        never be recognised as duplicates of their own other versions.
        """
        assert norm_title(title) != ""

    def test_different_non_latin_titles_do_not_collide(self):
        """The same fault ran the other way: two empty keys are equal.

        A Bulgarian study of mayors and a Ukrainian study of team motivation
        were briefly grouped as one work.
        """
        bulgarian = "Идентифициране на личностните типове на кметовете"
        ukrainian = "ПСИХОЛОГІЧНІ ТИПИ ЯК ІНСТРУМЕНТ ПІДВИЩЕННЯ МОТИВАЦІЇ"
        assert norm_title(bulgarian) != norm_title(ukrainian)

    def test_clean_title_keeps_the_title_readable(self):
        assert clean_title("Bleed in Dungeons &amp; Dragons") == "Bleed in Dungeons & Dragons"


class TestDuplicateGrouping:
    def test_same_doi_is_one_work(self):
        frame = records(
            {"doi": "10.1/x", "title": "A study"},
            {"doi": "10.1/x", "title": "A Study."},
        )
        assert len(set(groups(frame))) == 1

    def test_same_title_under_different_dois_is_one_work(self):
        """Zenodo and OSF mint a DOI per version; keying on the DOI split them."""
        frame = records(
            {"doi": "10.5281/zenodo.20131632", "title": "Evidence-Based Frameworks"},
            {"doi": "10.5281/zenodo.20131633", "title": "Evidence-Based Frameworks"},
        )
        assert len(set(groups(frame))) == 1

    def test_preprint_and_article_are_one_work(self):
        frame = records(
            {"doi": "10.48550/arxiv.2304.07333", "title": "The Self-Perception of ChatGPT"},
            {"doi": "10.1155/2024/7115633", "title": "The Self-Perception of ChatGPT"},
        )
        assert len(set(groups(frame))) == 1

    def test_grouping_is_transitive(self):
        """Three OSF versions reach each other through the shared title."""
        frame = records(
            {"doi": "10.31235/osf.io/c9raf", "title": "The MBTI and self-conceptions"},
            {"doi": "10.31235/osf.io/c9raf_v2", "title": "The MBTI and self-conceptions"},
            {"doi": "10.31235/osf.io/c9raf_v3", "title": "The MBTI and self-conceptions"},
        )
        assert len(set(groups(frame))) == 1

    def test_untitled_records_do_not_collapse_together(self):
        """An empty title key must join nothing but its own row."""
        frame = records(
            {"doi": "", "title": ""},
            {"doi": "", "title": ""},
        )
        assert len(set(groups(frame))) == 2

    def test_distinct_works_stay_distinct(self):
        frame = records(
            {"doi": "10.1/a", "title": "Personality and driving"},
            {"doi": "10.1/b", "title": "Personality and teaching"},
        )
        assert len(set(groups(frame))) == 2


class TestWorkVenueClass:
    def test_published_version_wins_over_preprint(self):
        """This is what keeps a preprint copy from inflating the main analysis."""
        frame = pd.DataFrame(
            [
                {"dup_group": 0, "venue_class": "preprint"},
                {"dup_group": 0, "venue_class": "journal_article"},
            ]
        )
        assert set(assign_work_venue_class(frame)["work_venue_class"]) == {"journal_article"}

    def test_conference_wins_over_preprint(self):
        frame = pd.DataFrame(
            [
                {"dup_group": 0, "venue_class": "preprint"},
                {"dup_group": 0, "venue_class": "conference"},
            ]
        )
        assert set(assign_work_venue_class(frame)["work_venue_class"]) == {"conference"}

    def test_unknown_class_ranks_last(self):
        frame = pd.DataFrame(
            [
                {"dup_group": 0, "venue_class": "something_new"},
                {"dup_group": 0, "venue_class": "repository"},
            ]
        )
        assert set(assign_work_venue_class(frame)["work_venue_class"]) == {"repository"}


class TestVenueClassification:
    def test_library_guide_is_not_scholarly(self):
        assert classify_openalex({"type": "libguides"}) == "non_scholarly"

    def test_journal_article_needs_a_journal_source(self):
        work = {
            "type": "article",
            "primary_location": {"source": {"type": "journal", "display_name": "Some Journal"}},
        }
        assert classify_openalex(work) == "journal_article"

    def test_article_without_a_source_is_unclassified(self):
        """The iMedPub record that Phase 2 had to rule on arrives this way."""
        assert classify_openalex({"type": "article", "primary_location": {}}) == "unclassified"

    def test_repository_host_beats_a_generic_article_type(self):
        work = {
            "type": "article",
            "primary_location": {"source": {"type": "repository", "display_name": "Zenodo"}},
        }
        assert classify_openalex(work) == "repository"


class TestRetrievalOrdering:
    def test_work_key_prefers_the_doi(self):
        row = pd.Series({"doi": "10.1/abc", "source_id": "https://openalex.org/W1"})
        assert work_key(row) == "10_1_abc"

    def test_work_key_falls_back_to_the_source_id(self):
        row = pd.Series({"doi": "", "source_id": "https://openalex.org/W1"})
        assert "w1" in work_key(row)

    def test_the_published_version_is_tried_first(self):
        """A coder should read the article, not the preprint of it."""
        frame = pd.DataFrame(
            [
                {"venue_class": "preprint", "oa_url": "https://arxiv.example/1"},
                {"venue_class": "journal_article", "oa_url": "https://journal.example/1"},
            ]
        )
        assert ordered_records(frame).iloc[0]["venue_class"] == "journal_article"
