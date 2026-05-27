# Bot description
help-text =
    Hi! I'm the <b>Wish Bot</b>.

    In a group, anyone can add a wish. Members see an anonymous list and can take a wish to fulfill. When done, send the author a message (anonymously).

    <b>Commands:</b>
    /group — current group
    /create_group — create a group
    /groups — public groups
    /group_admin — group settings (admin)
    /group_members — group members (admin)
    /group_blocked — blocked users (admin)
    /add_wish — add a wish
    /wishes — open wishes
    /my_wishes — my wishes
    /my_taken — my taken wishes
    /subscribe — notifications for new wishes in the group
    /unsubscribe — turn off notifications
    /language — language
    /help — this help

message-no-group =
    You are not in a group. Create one (/create_group) or join via link / list (/groups).

message-joined-group = You joined group «{ $name }».
message-group-not-found = Group not found. Check the link.

# Groups
message-create-group-name = Enter the group name:
message-create-group-visibility = Choose group visibility:
message-group-created =
    Group «{ $name }» created.
    Invite link:
    { $link }

message-current-group =
    Current group: <b>{ $name }</b>
    { $visibility }

message-current-group-admin =
    Current group: <b>{ $name }</b>
    { $visibility }

    Invite link:
    { $link }

visibility-public = Public — listed in /groups
visibility-private = Private — invite link only

message-invite-link = Invite link:
message-no-public-groups = No public groups yet.

message-group-admin =
    <b>Manage group «{ $name }»</b>
    { $visibility }
    { $link }

message-group-not-admin = Only the group admin can change settings.
message-group-visibility-changed = Group visibility updated.

message-group-members-header = <b>Group members</b>
message-group-blocked-header = <b>Blocked users</b>
message-no-group-members = There are no other members in the group.
message-no-blocked-members = No blocked users.
message-member-blocked = Member blocked.
message-member-unblocked = Member unblocked.
message-member-not-found = Member not found.
message-cannot-block-self = You cannot block yourself.
message-cannot-block-admin = You cannot block the administrator.
message-user-blocked =
    The administrator of group «{ $groupName }» has blocked you. You were removed and cannot join until unblocked.
message-blocked-in-group = You are blocked in group «{ $name }» and cannot join.

# Wishes
message-add-wish-prompt = Enter the wish text:
message-wish-added = Wish added.
message-wish-empty = Wish text cannot be empty.
message-no-open-wishes = No open wishes yet.
message-open-wishes-header = <b>Open wishes</b> (anonymous):

message-taken-for =
    You took this wish. Fulfill it for: <b>{ $name }</b>{ $usernamePart }

message-cannot-take-own = You cannot take your own wish.
message-wish-already-taken = This wish was already taken.
message-wish-not-found = Wish not found.

message-no-my-wishes = You have no wishes in this group.
message-my-wishes-header = <b>Your wishes:</b>
message-wish-deleted = Wish deleted.
message-not-wish-author = Only the wish author can delete it.
message-wish-deleted-for-taker =
    The author deleted a wish you had taken:
    <i>«{ $wishText }»</i>

message-no-taken-wishes = You have no taken wishes in this group.
message-taken-wishes-header = <b>Your taken wishes:</b>
message-taken-wish-item =
    { $wishText }

    For: <b>{ $name }</b>{ $usernamePart }

wish-status-open = open
wish-status-taken = taken
wish-status-completed = completed

message-complete-prompt = Write a message for the wish author (or send /skip for the default text):
message-wish-completed-taker = Wish marked as completed.
message-author-unreachable = Could not message the author (bot may be blocked). Wish is still marked completed.

message-wish-completed-author =
    🎁 Someone fulfilled your wish:
    <i>«{ $wishText }»</i>

    { $message }

message-wish-completed-default = Your wish has been fulfilled! 🎉

message-subscribed = You subscribed to new wishes in group «{ $name }».
message-unsubscribed = You unsubscribed from new wishes in group «{ $name }».
message-already-subscribed = You are already subscribed to new wishes in this group.
message-not-subscribed = You are not subscribed to new wishes in this group.
message-new-wish-notification =
    🔔 New wish in group <b>{ $groupName }</b>:
    { $wishText }

# Buttons
button-take = Take
button-complete = Done
button-my-taken = My taken wishes
button-delete = Delete
button-public = Public
button-private = Private
button-toggle-public = Make public
button-toggle-private = Make private
button-show-invite = Show invite link
button-group-members = Members
button-group-blocked = Blocked
button-block = Block
button-unblock = Unblock
button-language-russian = Русский
button-language-english = English
button-join-group = Join: { $name }

message-choose-language = Choose language:
message-language-selected = Language changed.
