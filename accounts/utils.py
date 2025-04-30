from profiles.models import UserProfile


def is_user_banned(user):
    try:
        return user.userprofile.is_banned
    except AttributeError:
        return False
    except (AttributeError, UserProfile.DoesNotExist):
        return False
