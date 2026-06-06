# Описание бота
help-text =
    👋 Привет! Я <b>Бот Желаний</b> ✨
    
    В группе каждый может анонимно загадать желание. Участники видят общий список и могут взять желание на исполнение.
    
    Когда желание будет выполнено, автор получит анонимное сообщение.
    
    Чтобы открыть меню, нажмите /menu

message-welcome =
    👋 Привет! Я <b>Бот Желаний</b> ✨

    Здесь можно анонимно загадывать желания и исполнять желания других участников.

    Для начала нажмите кнопку «Начать» 👇

message-welcome-invite =
    👋 Привет! Я <b>Бот Желаний</b> ✨

    Вас пригласили в группу <b>{ $groupName }</b>.

    Здесь можно анонимно загадывать желания и исполнять желания других участников.

    Для продолжения нажмите кнопку «Начать» 👇

message-welcome-invite-invalid =
    👋 Привет! Я <b>Бот Желаний</b> ✨

    Ссылка-приглашение не сработала: она неверная или уже недействительна.
    
    Попросите администратора отправить новую ссылку или нажмите «Начать» 👇

message-menu-no-group =
    Для работы с желаниями нужно состоять хотя бы в одной группе.

    Вы можете:
    • вступить в публичную группу;
    • создать свою группу;
    • получить ссылку-приглашение от администратора.

message-no-group =
    Вы не в группе. Откройте меню (/menu) и создайте группу или вступите в существующую.

message-joined-group = Вы вступили в группу «{ $name }».

message-menu-group-admin =
    Группа: <b>{ $groupName }</b>

    👑 Ваша роль: Администратор

    Участников: { $memberCount }

message-menu-group-member =
    Группа: <b>{ $groupName }</b>

message-group-not-found = Группа не найдена. Проверьте ссылку.
message-did-not-understand = Упс, не понял тебя

# Группы
message-create-group-name = Введите название группы:
message-create-group-visibility = Выберите видимость группы:
message-create-group-expired = Создание группы прервано. Начните заново через меню
message-group-created =
    🎉 Группа { $name } создана.

    👑 Вы являетесь администратором этой группы.

    Пока в группе только вы. Пригласите участников, чтобы начать обмен желаниями.

    🔗 Ссылка-приглашение:

    <code>{ $link }</code>

visibility-public = Публичная — видна в списке публичных групп
visibility-private = Приватная — только по ссылке

message-invite-link = Ссылка приглашения:
message-no-public-groups = Публичных групп пока нет.

message-group-admin =
    <b>Управление группой «{ $name }»</b>
    { $visibility }
    { $link }

message-group-not-admin = Только администратор группы может менять настройки.
message-group-visibility-changed = Видимость группы обновлена.

message-group-members-title = Участники группы { $groupName }
message-group-members-admins-header = 👑 Админы:
message-group-members-members-header = 👥 Участники:
message-group-members-blocked-header = 🚫 Заблокированные:
message-group-members-admin-line = { $name } — админ
message-group-members-select-prompt = Выберите участника, чтобы изменить статус.
message-group-member-detail =
    <b>{ $name }</b>

    Роль: { $role }
    Статус: { $status }
    Загадано желаний: { $wishesCount }
    Мои желания исполнены другими: { $wishesCompletedByOthers }
    Сейчас на исполнении: { $takenWishesCount }
    Исполнено чужих желаний: { $fulfilledOthersCount }
message-no-group-members = В группе нет участников.
member-role-admin = админ
member-role-participant = участник
member-status-active = активен
member-status-blocked = заблокирован
message-groups-select = <b>Группы</b>
message-share-group =
    🔗 Приглашение в группу <b>{ $name }</b>

    Отправьте эту ссылку людям, которых хотите добавить в группу

    <code>{ $link }</code>

message-share-invite-public-body =
    🎁 Присоединяйся к группе желаний { $name }!

    Здесь участники анонимно загадывают желания и исполняют желания друг друга

message-share-invite-private-body =
    🎁 Приглашаю в группу желаний { $name }

    В группе можно анонимно загадывать желания и исполнять желания других участников

message-share-invite-public =
    { message-share-invite-public-body }

    Вступить:
    { $link }

message-share-invite-private =
    { message-share-invite-private-body }

    Ссылка для вступления:
    { $link }

message-my-groups = <b>Мои группы</b>
message-no-my-groups = Вы пока не состоите ни в одной группе.
message-public-groups = <b>Публичные группы</b>
message-member-blocked = Участник заблокирован.
message-member-unblocked = Участник разблокирован.
message-member-not-found = Участник не найден.
message-cannot-block-self = Нельзя заблокировать себя.
message-cannot-block-admin = Нельзя заблокировать администратора.
message-user-blocked =
    Администратор группы «{ $groupName }» заблокировал вас. Вы удалены из группы и не можете в неё войти, пока вас не разблокируют.
