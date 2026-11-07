"""Accounts: who owns, shares and receives files.

Sign-in is out of scope for now; this model only gives the rest of the domain
someone to point at (owner, granted_by, created_by).
"""

import uuid
from typing import Any, ClassVar

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager["User"]):
    def create_user(
        self, email: str, display_name: str, password: str | None = None, **extra: Any
    ) -> "User":
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email), display_name=display_name, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, display_name: str, password: str | None = None, **extra: Any
    ) -> "User":
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, display_name, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = ["display_name"]

    objects = UserManager()

    class Meta:
        ordering: ClassVar[list[str]] = ["email"]

    def __str__(self) -> str:
        return self.display_name
