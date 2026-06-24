"""
Registry database. Uses SQLAlchemy Core so the exact same code runs
against local SQLite (zero-config default) or Postgres (set DATABASE_URL
in .env for production) -- no dual code paths, no raw SQL dialect drift.
"""

from datetime import datetime

from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, Boolean, ForeignKey,
)
from sqlalchemy.engine import Row
from sqlalchemy.pool import NullPool

from config import settings

metadata = MetaData()

media_records = Table(
    "media_records", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("certificate_id", String, unique=True, nullable=False),
    Column("file_name", String, nullable=False),
    Column("file_hash", String, unique=True, nullable=False),
    Column("signature", Text, nullable=False),
    Column("media_type", String),
    Column("owner_name", String),
    Column("owner_email", String),
    Column("created_at", String),
    Column("owner_key_id", String),
    Column("key_mode", String, default="server"),
    Column("public_key", Text),
    Column("org_id", String),
    Column("ai_probability", Integer),
    Column("review_status", String, default="clear"),  # clear | flagged | approved | rejected
)

verification_history = Table(
    "verification_history", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("certificate_id", String),
    Column("file_hash", String),
    Column("verification_status", String),
    Column("risk_score", Integer),
    Column("verified_at", String),
)

pending_registrations = Table(
    "pending_registrations", metadata,
    Column("certificate_id", String, primary_key=True),
    Column("file_name", String),
    Column("file_hash", String),
    Column("media_type", String),
    Column("secured_path", String),
    Column("owner_name", String),
    Column("owner_email", String),
    Column("actor_key_id", String),
    Column("extra_json", Text),
    Column("created_at", String),
)

api_keys = Table(
    "api_keys", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("key_id", String, unique=True, nullable=False),
    Column("key_hash", String, nullable=False),
    Column("user_name", String),
    Column("user_email", String),
    Column("public_key", Text),
    Column("key_mode", String),
    Column("org_id", String),
    Column("role", String, default="owner"),  # owner | admin | member | viewer
    Column("created_at", String),
    Column("revoked", Boolean, default=False),
)

custody_log = Table(
    "custody_log", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("certificate_id", String),
    Column("action", String),
    Column("actor_key_id", String),
    Column("actor_name", String),
    Column("detail", Text),
    Column("occurred_at", String),
)

review_queue = Table(
    "review_queue", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("certificate_id", String, unique=True),
    Column("ai_probability", Integer),
    Column("reason", String),
    Column("status", String, default="pending"),  # pending | approved | rejected
    Column("reviewed_by", String),
    Column("created_at", String),
    Column("reviewed_at", String),
)

