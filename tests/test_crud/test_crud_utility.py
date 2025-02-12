from tests.conftest import session
from api.models.models import (Person,
                        Patent,
                        City,
                        Address,
                        Image,
                        PersonHasAddresses,
                        PatentHasAddresses,
                        PatentHasImages,
                        PatentHasRelations,
                        generate_random_uuid)

def check_id_dil_routine(session: object,
                         model: object,
                         prefix: str,
                         add: bool=True):
    """Check the generation of a unique _id_dil for a given model."""
    if add:
        session.add(model)
        session.commit()
        assert model._id_dil is not None
        assert model._id_dil.startswith(f"{prefix}_dil_")
        assert len(model._id_dil.split("_")[-1]) == 8
    else:
        assert model is not None
        assert model.startswith(f"{prefix}_dil_")
        assert len(model.split("_")[-1]) == 8

def test_generate_random_uuid():
    """Test the generation of a unique random UUID with the expected prefix and format."""
    uuid_str = generate_random_uuid(prefix="test_dil_")
    check_id_dil_routine(session, uuid_str, "test", add=False)


def test_if_each_unique_id_dil_is_created_for_tables(session):
    """Test the creation of unique _id_dil for each table."""
    # add a person
    person = Person(lastname="Dupont", firstnames="Jean", birth_date="1970-01-01")
    check_id_dil_routine(session, person, "person")
    # add city
    city = City(label="Paris")
    check_id_dil_routine(session, city, "city")
    # add address
    address = Address(city_label="26, rue de l'ENC")
    check_id_dil_routine(session, address, "address")
    # add patent
    patent = Patent(person_id=person.id,
                    city_label="Paris",
                    city_id=city.id,
                    date_start="1970-01-01",
                    date_end="1970-01-01",
                    references="<p>test</p>",
                    comment="test .... lorem ipsum ...")
    check_id_dil_routine(session, patent, "patent")
    # add image
    image = Image(
        label="test_image",
        reference_url="http://test.com",
        img_name="test.jpg",
        iiif_url="http://test.com/iiif",
    )
    check_id_dil_routine(session, image, "img")
    # add patent_has_addresses
    patent_has_addresses = PatentHasAddresses(patent_id=patent.id, address_id=address.id)
    check_id_dil_routine(session, patent_has_addresses, "patent_address")
    # add patent_has_images
    patent_has_images = PatentHasImages(patent_id=patent.id, image_id=image.id)
    check_id_dil_routine(session, patent_has_images, "patent_image")
    # add another person
    person2 = Person(lastname="Martin", firstnames="Jean", birth_date="1970-01-01")
    check_id_dil_routine(session, person2, "person")
    # add patent_has_relations
    patent_has_relations = PatentHasRelations(patent_id=patent.id,
                                              person_id=person.id,
                                              person_related_id=person2.id,
                                              type="PARTNER")
    check_id_dil_routine(session, patent_has_relations, "patent_relation")
    # add person_has_addresses
    person_has_addresses = PersonHasAddresses(person_id=person.id, address_id=address.id)
    check_id_dil_routine(session, person_has_addresses, "person_address")
