import datetime as dt


def year(request):
    """Добавляет в контекст переменную с текущим годом."""
    return {
        'year': int(dt.datetime.now().strftime('%Y')),
    }
