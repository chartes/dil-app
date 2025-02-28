from api.models.models import (City,
                            Address,
                            Person,
                            Patent,
                            PatentHasAddresses,
                        PersonHasAddresses)

def test_add_adress_person(session):
    person = Person(lastname="TEST")
    session.add(person)
    session.commit()

    # retrieve id of the person
    person_id = person.id

    # create an address
    address = Address(city_label="26, rue de l'ENC")
    session.add(address)
    session.commit()

    # create another address
    address2 = Address(city_label="26, avenue de Marc")
    session.add(address2)
    session.commit()

    # retrieve id of the address
    address_id = address.id
    address2_id = address2.id

    # create a person address with bulk_save_objects for two addresses
    person_address = PersonHasAddresses(person_id=person_id, address_id=address_id)
    person_address2 = PersonHasAddresses(person_id=person_id, address_id=address2_id)

    session.add_all([person_address, person_address2])
    session.commit()

    # remove the person
    session.delete(person)
    session.commit()

    # est-ce que les adresses ne sont pas supprimées ?
    assert session.get(Address, address_id) is not None
    assert session.get(Address, address2_id) is not None

    # est-ce que les relations sont supprimées ?
    print(session.query(PersonHasAddresses).filter_by(person_id=person_id).count())
    assert session.query(PersonHasAddresses).filter_by(person_id=person_id).count() == 0