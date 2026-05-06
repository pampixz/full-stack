from sqlalchemy.orm import Session
from backend.app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, token: str, user_id: int) -> RefreshToken:
        refresh = RefreshToken(
            token=token,
            user_id=user_id,
            is_revoked=False
        )
        self.db.add(refresh)
        self.db.commit()
        self.db.refresh(refresh)
        return refresh

    def get_by_token(self, token: str) -> RefreshToken | None:
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token == token)
            .first()
        )

    def revoke(self, token: str) -> None:
        refresh = self.get_by_token(token)
        if refresh:
            refresh.is_revoked = True
            self.db.commit()

    def revoke_all_for_user(self, user_id: int) -> None:
        tokens = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id)
            .all()
        )
        for token in tokens:
            token.is_revoked = True
        self.db.commit()