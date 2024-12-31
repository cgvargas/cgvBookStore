from datetime import datetime
import logging
from core.infrastructure.persistence.django.models.contact import Contact as ContactModel
from core.domain.contact.entities import Contact as ContactEntity
from ..base import BaseRepository

logger = logging.getLogger(__name__)


class ContactRepository(BaseRepository[ContactModel]):
    def __init__(self):
        super().__init__(ContactModel)

    def save_contact(self, contact_data):
        """
        Salva um novo contato

        Args:
            contact_data: Dados do contato

        Returns:
            Contact: O contato salvo
        """
        try:
            logger.info(f"Tentando salvar contato com dados: {contact_data}")

            # Certifica que temos todos os campos necessários
            contact_data = {
                'nome': contact_data.get('nome'),
                'email': contact_data.get('email'),
                'assunto': contact_data.get('assunto'),
                'mensagem': contact_data.get('mensagem')
            }

            contact = self.create(**contact_data)
            logger.info(f"Contato salvo com sucesso: {contact}")

            return ContactEntity(
                nome=contact.nome,
                email=contact.email,
                assunto=contact.assunto,
                mensagem=contact.mensagem,
                data=contact.data
            )
        except Exception as e:
            logger.error(f"Erro ao salvar contato: {str(e)}")
            raise