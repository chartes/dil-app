import pytest
from api.models.models import (Person,
                            Patent,
                            Image,
                            PatentHasImages)

def test_image_constraints(session):
    """Ensure that a patent can only have one pinned image."""
    person = Person(lastname="Inventeur")
    session.add(person)
    session.commit()

    # check if person exists
    assert session.query(Person).filter(Person.id == person.id).one() is not None

    patent = Patent(person_id=person.id, date_start="2023-01-01")
    session.add(patent)
    session.commit()

    # check if patent exists
    assert session.query(Patent).filter(Patent.id == patent.id).one() is not None

    image1 = Image(label="Image 1")
    image2 = Image(label="Image 2")
    image3 = Image(label="Image 3")
    session.add_all([image1, image2, image3])
    session.commit()

    # check if images exist
    assert session.query(Image).filter(Image.id == image1.id).one() is not None
    assert session.query(Image).filter(Image.id == image2.id).one() is not None
    assert session.query(Image).filter(Image.id == image3.id).one() is not None


    patent_image1 = PatentHasImages(patent_id=patent.id, image_id=image1.id, is_pinned=True)
    session.add(patent_image1)
    session.commit()

    assert session.query(Person).filter(Person.id == person.id).one() is not None
    assert session.query(Patent).filter(Patent.id == patent.id).one() is not None
    assert session.query(Image).filter(Image.id == image1.id).one() is not None
    assert session.query(Image).filter(Image.id == image2.id).one() is not None
    assert session.query(PatentHasImages).filter(PatentHasImages.patent_id == patent.id).one() is not None



    patent_image2 = PatentHasImages(patent_id=patent.id, image_id=image2.id, is_pinned=True)
    session.add(patent_image2)
    session.commit()


    # check now if patent_image1 is not pinned and patent_image2 is pinned
    patent_image1_id = session.query(PatentHasImages).filter(PatentHasImages.image_id == image1.id).one().id
    patent_image2_id = session.query(PatentHasImages).filter(PatentHasImages.image_id == image2.id).one().id

    assert session.query(PatentHasImages).filter(PatentHasImages.id == patent_image1_id).one().is_pinned == False
    assert session.query(PatentHasImages).filter(PatentHasImages.id == patent_image2_id).one().is_pinned == True

    patent_image3 = PatentHasImages(patent_id=patent.id, image_id=image3.id, is_pinned=True)
    session.add(patent_image3)
    session.commit()

    # check now if patent_image1, patent_image2 are not pinned and patent_image3 is pinned
    patent_image3_id = session.query(PatentHasImages).filter(PatentHasImages.image_id == image3.id).one().id
    assert session.query(PatentHasImages).filter(PatentHasImages.id == patent_image1_id).one().is_pinned == False
    assert session.query(PatentHasImages).filter(PatentHasImages.id == patent_image2_id).one().is_pinned == False
    assert session.query(PatentHasImages).filter(PatentHasImages.id == patent_image3_id).one().is_pinned == True

def test_generate_img_name_with_extension():
    """Test the correct generation of an image name with a given file extension."""
    image = Image(_id_dil="img_12345678")

    # Valid case
    img_name = image._id_dil + image.generate_img_name("path/to/file.jpg")
    assert img_name == "img_12345678.jpg"

    # Invalid extensions should raise a ValueError
    invalid_extensions = ["pdf", "docx", "xml", "html"]
    for ext in invalid_extensions:
        with pytest.raises(ValueError, match="n'est pas autorisée"):
            image.generate_img_name(f"path/to/file.{ext}")
