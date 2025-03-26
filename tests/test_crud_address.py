from api.models.models import (City,
                            Address,
                            Person,
                            Patent,
                            PatentHasAddresses,
                               BASE)
from tests.conftest import local_session

def test_patent_address_relationship():
    """Test that patents can be correctly linked to addresses."""
    with local_session as session:
        city = City(label="Marseille", country_iso_code="FR")
        address = Address(label="Port", city_label="Marseille", city=city)
        session.add_all([city, address])
        session.commit()
        person = Person(lastname="Inventeur", firstnames="Paul")
        session.add(person)
        session.commit()
        patent = Patent(person_id=person.id, date_start="2022-01-01")
        session.add(patent)
        session.commit()
        # Create a relationship between the patent and the address
        patent_address_relation = PatentHasAddresses(patent_id=patent.id, address_id=address.id)
        session.add(patent_address_relation)
        session.commit()
        # Verify that the relationship is correctly established
        linked_address = session.query(PatentHasAddresses).filter_by(patent_id=patent.id).first()
        assert linked_address is not None
        assert linked_address.address_id == address.id
