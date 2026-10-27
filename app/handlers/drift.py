from app.constants import DriftStatus, UserRole


class DriftHandler:
    def __init__(self, drift, current_user_id):
        self.current_user_id = current_user_id
        self.data = self._parse(drift)

    @staticmethod
    def requester_or_gifter(drift, current_user_id):
        role = UserRole.GIFTER.value
        if drift.requester_id == current_user_id:
            role = UserRole.REQUESTER.value
        return role

    def _parse(self, drift):
        you_are = self.requester_or_gifter(drift, self.current_user_id)
        drift_status = DriftStatus.drift_status_map(drift.status, you_are)
        data = {
            "you_are": you_are,
            "drift_id": drift.id,
            "book_title": drift.book_title,
            "book_author": drift.book_author,
            "book_img": drift.book_img,
            "operator": drift.requester_nickname
            if you_are != UserRole.REQUESTER.value
            else drift.gifter_nickname,
            "date": drift.created_at.strftime("%Y-%m-%d"),
            "message": drift.message,
            "address": drift.address,
            "recipient_name": drift.recipient_name,
            "mobile": drift.mobile,
            "status": drift.status,
            "status_str": drift_status,
        }
        return data


class DriftCollection:
    def __init__(self, drifts, current_user_id):
        self.data = []
        self._parse(drifts, current_user_id)

    def _parse(self, drifts, current_user_id):
        for drift in drifts:
            single = DriftHandler(drift, current_user_id)
            self.data.append(single.data)
