import logging
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
user_id_var: ContextVar[str] = ContextVar("user_id", default="-")
document_id_var: ContextVar[str] = ContextVar("document_id", default="-")


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.user_id = user_id_var.get()
        record.document_id = document_id_var.get()
        return True


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s %(levelname)s %(name)s "
            "request_id=%(request_id)s user_id=%(user_id)s document_id=%(document_id)s "
            "%(message)s"
        ),
    )
    logging.getLogger().addFilter(ContextFilter())


def set_request_id(request_id: str):
    return request_id_var.set(request_id)


def reset_request_id(token) -> None:
    request_id_var.reset(token)


def set_user_id(user_id: str):
    return user_id_var.set(user_id)


def set_document_id(document_id: str):
    return document_id_var.set(document_id)


def reset_document_id(token) -> None:
    document_id_var.reset(token)
