from api.models.models import (City,
                            Address)
from tests.conftest import local_session

def test_create_city():
    """Test the creation of a city and verify data persistence."""
    with local_session as session:
        city = City(label="Paris", country_iso_code="FR")
        session.add(city)
        session.commit()

        retrieved_city = session.query(City).filter_by(label="Paris").first()
        assert retrieved_city is not None
        assert retrieved_city.label == "Paris"

def test_city_address_relationship():
    """Verify that a city can have multiple addresses associated with it."""
    with local_session as session:
        city = City(label="Lyon", country_iso_code="FR")
        address1 = Address(label="Place Bellecour", city_label="Lyon", city=city)
        address2 = Address(label="Rue de la République", city_label="Lyon", city=city)

        session.add_all([city, address1, address2])
        session.commit()

        assert len(city.addresses) == 2

def test_insee_code_uniqueness():
    """Verify the uniqueness constraint on the INSEE code of cities."""
    with local_session as session:
        city1 = City(label="Paris", insee_fr_code="75056")
        city2 = City(label="Lyon", insee_fr_code="69123")
        session.add_all([city1, city2])
        session.commit()

        assert session.query(City).filter_by(insee_fr_code="75056").count() == 1
        assert session.query(City).filter_by(insee_fr_code="69123").count() == 1
