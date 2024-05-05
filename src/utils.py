def printing(dbmanager):
    priiv = {1: dbmanager.get_companies_and_vacancies_count,
             2: dbmanager.get_all_vacancies,
             3: dbmanager.get_avg_salary,
             4: dbmanager.get_vacancies_with_higher_salary,
             5: dbmanager.get_vacancies_with_keyword
             }
    print('Доступные режимы вывода и фильтрации  информации из базы данных')
    print()
    for a, b in priiv.items():
        ab = b.__doc__
        print(a, ab)

    while True:
        user_input = input('Выберите номер фильтрации, который Вас интересует: ')
        if user_input in ['1', '2', '3', '4', '5']:
            if user_input in '5':
                user_input_name = input('Введите параметр поиска: ')
                method = priiv[int(user_input)]
                result = method(user_input_name)
                for c in result:
                    print(*c)
                user_input_select = input('Для остановки нажмите n : ')
                if user_input_select in 'n':
                    break
                continue
            method = priiv[int(user_input)]
            result = method()
            for c in result:
                print(*c)
            user_input_select = input('Для остановки нажмите n : ')
            if user_input_select in 'n':
                break
            continue
        else:
            print('Пожалуйста, введите число от 1 до 5.')