# core/domain/recommendations/contact.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime

@dataclass
class BookRecommendation:
    """Representa uma recomendação de livro"""
    livro_id: str
    titulo: str
    autor: str
    categoria: str
    score: Decimal
    imagem_url: Optional[str] = None

@dataclass
class UserPreference:
    """Representa as preferências do usuário"""
    usuario_id: int
    categorias_favoritas: Dict[str, int]  # categoria: contagem
    autores_favoritos: Dict[str, int]     # autor: contagem
    ultima_atualizacao: datetime