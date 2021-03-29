# Courier api
**alpha version**

### Как запускать на Ubuntu?
1) Прописываем команды:

```
sudo apt install python3-pip
pip3 install pydantic
pip3 install SQLAlchemy
pip3 install flask
sudo apt install git
```
2) Клонируем проект на виртуальную машину
3) Заходим в папку courier_api
```cd courier_api```
   
4) Прописываем команду
```python3 main.py```
   
***Минусы этого способа***
* При перезагрузке виртуальной машины необходимо вручную запускать сервер
* Устанавливать все пакеты приходится в ручную 
***
### Вариант установки номер 2
***На случай, если вы работали с docker'ом или у Вас было больше недели на проект***
</br>Я не успел разобраться, но [Dockerfile](https://github.com/qvntz/courier_api/blob/main/Dockerfile) и [docker-compose.yml](https://github.com/qvntz/courier_api/blob/main/docker-compose.yml) вроде бы сделал,
__простите__

***Минусы этого способа***
* Еще не знаю

Для тех, кто дочитал:

Спасибо за этот опыт, который я получил, потратив недельку на этот проект (поздно прошел первый тур).
Эти знания мне пригодятся, да, и я освежил свои знания python.

Вы делаете круто в Яндексе, спасибо!