organizations = Table(
    "organizations", metadata,
    Column("org_id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("webhook_url", String),
    Column("webhook_secret", String),
    Column("created_at", String),
)

org_members = Table(
    "org_members", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("org_id", String),
    Column("key_id", String),
    Column("role", String, default="member"),  # owner | admin | member | viewer
    Column("joined_at", String),
)


def _connect_args(url):
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def _engine_kwargs(url):
    """
    Supabase's transaction pooler (pgbouncer) closes idle connections
    aggressively and doesn't support server-side prepared statements the
    way SQLAlchemy's default pool assumes. Two fixes:
      - NullPool: don't pool connections on our side at all -- pgbouncer is
        already pooling for us, so double-pooling just means we hold onto
        connections pgbouncer has silently killed.
      - pool_pre_ping: for the SQLite/direct-Postgres case (NullPool isn't
        used there), verify a connection is alive before handing it out.
    """
    if url.startswith("sqlite"):
        return {"pool_pre_ping": True}
    if "pooler.supabase.com" in url or "pgbouncer" in url:
        return {"poolclass": NullPool}
    return {"pool_pre_ping": True, "pool_recycle": 300}


class DatabaseManager:

    def __init__(self, database_url=None):
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_engine(
            self.database_url,
            connect_args=_connect_args(self.database_url),
            **_engine_kwargs(self.database_url),
        )
        metadata.create_all(self.engine)

    def get_connection(self):
        return self.engine.connect()

    @staticmethod
    def _row_to_dict(row):
        if row is None:
            return None
        return dict(row._mapping) if isinstance(row, Row) else dict(row)

    # -----------------------
    # Media Records
    # -----------------------

    def add_media_record(self, certificate_id, file_name, file_hash,
                          signature, media_type, owner_name=None, owner_email=None,
                          owner_key_id=None, key_mode="server", public_key=None,
                          org_id=None, ai_probability=None, review_status="clear"):
        with self.engine.begin() as conn:
            conn.execute(media_records.insert().values(
                certificate_id=certificate_id, file_name=file_name, file_hash=file_hash,
                signature=signature, media_type=media_type, owner_name=owner_name,
                owner_email=owner_email, created_at=str(datetime.now()),
                owner_key_id=owner_key_id, key_mode=key_mode, public_key=public_key,
                org_id=org_id, ai_probability=ai_probability, review_status=review_status,
            ))

    def get_record_by_certificate(self, certificate_id):
        with self.get_connection() as conn:
            row = conn.execute(
                media_records.select().where(media_records.c.certificate_id == certificate_id)
            ).fetchone()
            return self._row_to_dict(row)

    def get_record_by_hash(self, file_hash):
        with self.get_connection() as conn:
            row = conn.execute(
                media_records.select().where(media_records.c.file_hash == file_hash)
            ).fetchone()
            return self._row_to_dict(row)

    def list_records_by_org(self, org_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                media_records.select().where(media_records.c.org_id == org_id)
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def list_records_by_key(self, key_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                media_records.select()
                .where(media_records.c.owner_key_id == key_id)
                .order_by(media_records.c.created_at.desc())
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]

    # -----------------------
    # Verification History
    # -----------------------

    def add_verification_record(self, certificate_id, file_hash, status, risk_score):
        with self.engine.begin() as conn:
            conn.execute(verification_history.insert().values(
                certificate_id=certificate_id, file_hash=file_hash,
                verification_status=status, risk_score=risk_score,
                verified_at=str(datetime.now()),
            ))

    def get_verification_history(self, certificate_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                verification_history.select()
                .where(verification_history.c.certificate_id == certificate_id)
                .order_by(verification_history.c.verified_at.desc())
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]

    # -----------------------
    # Pending registrations (two-step self-sign flow)
    # -----------------------

    def add_pending_registration(self, certificate_id, file_name, file_hash, media_type,
                                  secured_path, owner_name, owner_email, actor_key_id,
                                  extra_json=None):
        with self.engine.begin() as conn:
            conn.execute(pending_registrations.insert().values(
                certificate_id=certificate_id, file_name=file_name, file_hash=file_hash,
                media_type=media_type, secured_path=secured_path, owner_name=owner_name,
                owner_email=owner_email, actor_key_id=actor_key_id, extra_json=extra_json,
                created_at=str(datetime.now()),
            ))

    def get_pending_registration(self, certificate_id):
        with self.get_connection() as conn:
            row = conn.execute(
                pending_registrations.select().where(pending_registrations.c.certificate_id == certificate_id)
            ).fetchone()
            return self._row_to_dict(row)

    def delete_pending_registration(self, certificate_id):
        with self.engine.begin() as conn:
            conn.execute(
                pending_registrations.delete().where(pending_registrations.c.certificate_id == certificate_id)
            )

    # -----------------------
    # API keys
    # -----------------------

    def add_api_key(self, key_id, key_hash, user_name, user_email,
                     public_key=None, key_mode="server", org_id=None, role="owner"):
        with self.engine.begin() as conn:
            conn.execute(api_keys.insert().values(
                key_id=key_id, key_hash=key_hash, user_name=user_name, user_email=user_email,
                public_key=public_key, key_mode=key_mode, org_id=org_id, role=role,
                created_at=str(datetime.now()), revoked=False,
            ))

    def get_api_key(self, key_id):
        with self.get_connection() as conn:
            row = conn.execute(api_keys.select().where(api_keys.c.key_id == key_id)).fetchone()
            return self._row_to_dict(row)

    def get_api_key_by_hash(self, key_hash):
        with self.get_connection() as conn:
            row = conn.execute(api_keys.select().where(api_keys.c.key_hash == key_hash)).fetchone()
            return self._row_to_dict(row)

    def revoke_api_key(self, key_id):
        with self.engine.begin() as conn:
            conn.execute(api_keys.update().where(api_keys.c.key_id == key_id).values(revoked=True))

    def set_api_key_org(self, key_id, org_id, role="member"):
        with self.engine.begin() as conn:
            conn.execute(api_keys.update().where(api_keys.c.key_id == key_id).values(org_id=org_id, role=role))

    # -----------------------
    # Chain of custody
    # -----------------------

    def add_custody_entry(self, certificate_id, action, actor_key_id=None,
                           actor_name=None, detail=None):
        with self.engine.begin() as conn:
            conn.execute(custody_log.insert().values(
                certificate_id=certificate_id, action=action, actor_key_id=actor_key_id,
                actor_name=actor_name, detail=detail, occurred_at=str(datetime.now()),
            ))

    def get_custody_log(self, certificate_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                custody_log.select()
                .where(custody_log.c.certificate_id == certificate_id)
                .order_by(custody_log.c.occurred_at.asc())
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]

    # -----------------------
    # Review queue (AI-detection gate)
    # -----------------------

    def add_review_entry(self, certificate_id, ai_probability, reason):
        with self.engine.begin() as conn:
            conn.execute(review_queue.insert().values(
                certificate_id=certificate_id, ai_probability=ai_probability, reason=reason,
                status="pending", created_at=str(datetime.now()),
            ))

    def get_review_queue(self, status="pending"):
        with self.get_connection() as conn:
            q = review_queue.select()
            if status:
                q = q.where(review_queue.c.status == status)
            rows = conn.execute(q.order_by(review_queue.c.created_at.asc())).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def resolve_review_entry(self, certificate_id, status, reviewed_by):
        with self.engine.begin() as conn:
            conn.execute(review_queue.update().where(review_queue.c.certificate_id == certificate_id).values(
                status=status, reviewed_by=reviewed_by, reviewed_at=str(datetime.now()),
            ))
            conn.execute(media_records.update().where(media_records.c.certificate_id == certificate_id).values(
                review_status=status,
            ))

    # -----------------------
    # Organizations / RBAC
    # -----------------------

    def create_organization(self, org_id, name, webhook_url=None, webhook_secret=None):
        with self.engine.begin() as conn:
            conn.execute(organizations.insert().values(
                org_id=org_id, name=name, webhook_url=webhook_url, webhook_secret=webhook_secret,
                created_at=str(datetime.now()),
            ))

    def get_organization(self, org_id):
        with self.get_connection() as conn:
            row = conn.execute(organizations.select().where(organizations.c.org_id == org_id)).fetchone()
            return self._row_to_dict(row)

    def set_org_webhook(self, org_id, webhook_url, webhook_secret):
        with self.engine.begin() as conn:
            conn.execute(organizations.update().where(organizations.c.org_id == org_id).values(
                webhook_url=webhook_url, webhook_secret=webhook_secret,
            ))

    def add_org_member(self, org_id, key_id, role="member"):
        with self.engine.begin() as conn:
            conn.execute(org_members.insert().values(
                org_id=org_id, key_id=key_id, role=role, joined_at=str(datetime.now()),
            ))

    def get_org_members(self, org_id):
        with self.get_connection() as conn:
            rows = conn.execute(org_members.select().where(org_members.c.org_id == org_id)).fetchall()
            return [self._row_to_dict(r) for r in rows]
