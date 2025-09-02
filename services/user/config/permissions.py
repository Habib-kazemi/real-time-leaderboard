from enum import Enum


class Permission(str, Enum):
    """Enum for defining valid permissions in the system."""
    CAN_SUBMIT_SCORE = "can_submit_score"
    CAN_VIEW_LEADERBOARD = "can_view_leaderboard"
    CAN_VIEW_REPORT = "can_view_report"
    CAN_MANAGE_GAME = "can_manage_game"
    CAN_MANAGE_USER = "can_manage_user"
    CAN_MANAGE_LEADERBOARD = "can_manage_leaderboard"
    CAN_MANAGE_SCORE = "can_manage_score"


PERMISSIONS = {perm.value: perm.value for perm in Permission}
