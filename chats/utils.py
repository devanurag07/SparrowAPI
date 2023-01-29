# Conversation
def get_conv_messages(conv, user):
    if (hasattr(conv, "deleted")):

        if user == conv.deleted.user:
            deleted_at = conv.deleted.deleted_at
            return conv.messages.filter(created_at__gt=deleted_at)
        return conv.messages.all()
    else:
        return conv.messages.all()
