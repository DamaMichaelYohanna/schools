from .models import SchoolSetting


def school_settings(request):
    """
    Makes current school details, active session, active term, and branding
    available across all templates seamlessly.
    """
    setting = SchoolSetting.load()
    return {
        'school_setting': setting,
        'active_session': setting.current_session,
        'active_term': setting.current_term,
    }
