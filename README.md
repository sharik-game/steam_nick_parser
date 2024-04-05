# Steam nickname parser

## Task
This code make by this task:  
Описание:  
Написать программу для сбора аккаунтов в стим по ник нейму.
Вы пишите тут nickname “Тут ник” и вам высвечиваются все аккаунты с этим nickname 
По запросу “Тут ник”, всего 589 аккаунта, значит они должны быть собраны  

https://steamcommunity.com/search/users/#text=%D0%A2%D1%83%D1%82+%D0%BD%D0%B8%D0%BA  

Требуется сделать программу в которой можно написать любой nickname и получить выгрузку всех аккаунтов в виде экселя.  
- Столбец A: Ссылка на аккаунт
- Столбец B: Описание из аккаунта 
- Столбец C: Страна, город указанные в аккаунте 
- Столбец D: Имя указанное в аккаунте (Не nickname!)
Ещё 10 столбцов: в каждом по отдельности указаны все nickname данного пользователя. Их может быть от 1 до 10 


Функциональные требования:
1. Обеспечение отсутствия капчи при обработке большого объема данных по запросу пользователя, чтобы обеспечить бесперебойную работу системы.
2. Высокая скорость сбора и обработки информации.
3. Создание удобного интерфейса приложения, обеспечивающего удобство работы с помощью исполняемого файла (exe), что упростит процесс работы с приложением.

## Instalation
```poweshell
git clone https://github.com/sharik-game/steam_nick_parser.git
pip install -r requirements.txt
```

## Start
```poweshell
python main.py "Тут ник" test.xlsx
```
To get help: 
```powershell
python main.py -h
```

## How does it work?

steam_nickname_parser uses asyncio(create by default 4 coroutines for parse search and coroutines*2 for parse each user) for more performance and also use ProcessPoolExecutor for html parse.

## TODO:
2. Высокая скорость сбора и обработки информации.
3. Создание удобного интерфейса приложения, обеспечивающего удобство работы с помощью исполняемого файла (exe), что упростит процесс работы с приложением.

