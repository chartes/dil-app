import pytest
import datetime
from sqlalchemy import select
from api.models.models import Person

@pytest.mark.asyncio
async def test_create_person(db_session):
    """Test: Create a new person"""

    # Création d'une personne
    person = Person(
        lastname="Dupont",
        firstnames="Jean",
        birth_date="1970-1-1",  # Utilisation d'un objet `date`
        personal_information="Information personnelle",
    )

    db_session.add(person)
    await db_session.commit()  # Utilisation de `await`

    # Récupération de la personne
    result = await db_session.execute(select(Person).where(Person.lastname == "Dupont"))
    retrieved_person = result.scalars().first()  # `scalars().first()` pour récupérer l'objet

    # Vérifications
    assert retrieved_person is not None
    assert retrieved_person.lastname == "Dupont"
    assert retrieved_person.firstnames == "Jean"

"""
def test_create_person_integrity_error_lastname(session):
    "Test: Check integrity error if lastname not added"
    person = Person(
        firstnames="Jean",
    )
    with pytest.raises(IntegrityError):
        session.add(person)
        session.commit()
"""

"""
def test_create_multiple_person(session):
    "Test: Check when create multiple person"
    person = Person(
        lastname="Mic"
    )
    session.add(person)
    session.commit()
    person = Person(
        lastname="Mac"
    )
    session.add(person)
    session.commit()
    person = Person(
        lastname="Moc"
    )
    session.add(person)
    session.commit()
    retrieved_person = session.query(Person).filter_by(lastname="Mic").first()
    assert retrieved_person is not None
    assert retrieved_person.lastname == "Mic"
    retrieved_person = session.query(Person).filter_by(lastname="Mac").first()
    assert retrieved_person is not None
    assert retrieved_person.lastname == "Mac"
    retrieved_person = session.query(Person).filter_by(lastname="Moc").first()
    assert retrieved_person is not None
    assert retrieved_person.lastname == "Moc"
    assert len(session.query(Person).all()) == 3
    retrieved_person = session.query(Person).filter_by(lastname="Mlk").first()
    assert retrieved_person is None
"""

# ====== TODO:
# test du markup <br> et <p></p>

"""
def test_read_city(session):
    Test de lecture d'une ville.
    city = City(label="Paris", country_iso_code="FR")
    session.add(city)
    session.commit()

    # Vérification
    retrieved_city = session.query(City).filter_by(label="Paris").first()
    assert retrieved_city is not None
    assert retrieved_city.label == "Paris"


def test_update_patent(session):
    Test de mise à jour d'un brevet.
    patent = Patent(
        person_id=1,
        date_start="2024-01-01",
        city_label="Lyon",
    )
    session.add(patent)
    session.commit()

    # Mise à jour
    patent.date_start = "2025-01-01"
    session.commit()

    # Vérification
    updated_patent = session.query(Patent).filter_by(city_label="Lyon").first()
    assert updated_patent.date_start == "2025-01-01"


def test_delete_address_with_relations(session):
    Test de suppression d'une adresse avec des relations.
    city = City(label="Marseille", country_iso_code="FR")
    address = Address(label="Rue de Paris", city=city)
    session.add(city)
    session.add(address)
    session.commit()

    # Vérification avant suppression
    assert session.query(Address).count() == 1
    assert session.query(City).count() == 1

    # Suppression de l'adresse
    session.delete(address)
    session.commit()

    # Vérification après suppression
    assert session.query(Address).count() == 0
    assert session.query(City).count() == 1  # La ville ne doit pas être supprimée


def test_cascade_delete_person_with_patents(session):
    Test de suppression en cascade d'une personne avec ses brevets.
    person = Person(lastname="Martin", firstnames="Sophie")
    patent1 = Patent(person=person, date_start="2023-01-01")
    patent2 = Patent(person=person, date_start="2024-01-01")

    session.add(person)
    session.add(patent1)
    session.add(patent2)
    session.commit()

    # Vérification avant suppression
    assert session.query(Person).count() == 1
    assert session.query(Patent).count() == 2

    # Suppression de la personne
    session.delete(person)
    session.commit()

    # Vérification après suppression
    assert session.query(Person).count() == 0
    assert session.query(Patent).count() == 0  # Les brevets doivent être supprimés


def test_image_constraints(session):
    Test de la contrainte d'unicité de l'image épinglée.
    patent = Patent(person_id=1)
    image1 = Image(label="Image 1")
    image2 = Image(label="Image 2")
    patent_image1 = PatentHasImages(patent=patent, image=image1, is_pinned=True)
    patent_image2 = PatentHasImages(patent=patent, image=image2, is_pinned=True)

    session.add(patent)
    session.add(image1)
    session.add(image2)
    session.add(patent_image1)

    session.commit()

    # Ajout d'une deuxième image épinglée (doit lever une exception)
    with pytest.raises(ValueError):
        session.add(patent_image2)
        session.commit()
"""