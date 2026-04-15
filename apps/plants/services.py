from apps.plants.models import ControlConfig


def get_or_create_control_config():
    obj, _ = ControlConfig.objects.get_or_create(
        pk=1,
        defaults={
            "auto_mode": True,
            "manual_override": False,
            "motor_enabled": True,
        },
    )
    return obj