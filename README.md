# c41c_converter
конвертер замеров для [coverage41c](https://github.com/1c-syntax/Coverage41C)

написал конвертер из `<file path="ce9e15dd-8927-49d5-a8ff-b33c337b7c1e/32e087ab-1491-49b6-aba7-43571b41ac2b">` в `<file path="DataProcessors/ЖурналДокументовНМА2_4/Forms/ДокументыПоНМА/Ext/Form/Module.bsl">`

работает как с исходниками в формате выгрузки в xml, так и с edt (mdo)

пример использования
```console
> .\c41c_convert.py --config-path C:\test\src --measures-path C:\Users\Kuznetsov_NA\Desktop\temp\coverage41c\Zamer\pff\xml --output C:\test\res
Parsing .xml: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 21794/21794 [00:05<00:00, 4323.48it/s]
Parsing .mdo: 0it [00:00, ?it/s]
Результат записан в C:\test\res\openformsdataprocessors\genericCoverage.xml
```
