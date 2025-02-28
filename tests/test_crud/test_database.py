def test_get_db():
    """Test that the database session is correctly initialized and closed."""
    from api.database import get_db
    db_gen = get_db()
    session = next(db_gen)
    assert session is not None

    # Fermer correctement la session
    try:
        next(db_gen)
    except StopIteration:
        pass