message-blocked-in-group = Вы заблокированы в группе «{ $name }» и не можете в неё вступить.

# Желания
message-add-wish-prompt = Напишите текст желания:
message-wish-added = 
    Желание добавлено ✨

    Теперь его увидят участники группы.

message-wish-empty = Текст желания не может быть пустым
message-no-open-wishes = Открытых желаний пока нет
message-open-wishes-header = <b>Доступные желания</b>:
message-open-wishes-take-prompt = Нажмите на желание, которое хотите взять:
message-taken-for =
    Вы взяли желание. Выполняйте для: <b>{ $name }</b>{ $usernamePart }

message-cannot-take-own = Нельзя взять своё желание.
message-wish-already-taken = Это желание уже взяли.
message-wish-not-found = Желание не найдено.

message-no-my-wishes = У вас нет желаний в этой группе.
message-my-wishes-title = <b>Ваши желания:</b>
message-my-wishes-delete-prompt = Нажмите на номер желания, которое хотите удалить:
message-wish-deleted = Желание удалено.
message-not-wish-author = Удалить может только автор желания.
message-wish-deleted-for-taker =
    Автор удалил желание, которое вы взяли:
    <i>«{ $wishText }»</i>

message-no-taken-wishes = У вас нет взятых желаний в этой группе.
message-taken-wishes-header = <b>Ваши взятые желания:</b>
message-taken-wishes-complete-prompt = Нажмите на желание, которое хотите отметить выполненным:
message-taken-wish-for =    Для: <b>{ $name }</b>{ $usernamePart }
message-taken-wish-item =
    { $wishText }

    Для: <b>{ $name }</b>{ $usernamePart }

message-complete-prompt = Напишите сообщение для автора желания (или отправьте /skip для стандартной фразы):
message-wish-completed-taker = Желание отмечено выполненным.
message-author-unreachable = Не удалось отправить сообщение автору (возможно, бот заблокирован). Желание всё равно отмечено выполненным.

message-wish-completed-author =
    🎁 Кто-то выполнил ваше желание:
    <i>«{ $wishText }»</i>

    { $message }

message-wish-completed-default = Ваше желание выполнено! 🎉

message-archive-title = <b>Архив желаний</b>
message-archive-my-wishes-header = <b>Мои желания</b> (выполненные другими):
message-archive-fulfilled-header = <b>Выполненные мной</b>:
message-archive-section-empty = — нет записей
message-archive-my-item = • «{ $wishText }» — { $name }{ $usernamePart }, { $date }
message-archive-fulfilled-item = • «{ $wishText }» — для { $name }{ $usernamePart }, { $date }

message-subscribed = Вы подписаны на новые желания в группе «{ $name }».
message-unsubscribed = Вы отписаны от новых желаний в группе «{ $name }».
message-new-wish-notification =
    🔔 Новое желание в группе <b>{ $groupName }</b>:
    { $wishText }

# Кнопки
button-take = Взять
button-complete = Выполнено
button-my-taken = 🤝 Мои взятые желания
button-public = Публичная
button-private = Приватная
button-toggle-public = Сделать публичной
button-toggle-private = Сделать приватной
button-show-invite = Показать ссылку
button-group-members = 👥 Участники группы 👑
button-groups = 📂 Группы
button-share-group = 🔗 Поделиться группой
button-share-group-admin = 🔗 Поделиться группой 👑
button-share = 📤 Поделиться
button-start = 🚀 Начать
button-my-groups = 📂 Мои группы
button-language = 🌐 Язык
button-my-wishes = 📋 Мои желания
button-subscribe = 🔕 Уведомления выключены
button-unsubscribe = 🔔 Уведомления включены
button-archive = ✅ Архив желаний
button-back = Назад
button-block = Заблокировать
button-unblock = Разблокировать
button-language-russian = Русский
button-language-english = English
button-make-wish = ✨ Загадать желание
button-open-wishes = 🎁 Доступные желания
button-public-groups = 🌍 Публичные группы
button-create-group = ➕ Создать группу

message-choose-language = Выберите язык:
message-language-selected = Язык изменён.

message-delete-db-warning =
    ⚠️ Будут удалены все ваши данные: профиль, группы (где вы админ), желания, подписки и участие в группах.

    Нажмите кнопку ниже для подтверждения.
message-delete-db-done = Все ваши данные удалены из базы.

button-delete-db = Удалить БД
