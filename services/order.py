from typing import Optional, List
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.db.models import QuerySet

from db.models import Order, Ticket, User, MovieSession


@transaction.atomic
def create_order(
    tickets: List[dict], username: str, date: Optional[str] = None
) -> Order:
    user = User.objects.get(username=username)

    created_at = parse_datetime(date) if date else None

    order = Order.objects.create(user=user)
    if created_at:
        Order.objects.filter(id=order.id).update(created_at=created_at)
        order.refresh_from_db()

    # Создаём все тикеты
    for ticket_data in tickets:
        movie_session = MovieSession.objects.get(
            id=ticket_data["movie_session"]
        )
        Ticket.objects.create(
            movie_session=movie_session,
            order=order,
            row=ticket_data["row"],
            seat=ticket_data["seat"],
        )

    return order


def get_orders(username: Optional[str] = None) -> QuerySet[Order]:
    queryset = (
        Order.objects.all()
        .select_related("user")
        .prefetch_related("tickets")
    )
    if username:
        queryset = queryset.filter(user__username=username)
    return queryset
