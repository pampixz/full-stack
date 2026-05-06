ROLE_PERMISSIONS = {
    "user": {
        "entries:read_own",
        "entries:create",
        "entries:update_own",
        "entries:delete_own",
        "meetings:read",
    },
    "admin": {
        "entries:read_own",
        "entries:create",
        "entries:update_own",
        "entries:delete_own",
        "meetings:read",
        "meetings:create",
        "users:manage_roles",
    },
}