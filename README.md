# Эмулятор командной строки

Практическая работа по дисциплине «Конфигурационное управление», вариант 15.

Эмулятор оболочки UNIX-подобной ОС с графическим интерфейсом.
Написан на Python, интерфейс сделан на tkinter. Заголовок окна строится
из реальных данных ОС: `Эмулятор - [username@hostname]`.

## Структура проекта

```
src/
  main.py    запуск эмулятора
  gui.py     окно программы (tkinter)
  shell.py   разбор и выполнение команд
  vfs.py     виртуальная файловая система
tests/       модульные тесты
scripts/     скрипты ОС для проверки эмулятора
startup/     стартовые скрипты эмулятора
vfs/         примеры VFS в формате XML
run.sh       скрипт запуска
Makefile     цели run и test
```

## Параметры запуска

| Параметр | Описание |
|----------|----------|
| `--vfs ПУТЬ` | путь к физическому расположению VFS |
| `--script ПУТЬ` | путь к стартовому скрипту |

При запуске все параметры выводятся в консоль (отладочный вывод).
Внутри эмулятора их можно посмотреть командой `conf-dump`.

Стартовый скрипт представляет собой текстовый файл, каждая строка которого
является командой эмулятора. Пустые строки и строки, начинающиеся с `#`,
пропускаются. Команды скрипта и их вывод показываются в окне так,
как будто их ввел пользователь. Выполнение останавливается на первой
ошибке.

## Виртуальная файловая система

VFS загружается из XML-файла, указанного в `--vfs`, и полностью
хранится в памяти. Сам файл при работе эмулятора не изменяется.
Если параметр не задан, используется пустая VFS.

Формат файла:

```xml
<vfs name="example">
  <dir name="home">
    <file name="notes.txt">обычный текст</file>
    <file name="data.bin" encoding="base64">AAECAwQ=</file>
  </dir>
  <dir name="tmp" mode="777"/>
</vfs>
```

- `<vfs>` корневой элемент, атрибут `name` задает имя VFS;
- `<dir>` каталог, может содержать другие `<dir>` и `<file>`;
- `<file>` файл, его текст лежит внутри элемента;
- `encoding="base64"` для двоичных данных;
- `mode` права доступа в восьмеричном виде (по умолчанию 755 для
  каталогов и 644 для файлов).

Если файл не найден или имеет неверный формат, в окне выводится
сообщение об ошибке, например `vfs: file not found: vfs/a.xml`
или `vfs: invalid format: mismatched tag: line 5, column 2`.

Примеры в папке `vfs/`:

| Файл | Содержимое |
|------|------------|
| `minimal.xml` | минимальная VFS из одного файла |
| `files.xml` | несколько текстовых и двоичных файлов |
| `deep.xml` | каталоги и файлы с вложенностью больше 3 уровней |
| `broken.xml` | некорректный XML для проверки ошибок |

## Команды эмулятора

| Команда | Описание |
|---------|----------|
| `ls [-a] [-h] [-l] [путь]` | содержимое каталога или имя файла |
| `cd [путь]` | переход в каталог, без аргумента в корень `/` |
| `date [+формат]` | текущие дата и время |
| `tac файл...` | строки файлов в обратном порядке |
| `uname [-snrvma]` | информация о системе |
| `mkdir [-p] каталог...` | создание каталогов |
| `chmod режим путь...` | изменение прав доступа |
| `conf-dump` | параметры эмулятора в формате ключ=значение |
| `vfs-info` | имя VFS и хеш SHA-256 ее данных |
| `exit [код]` | закрывает эмулятор с указанным кодом (по умолчанию 0) |

Строка ввода разбивается на команду и аргументы по пробелам.
Пути могут быть абсолютными (`/home/user`) и относительными
(`docs`, `../etc`), поддерживаются `.` и `..`. В приглашении
показывается текущий каталог VFS.

Опции команд:

- `ls -a` показывает скрытые файлы, а также `.` и `..`;
- `ls -l` выводит права доступа, владельца и размер;
- `ls -h` вместе с `-l` выводит размер в читаемом виде, например
  `2.6K` вместо `2600`, без `-l` вывод не меняется;
- опции можно объединять: `ls -la`, `ls -lh`;
- `date +ФОРМАТ` выводит дату в формате strftime, например
  `date +%d.%m.%Y`;
- `uname -s` имя системы, `-n` имя узла, `-r` версия ядра,
  `-v` описание ядра, `-m` архитектура, `-a` все сразу. Без опций
  работает как `uname -s`. Данные берутся из реальной ОС;
- `mkdir -p` создает и все недостающие родительские каталоги,
  а для существующего каталога не выдает ошибку;
- `chmod` принимает права в восьмеричном виде (`chmod 755 файл`)
  и в символьном (`chmod u+x файл`, `chmod go-w файл`,
  `chmod a=r файл`, `chmod u=rwx,go=r каталог`).

