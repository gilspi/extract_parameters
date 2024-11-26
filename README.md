1. В курсовую работу пойдет следующее, чтобы было показано, скриншоты того как мы собираем проект с переносом всех файлов в нужные директории

2. Также нужно описать разницу моделей, почему одна модель называется bjt505t/bjt505

3. После того как мы провели изменения файла нужно переделать конфигурацию.
Мы изменили файл parameters.inc в директории /home/nikita/Рабочий стол/VA-Models/code/mextram/vacode
Далее нужно выполнить консольную команду посредством python ./openvaf bjt505.va
После этого сгенерируется файл bjt505.osdi, который нужно перенести в директорию /home/nikita/Рабочий стол/VA-Models/examples/mextram/ngspice
После того как перенесли файл в каталог мы запускаем его посредством языка python как делали это ранее

4. Возможность ввода данных с клавиатуры для изменения parameters.inc (если пользователь нажал Enter пустое значение, то оставить дефолтное значение)

5. Сделать построение графиков от изначальных значений ии от значений, которые получаются в результате изменения parameters.inc.

6. Сделать графический пользовательский интерейс, где можно будет ячейка для вписывания данных для каждого параметры. Эта область будет подписана, названием параметра. Если область пустая подразумевается, что она будет использовать значение по умолчанию. После того как пользователь изменил значение в какой-то ячейке он нажимает кнопку выполнить и выполняется алгоритм:
(После того как мы провели измененеия файла нужно переделать конфигурацию.
Мы изменили файл parameters.inc в директории /home/nikita/Рабочий стол/VA-Models/code/mextram/vacode
Далее нужно выполнить консольную команду посредством python ./openvaf bjt505.va
После этого сгенерируется файл bjt505.osdi, который нужно перенести в директорию /home/nikita/Рабочий стол/VA-Models/examples/mextram/ngspice
После того как перенесли файл в каталог мы запускаем его посредством языка python как делали это ранее). И на экран выводится график с результатом.

7. Добавить кнопку для подгрузки sp модели. Получается, что нужна кнопка, чтобы пользователь нажимал добавить, дальше выскакивал открыть и после этого на экран парсились только main parameters модели и дальше пользователь имел возможность их менять.


8. Добавить график измененный и по умолчанию, в одной системе координат (TODO)

9. Добавить выбор модели в директории например mextram ибо в одной директории может лежать несколько моделей
но сначала я прохожу по директории от /code/навзание модели/vacode и далее выбираю модель которая мне нужна. А сейчас выбирается только папка, но в папке можеть быть и две и три и четыре модели. И еще внутри модели у меня может быть несколько папок, например, vacode vacode504p12p1 и вообще любые, пользователь вручную выбирает путь к .va. 

10. Добавить чтобы сейчас хотел добавить
получается параметров много и не все для нас актуальны
поэтому нужно немного изменить парсер
сделать игнор файл, в котором будут прописаны параметры которые не нужно заносить в наш список
например, меня не интересует версия ибоя ее менять нельзя просто так
поэтому вот небольшой список параметров которые если парсер встретил, то мы не меняем

11. Добавить функционал для кнопки "Применить изменения", чтобы выбранный файл (parameters.inc или .va модель перезаписывались с новыми параметрами, а то что мы не изменяем осталвляло как было). Нужно будет искать в файл имена параметров которые совпадают с именами, которые мы изменили в GUI. Я вижу так мы выбрали файл, далее изменили какие-то параметры -> нажали кнопку ПРИМЕНИТЬ ИЗМЕНЕНИЯ -> пробигаемся по файлу который мы выбрали и ищем ключ (в нашем случае это имя параметра) и подставляем в его строку новое значение из поля GUI. Вот пример строки из файла
MPRco( nff            ,1.0,""            ,1.0         ,inf          ,"Non-ideality factor of forward main current" )
nff - ключ который мы нашли, а далее значение по умочанию, которое мы и должны перезаписать значением, которое ввел пользователь в нашем GUI.  

