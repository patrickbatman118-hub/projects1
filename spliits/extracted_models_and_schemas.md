# Extracted Database Models & Pydantic Schemas

This document contains all SQLAlchemy Database ORM classes extracted from `app/models` and Pydantic schema classes extracted from `app/schemas`.

---

## Part 1: Database Models (`app/models`)

All models inherit from `Base` (`app.db.Base`).

### 1. `AuditLog`
- **File**: [audit_log.py](file:///home/nithin/projects/projects/spliits/app/models/audit_log.py#L11)
- **Table Name**: `audit_log`

```python
class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    jti: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str] = mapped_column(Text, nullable=False)
    resource_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'))

    actor = relationship("User", back_populates="audit_logs")
```

---

### 2. `revoked_tokens`
- **File**: [jwt.py](file:///home/nithin/projects/projects/spliits/app/models/jwt.py#L9)
- **Table Name**: `revoked_tokens`

```python
class revoked_tokens(Base):
    __tablename__ = 'revoked_tokens'

    jti: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.user_id', ondelete='CASCADE'), index=True)
    revoked_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    reason: Mapped[str] = mapped_column(Text, nullable=False)
```

---

### 3. `notifications`
- **File**: [notifications.py](file:///home/nithin/projects/projects/spliits/app/models/notifications.py#L8)
- **Table Name**: `notifications`

```python
class notifications(Base):
    __tablename__ = 'notifications'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    receiver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    pool_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('pools.pool_id', ondelete='CASCADE'))
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'))
```

---

### 4. `pool_members`
- **File**: [pool_members.py](file:///home/nithin/projects/projects/spliits/app/models/pool_members.py#L8)
- **Table Name**: `pool_members`

```python
class pool_members(Base):
    __tablename__ = 'pool_members'

    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    pool_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('pools.pool_id', ondelete='CASCADE'), index=True)
    user_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    host_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    status: Mapped[request_status] = mapped_column(Enum(request_status, values_callable=lambda enum: [e.value for e in enum], name='pool_status_enum'), nullable=False, server_default=request_status.REQUESTED.value)
    role: Mapped[pool_role] = mapped_column(Enum(pool_role, values_callable=lambda enum: [e.value for e in enum], name='pool_role_enum'), nullable=False, server_default=pool_role.NONE.value)
    joined_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text('now()'))

    __table_args__ = (
        UniqueConstraint('pool_id', 'user_id', name='unq_pool_user'),
    )
```

---

### 5. `pool`
- **File**: [pools.py](file:///home/nithin/projects/projects/spliits/app/models/pools.py#L13)
- **Table Name**: `pools`

```python
class pool(Base):
    __tablename__ = 'pools'

    pool_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)
    max_members: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    cost_per_member: Mapped[float] = mapped_column(Numeric(10,2), Computed("total_cost / max_members"), nullable=False)
    host_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=lambda: datetime.now(timezone.utc))
    
    host = relationship('User', back_populates='hosted_pools')

    __table_args__ = (
        CheckConstraint('total_cost > 0', name='chq_cost'),
        CheckConstraint('max_members > 0', name='chq_maxmembers')
    )
```

---

### 6. `User`
- **File**: [users.py](file:///home/nithin/projects/projects/spliits/app/models/users.py#L10)
- **Table Name**: `users`

```python
class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    pfp: Mapped[str] = mapped_column(String(250), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=lambda: datetime.now(timezone.utc))
    disabled: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    hosted_pools = relationship('pool', back_populates='host')
    audit_logs = relationship("AuditLog", back_populates="actor", passive_deletes=True)
```

---

## Part 2: Pydantic Schemas (`app/schemas`)

All schemas inherit from `pydantic.BaseModel`.

### 1. Miscellaneous Schemas (`app/schemas/micallenious.py`)
- **File**: [micallenious.py](file:///home/nithin/projects/projects/spliits/app/schemas/micallenious.py)

```python
class NotificationSchema(BaseModel):
    content: str
    sender_id: UUID
    receiver_id: UUID
    pool_id: UUID
    is_read: bool
    id: int

    class Config:
        from_attributes = True


class NotificationResponseSchema(BaseModel):
    unread_count: int
    notifications: List[NotificationSchema]
```

---

### 2. Pool Schemas (`app/schemas/pools.py`)
- **File**: [pools.py](file:///home/nithin/projects/projects/spliits/app/schemas/pools.py)

```python
class pool(BaseModel):
    title: str
    description: str
    total_cost: float = Field(gt=0)
    max_members: int = Field(gte=2)
    category: PoolCategory


class UserResponsePool(BaseModel):
    name: str
    email: str
    pfp: str
    role: str


class PoolResponse(BaseModel):
    title: str
    description: str
    total_cost: float
    max_members: int
    category: PoolCategory
    is_active: bool
    people: UserResponsePool

    class Config:
        from_attributes = True


class updatepool(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    total_cost: Optional[float] = None
    max_members: Optional[int] = None
```

---

### 3. User Schemas (`app/schemas/users.py`)
- **File**: [users.py](file:///home/nithin/projects/projects/spliits/app/schemas/users.py)

```python
class user(BaseModel):
    name: str
    email: EmailStr
    pfp: str
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)
    
    @model_validator(mode='after')
    def check_pass_match(self):
        if self.password == self.confirm_password:
            return self
        else:
            raise ValueError('Password does not match')


class UserResponse(BaseModel):
    name: str
    email: EmailStr
    pfp: str
    hosted_pools: list[pool] = []

    class Config:
        from_attributes = True


class userupdate(BaseModel):
    name: Optional[str] = None
    pfp: Optional[str] = None
```
