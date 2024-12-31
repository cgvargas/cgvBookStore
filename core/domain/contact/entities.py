"""Domain entities for the contact module."""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Contact:
    """Entity representing a contact message from users."""
    nome: str
    email: str
    assunto: str
    mensagem: str
    data: datetime = None

    def get_summary(self):
        """Returns a summary of the contact message"""
        return {
            'nome': self.nome,
            'email': self.email,
            'assunto': self.assunto,
            'data': self.data.strftime('%d/%m/%Y %H:%M') if self.data else '',
            'mensagem_preview': self.mensagem[:100] + '...' if len(self.mensagem) > 100 else self.mensagem
        }