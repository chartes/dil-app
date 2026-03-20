# -*- coding: utf-8 -*-

"""loaders.py

Loaders for the admin views.
"""

from typing import Tuple, Union, Type
from flask_admin.model.ajax import DEFAULT_PAGE_SIZE
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from sqlalchemy.orm import Session


class GenericAjaxModelLoader(QueryAjaxModelLoader):
    """Generic Ajax model loader for Flask-Admin with a customizable search field."""

    def __init__(
        self,
        name: object,
        session: Session,
        model: Type,
        search_field: str = "label",
        **kwargs: object,
    ) -> None:
        """
        Generic loader Ajax with custom search field.

        :param name: Ajax field name
        :type name: str
        :param session: SQLAlchemy session
        :type session: Session
        :param model: SQLAlchemy model to query
        :type model: Type
        :param search_field: Field to search on
        :type search_field: str
        :param kwargs: Additional parameters
        :type kwargs: dict
        """
        super().__init__(name, session, model, fields=[search_field], **kwargs)
        self.search_field = search_field
        self.model = model
        self.session = session

    def format(self, model: Type) -> Union[None, Tuple[int, str]]:
        """Return a tuple with the ID and the representation of the model.

        :param model: The model instance to format.
        :type model: Type
        :return: A tuple containing the model's ID and its string representation, or None if
                    the model is None.
        :rtype: Union[None, Tuple[int, str]]
        """
        if model is None:
            return None
        return model.id, repr(model)

    def get_one(self, pk: int) -> Type:
        """Retrieve a model by its primary key.

        :param pk: The primary key of the model to retrieve.
        :type pk: int
        :return: The model instance corresponding to the given primary key, or None if not found
        :rtype: Type
        """
        return self.session.query(self.model).get(pk)

    def get_list(self, query: str, offset: int = 0, limit: int = DEFAULT_PAGE_SIZE):
        """Efficiently retrieve a list of models based on a query.

        :param query: The search term to filter the models by.
        :type query: str
        :param offset: The number of records to skip before starting to return results, defaults to
                    0
        :type offset: int, optional
        :param limit: The maximum number of records to return, defaults to DEFAULT_PAGE_SIZE
        :type limit: int, optional
        :return: A list of model instances that match the search query, limited by the offset
                    and limit parameters.
        :rtype: list[Type]
        """
        search_term = query.strip().lower()
        return (
            self.session.query(self.model)
            .filter(getattr(self.model, self.search_field).ilike(f"%{search_term}%"))
            .offset(offset)
            .limit(limit)
            .all()
        )
