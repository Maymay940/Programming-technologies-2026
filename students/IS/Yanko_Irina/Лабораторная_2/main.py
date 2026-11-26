
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from openai import APIConnectionError, APITimeoutError, APIStatusError
from database import Base, engine, get_db
from models import Book, LibraryRequest
from schemas import MessageInput, RequestOutput
from llm import extract_data, InvalidLLMResponse

app = FastAPI(
    title="Library Requests API",
    description="Обработка запросов читателей библиотеки с помощью локальной LLM",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

@app.post(
    "/library-requests",
    response_model=RequestOutput,
    status_code=status.HTTP_201_CREATED,
)
def create_library_request(
    payload: MessageInput,
    db: Session = Depends(get_db),
):
    try:
        data = extract_data(payload.message)

    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Превышено время ожидания ответа LLM",
        )
    except APIConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Не удалось подключиться к LM Studio",
        )
    except APIStatusError:
        raise HTTPException(
            status_code=503,
            detail="LM Studio вернул ошибку",
        )
    except InvalidLLMResponse:
        raise HTTPException(
            status_code=502,
            detail="LLM вернула некорректный JSON или структуру данных",
        )

    book_id = None
    match_status = "not_provided"

    if data.book_code is not None:
        normalized_code = data.book_code.strip().upper()

        book = db.scalar(
            select(Book).where(
                func.upper(func.trim(Book.code)) == normalized_code
            )
        )

        if book is not None:
            book_id = book.id
            match_status = "matched"
        else:
            match_status = "not_found"

    record = LibraryRequest(
        original_text=payload.message,
        **data.model_dump(),
        book_id=book_id,
        match_status=match_status,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record

@app.get(
    "/library-requests",
    response_model=list[RequestOutput],
)
def get_library_requests(
    db: Session = Depends(get_db),
):
    requests = db.scalars(
        select(LibraryRequest).order_by(
            LibraryRequest.id.desc()
        )
    ).all()

    return requests

@app.get(
    "/library-requests/{request_id}",
    response_model=RequestOutput,
)
def get_library_request(
    request_id: int,
    db: Session = Depends(get_db),
):
    record = db.get(LibraryRequest, request_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail="запрос не найден",
        )
    return record
