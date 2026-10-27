from enum import Enum


class DriftStatus(Enum):
    """交易状态"""

    WAITING = "WAITING"
    SUCCESS = "SUCCESS"
    REJECT = "REJECT"
    REVOKE = "REVOKE"

    @classmethod
    def drift_status_map(cls, status, key):
        key_map = {
            cls.WAITING.value: {"requester": "等待对方邮寄", "gifter": "等待你邮寄"},
            cls.REJECT.value: {"requester": "对方已拒绝", "gifter": "你已拒绝"},
            cls.REVOKE.value: {"requester": "你已撤销", "gifter": "对方已撤销"},
            cls.SUCCESS.value: {
                "requester": "对方已邮寄",
                "gifter": "你已邮寄，交易完成",
            },
        }
        return key_map[status][key]


class UserRole(Enum):
    """用户角色"""

    REQUESTER = "requester"
    GIFTER = "gifter"
