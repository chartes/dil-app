from api.models.models import (Patent,
                            Person)

def test_create_patent(session):
    """Test the creation of a patent and verify data persistence."""
    person = Person(lastname="Inventeur")
    session.add(person)
    session.commit()

    patent = Patent(person_id=person.id, date_start="2023-01-01", city_label="Lyon")
    session.add(patent)
    session.commit()

    retrieved_patent = session.query(Patent).filter_by(city_label="Lyon").first()
    assert retrieved_patent is not None
    assert retrieved_patent.date_start == "2023-01-01"

def test_update_patent(session):
    """Test updating a patent's information."""
    person = Person(lastname="Inventeur")
    session.add(person)
    session.commit()

    patent = Patent(person_id=person.id, date_start="2023-01-01", city_label="Lyon")
    session.add(patent)
    session.commit()

    patent = session.query(Patent).filter_by(city_label="Lyon").first()
    patent.date_start = "2025-01-01"
    session.commit()

    updated_patent = session.query(Patent).filter_by(city_label="Lyon").first()
    assert updated_patent.date_start == "2025-01-01"
