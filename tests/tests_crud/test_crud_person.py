import pytest
from sqlalchemy.exc import IntegrityError
from api.models.models import Person
from tests.conftest import local_session

def test_create_person():
    """Test the creation of a person and verify data persistence."""
    with local_session as session:
        person = Person(lastname="Dupont", firstnames="Jean", birth_date="1970-01-01")
        session.add(person)
        session.commit()

        retrieved_person = session.query(Person).filter_by(lastname="Dupont").first()
        assert retrieved_person is not None
        assert retrieved_person.lastname == "Dupont"
        assert retrieved_person.firstnames == "Jean"

def test_create_person_integrity_error_lastname():
    """Ensure that trying to create a person without a lastname raises an IntegrityError."""
    with local_session as session:
        person = Person(firstnames="Jean")
        with pytest.raises(IntegrityError):
            session.add(person)
            session.commit()

def test_update_person():
    """Test updating a person's information in the database."""
    with local_session as session:
        person = Person(lastname="Dupont", firstnames="Jean")
        session.add(person)
        session.commit()

        person = session.query(Person).filter_by(lastname="Dupont").first()
        person.lastname = "Martin"
        session.commit()

        updated_person = session.query(Person).filter_by(firstnames="Jean").first()
        assert updated_person.lastname == "Martin"

def test_before_insert_id_generation():
    """Verify that an ID is generated automatically before inserting a person."""
    with local_session as session:
        person = Person(lastname="Test")
        session.add(person)
        session.commit()

        assert person._id_dil is not None
        assert person._id_dil.startswith("person")

def test_unique_constraint_id_dil():
    """Ensure that inserting two persons with the same _id_dil raises an IntegrityError."""
    with local_session as session:
        person1 = Person(lastname="Testeur", _id_dil="person_12345678")
        session.add(person1)
        session.commit()

        person2 = Person(lastname="Duplicate", _id_dil="person_12345678")
        with pytest.raises(IntegrityError):
            session.add(person2)
            session.commit()

def test_markup_correction():
    """Test correction of HTML markup in person-related text fields."""
    with local_session as session:
        person = Person(
            lastname="Dupont",
            personal_information="<p><br></p><p>Information correcte</p>",
            professional_information="<p><br></p><p>Professionnel</p>",
            comment="<p><br></p><p>Commentaires</p>"
        )
        session.add(person)
        session.commit()

        corrected_person = session.query(Person).filter_by(lastname="Dupont").first()
        assert person.personal_information == "<br /><p>Information correcte</p>"
        assert person.professional_information == "<br /><p>Professionnel</p>"
        assert person.comment == "<br /><p>Commentaires</p>"

def test_before_update_markup_correction():
    """Verify that HTML markup correction occurs before updating a person's fields."""
    with local_session as session:
        person = Person(
            lastname="Test",
            personal_information="<p><br></p><p>Information</p>",
            professional_information="<p><br></p><p>Profession</p>",
            comment="<p><br></p><p>Commentaire</p>"
        )
        session.add(person)
        session.commit()

        person.personal_information = "<p><br></p><p>Mise à jour</p>"
        session.commit()

        updated_person = session.query(Person).filter_by(lastname="Test").first()
        assert person.personal_information == "<br /><p>Mise à jour</p>"
