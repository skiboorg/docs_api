from random import choices
import string

def create_random_string(digits=False, num=4):
    if not digits:
        random_string = ''.join(choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=num))
    else:
        random_string = ''.join(choices(string.digits, k=num))
    return random_string

def set_user_rating(id,value):
    """Обновление рейтинга техники при создании отзыва"""
    from .models import User

    user = User.objects.get(id=id)
    user.rate_times += 1
    user.rate_value += value
    user.rating = round(user.rate_value / user.rate_times)
    user.save()
    return
