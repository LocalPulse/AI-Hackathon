import sys
from db_manager import create_connection, create_tables, add_user, log_activity, USERS_DB, ACTIVITY_DB

def main():
    # Create connections to both databases
    users_conn = create_connection(USERS_DB)
    activity_conn = create_connection(ACTIVITY_DB)

    if users_conn is not None and activity_conn is not None:
        create_tables(users_conn, activity_conn)
    else:
        print("Error! cannot create the database connections.")
        return

    print("--- Factory Activity Logger ---")
    
    while True:
        fio = input("Введите ФИО (или 'exit' для выхода): ").strip()
        if fio.lower() == 'exit':
            break
        if not fio:
            print("ФИО не может быть пустым.")
            continue

        # Use users_conn for user operations
        user_id = add_user(users_conn, fio)
        if user_id is None:
            print("Ошибка при добавлении/получении пользователя.")
            continue

        activity = input(f"Что делает {fio}? ").strip()
        if not activity:
            print("Описание деятельности не может быть пустым.")
            continue

        # Use activity_conn for logging, passing the user_id
        log_activity(activity_conn, user_id, activity)
        print("Запись успешно добавлена!\n")

    users_conn.close()
    activity_conn.close()
    print("Программа завершена.")

if __name__ == '__main__':
    main()
