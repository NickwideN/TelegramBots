# Bot description
help-text =
    Hi! I'm the <b>Wish Bot</b>.

    In a group, anyone can add a wish. Members see an anonymous list and can take a wish to fulfill. When done, send the author a message (anonymously)

    To open the menu, tap /menu

message-welcome =
    👋 Hi! I'm the <b>Wish Bot</b> ✨

    Here you can anonymously make wishes and fulfill wishes for other members.

    To get started, tap the «Start» button 👇

message-welcome-invite =
    👋 Hi! I'm the <b>Wish Bot</b> ✨

    You've been invited to group <b>{ $groupName }</b>.

    Here you can anonymously make wishes and fulfill wishes for other members.

    To continue, tap the «Start» button 👇

message-welcome-invite-invalid =
    👋 Hi! I'm the <b>Wish Bot</b> ✨

    Here you can anonymously make wishes and fulfill wishes for other members.

    You were invited to a group, but the link is incorrect or no longer valid.

    Ask the administrator for a new link or tap the «Start» button 👇

message-menu-no-group =
    To work with wishes, you need to be a member of at least one group.

    You can:
    • join a public group;
    • create your own group;
    • get an invite link from an administrator.

message-no-group =
    You are not in a group. Open the menu (/menu) and create a group or join an existing one.

message-joined-group = You joined group «{ $name }».

message-menu-group-admin =
    Group: <b>{ $groupName }</b>

    👑 Your role: Administrator

    Members: { $memberCount }

message-menu-group-member =
    Group: <b>{ $groupName }</b>

message-joined-welcome =
    Hi! I'm the <b>Wish Bot</b> 💫

    Welcome to group <b>{ $groupName }</b>
    In this bot, everyone can anonymously make a wish and fulfill someone else's. Try making your first wish!
message-group-not-found = Group not found. Check the link.
message-did-not-understand = Oops, I didn't understand you

# Groups
message-create-group-name = Enter the group name:
message-create-group-visibility = Choose group visibility:
message-create-group-expired = Please create a group again via the menu
message-group-created =
    🎉 Group { $name } created.

    👑 You are the admin of this group.

    You're the only member for now. Invite others to start exchanging wishes.

    🔗 Invite link:

    <code>{ $link }</code>

message-current-group =
    Current group: <b>{ $name }</b>
    { $visibility }

message-current-group-admin =
    Current group: <b>{ $name }</b>
    { $visibility }

    Invite link:
    { $link }

visibility-public = Public — listed in public groups
visibility-private = Private — invite link only

message-invite-link = Invite link:
message-no-public-groups = No public groups yet.
message-public-group-already-member = <b>{ $name }</b> — you are already in this group

message-group-admin =
    <b>Manage group «{ $name }»</b>
    { $visibility }
    { $link }

message-group-not-admin = Only the group admin can change settings.
message-group-visibility-changed = Group visibility updated.

message-group-members-header = <b>Group members</b>
message-no-group-members = There are no members in the group.
member-role-admin = admin
message-groups-select = <b>Groups</b>
message-share-group =
    Group <b>{ $name }</b>

    { $link }
message-share-invite =
    Join group «{ $name }» in Wish Bot:
    { $link }
message-my-groups = <b>My groups</b>
message-no-my-groups = You are not a member of any group yet.
message-public-groups = <b>Public groups</b>
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

message-archive-title = <b>Wish archive</b>
message-archive-my-wishes-header = <b>My wishes</b> (completed by others):
message-archive-fulfilled-header = <b>Completed by me</b>:
message-archive-section-empty = — no entries
message-archive-my-item = • «{ $wishText }» — { $name }{ $usernamePart }, { $date }
message-archive-fulfilled-item = • «{ $wishText }» — for { $name }{ $usernamePart }, { $date }

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
button-my-taken = 🤝 My taken wishes
button-delete = Delete
button-public = Public
button-private = Private
button-toggle-public = Make public
button-toggle-private = Make private
button-show-invite = Show invite link
button-group-members = 👥 Group members (admin)
button-groups = 📂 Groups
button-share-group = 🔗 Share group
button-share-group-admin = 🔗 Share group (admin)
button-share = Share
button-start = 🚀 Start
button-my-groups = 📂 My groups
button-language = 🌐 Language
button-my-wishes = 📋 My wishes
button-subscribe = 🔔 Get notifications
button-unsubscribe = 🔕 Disable notifications
button-archive = ✅ Archive of completed wishes
button-back = Back
button-block = Block
button-unblock = Unblock
button-language-russian = Русский
button-language-english = English
button-join-group = Join: { $name }
button-make-wish = ✨ Make a wish
button-open-wishes = 🎁 Available wishes
button-public-groups = 🌍 Public groups
button-create-group = ➕ Create group

message-choose-language = Choose language:
message-language-selected = Language changed.

message-delete-db-warning =
    ⚠️ All your data will be deleted: profile, groups (where you are admin), wishes, subscriptions, and group memberships.

    Press the button below to confirm.
message-delete-db-done = All your data has been deleted from the database.

button-delete-db = Delete DB
