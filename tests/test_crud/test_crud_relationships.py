from api.models.models import (Person,
                            Patent,
                            PatentHasRelations,
                            PatentRelationType,
                            Image,
                            PatentHasImages)

def test_patent_relation_constraints(session):
    """Test that a patent can correctly establish relationships with other entities."""
    person1 = Person(lastname="Inventeur1")
    person2 = Person(lastname="Inventeur2")
    session.add_all([person1, person2])
    session.commit()

    patent1 = Patent(person_id=person1.id, date_start="~2023-01-01")
    patent2 = Patent(person_id=person2.id, date_start="2024-01")
    session.add_all([patent1, patent2])
    session.commit()

    relation = PatentHasRelations(
        person_id=person1.id,
        person_related_id=person2.id,
        patent_id=patent1.id,
        type=PatentRelationType.SPONSOR
    )
    session.add(relation)
    session.commit()

    assert session.query(PatentHasRelations).count() == 1
    retrieved_relation = session.query(PatentHasRelations).first()
    assert retrieved_relation.type == PatentRelationType.SPONSOR

def test_person_patent_relationship(session):
    """Verify that a person can have multiple patents associated with them."""
    person = Person(lastname="Inventeur")
    session.add(person)
    session.commit()

    patent1 = Patent(person_id=person.id, date_start="2023-01-01")
    patent2 = Patent(person_id=person.id, date_start="2024-01-01")
    session.add_all([patent1, patent2])
    session.commit()

    assert len(person.patents) == 2
    assert person.patents[0].date_start == "2023-01-01"

def test_cascade_delete_patent_images(session):
    """Ensure that deleting a patent also deletes its associated image relationships."""
    person = Person(lastname="Testeur")
    session.add(person)
    session.commit()

    patent = Patent(person_id=person.id)
    session.add(patent)
    session.commit()

    image = Image(label="Test Image")
    session.add(image)
    session.commit()

    # Establish relationship between the patent and image
    patent_image_relation = PatentHasImages(patent_id=patent.id, image_id=image.id)
    session.add(patent_image_relation)
    session.commit()

    # Delete the patent
    session.delete(patent)
    session.commit()

    assert session.query(Patent).count() == 0
    assert session.query(PatentHasImages).count() == 0
