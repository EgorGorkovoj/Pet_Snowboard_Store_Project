from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def hello_word():
    """Тест"""
    return {'info': 'Hello World!'}


if __name__ == '__main__':
    hello_word()
