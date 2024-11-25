# test_api.py
import requests
from decouple import config


def test_google_books_api():
    api_key = config('GOOGLE_BOOKS_API_KEY')
    test_query = 'Harry Potter'
    url = 'https://www.googleapis.com/books/v1/volumes'

    params = {
        'q': test_query,
        'key': api_key
    }

    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            total_items = data.get('totalItems', 0)
            print(f"Total de itens encontrados: {total_items}")

            if 'items' in data:
                first_book = data['items'][0]
                print("\nPrimeiro livro encontrado:")
                print(f"Título: {first_book['volumeInfo'].get('title')}")
                print(f"Autor(es): {', '.join(first_book['volumeInfo'].get('authors', []))}")
            else:
                print("Nenhum livro encontrado")

        elif response.status_code == 400:
            print("Erro na requisição: Verifique os parâmetros")
        elif response.status_code == 403:
            print("Erro de autorização: API Key inválida ou com restrições")

        print("\nResponse completa:")
        print(response.text[:500])  # Primeiros 500 caracteres da resposta

    except Exception as e:
        print(f"Erro ao fazer requisição: {str(e)}")


if __name__ == "__main__":
    test_google_books_api()