Команды `mkdir` и `chmod` меняют VFS только в памяти, XML-файл
остается прежним. Поэтому `vfs-info` после изменений выводит тот
же хеш, а после перезапуска эмулятора VFS снова загружается из файла.

Сообщения об ошибках:

| Ситуация | Пример сообщения |
|----------|------------------|
| неизвестная команда | `hello: command not found` |
| нет файла или каталога | `cd: /nope: No such file or directory` |
| не каталог | `cd: /etc/passwd: Not a directory` |
| каталог вместо файла | `tac: /etc: Is a directory` |
| неизвестная опция | `ls: invalid option -- 'z'` |
| лишние аргументы | `cd: too many arguments` |
| нет аргумента | `tac: missing file operand` |
| каталог уже есть | `mkdir: cannot create directory '/etc': File exists` |
| неверные права | `chmod: invalid mode: '999'` |
| неверный аргумент | `exit: abc: numeric argument required` |

## Сборка и запуск

Нужен Python 3.8 или новее с модулем tkinter. Сторонние библиотеки
не используются, отдельная сборка не требуется.

Запуск эмулятора:

```
./run.sh
```

или

```
make run
```

Запуск с параметрами:

```
./run.sh --vfs vfs/minimal.xml --script startup/stage2.txt
```

Запуск тестов:

```
make test
```

То же без make:

```
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Скрипты ОС для проверки эмулятора:

| Скрипт | Что проверяет |
|--------|---------------|
| `scripts/test_params.sh` | параметры `--vfs` и `--script` |
| `scripts/test_bad_params.sh` | неверные параметры запуска |
| `scripts/test_script.sh` | пути к стартовому скрипту |
| `scripts/test_vfs_minimal.sh` | минимальную VFS |
| `scripts/test_vfs_files.sh` | VFS из нескольких файлов |
| `scripts/test_vfs_deep.sh` | VFS с несколькими уровнями вложенности |
| `scripts/test_vfs_errors.sh` | ошибки загрузки VFS |
| `scripts/test_stage4.sh` | команды этапа 4 |
| `scripts/test_stage5.sh` | команды этапа 5 |

Каждый скрипт по очереди открывает несколько окон эмулятора,
следующее окно открывается после закрытия предыдущего.

## Пример работы

Запуск `./run.sh --vfs vfs/deep.xml`:

```
user@host:/$ vfs-info
name: deep
sha256: 004ca3aa3798557d89b3ca0262f266fd1f109a7f8eb56bce0a12a57e6a6b2335
user@host:/$ ls
bin  etc  home  tmp
user@host:/$ ls -la /home/user
drwxr-xr-x user      0 .
drwxr-xr-x user      0 ..
-rw------- user     25 .profile
drwxr-xr-x user      0 docs
user@host:/$ ls -l /bin
-rwxr-xr-x user   2600 hello
user@host:/$ ls -lh /bin
-rwxr-xr-x user   2.6K hello
user@host:/$ cd /home/user/docs
user@host:/home/user/docs$ ls -l
-rw-r--r-- user     34 notes.txt
drwxr-xr-x user      0 old
user@host:/home/user/docs$ tac notes.txt
third line
second line
first line
user@host:/home/user/docs$ cd ../../..
user@host:/$ date
Thu Oct 08 19:00:03 MSK 2026
user@host:/$ date +%d.%m.%Y
08.10.2026
user@host:/$ uname -sm
Darwin arm64
user@host:/$ mkdir -p /home/user/projects/lab
user@host:/$ mkdir /tmp/a /tmp/b
user@host:/$ ls /tmp
a  b
user@host:/$ chmod 700 /home/user/projects
user@host:/$ chmod go-r /etc/passwd
user@host:/$ chmod +x /etc/hostname
user@host:/$ ls -l /etc
-rwxr-xr-x user      8 hostname
-rw------- user     71 passwd
user@host:/$ mkdir /etc
mkdir: cannot create directory '/etc': File exists
user@host:/$ cd /etc/passwd
cd: /etc/passwd: Not a directory
user@host:/$ hello
hello: command not found
user@host:/$ exit
```

После `exit` окно закрывается.

Выполнение стартового скрипта `startup/stage3.txt` с минимальной VFS
(скрипт останавливается на первой ошибке):

```
user@host:/$ vfs-info
name: minimal
sha256: f8140ba88b1f3d0d526b351aeff0501cef74d159164ccb825f5748b0b1cc26c6
user@host:/$ conf-dump
vfs=vfs/minimal.xml
script=startup/stage3.txt
user@host:/$ ls
hello.txt
user@host:/$ ls -l
-rw-r--r-- user     13 hello.txt
user@host:/$ cd /
user@host:/$ cd
user@host:/$ vfs-info --all
vfs-info: too many arguments
Выполнение скрипта остановлено из-за ошибки
```
