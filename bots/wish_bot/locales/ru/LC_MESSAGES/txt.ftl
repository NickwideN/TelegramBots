# Описание бота
help-text =
    Привет! Я <b>Бот желаний</b>.

    В группе каждый может добавить желание. Участники видят общий анонимный список и могут взять желание на исполнение. Когда выполните — отправьте автору сообщение (анонимно)

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

    Здесь можно анонимно загадывать желания и исполнять желания других участников.

    Вас пригласили в группу, но ссылка указана неверно или уже недействительна.

    Попросите администратора отправить новую ссылку или нажмите кнопку «Начать» 👇

message-menu-no-group =
    Для работы с желаниями нужно состоять хотя бы в одной группе.

    Вы можете:
    • вступить в публичную группу;
    • создать свою группу;
    • получить ссылку-приглашение от администратора.

message-no-group =
    Вы не в группе. Откройте меню (/menu) и создайте группу или вступите в существующую.

message-joined-group = Вы вступили в группу «{ $name }».

message-start-in-group =
    Привет! Я <b>Бот Желаний</b> 💫

    Вы находитесь в группе <b>{ $groupName }</b>

message-joined-welcome =
    Привет! Я <b>Бот Желаний</b> 💫

    Добро пожаловать в группу <b>{ $groupName }</b>
    В этом боте каждый может анонимно загадать желание и исполнить чужое. Попробуй загадать первое желание
message-group-not-found = Группа не найдена. Проверьте ссылку.
message-did-not-understand = Упс, не понял тебя

# Группы
message-create-group-name = Введите название группы:
message-create-group-visibility = Выберите видимость группы:
message-create-group-expired = Сначала создайте группу заново через меню
message-group-created =
    Группа «{ $name }» создана.
    Отправьте ссылку в ваш чат, чтобы начать обмениваться желаниями:
    { $link }

message-current-group =
    Текущая группа: <b>{ $name }</b>
    { $visibility }

message-current-group-admin =
    Текущая группа: <b>{ $name }</b>
    { $visibility }

    Ссылка для приглашения:
    { $link }

visibility-public = Публичная — видна в списке публичных групп
visibility-private = Приватная — только по ссылке

message-invite-link = Ссылка приглашения:
message-no-public-groups = Публичных групп пока нет.
message-public-group-already-member = <b>{ $name }</b> — вы уже в этой группе

message-group-admin =
    <b>Управление группой «{ $name }»</b>
    { $visibility }
    { $link }

message-group-not-admin = Только администратор группы может менять настройки.
message-group-visibility-changed = Видимость группы обновлена.

message-group-members-header = <b>Участники текущей группы</b>
message-no-group-members = В группе нет участников.
member-role-admin = админ
message-groups-select = <b>Группы</b>
message-share-group =
    Группа <b>{ $name }</b>

    { $link }
message-share-invite =
    Присоединяйтесь к группе «{ $name }» в Боте желаний:
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
message-wish-added = Желание добавлено.
message-wish-empty = Текст желания не может быть пустым.
message-no-open-wishes = Открытых желаний пока нет.
message-open-wishes-header = <b>Доступные желания</b>:

message-taken-for =
    Вы взяли желание. Выполняйте для: <b>{ $name }</b>{ $usernamePart }

message-cannot-take-own = Нельзя взять своё желание.
message-wish-already-taken = Это желание уже взяли.
message-wish-not-found = Желание не найдено.

message-no-my-wishes = У вас нет желаний в этой группе.
message-my-wishes-header = <b>Ваши желания:</b>
message-wish-deleted = Желание удалено.
message-not-wish-author = Удалить может только автор желания.
message-wish-deleted-for-taker =
    Автор удалил желание, которое вы взяли:
    <i>«{ $wishText }»</i>

message-no-taken-wishes = У вас нет взятых желаний в этой группе.
message-taken-wishes-header = <b>Ваши взятые желания:</b>
message-taken-wish-item =
    { $wishText }

    Для: <b>{ $name }</b>{ $usernamePart }

wish-status-open = открыто
wish-status-taken = взято
wish-status-completed = выполнено

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
message-already-subscribed = Вы уже подписаны на новые желания в этой группе.
message-not-subscribed = Вы не подписаны на новые желания в этой группе.
message-new-wish-notification =
    🔔 Новое желание в группе <b>{ $groupName }</b>:
    { $wishText }

# Кнопки
button-take = Взять
button-complete = Выполнено
button-my-taken = Мои взятые желания
button-delete = Удалить
button-public = Публичная
button-private = Приватная
button-toggle-public = Сделать публичной
button-toggle-private = Сделать приватной
button-show-invite = Показать ссылку
button-group-members = Участники группы
button-groups = Группы
button-share-group = Поделиться группой
button-share = Поделиться
button-start = 🚀 Начать
button-my-groups = 📂 Мои группы
button-language = 🌐 Язык
button-my-wishes = Мои желания
button-subscribe = Получать уведомления
button-unsubscribe = Отключить уведомления
button-archive = Архив выполненных желаний
button-back = Назад
button-block = Заблокировать
button-unblock = Разблокировать
button-language-russian = Русский
button-language-english = English
button-join-group = Вступить: { $name }
button-make-wish = Загадать желание
button-open-wishes = Доступные желания
button-public-groups = 🌍 Публичные группы
button-create-group = ➕ Создать группу

message-choose-language = Выберите язык:
message-language-selected = Язык изменён.

message-delete-db-warning =
    ⚠️ Будут удалены все ваши данные: профиль, группы (где вы админ), желания, подписки и участие в группах.

    Нажмите кнопку ниже для подтверждения.
message-delete-db-done = Все ваши данные удалены из базы.

button-delete-db = Удалить БД
