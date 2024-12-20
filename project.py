import os
import csv


class PriceMachine():
    '''
    Класс для обработки и анализа данных о ценах товаров.
    Позволяет загружать цены товаров из файлов, извлекать информацию о весе,
    цене за килограмм и экспортировать результаты в HTML.
    '''

    def __init__(self):
        '''
        Инициализация объекта PriceMachine.
        Создает пустой список для данных и строку для результатов.
        '''
        self.data = []  # Список для хранения данных о товаре
        self.result = ''  # Результаты для экспорта в HTML
        self.name_length = 0  # Длина для отступа (не используется в коде, можно удалить)

    def load_prices(self, directory_path):
        '''
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт

            Допустимые названия для столбца с ценой:
                розница
                цена

            Допустимые названия для столбца с весом (в кг.):
                вес
                масса
                фасовка
        '''
        valid_files = []  # Список для хранения валидных файлов
        # Проходим по всем файлам в указанной директории и подкаталогах
        for root, _, files in os.walk(directory_path):
            for file in files:
                # Ищем файлы, содержащие слово "price" в названии
                if 'price' in file.lower():
                    valid_files.append(os.path.join(root, file))

        # Обрабатываем каждый найденный файл
        for file_path in valid_files:
            try:
                # Чтение файла в зависимости от его расширения
                if file_path.endswith('.csv'):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)  # Чтение CSV с заголовками
                        headers = reader.fieldnames  # Получаем заголовки столбцов
                        product_idx, price_idx, weight_idx = self._search_product_price_weight(headers)

                        if product_idx is not None and price_idx is not None:
                            for row in reader:
                                # Извлекаем данные из строки файла
                                product = row[headers[product_idx]]
                                price = row[headers[price_idx]]
                                weight = row[headers[weight_idx]] if weight_idx is not None else None

                                # Обработка веса (преобразуем в кг)
                                weight_kg = None
                                if weight:
                                    try:
                                        weight_kg = float(weight)  # Пытаемся преобразовать вес в кг
                                    except ValueError:
                                        pass

                                # Вычисление цены за килограмм
                                price_per_kg = None
                                if weight_kg:
                                    price_per_kg = float(price) / weight_kg if weight_kg > 0 else None

                                # Добавление данных в список
                                self.data.append({
                                    'product': product,
                                    'price': price,
                                    'weight': weight_kg,  # Храним вес в кг
                                    'file': os.path.basename(file_path),  # Имя файла
                                    'price_per_kg': price_per_kg  # Цена за килограмм
                                })
                else:
                    continue
            except Exception as e:
                print(f"Ошибка при обработке файла {file_path}: {e}")

        # Сортировка данных по цене за килограмм (по возрастанию)
        self.data = sorted(self.data, key=lambda x: x['price_per_kg'] if x['price_per_kg'] else float('inf'))

    def _search_product_price_weight(self, headers):
        '''
            Возвращает индексы столбцов, соответствующие названию товара, цене и весу.
            Если столбец не найден, возвращает None.
        '''
        # Ключевые слова для поиска столбцов
        product_keywords = ['товар', 'название', 'наименование', 'продукт']
        price_keywords = ['розница', 'цена']
        weight_keywords = ['вес', 'масса', 'фасовка']

        # Индексы столбцов
        product_idx = None
        price_idx = None
        weight_idx = None

        # Определяем, в каких столбцах находятся данные
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if any(keyword in header_lower for keyword in product_keywords):
                product_idx = i
            if any(keyword in header_lower for keyword in price_keywords):
                price_idx = i
            if any(keyword in header_lower for keyword in weight_keywords):
                weight_idx = i

        return product_idx, price_idx, weight_idx

    def export_to_html(self, fname='output.html'):
        '''
            Экспортирует данные в HTML файл.
            Формирует таблицу с данными: номер, название, цена, вес, файл и цена за кг.
        '''
        # Сортируем данные по цене за килограмм (по возрастанию)
        sorted_data = sorted(self.data, key=lambda x: x['price_per_kg'] if x['price_per_kg'] else float('inf'))

        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table border="1" style="width:100%; text-align:left; border-collapse: collapse;">
                <tr>
                    <th>Номер</th>
                    <th>Наименование</th>
                    <th>Цена</th>
                    <th>Вес</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''

        # Формируем строки таблицы для каждого товара
        for idx, item in enumerate(sorted_data, start=1):
            price_per_kg = item['price_per_kg']
            # Форматируем цену за килограмм с двумя знаками после запятой
            price_per_kg_formatted = f"{price_per_kg:.2f}" if price_per_kg else 'N/A'
            result += f'''
                <tr>
                    <td>{idx}</td>
                    <td>{item['product']}</td>
                    <td>{item['price']}</td>
                    <td>{item['weight']}</td>
                    <td>{item['file']}</td>
                    <td>{price_per_kg_formatted}</td>
                </tr>
            '''

        result += '''
            </table>
        </body>
        </html>
        '''

        # Записываем результат в файл
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(result)

        print(f"Данные успешно экспортированы в {fname}")

    def find_text(self, text):
        '''
            Поиск текста в данных, исключая наименование из результатов.
            Возвращает результаты, отсортированные по цене за килограмм.
        '''
        # Фильтруем данные, исключая наименование и ищем совпадения с текстом
        results = [item for item in self.data if
                   text.lower() in str(item['product']).lower() and 'наименование' not in item['product'].lower()]

        # Сортировка результатов по цене за килограмм
        results = sorted(results, key=lambda x: x['price_per_kg'] if x['price_per_kg'] else float('inf'))

        return results


# Пример использования
pm = PriceMachine()

# Запрашиваем путь к каталогу с файлами
catalog_path = input("Введите путь к каталогу: ").strip()
pm.load_prices(catalog_path)

# Основной цикл для поиска
while True:
    query = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
    if query.lower() == 'exit':
        print("Работа завершена.")
        break

    # Выводим результаты поиска
    results = pm.find_text(query)
    if results:
        print(f"{'№':<5}{'Наименование':<40}{'Цена':<10}{'Вес':<10}{'Файл':<15}{'Цена за кг.':<10}")
        for idx, item in enumerate(results, start=1):
            print(
                f"{idx:<5}{item['product']:<40}{item['price']:<10}{item['weight']:<10}{item['file']:<15}{item['price_per_kg'] if item['price_per_kg'] else 'N/A':<10}")
    else:
        print("Совпадений не найдено.")

# Экспортируем данные в HTML
pm.export_to_html()
print('Данные сохранены в HTML файл.')
