import pytest
from sqlalchemy.exc import IntegrityError
from api.models.models import Patent
from tests.conftest import local_session

def test_foreign_key_violation():
    """Test that adding a patent with a non-existing person_id raises an IntegrityError."""
    with local_session as session:
        patent = Patent(person_id=9999, date_start="2023-01-01")  # Non-existing person ID

        with pytest.raises(IntegrityError):
            session.add(patent)
            session.commit()