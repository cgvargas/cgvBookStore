from datetime import datetime
from core.domain.contact.entities import Contact
from ..base import BaseRepository

class ContactRepository(BaseRepository[Contact]):
    def __init__(self):
        super().__init__(Contact)

    def create_contact(self, name: str, email: str, message: str) -> Contact:
        """Cria um novo contato"""
        return self.create(
            name=name,
            email=email,
            message=message,
            date_sent=datetime.now()
        )

    def get_unread_contacts(self):
        """Retorna contatos não lidos"""
        return list(self.filter(read=False).order_by('-date_sent'))

    def save_contact(self, contact_data):
        """
        Salva um novo contato

        Args:
            contact_data: Dados do contato

        Returns:
            Contact: O contato salvo
        """
        return self.model.objects.create(**contact_data)