12. Добавить проверку, чтобы значения которые ввел пользователь входили в диапазон параметра. Пример
`MPRoo( njgs           ,2.53            ,""            ,0.0         ,50.0        ," Gate-source junction diode current ideality factor" )
0.0 - минимальной значение
50.0 - максимальное
`MPRco( ikbx           ,14.29m         ,"A"           ,1.0p        ,inf          ,"Extrinsic CB high injection knee current" )
1.0p - минммальное значение (p - пико)
inf - бесконечность, т.е верхнего предела нет
`MPRcz( ibr            ,1.0f           ,"A"                                      ,"Saturation current of non-ideal reverse base current" )
здесь вообще границ нет
Могут быть ситуации, когда нижней границы нет, но вехрняя есть или наоборот. (Доделать)

13. Вот я получаю такое окно после того, как нажал ЗАПУСТИТЬ СИМУЛЯЦИЮ и увидел что нельзя запустить  parameters.inc запускается вместе с openvaf
но так быть не должно потому что должен выбирать параметры модели и потом саму модель и уже эта модель должна учавствоать в openvaf 
например я нажал выбрать параметры у меня отобразились параметры (это может быть как parameters.inc так и .va, но .va модель сначала используем только для парсинга, но впоследствии мы должны нажать кнопку выбор модели и там мы уже выбираем модель и измененными параметрами) далее высветились параметры мы их меняем или не меняем
после это нужно сделать так чтобы пользователь выбирал КОНКРЕТНО МОДЕЛЬ которая будет использоваться в команде openvaf
поэтому сейчас мы должны изначально добавить кнопку применить изменения которая перезапишет или .inc или .va
добавить кнопку выбрать модель (самое главное что эта модель должна быть выбрана строго из той директории с которой был выбран parameters.inc или .va модель ранее)

Конкретно, что исправить
Добавить следующий функционал. На данном этапе у нас данные отлично парсятся из файла parameters.inc и из файла asmhemt.va. Нажимая на кнопку запустить симуляцию неправильно работает функционал:
1. изменили параметры модели
2. сохранили изменения (перезаписали файл)
3. выбрать модель (если файл не с расширением .va), если на предыдущем шаге меняли .va (например asmhemt.va) то эту модель и используем дальше
4. openvaf asmhent.va (пересобрать модель)
5. получили файл ashment.osdi -> переместить в OSDILIBS_PATH
6. выбрали схему из GUI (например nfet.sp)
7. нажать запустить симуляцию
8. отобразить графики

14. Доделать пункт 8 ибо на данном этапе парсер для simulation_data.txt работает неверно. Конкретно парсер должен быть гибким, это означает, что парсер должен гибко извлечь данные из файла simulation_data.txt. Пример файла
                      sample netlist asmhemt: id plot hemt
                      DC transfer characteristic  Tue Nov 26 17:51:56  2024
--------------------------------------------------------------------------------
Index   v-sweep         v(dt)           abs(i(vd))      
--------------------------------------------------------------------------------
0	0.000000e+00	0.000000e+00	0.000000e+00	
1	1.000000e-01	9.609412e-02	3.843765e-01	
2	2.000000e-01	3.600227e-01	7.200454e-01	
3	3.000000e-01	7.396821e-01	9.862428e-01	
4	4.000000e-01	1.185355e+00	1.185355e+00	
5	5.000000e-01	1.663121e+00	1.330496e+00	
6	6.000000e-01	2.153802e+00	1.435868e+00	
7	7.000000e-01	2.647728e+00	1.512988e+00	
8	8.000000e-01	3.140434e+00	1.570217e+00	
9	9.000000e-01	3.630077e+00	1.613367e+00	
10	1.000000e+00	4.116075e+00	1.646430e+00	
11	1.100000e+00	4.598418e+00	1.672152e+00	
12	1.200000e+00	5.077339e+00	1.692446e+00	
13	1.300000e+00	5.553154e+00	1.708663e+00	
14	1.400000e+00	6.027525e+00	1.723187e+00	
15	1.500000e+00	6.497933e+00	1.733569e+00	
16	1.600000e+00	6.966155e+00	1.742144e+00	
17	1.700000e+00	7.432428e+00	1.749277e+00	
18	1.800000e+00	7.896955e+00	1.755249e+00	
19	1.900000e+00	8.359912e+00	1.760275e+00	
20	2.000000e+00	8.821447e+00	1.764525e+00	
21	2.100000e+00	9.281689e+00	1.768130e+00	

Мы видим количество точек и знчение в этих точках, далее строим график по этим точкам. НО ключи v(dt) abs(i(vd)) могут отличаться. В данном случае они такие, в ином будут другие, парсер должен это учитывать.