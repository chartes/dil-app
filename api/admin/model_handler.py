from typing import Dict, Any, List
from sqlalchemy.orm import Session
from flask import request
from ..models.models import Patent, PatentHasImages, PatentHasRelations
from .validators import is_circular_person_patent_relation

class ModelChangeHandler:
    def __init__(self, session: Session, model: Any, form):
        self.session = session
        self.model = model
        self.model_id = model.id
        # form from FlaskForm model instance !
        self.form = form
        # form_data is a dictionary of lists from the request form ! (contains
        # form elements don't directly binded to FlaskForm)
        self.form_data = request.form.to_dict(flat=False)

    def on_model_change(self) -> None:
        """
        Placeholder for model-specific validation logic. Should be implemented in subclasses.
        for examples tests and validation of the form data.
        """
        pass

    def after_model_change(self, is_created: bool) -> None:
        """
        Placeholder for model-specific logic to handle updates after form submission.
        Should be implemented in subclasses.
        for examples for update model from form elements builded not directly in FlaskForm (=> JS scripts).
        """
        pass

    def prepare_grouped_data(self) -> None:
        """
        Placeholder for model-specific logic to prepare grouped form data from model form request.
        Should be implemented in subclasses.
        for examples to group form data related to pinned images and patent relations.
        """
        pass


class PrinterModelChangeHandler(ModelChangeHandler):
    def __init__(self, session: Session, model: Any, form):
        super().__init__(session, model, form)
        self.grouped_data = {}

    def on_model_change(self) -> None:
        """
        Validates the model change to ensure no conflicting printer relations.
        """
        self.prepare_grouped_data()

        for data in self.grouped_data.values():
            for printer_id, relation_type in zip(data.get("printer_relations", []), data.get("relation_types", [])):
                if printer_id.strip():
                    is_circular_person_patent_relation(self.model_id, int(printer_id), relation_type, data['patent_id'])

        #self.form.populate_obj(self.model)

    def after_model_change(self, is_created: bool) -> None:
        """
        Handles changes to the model after form submission.
        """
        self._update_pinned_images()
        self._update_patent_relations()

    def prepare_grouped_data(self) -> None:
        """
        Prepares and stores grouped form data related to pinned images and patent relations.
        """
        patents = self.session.query(Patent).filter_by(person_id=self.model_id).all()
        patents_id = [p.id for p in patents]
        self.grouped_data = self._group_form_data(self.form_data, patents_id)

    @staticmethod
    def _group_form_data(form_data: Dict[str, List[str]], patents_id: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Groups form data related to pinned images and patent relations by patent.

        Args:
            form_data (Dict[str, List[str]]): The submitted form data.
            patents_id (List[int]): List of valid patent IDs.

        Returns:
            Dict[int, Dict[str, Any]]: Grouped data mapping index to relevant fields.
        """
        grouped_data = {}
        for i, _ in enumerate(patents_id):
            try:
                patent_id = int(form_data.get(f'patents-{i}-id', [None])[0] or 0)
                if patent_id in patents_id:
                    grouped_data[i] = {
                        "patent_id": patent_id,
                        "pinned_images": form_data.get(f'patents-{i}-images-pinned-image', [None])[0],
                        "printer_relations": form_data.get(f'dynamic_printers[{i}][]', []),
                        "relation_types": form_data.get(f'dynamic_relation_types[{i}][]', [])
                    }
            except (ValueError, TypeError):
                continue
        return grouped_data

    def _update_pinned_images(self) -> None:
        """Updates the pinned images for the patents related to the given model.
        """
        self.session.commit()
        for values in self.grouped_data.values():
            if "pinned_images" in values and values["pinned_images"]:
                relations = self.session.query(PatentHasImages).filter_by(patent_id=values["patent_id"]).all()
                relation_to_pinned = self.session.query(PatentHasImages).filter_by(
                    patent_id=values["patent_id"], image_id=int(values["pinned_images"])
                ).first()
                # Unpin existing relations and pin the selected image
                if  len(relations) > 0:
                    if relation_to_pinned:
                        for relation in relations:
                            relation.is_pinned = False
                        relation_to_pinned.is_pinned = True
                        self.session.commit()
                    else:
                        # probably the first time the image is pinned
                        for relation in relations:
                            image_id = relation.image_id
                            if image_id == int(values["pinned_images"]):
                                relation.is_pinned = True
                            else:
                                relation.is_pinned = False
                        self.session.commit()
                else:
                    pass

    def _update_patent_relations(self) -> None:
        """Updates the relations between patents and printers based on the grouped data.
        """
        for data in self.grouped_data.values():
            if "printer_relations" in data and "relation_types" in data:
                self._process_patent_relations(data)

    def _process_patent_relations(self, data: Dict[str, Any]) -> None:
        """Processes the patent relations by creating or deleting them based on the grouped data.
        """
        relations = self.session.query(PatentHasRelations).filter_by(patent_id=data["patent_id"]).all()
        relations_id = [r.id for r in relations]
        final_relations_id = []

        for printer_id, relation_type in zip(data["printer_relations"], data["relation_types"]):
            if printer_id.strip():
                self._add_or_update_relation(int(printer_id), relation_type, data["patent_id"], final_relations_id)

        # Remove obsolete relations
        for rid in relations_id:
            if rid not in final_relations_id:
                relation_to_delete = self.session.query(PatentHasRelations).filter_by(id=rid).first()
                if relation_to_delete:
                    self.session.delete(relation_to_delete)
        self.session.commit()

    def _add_or_update_relation(self, printer_id: int, relation_type: str, patent_id: int, final_relations_id: List[int]) -> None:
        """Adds or updates a relation between a patent and a printer.
        """
        relation = self.session.query(PatentHasRelations).filter_by(
            patent_id=patent_id,
            person_id=self.model_id,
            person_related_id=printer_id,
            type=relation_type
        ).first()

        if not relation:
            new_relation = PatentHasRelations(
                person_id=self.model_id,
                person_related_id=printer_id,
                patent_id=patent_id,
                type=relation_type
            )
            self.session.add(new_relation)
            self.session.commit()
            final_relations_id.append(new_relation.id)
        else:
            final_relations_id.append(relation.id)
