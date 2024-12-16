# core/domain/recommendations/services.py
import re
from typing import List
from decimal import Decimal
from .entities import BookRecommendation, UserPreference


class RecommendationService:
    """Serviço de domínio para recomendações"""

    @staticmethod
    def normalizar_titulo(titulo: str) -> str:
        """Normaliza o título do livro para comparação"""
        if not titulo:
            return ""

        # Remove texto entre parênteses
        titulo = re.sub(r'\([^)]*\)', '', titulo)

        # Remove prefixos comuns de séries
        prefixos = [
            "crônicas de", "chronicles of", "saga", "série", "series",
            "vol.", "volume", "livro", "book", "parte", "part",
            "trilogia", "trilogy"
        ]

        titulo_lower = titulo.lower()
        for prefixo in prefixos:
            if titulo_lower.startswith(prefixo):
                titulo_lower = titulo_lower.replace(prefixo, "", 1)

        # Remove números e caracteres especiais
        titulo_clean = re.sub(r'[0-9#@$%^&*()_+\-=\[\]{};:"|<>?,.\/\\]', '', titulo_lower)

        # Remove palavras conectoras comuns
        conectores = ["de", "do", "da", "dos", "das", "the", "a", "an", "of"]
        palavras = titulo_clean.split()
        palavras = [p for p in palavras if p not in conectores]

        return " ".join(palavras).strip().strip("-— ")

    @staticmethod
    def normalizar_autor(autor: str) -> str:
        """Normaliza o nome do autor para comparação"""
        if not autor:
            return ""

        # Remove prefixos comuns
        prefixos = ["por", "by", "de"]
        autor_lower = autor.lower()
        for prefixo in prefixos:
            if autor_lower.startswith(prefixo):
                autor_lower = autor_lower.replace(prefixo, "", 1)

        # Separa os autores se houver múltiplos
        autores = re.split(r'[,&]', autor_lower)

        # Normaliza cada nome de autor
        autores_normalizados = []
        for nome in autores:
            # Remove caracteres especiais
            nome = re.sub(r'[^a-zA-Z\s]', '', nome)
            # Divide em palavras e ordena
            palavras = sorted(nome.split())
            # Junta novamente
            autores_normalizados.append(" ".join(palavras).strip())

        # Ordena os autores para garantir mesma ordem
        return ", ".join(sorted(autores_normalizados))

    def calcular_score(self, livro: dict, preferencias: UserPreference) -> Decimal:
        """Calcula o score de recomendação para um livro"""
        score = Decimal('1.0')

        # Aumenta score baseado em categorias favoritas
        if livro.get('categoria') and preferencias.categorias_favoritas:
            categoria_livro = livro['categoria'].lower()
            for cat, count in preferencias.categorias_favoritas.items():
                if cat.lower() in categoria_livro or categoria_livro in cat.lower():
                    score += Decimal('0.5') * Decimal(str(count))

        # Aumenta score baseado em autores favoritos
        if livro.get('autor') and preferencias.autores_favoritos:
            autor_livro = self.normalizar_autor(livro['autor'])
            for autor, count in preferencias.autores_favoritos.items():
                autor_norm = self.normalizar_autor(autor)
                if autor_norm in autor_livro or autor_livro in autor_norm:
                    score += Decimal('0.7') * Decimal(str(count))

        return score